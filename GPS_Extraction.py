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

for i in GROUPS:
    paths = os.listdir(MainPath + str(i) + AddPath)
    paths = [k for k in paths if 'DS_Store' not in k] #DS_Store not in k is a workaround .DS_Store files in Macs
    for y in paths:
        Data = load_GPS_files(y,MainPath,i)
        Data = GPS_Extraction(Data)
        Data.to_csv(SavePath + str(i) + '/GPS/' + y +'.csv')
