import numpy as np
import pandas as pd
import os
from pathlib import Path
import shutil
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pyproj import Proj
#Variables from configuration files
import config

ProcessedPath = config.SavePath
GROUPS = config.GROUPS

# Maximum number of individuals days for each group(atleast 4)
#{'NQ_2021_1': [['2021-08-11', '2021-08-12'], 5]
# 'ZU_2021_1': [['2021-05-18', '2021-05-19', '2021-05-20', '2021-05-21', '2021-05-22'], 6]
# 'ZU_2021_2': [['2021-07-21', '2021-07-22'], 4]}




def sync_gps_simultaneous(data,k,j):
    print('Duration of data',data.shape[0])
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    df =  data.groupby('Timestamp')
    dfnew = df.filter(lambda x: len(x['Individual'].unique())>=5)
    
    pp = Proj(proj='utm',zone=34,ellps='WGS84',south=True)

    xx, yy = pp(dfnew["lon"].values,dfnew["lat"].values)
    dfnew["X"] = xx
    dfnew["Y"] = yy 

    
    
    dfnew = dfnew.reset_index(drop=True)
    
    times = sorted(dfnew['Timestamp'].unique())
    time_start = times[0]
    time_end = times[-1]

    time_start = time_start + pd.Timedelta(seconds=30)
    time_end = time_end - pd.Timedelta(seconds=30)

    dfnew = dfnew.loc[(dfnew['Timestamp']>=time_start) & (dfnew['Timestamp']<=time_end)] 
    if j == '2021-05-18':  
        print('Seconds removed: ',len(dfnew.loc[((dfnew['X']<581950) & (dfnew['Y']>(7.02035e6)))]))
        dfnew = dfnew.loc[~((dfnew['X']<581950) & (dfnew['Y']>(7.02035e6)))] #for 3 erroneous points on '2021-05-18', remove for others
    
    else:
        pass
    dfnew=dfnew.reset_index(drop=True)
    
    print('Duration of Simultaneous data',dfnew.shape[0])
    return dfnew


k = 'ZU_2021_1' #ZGroups
j = '2021-05-19' #Day
fig,ax= plt.subplots(dpi=250)
data = pd.read_csv(ProcessedPath + str(k) + '/GPS_Days/'+ j,index_col=0)
data = sync_gps_simultaneous(data,k,j)

cdict = {0:'green', 1: 'blue', 2: 'red'}
data['codes'] = data['Behavior'].astype('category').cat.codes
path = '/media/amlan/Data/Thesis Data/Plots/'+str(j)+'_'+str(k)


time_start= j +' 09:20:46'
time_start =  pd.to_datetime(time_start)

time_end = j +' 09:30:47'
time_end =  pd.to_datetime(time_end)


subset = data.loc[(data['Timestamp']>=time_start) & (data['Timestamp']<=time_end)]
subset = subset.replace([np.inf, -np.inf], np.nan)
subset= subset.reset_index(drop=True)

shutil.rmtree(path, ignore_errors=True)
os.makedirs(path, exist_ok=True) 


for key,value in subset.groupby('Timestamp'):
    fig,ax = plt.subplots(dpi=300)
    #ax.set_aspect('equal', adjustable='box')

    width = 3
    ax.set_xlim(subset['X'].dropna().min()-width, subset['X'].dropna().max()+width)
    ax.set_ylim(subset['Y'].dropna().min()-width, subset['Y'].dropna().max()+width)
    
    ax.set_ylabel("UTM North")
    ax.set_xlabel("UTM East")
    ax.set_title('{} : {}'.format(k,key))
    ax.tick_params(axis='both', which='major', labelsize=8)
    ax.tick_params(axis='both', which='minor', labelsize=8)
    
    colors = value['codes'].apply(lambda x: cdict[x])
    ax.grid()
    ax.tick_params(axis='x', rotation=45)
    ax.scatter(value['X'],value['Y'],c=colors,label=value['Individual'])
    
    red_patch = mpatches.Patch(color='red', label='Vigilance')
    green_patch = mpatches.Patch(color='green', label='Foraging')
    blue_patch = mpatches.Patch(color='blue', label='Running')

    ax.legend(handles=[red_patch,green_patch, blue_patch])
    
    plt.tight_layout()
    plt.savefig(path +'/' + str(key),dpi=250)
    plt.close(fig)
    


import imageio.v2 as imageio
png_dir = path
with imageio.get_writer('/media/amlan/Data/Thesis Data/Plots/'+str(k + '_' + j)+'.gif', mode='I',fps=15) as writer:
    for filename in sorted(os.listdir(png_dir)):
        image = imageio.imread(path+'/'+filename)
        writer.append_data(image)