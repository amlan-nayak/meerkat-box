import numpy as np
import pandas as pd
import os
from pathlib import Path

import config

MainPath = config.BorisPath
SavePath = config.SavePath
GROUPS = config.GROUPS
AddPath = config.BorisAddPath


for k in GROUPS:
    paths = os.listdir(MainPath + str(k) + AddPath)
    paths = [i for i in paths if 'Aggregated' in i]
    for file in paths:
        print(file)
        Data = pd.read_csv(MainPath + str(k) + AddPath + file, usecols = ['Total length', 'Behavior','Start (s)', 'Stop (s)', 'Duration (s)', 'Time Elapsed','Timestamp'])
        Data = Data.loc[Data['Duration (s)']>3]
        Data = Data.reset_index(drop=True)

        time = pd.to_datetime(Data.Timestamp.loc[0])
        day = file.split('_')[3]
        audit_start_time = time.replace(year=int(day[0:4]), month=int(day[4:6]), day=int(day[6:8]))
        vid_start_time = Data['Time Elapsed'].loc[0]

        starts = np.ceil(Data['Start (s)'] - vid_start_time).astype(int) + 1
        starts[starts<0] = 0
        stops = np.floor(Data['Stop (s)'] - vid_start_time).astype(int) - 1

        times,labels =[],[]
        for i in range(len(starts)):
            for j in range(starts[i],stops[i]):
                times.append(audit_start_time + pd.Timedelta(seconds=j) - pd.Timedelta(hours=2))
                labels.append(Data.loc[starts == starts[i],'Behavior'].values[0])
        Boris = pd.DataFrame(zip(times,labels),columns=['Timestamp','Behavior'])
        final_save_path = SavePath + str(k) + '/Labels/'
        os.makedirs(final_save_path, exist_ok = True)
        newnames = file.split('Aggregated')[0]
        newnames = newnames.split('_')[3:]
        newnames[0] = newnames[0][0:4] +'-' + newnames[0][4:6] + '-' + newnames[0][6:]
        Boris.to_csv(final_save_path + '_'.join(newnames) + 'labels')