#All the necessary packages imported

import numpy as np
import pandas as pd
import os
from pathlib import Path

#Import the necessary configurations
#In my case, 4 Different Groups -  ZU_2021_1, ZU_2021_2, NQ_2021_1 and RW_2021_1
import config

MainPath = config.MainPath
SavePath = config.SavePath
GROUPS = config.GROUPS
AddPath = config.AddPath #

for i in GROUPS:
    os.makedirs(SavePath + str(i) + '/GPS', exist_ok=True) #Checks if Directory is present, if not, it creates one

def GPS_Extraction(Data):
    
    Data = Data.dropna(axis=0)
    print('Dimensions after removing NaN rows: ',Data.shape)
    Data = Data.reset_index(drop=True)
    Data['Timestamp'] = pd.to_datetime(Data['Timestamp'],format="%d/%m/%Y %H:%M:%S.%f")
    return Data

def load_GPS_files(FileName,MainPath,Group): 
    File = str(FileName) + '/' + str(FileName) + '.csv' 
    Data = pd.read_csv(MainPath + str(Group) + AddPath + File,usecols = ['Timestamp','location-lat','location-lon','height-msl']) 
    print('\nFile: ',FileName)
    print('Dimensions: ',Data.shape)
    return Data

def rename_df(Data):
    Data = Data.rename(columns={'location-lat': 'lat', 'location-lon': 'lon'})
    return Data

for i in GROUPS:
    paths = os.listdir(MainPath + str(i) + AddPath)
    paths = [k for k in paths if 'DS_Store' not in k] #DS_Store not in k is a workaround .DS_Store files in Macs
    for y in paths:
        Data = load_GPS_files(y,MainPath,i)
        Data = GPS_Extraction(Data)
        Data = rename_df(Data)
        if Data.empty:
            pass
        else:
            filename = '_'.join(y.split('_')[0:-1])
            Data['Day'] = pd.to_datetime(Data['Timestamp']).dt.date
            for key,value in Data.groupby('Day'):
                    value.drop(['Day'],axis=1,inplace=True)
                    value.reset_index(inplace=True)
                    value.to_csv(SavePath + filename + '_' + str(key))
            print("Data Processed for file: ",y)
            print('----')
