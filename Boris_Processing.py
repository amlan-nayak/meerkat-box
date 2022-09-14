import numpy as np
import pandas as pd


path = '/media/amlan/Data/Thesis Data/BORIS Data/NQ_2021_1/Event Data/'
file = 'NQ_VIDEO_BEHAVIOUR_20210811_VNQM011_Aggregated.csv'

Data = pd.read_csv(path + file, usecols = ['Total length', 'Behavior','Start (s)', 'Stop (s)', 'Duration (s)', 'Video Seconds Of Timestamp','Timestamp'])

Data = Data.loc[Data['Duration (s)']>1]

time = pd.to_datetime(Data.Timestamp.loc[0])
day = file.split('_')[3]
audit_start_time = time.replace(year=int(day[0:4]), month=int(day[4:6]), day=int(day[6:8]))
vid_start_time = Data['Video Seconds Of Timestamp'].loc[0]

starts = np.ceil(Data['Start (s)'] - vid_start_time).astype(int)
starts[starts<0] = 0
stops = np.floor(Data['Stop (s)'] - vid_start_time).astype(int)

times,labels =[],[]
for i in range(len(starts)):
    for j in range(starts[i],stops[i]):
        times.append(audit_start_time + pd.Timedelta(seconds=j))
        labels.append(Data.loc[starts == starts[i],'Behavior'].values[0])

Boris = pd.DataFrame(zip(times,labels),columns=['Timestamp','Behavior'])

Boris.to_csv(file.split('Aggregated')[0] + 'labels' + '.csv')