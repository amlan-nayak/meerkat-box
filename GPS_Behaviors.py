import numpy as np
import pandas as pd
import os
from pathlib import Path
import shutil

#Import the necessary configurations
#In my case, 4 Different Groups -  ZU_2021_1, ZU_2021_2, NQ_2021_1 and RW_2021_1
import config


ProcessedPath = config.SavePath
GROUPS = config.GROUPS 


#The loop below uses the ML model and predicts the behavior bouts for all the GPS files 
#it also smooths GPS files and inputs single missing NaN values between two actuals values with their mean

for k in GROUPS:
    
    SavePath = ProcessedPath + str(k) + '/GPS_Behaviors/'
    shutil.rmtree(SavePath, ignore_errors=True)
    os.makedirs(SavePath, exist_ok=True)    

    prediction = os.listdir(ProcessedPath + str(k) + '/Predictions/')
    paths = os.listdir(ProcessedPath + str(k) + '/GPS/')
    paths = [i for i in paths if '.ipynb' not in i]
    dates = [i.split('_')[-1] for i in paths]
    dates = list(np.unique(dates))
    individuals = [i.split('_')[1] for i in paths]
    individuals = list(np.unique(individuals))

    for p in paths:
        file = p.split('_')
        for i in prediction:
            if str(file[1]) in i and str(file[-1]) in i:
                gps =  pd.read_csv(ProcessedPath + str(k) + '/GPS/'+ p,usecols = ['Timestamp','lat','lon','height-msl'])
                gps.iloc[:,1:] = gps.iloc[:,1:].rolling(window=3,center=True,min_periods=2).mean()
                gps =  gps.iloc[1:-1]
                behavior = pd.read_csv(ProcessedPath + str(k) + '/Predictions/'+ i,usecols = ['Timestamp','Behavior'])
                final_gps = pd.merge(gps, behavior, on=['Timestamp'],how='inner')
                final_gps.reset_index(inplace=True,drop=True)
                final_gps.to_csv(SavePath + '/' + p)  

#The loop uses the predictions files, and separates them according to the specific days making a GPS Days folders 
#The GPS folders has all the locations of all individuals of a particular group for a particular day

for k in GROUPS:
    
    SavePath = ProcessedPath + str(k) + '/GPS_Days/'
    shutil.rmtree(SavePath, ignore_errors=True)
    os.makedirs(SavePath, exist_ok=True) 
    
    paths = os.listdir(ProcessedPath + str(k) + '/GPS_Behaviors/')
    paths = [i for i in paths if '.ipynb' not in i]
    dates = [i.split('_')[-1] for i in paths]
    dates = list(np.unique(dates))
    individuals = [i.split('_')[1] for i in paths]
    individuals = list(np.unique(individuals))
    
    for i in dates:
        day_data = pd.DataFrame(columns=['Timestamp','lat','lon','height-msl','Behavior','Individual'])
        for j in paths:
            if i in j:
                data = pd.read_csv(ProcessedPath + str(k) + '/GPS_Behaviors/'+ j,index_col=0)
                data['Individual'] = j.split('_')[1]
                day_data = pd.concat([day_data,data],axis=0)
        day_data.reset_index(inplace=True,drop=True)
        day_data.to_csv(SavePath+'/'+ i)
    