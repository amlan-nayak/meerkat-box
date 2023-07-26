# %%
import numpy as np
import pandas as pd
import os
from pathlib import Path
from collections import defaultdict
import shutil
import joblib

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

 
pipeline = joblib.load('/media/amlan/Data/Thesis Data/Processed Data/RF_model.mod')


GROUPS = ['NQ_2021_1','RW_2021_1','ZU_2021_1','ZU_2021_2']


predict_data = pd.DataFrame()
for k in GROUPS:
    ACCPath = '/media/amlan/Data/Thesis Data/Processed Data/'+k+'/ACC/'
    PredictPath = '/media/amlan/Data/Thesis Data/Processed Data/'+k+'/Predictions/'
      
    shutil.rmtree(PredictPath, ignore_errors=True)
    os.makedirs(PredictPath, exist_ok=True)

    ACCpaths = os.listdir(ACCPath)
    
    ACCpaths = [i for i in ACCpaths if '.ipynb_checkpoints' not in i]
    

    for i in ACCpaths:
        
        main_file = pd.read_csv(ACCPath + i,index_col=0)
        
        main_file.reset_index(drop=True,inplace=True)
    
        Data= main_file.drop(['StdNorm','VeDBA'],axis=1).iloc[:,1:]
        
        main_file['Behavior'] = pipeline.predict(Data)
        filename = i.split('_')
        main_file['Group'] = filename[0]
        main_file['Individual'] = filename[1]
        if k == 'NQ_2021_1':
            main_file['Axy'] = filename[4]
        else:
            main_file['Axy'] = filename[3][3:]
        
        main_file.to_csv(PredictPath + '_'.join(filename[0:2]) + '_' + filename[-1])
        #predict_data = pd.concat([predict_data,main_file],axis=0)
        print('Predicted For: ','_'.join(filename[0:2]) + '_' + filename[-1])
        



