import numpy as np
import pandas as pd
import os
from pathlib import Path
from collections import defaultdict

import config
GROUPS = config.GROUPS
#GROUPS = ['NQ_2021_1','RW_2021_1','ZU_2021_2']

train_data = pd.DataFrame(columns=['Timestamp','Behavior','Group','Individual'])

for k in GROUPS:
    ACCPath = '/media/amlan/Data/Thesis Data/Processed Data/'+k+'/ACC/'
    LabelPath = '/media/amlan/Data/Thesis Data/Processed Data/'+k+'/Labels/'
    ModelData = '/media/amlan/Data/Thesis Data/Processed Data/'+k+'/ModelData/'

    os.makedirs(ModelData, exist_ok=True)

    ACCpaths = os.listdir(ACCPath)
    Labelpaths = os.listdir(LabelPath)
    
    d = defaultdict(list)

    for i in ACCpaths:
        for j in Labelpaths:
            if i.split('_')[1] in j:
                d[i].append(j)
                
    for i in d.keys():
        
        main_file = pd.read_csv(ACCPath + i,index_col=0)
        side_files = pd.DataFrame(columns=['Timestamp','Behavior'])
        
        for j in d[i]:
            label_files = pd.read_csv(LabelPath + j,index_col=0)
            side_files = pd.concat([side_files,label_files])
            side_files = side_files.reset_index(drop=True)
        training_data = pd.merge(main_file, side_files, on=['Timestamp'],how='inner')
        training_data['Group'] = i.split('_')[0]
        training_data['Individual'] = i.split('_')[1]
        if training_data.empty:
                pass
        else:
                training_data.to_csv(ModelData+i)    
                train_data = pd.concat([train_data,training_data])  
                print(j) 
        

train_data.to_csv('/media/amlan/Data/Thesis Data/Processed Data/'+'train_data.csv')
