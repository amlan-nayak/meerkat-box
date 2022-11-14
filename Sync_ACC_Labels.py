#Necessary Packages
import numpy as np
import pandas as pd
import os
from pathlib import Path
from collections import defaultdict
import shutil

#Configuration files
import config
GROUPS = config.GROUPS

#We define an empty dataframe to concat data later in our loop
train_data = pd.DataFrame(columns=['Timestamp','Behavior','Group','Individual'])


#We iterate through the groups and a make special dictionary with keys as ACC file names and values as audit labels for the same day as ACC files
#We extract timestamp and behavior from the audit labels and combine with the ACC file to form a dataset of features and corresponding behavior with timestamps

for k in GROUPS:
    ACCPath = '/media/amlan/Data/Thesis Data/Processed Data/'+k+'/ACC/'
    LabelPath = '/media/amlan/Data/Thesis Data/Processed Data/'+k+'/Labels/'
    ModelData = '/media/amlan/Data/Thesis Data/Processed Data/'+k+'/ModelData/'
    RunningPath = '/media/amlan/Data/Thesis Data/Processed Data/'+k+'/RunningLabels/'  

    shutil.rmtree(ModelData, ignore_errors=True)
    os.makedirs(ModelData, exist_ok=True)

    ACCpaths = os.listdir(ACCPath)
    Labelpaths = os.listdir(LabelPath)
    Runningpaths = os.listdir(RunningPath)
    sync_dict = defaultdict(list)

    for i in ACCpaths:
        for j in Labelpaths:
            if i.split('_')[1] in j and i.split('_')[-1] in j: 
                sync_dict[i].append(j)
            
           
    for i in sync_dict.keys():
        
        main_file = pd.read_csv(ACCPath + i,index_col=0)
        side_files = pd.DataFrame(columns=['Timestamp','Behavior'])
        print(i,sync_dict[i])

        for j in sync_dict[i]:
            label_files = pd.read_csv(LabelPath + j,index_col=0)
            #label_files = label_files[label_files['Behavior']!='Running'] #Excludes videos running bouts
            side_files = pd.concat([side_files,label_files])
            #try:
            #    running_files =  pd.read_csv(RunningPath + j,index_col=0) #Includes GPS running Bouts
            #    side_files = pd.concat([side_files,running_files])
            #    #side_files = side_files.drop_duplicates(subset=['Timestamp'])
            #except:
            #   pass
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
            print('No Sync Possible for','_'.join(filename[0:2]) + '_' + filename[-1])
        else:
            training_data.to_csv(ModelData + '_'.join(filename[0:2]) + '_' + filename[-1])    
            train_data = pd.concat([train_data,training_data])  
            print('Synced: ' + '_'.join(filename[0:2]) + '_' + filename[-1]) 
            print('----------')

train_data.to_csv('/media/amlan/Data/Thesis Data/Processed Data/'+'train_data.csv')
