
#Necessary Packages
import numpy as np
import pandas as pd
import os
import random
from pathlib import Path
from collections import defaultdict
import shutil

#Configuration files
import config
GROUPS = config.GROUPS

#We define an empty dataframe to concat data later in our loop
train_data = pd.DataFrame(columns=['Timestamp','Behavior','Group','Individual'])

#We iterate through the groups and a make special dictionary with keys as ACC file names and values as Running labels for the same day as ACC files
#We extract timestamp and behavior from the running labels and combine with the ACC file to form a dataset of features and corresponding behavior with timestamps

for k in GROUPS:

    ACCPath = '/media/amlan/Data/Thesis Data/Processed Data/'+k+'/ACC/'
    ModelData = '/media/amlan/Data/Thesis Data/Processed Data/'+k+'/ModelData/'
    RunningPath = '/media/amlan/Data/Thesis Data/Processed Data/'+k+'/RunningLabels/' 
    
    os.makedirs(ModelData, exist_ok=True)
    

    ACCpaths = os.listdir(ACCPath)
    Runningpaths = os.listdir(RunningPath)
    sync_dict = defaultdict(list)

    for i in ACCpaths:
        for j in Runningpaths:

            if i.split('_')[1] in j and i.split('_')[-1] in j: 

                sync_dict[i].append(j)
    print(sync_dict)        

    for i in sync_dict.keys():
        
        main_file = pd.read_csv(ACCPath + i,index_col=0)
        side_files = pd.DataFrame(columns=['Timestamp','Behavior'])
        
        for j in sync_dict[i]:

            label_files = pd.read_csv(RunningPath + j,index_col=0)
            side_files = pd.concat([side_files,label_files])
            side_files = side_files.reset_index(drop=True)
       
        training_data = pd.merge(main_file, side_files, on=['Timestamp'],how='inner')
        filename = i.split('_')
        training_data['Group'] = filename[0]
        training_data['Individual'] = filename[1]
        
        if k == 'NQ_2021_1':
            training_data['Axy'] = filename[4]
        else:
            training_data['Axy'] = filename[3][3:]

        if training_data.empty:
            pass
        else:   
    
            training_data.to_csv(ModelData + '_'.join(filename[0:2]) + '_' + filename[-1] + '_' + 'Running')    
            train_data = pd.concat([train_data,training_data])  
            print('_'.join(filename[0:2]) + '_' + filename[-1]) 
        

train_data.to_csv('/media/amlan/Data/Thesis Data/Processed Data/'+'run_train_data.csv')