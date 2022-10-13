import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from pathlib import Path

import config
Groups = config.GROUPS
Group_freq = config.FREQUENCY

def clean_leading_zeros(df):
    
    if pd.to_datetime(df.loc[1,'Timestamp']) - pd.to_datetime(df.loc[0,'Timestamp']) >= pd.Timedelta(1, "s") :
        Leading_Zeros = df.loc[~(df.drop(['Timestamp'],axis=1)==0).all(axis=1)]
        if Leading_Zeros.empty:
            return Leading_Zeros
        else:
            print('There are leading zeros till ',Leading_Zeros.index[0])
            return df.loc[Leading_Zeros.index[0]::,:]
    else:
        return df

def load_ACC_files(x,MainPath):
    
    File = str(x) + '/' + str(x) + '.csv' 
    Data = pd.read_csv(MainPath + File,usecols = ['Timestamp','X','Y','Z'])
    print('--------------------------------------------------')
    print('\nFile: {} with Dimensions {}'.format(x,Data.shape))
    print('Data in the file:')
    print(Data.head(3))
    
    Data = clean_leading_zeros(Data)
    print('\nData After Cleaning Leading Zeros:')
    print(Data.head(3)) 
    
    print('Dimensions after removing leading empty rows: ',Data.shape)
    Data = Data.reset_index(drop=True)
          
    return Data    
    

def feature_extraction_ACC(Data,Unique_Time,freq):

        Values = Data.iloc[0:Unique_Time*freq,1:4].to_numpy()
        Norm = np.sqrt(np.sum(np.square(Values),axis=1))
        t = pd.to_datetime(Data.loc[0:Unique_Time*freq-1:freq,'Timestamp'],format="%d/%m/%Y %H:%M:%S.%f")
        StdNorm = np.std(Norm.reshape(Unique_Time,freq),axis=1,ddof=1)
        
        
        Values_reshape = Values.reshape((Unique_Time,freq,3))
        means = np.mean(Values_reshape,axis=1)
        maxes = np.max(Values_reshape,axis=1)
        mins = np.min(Values_reshape,axis=1)
        var = np.var(Values_reshape,axis=1)
        
        Normalised_Values = Values - np.repeat(means,freq,axis=0)
        NORM = np.sum(np.square(Normalised_Values),axis=1)
        VEDBA = np.sqrt(NORM)
        VEDBA = np.mean(VEDBA.reshape((Unique_Time,freq)),axis=1)
        
        Features_Data = pd.DataFrame(columns=['Timestamp','X_Mean','Y_Mean','Z_Mean','X_Var','Y_Var','Z_Var','X_Max','Y_Max','Z_Max','X_Min','Y_Min','Z_Min','VeDBA','StdNorm'])
        Features_Data['Timestamp'] = t
        Features_Data['StdNorm'] = StdNorm
        Features_Data['VeDBA'] = VEDBA
        Features_Data.iloc[:,1:4] = means
        Features_Data.iloc[:,4:7] = var
        Features_Data.iloc[:,7:10] = maxes
        Features_Data.iloc[:,10:13] = mins
        
        
        return Features_Data



for k in range(len(Groups)):
    
    MainPath = 'MoveComm2021/' + str(Groups[k]) + '/GPS/'
    SavePath = 'Processed Data/' + str(Groups[k]) + '/ACC/'

    paths = os.listdir(MainPath)
    paths = [i for i in paths if 'DS_Store' not in i]

    os.makedirs(SavePath, exist_ok=True)
    
    freq = int(Group_freq[k])
    
    
    for y in paths:


        Data = load_ACC_files(y,MainPath)
        
        Unique_Time= Data.shape[0]//freq
        print('\nUnique Times: ',Unique_Time)

        print('Dimension of ACC Values After Considering Unique Times: ({},{}) '.format(Unique_Time*freq,4))
        Features_Data = feature_extraction_ACC(Data,Unique_Time,freq)
        Features_Data = Features_Data.reset_index(drop=True)
        
        if Features_Data.empty:
            pass
        else:
            print("Data Processed for file: ",y)
            Features_Data.to_csv(SavePath + y)