import numpy as np
import pandas as pd
import os
from pathlib import Path


#Variables from configuration files
import config

MainPath = config.BorisPath
SavePath = config.SavePath
GROUPS = config.GROUPS
AddPath = config.BorisAddPath

#The loop iterates through all audit files. It extracts the bouts which occur for more than 2 secs alonside the time elapsed in the video when the timestamp is mentioned
#The file name is used to find the day, and combined with the video timestamp. 
#During transitions of a behavior to another, the time is rounded down and up to the nearest second for the respective behaviors and additional sec is added and removed to robustly avoid transition period data.
#Kalahari time(UTC +2 Hrs) is corrected into UTC and a dataframe is prepared with timestamps and corresponding behavior.


for k in GROUPS:

    paths = os.listdir(MainPath + str(k) + AddPath)
    paths = [i for i in paths if 'Aggregated' in i]

    for file in paths:

        print(file)

        Data = pd.read_csv(MainPath + str(k) + AddPath + file, usecols = ['Total length', 'Behavior','Start (s)', 'Stop (s)', 'Duration (s)', 'Time Elapsed','Timestamp'])
        Data = Data.loc[Data['Duration (s)']>2]
        Data = Data.reset_index(drop=True)

        time = pd.to_datetime( Data.loc[0,'Timestamp'] )
        day = file.split('_')[3]
        audit_start_time = time.replace(year=int(day[0:4]), month=int(day[4:6]), day=int(day[6:8]))
        vid_start_time = Data.loc[0,'Time Elapsed']

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