# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime as dt
import random
import matplotlib.dates as mdates


plt.rcParams.update({'font.size': 22})
# %%


k = 'ZU_2021_1'
ModelData = '/media/amlan/Data/Thesis Data/Processed Data/'+k+'/ModelData/'



Modelpaths = os.listdir(ModelData)
Modelpaths = [i for i in Modelpaths if 'Running' not in i]
print(Modelpaths)

def Group_Behaviours(df):
    df.loc[df['Behavior'] == 'Sitting vigilance','Behavior'] = 'Vigilance'
    df.loc[df['Behavior'] == 'Bipedal vigilance','Behavior'] = 'Vigilance'
    df.loc[df['Behavior'] == 'Haunch quadrupedal vigilance','Behavior'] = 'Vigilance'
    df.loc[df['Behavior'] == 'Standing quadrupedal vigilance','Behavior'] = 'Vigilance'
    df.loc[df['Behavior'] == 'Walking','Behavior'] = 'Foraging'
    df.loc[df['Behavior'] == 'Scrabbling','Behavior'] = 'Foraging' #Change
    df.loc[df['Behavior'] == 'Reforage','Behavior'] = 'Foraging'
    df.loc[df['Behavior'] == 'Social','Behavior'] = 'Others'
    df.loc[df['Behavior'] == 'Processing','Behavior'] = 'Others'
    df.loc[df['Behavior'] == 'Self groom','Behavior'] = 'Others'
    df.loc[df['Behavior'] == 'Marking','Behavior'] = 'Others' 
    return df

r = random.Random()
r.seed("test")
myFmt = mdates.DateFormatter('%H:%M')



#Plots the Log Vedba alongside the behavioral audits with dotted lines showing the transitions
for i in Modelpaths:
    
    Data = pd.read_csv(ModelData+i,usecols =['Timestamp','VeDBA','Behavior'])
    Data = Data[Data['Behavior'] != 'No observation']
    Data = Data[Data['VeDBA'] > 1e-6]
    Data['VeDBA']  = np.log(Data['VeDBA'])
    Data['VeDBA']  = Data['VeDBA'].rolling(window=3,center=True).mean()
    Data = Data.dropna(axis=0)
    Data = Data.rename(columns={'VeDBA': 'Log VeDBA'})
    Data = Group_Behaviours(Data)
    Data['Timestamp'] = pd.to_datetime(Data['Timestamp'])
    
    
    

    
    n = random.randint(0, Data.shape[0]- Data.shape[0]//2)
    Data = Data.loc[n:n+Data.shape[0]//4,:]
    Data = Data.reset_index(drop=True)
    fig,ax = plt.subplots(figsize=(14,7),dpi=100)
    x = Data['Timestamp']
    z = Data['Log VeDBA']
    
    ax.plot(x, z, label='Log VeDBA')
    ax.set(xlabel='Time', ylabel='Log VeDBA')
    ax.set_title(i)
    ax.xaxis.set_major_formatter(myFmt)

    for state, values in Data.groupby('Behavior'):
        ax.scatter(values['Timestamp'], [1.4]*len(values['Timestamp']), label=state)
    
    for j in range(1,Data.shape[0]-1):
        if Data.loc[j,'Behavior'] != Data.loc[j+1,'Behavior']:
            plt.axvline(x=Data.loc[j+1,'Timestamp'], color='r',label = 'Transition',ls='--')
        else:
            pass
    
    
    handles, labels = ax.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
    ax.legend(*zip(*unique))
    
    
    plt.tight_layout()
    plt.show()
    


