# %%
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from pathlib import Path
from math import sin, cos, sqrt, atan2, radians
import random
import shutil
import config

plt.rcParams.update({'font.size': 15})

GROUPS = config.GROUPS
ProcessedPath = config.SavePath

def calc_velocity(lat1,lat2,lon1,lon2,time_res):
        R = 6371 # Radius of the earth in km
        dLat = radians(lat2-lat1)
        dLon = radians(lon2-lon1)
        rLat1 = radians(lat1)
        rLat2 = radians(lat2)
        a = sin(dLat/2) * sin(dLat/2) + cos(rLat1) * cos(rLat2) * sin(dLon/2) * sin(dLon/2) 
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        d = R * c * 1000 # Distance in metres
        velocity = d/time_res
        return velocity

# %%





Velo = pd.Series(dtype='float64')
for k in GROUPS:
    MainPath =ProcessedPath + str(k) + '/GPS/'
    RunningData = ProcessedPath + k + '/RunningLabels/' 

    shutil.rmtree(RunningData, ignore_errors=True)
    os.makedirs(RunningData)

    paths = os.listdir(MainPath)
    paths = [i for i in paths if '.ipynb_checkpoints' not in i]
    paths = random.sample(paths,len(paths)//4)
    
    for y in paths:
        try:    
            Data = pd.read_csv(MainPath + y,usecols = ['Timestamp','lat','lon'],dtype = {'Timestamp': str, 'lat': float, 'lon': float})
            Data['Timestamp'] = pd.to_datetime(Data['Timestamp'])
            Data.iloc[:,1] = Data[['lat','lon']].rolling(window=3,center=True).mean()
            Data = Data.dropna(axis=0)
            vels = []  
            time_res = 1  
            for i in Data.index:
                lat2 = Data.loc[i,'lat']
                lon2 = Data.loc[i,'lon']
                try:
                    lat1 = Data.loc[i-time_res,'lat']
                    lon1 = Data.loc[i-time_res,'lon']
                    vels.append(calc_velocity(lat1,lat2,lon1,lon2,time_res))
                except:
                    vels.append(0)

            Data['Velocity'] = vels
            Velo =  pd.concat([Velo,Data['Velocity']],axis=0)

            Data = Data[(Data['Velocity']>4) & (Data['Velocity']<10)]
            Data['Behavior'] = 'RunningGPS'
            Data['Current'] =  Data.index
            Data['End'] =  Data['Current'].shift(-1)
            Data['Previous'] =  Data['Current'].shift(1)
            Data = Data[((Data['End'] - Data['Current']) == 1) & ((Data['Current'] - Data['Previous']) == 1)]
            Data.drop(['lat','lon','Velocity','Current','Previous','End'],axis=1,inplace=True)
            if Data.empty:
                pass
            else:
                filename = y.split('_')
                Data.to_csv(RunningData + filename[-1] + '_' + filename[1]+'_labels')
                print(filename[-1] + '_' + filename[1]+'_labels')
        except:
            pass
  


# %%

plt.figure(dpi=250)
plt.hist((Velo[(Velo>2) & (Velo<10)]),bins=60) 
plt.title('Histogram of Velocity')
plt.xlabel('Velocity')
plt.ylabel('Instances(Log Scale)')
plt.yscale('log')
plt.show()

# %%



