import io
import os
from flask import Flask,request,render_template,jsonify,send_file,redirect,url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from src.preprocessing import Preprocessor
import pickle
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
application=Flask(__name__)

app=application
app.secret_key = 'your secret key'
 
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'rohit'
app.config['MYSQL_DB'] = 'thyroid'
 
 
mysql = MySQL(app)

app.static_folder = 'reports'
hospital=[]
pre = Preprocessor()
@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
# @cross_origin()
def predict():
    if request.method == 'POST':
        try:
            if 'csvfile' not in request.files:
                return render_template("invalid.html")
            file = request.files['csvfile']
            split_tup = os.path.splitext(file.filename)
            if split_tup[1] !='.csv' or split_tup[1] =='.xlsx':
                return render_template("invalid.html")
            if split_tup[1]=='.csv':
              df = pd.read_csv(file)
            else:
                df= pd.read_excel(file)
            hospital.append(str(request.form.get('hospital')))
            data = pre.dropUnnecessaryColumns(df)
            data = pre.replaceInvalidValuesWithNull(data)
            lblEn = pre.encodeClass(data)
            data= pre.encodeColumns(data)
            data= pre.convertToint(data)
            user_x_test = pre.pipeline(data)
            model = pickle.load(open('C:/Users/Rohit/Desktop/IMCC/projects/Thyroid-project/src/thyroid.pkl','rb'))
            print(user_x_test)
            result = model.predict(user_x_test)
            predictions = lblEn.inverse_transform(result)
            prediction_df = pre.prediction_data(df,predictions)
            print(np.unique(predictions))
            prediction_df.to_csv('notebooks/predictions.csv')
            savePredictions(prediction_df,hospital[-1])
            saveReports(df,hospital[-1])
        except Exception as e:
            print(e)
            return render_template("invalid.html")
    # return redirect(url_for('result'))
    return redirect(url_for('showReport'))

def savePredictions(data,hospital):
    try:
        cursor = mysql.connection.cursor()
        for i in range(len(data)):
            row_values = list(data.iloc[i].values)
            row_values.append(str(hospital))
            # row_values.append('abc')
            print(tuple(row_values))
            placeholders = ', '.join(['%s'] * len(row_values))
            sql_insert = "INSERT INTO thyroid_prediction VALUES ({})".format(placeholders)
            cursor.execute(sql_insert, tuple(row_values))
            mysql.connection.commit()
            # cursor.execute(''' INSERT INTO thyroid_prediction VALUES(%s)''',(final_data,))
            # value = cursor.fetch()
            row_values.clear()
        cursor.close()
        
            # print(value)
    except Exception as e:
        print('91')
        print(e)
    # return True


def saveReports(df,hosptial):
    try:
        i=1
        placeholders=[]
        data = pre.replaceInvalidValuesWithNull(df)
        data = pre.convertToint(data)
        # # data['Class'] = data['Class'].map({0 : 'negative', 1 : 'compensated_hypothyroid', 2:'primary_hypothyroid', 3:'secondary_hypothyroid'})
        # fig = Figure(figsize=(12, 6))
        # canvas = FigureCanvas(fig)
        # ax = fig.add_subplot(111)
        # sns.histplot(binwidth=0.5, x="Class", hue="sex", data=data, stat="count", multiple="stack", ax=ax)
        # ax.set_xticklabels(ax.get_xticks(), rotation='vertical')

        # # Create a buffer to store the plot image
        # buffer = io.BytesIO()
        # canvas.print_png(buffer)
        # buffer.seek(0)

        # # Read the image data from the buffer
        # image_data = buffer.getvalue()
        # cursor = mysql.connection.cursor()
        # # row_values=[hospital,image_data,str(hospital[-1])+str(i)]
        # placeholders.append(', '.join(['%s'] * len(row_values)))
        # sql_insert = "INSERT INTO thyroid_reports VALUES ({})".format(placeholders[-1])
        # # Execute the SQL INSERT statement
        # cursor.execute(sql_insert, tuple(row_values))
        # mysql.connection.commit()
        # i+=1

       

      # Define the filepath where you want to store the image
        image_filepath = os.path.join('reports', f'{str(hospital[-1])}_{str(i)}.png')
        # Create the plot
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        sns.histplot(binwidth=0.5, x="Class", hue="sex", data=data, stat="count", multiple="stack", ax=ax)
        ax.set_xticklabels(ax.get_xticks(), rotation='vertical')
        if os.path.exists(image_filepath):
            # Remove the existing image file
            os.remove(image_filepath)
        # Save the plot to the file path
        fig.savefig(image_filepath)

        # Close the plot to release resources
        plt.close(fig)
        row_values=[hospital[-1],'',str(hospital[-1])+'_'+str(i)]
        placeholders.append(', '.join(['%s'] * len(row_values)))
        cursor = mysql.connection.cursor()
        sql_insert = "INSERT INTO thyroid_reports VALUES ({})".format(placeholders[-1])
        # Execute the SQL INSERT statement
        cursor.execute(sql_insert, tuple(row_values))
        mysql.connection.commit()
        i+=1

      # Define the filepath where you want to store the image
        image_filepath = os.path.join('reports', f'{str(hospital[-1])}_{str(i)}.png')
      # Create the plot
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        sns.histplot(binwidth=0.5, x="Class", hue="pregnant", data=data, stat="count", multiple="stack",ax=ax)
        ax.set_xticklabels(ax.get_xticks(), rotation='vertical')
        if os.path.exists(image_filepath):
            # Remove the existing image file
            os.remove(image_filepath)
        # Save the plot to the file path
        fig.savefig(image_filepath)

        # Close the plot to release resources
        plt.close(fig)
        i+=1

        # Define the filepath where you want to store the image
        image_filepath = os.path.join('reports', f'{str(hospital[-1])}_{str(i)}.png')
      # Create the plot
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        sns.histplot(binwidth=0.5, x="Class", hue="thyroid_surgery", data=data, stat="count", multiple="stack")
        ax.set_xticklabels(ax.get_xticks(), rotation='vertical')
        if os.path.exists(image_filepath):
            # Remove the existing image file
            os.remove(image_filepath)
        # Save the plot to the file path
        fig.savefig(image_filepath)

        # Close the plot to release resources
        plt.close(fig)
        i+=1

        # Define the filepath where you want to store the image
        image_filepath = os.path.join('reports', f'{str(hospital[-1])}_{str(i)}.png')
      # Create the plot
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        sns.histplot(binwidth=0.5, x="Class", hue="tumor", data=data, stat="count", multiple="stack")
        ax.set_xticklabels(ax.get_xticks(), rotation='vertical')
        if os.path.exists(image_filepath):
            # Remove the existing image file
            os.remove(image_filepath)
        # Save the plot to the file path
        fig.savefig(image_filepath)

        # Close the plot to release resources
        plt.close(fig)
        i+=1

      # Define the filepath where you want to store the image
        image_filepath = os.path.join('reports', f'{str(hospital[-1])}_{str(i)}.png')
      # Create the plot
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        data["thyroid_surgery"].value_counts().plot(kind = "bar")
        ax.set_xticklabels(ax.get_xticks(), rotation='vertical')
        if os.path.exists(image_filepath):
            # Remove the existing image file
            os.remove(image_filepath)
        # Save the plot to the file path
        fig.savefig(image_filepath)

        # Close the plot to release resources
        plt.close(fig)
        i+=1

     # Define the filepath where you want to store the image
        image_filepath = os.path.join('reports', f'{str(hospital[-1])}_{str(i)}.png')
      # Create the plot
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        data["Class"].value_counts().plot(kind = "bar")
        ax.set_xticklabels(ax.get_xticks(), rotation='vertical')
        if os.path.exists(image_filepath):
            # Remove the existing image file
            os.remove(image_filepath)
        # Save the plot to the file path
        fig.savefig(image_filepath)

        # Close the plot to release resources
        plt.close(fig)
        
    except Exception as e:
       print('191')
       print(e)


@app.route('/fetchReport/<string:report_id>', methods=['GET'])
def fetchReport(report_id):
    try:
        sql_query = "SELECT report FROM thyroid_reports WHERE report_id =%s"
        # hospital_name = str(hospital[-1])  # Replace with the appropriate image ID
        cursor = mysql.connection.cursor()
        cursor.execute(sql_query, (report_id,))
        image_data = cursor.fetchone()[0]
        mysql.connection.commit()
        cursor.close()
        if image_data is not None:
           return send_file(io.BytesIO(image_data[0]), mimetype='image/png')
        else:
             return "Report not found"
    except Exception as e:
        print('206')
        print(e)
   


@app.route('/showReport', methods=['GET'])
def showReport():
    filePath=[]
    if len(hospital)!=0:
        for i in range(1,7):
            filePath.append(str(hospital[-1])+'_'+str(i)+'.png')
        return render_template('reports.html',file_paths=filePath)
    else:
        return render_template('reports.html')


@app.route('/showPredictions')
def showPredictions():
    try:
        sql_query = "SELECT patient_name,thyroid_type FROM thyroid_prediction WHERE hospital =%s"
        cursor = mysql.connection.cursor()
        cursor.execute(sql_query, (str(hospital[-1]),))
        prediction_data = cursor.fetchall()
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print('282')
        print(e)
    if len(hospital)==0:
        return render_template('predictions.html')
    return render_template('predictions.html',data=prediction_data)


@app.route('/hospitalReport')
def hospitalReport():
    try:
        sql_query = "SELECT hospital_name FROM thyroid_reports"
        cursor = mysql.connection.cursor()
        cursor.execute(sql_query)
        hospitals = cursor.fetchall()
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print('300')
        print(e)
    return render_template('hospitalReport.html',data=set(hospitals))    


@app.route('/showHospitalReport',methods=['POST'])
def showHospitalReport():
    if request.method =='POST':
        try:
            sql_query = "SELECT hospital_name FROM thyroid_reports"
            cursor = mysql.connection.cursor()
            cursor.execute(sql_query)
            hospital_data = cursor.fetchall()
            mysql.connection.commit()
            cursor.close()
            hospitals = set(hospital_data)
            filePath=[]
            for i in range(1,7):
                filePath.append(str(request.form.get('hospital'))+'_'+str(i)+'.png')
        except Exception as e:
            print('300')
            print(e)
        return render_template('hospitalReport.html',data=hospitals,file_paths=filePath)


@app.route('/hospitalPredictions',methods=['GET'])
def hospitalPredictions():
    try:
        sql_query = "SELECT hospital_name FROM thyroid_reports"
        cursor = mysql.connection.cursor()
        cursor.execute(sql_query)
        hospitals = cursor.fetchall()
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print('300')
        print(e)
    return render_template('hospital_predictions.html',data=set(hospitals))


@app.route('/showHospitalPredictions',methods=['POST'])
def showHospitalPredictions():
    if request.method =='POST':
        try:
            sql_query = "SELECT patient_name,thyroid_type FROM thyroid_prediction WHERE hospital =%s"
            cursor = mysql.connection.cursor()
            cursor.execute(sql_query, (str(request.form.get('hospital')),))
            prediction_data = cursor.fetchall()
            mysql.connection.commit()
            cursor.close()
        except Exception as e:
            print('282')
            print(e)
    return render_template('hospital_predictions.html',data=prediction_data)

if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)

