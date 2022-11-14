#The following packages are needed
import numpy as np
import pandas as pd
import os
from pathlib import Path

#config files has the important directory information for the different files
import config
Groups = config.GROUPS
Group_freq = config.FREQUENCY

#the raw ACC files have  preciding zero entries in some files, but not all files
#clean_leading_zeros function finds the first instant of a non zero entry and filters the data accordingly
def clean_leading_zeros(df):
    #the zero entries are every 30 seconds at the beginning. The files without zeros start with reading directly
    #the if statement checks if such a 30 seconds data exists at the start
    if pd.to_datetime(df.loc[1,'Timestamp']) - pd.to_datetime(df.loc[0,'Timestamp']) >= pd.Timedelta(1, "s") :
        #
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
        
        Normalised_Values = Data.iloc[freq:Unique_Time*freq,1:4].to_numpy() - np.repeat(means.to_numpy(),freq,axis=0)
        NORM = np.sum(np.square(Normalised_Values),axis=1)
        Residuals = np.sqrt(NORM)
        VAR_VEDBA = np.var(Residuals.reshape((Unique_Time-1,freq)),axis=1)
        MAX_VEDBA = np.max(Residuals.reshape((Unique_Time-1,freq)),axis=1)    
        MIN_VEDBA = np.min(Residuals.reshape((Unique_Time-1,freq)),axis=1)
        MEAN_VEDBA = np.mean(Residuals.reshape((Unique_Time-1,freq)),axis=1)
        
        
        Features_Data = pd.DataFrame(columns=['Timestamp','X_Mean','Y_Mean','Z_Mean','X_Var','Y_Var','Z_Var','X_Max','Y_Max','Z_Max','X_Min','Y_Min','Z_Min','VeDBA','Var_VeDBA','Min_VeDBA','Max_VeDBA','StdNorm'])
        Features_Data['Timestamp'] = t
        Features_Data['VeDBA'] = MEAN_VEDBA
        Features_Data['Min_VeDBA'] = MIN_VEDBA
        Features_Data['Max_VeDBA'] = MAX_VEDBA
        Features_Data['Var_VeDBA'] = VAR_VEDBA
        Features_Data['StdNorm'] = StdNorm
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
            filename = '_'.join(y.split('_')[0:-1])
            Features_Data['Day'] = pd.to_datetime(Features_Data['Timestamp']).dt.date
            for key,value in Features_Data.groupby('Day'):
                    value.drop(['Day'],axis=1,inplace=True)
                    value.reset_index(inplace=True)
                    value.to_csv(SavePath + filename + '_' + str(key))
            print("Data Processed for file: ",y)