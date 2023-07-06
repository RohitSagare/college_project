import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder,StandardScaler
from sklearn.compose import ColumnTransformer
import pickle

class Preprocessor:
         def dropUnnecessaryColumns(self,data):
            """
                        Method Name: dropUnnecessaryColumns
                        Description: This method drops the unwanted columns.
                                """
            try:
               data = data.drop(['TSH_measured', 'T3_measured', 'TT4_measured', 'T4U_measured',
                                                        'FTI_measured', 'TBG_measured', 'TBG','name'],axis=1)
            except Exception as e:
                print('20')
                print(e)
            return data
         

         def replaceInvalidValuesWithNull(self,data):

             """
                               Method Name: replaceInvalidValuesWithNull
                               Description: This method replaces invalid values i.e. '?' with null.
                                       """
             try:
               for column in data.columns:
                  count = data[column][data[column] == '?'].count()
                  if count != 0:
                     data[column] = data[column].replace('?', np.nan)
             except Exception as e:
                print('36')
                print(e)
             return data
         

         def encodeColumns(self,data):
            try:
               # We can map the categorical values like below:
               data['sex'] = data['sex'].map({'F' : 0, 'M' : 1})

               # except for 'Sex' column all the other columns with two categorical data have same value 'f' and 't'.
               # so instead of mapping indvidually, let's do a smarter work
               for column in data.columns:
                  if  len(data[column].unique())==2:
                     data[column] = data[column].map({'f' : 0, 't' : 1})
                  elif data[column].unique().any()=='f':
                       data[column] = data[column].map({'f' : 0})
                  elif data[column].unique().any()=='t':
                       data[column] = data[column].map({'t' : 1})
               data = pd.get_dummies(data, columns=['referral_source'])
            except Exception as e:
                print('52')
                print(e)
            return data

         def convertToint(self,data):
                  try:
                     numerical_cols=['age','T3','TT4','T4U','FTI']
                     imputer=KNNImputer(n_neighbors=3, weights='uniform',missing_values=np.nan)
                     new_array=imputer.fit_transform(data[numerical_cols]) # impute the missing values
                     # convert the nd-array returned in the step above to a Dataframe
                     new_data=pd.DataFrame(data=np.round(new_array), columns=numerical_cols)
                     new_data=new_data[numerical_cols].astype(int)
                     print(data.columns)
                     data[numerical_cols]=new_data
                  except Exception as e:
                     print('68')
                     # print(new_data)
                     # print(data.columns)
                     print(e)
                  return data


         def pipeline(self,data):
             """
                               Method Name: pipeline
                               Description: This method preprocesses and standardizes the data.

                                       """
             try:
               cat_data = data.drop(['age','T3','TT4','T4U','FTI','Class'],axis=1)
               cat_cols=cat_data.columns
               numerical_cols=['age','T3','TT4','T4U','FTI']
               
               ## Numerical Pipeline
               num_pipeline=Pipeline(
                  steps=[
                  ('scaler',StandardScaler())

                  ]

               )

               # Categorigal Pipeline
               cat_pipeline=Pipeline(
                  steps=[
                        ('imputer',SimpleImputer(strategy='most_frequent')),
                  ('scaler',StandardScaler())
                  ]

               )

               preprocessor=ColumnTransformer([
               ('num_pipeline',num_pipeline,numerical_cols),
               ('cat_pipeline',cat_pipeline,cat_cols)
               ])
               x_data=data.drop(['Class'],axis=1)
               user_x_test = preprocessor.fit_transform(x_data)
             except Exception as e:
                print('105')
                print(cat_cols)
               #  print(data.columns)
                print(e)
             return user_x_test
         

         def encodeClass(slef,data):
             lblEn = LabelEncoder()
             lblEn.fit(data['Class'])
             return lblEn
             

         def prediction_data(self,data,predictions):
             data = self.replaceInvalidValuesWithNull(data)
             prediction_df= pd.DataFrame(data['name'],columns=['name'])
             prediction_df['type'] = pd.DataFrame(predictions)
             return prediction_df