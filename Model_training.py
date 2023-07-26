import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix,accuracy_score,plot_confusion_matrix,mean_absolute_error,classification_report
from sklearn.pipeline import make_pipeline
import joblib

#Importing variables from config
from config import RunningEnough

#Loading the data consisting of features and labels 
data_file = '/media/amlan/Data/Thesis Data/Processed Data/kmeans_train_data'
df = pd.read_csv(data_file, index_col=0)
df = df.reset_index(drop=True)

#Removing labels with no observations, and very low vedba values for conversion in log scale
df = df[df.Behavior != 'No observation']
df = df[df.VeDBA > 1e-6]
df.VeDBA  = np.log(df.VeDBA)
df = df.rename(columns={'VeDBA': 'Log VeDBA'})

#Converting timestamps into pandas datetime
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df.reset_index(drop=True,inplace=True)

#A function to group various behaviors for preprocessing
def group_behaviors(df):
    df.loc[df['Behavior'] == 'Sitting vigilance','Behavior'] = 'Vigilance'
    df.loc[df['Behavior'] == 'Bipedal vigilance','Behavior'] = 'Vigilance'
    df.loc[df['Behavior'] == 'Haunch quadrupedal vigilance','Behavior'] = 'Vigilance'
    df.loc[df['Behavior'] == 'Standing quadrupedal vigilance','Behavior'] = 'Vigilance'


    df.loc[df['Behavior'] == 'Scrabbling','Behavior'] = 'Foraging' #Change
    df.loc[df['Behavior'] == 'Walking','Behavior'] = 'Foraging'
    df.loc[df['Behavior'] == 'Reforage','Behavior'] = 'Foraging'

    df.loc[df['Behavior'] == 'Social','Behavior'] = 'Others'
    df.loc[df['Behavior'] == 'Processing','Behavior'] = 'Others'
    df.loc[df['Behavior'] == 'Self groom','Behavior'] = 'Others'
    df.loc[df['Behavior'] == 'Marking','Behavior'] = 'Others'
    return df


df = group_behaviors(df)

#Defining two functions for different preprocessing depending upon data collected. The functions is be run is determined by the RunningEnough variable in config files

#EnoughRunning functions is more cases where you have relatively good number of data across all label classes. It is simple and straightforward training procedure
def EnoughRunning(df):
    df_copy= df.copy()
    df_copy.drop(['Axy','StdNorm'],axis=1,inplace=True) 
    df_copy = df_copy[df_copy['Behavior']!='Others']
    x=df_copy.iloc[:,4:]  # Features
    y=df_copy['Behavior'].values  # Labels
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.35,random_state=42)
    return X_train, X_test, y_train, y_test,df_copy


#NotEnoughRunning is for cases when you have less running instances which is often the case. In these cases, we use GPS derived running instances
#We these the corresponding features of these running instance to augment our dataset
#We then train model on the GPS running instances and test on the few actual observed running instances
#Final model derived in later train_rf function uses both running types 
def NotEnoughRunning(df):
    df_copy= df.copy()
    df_copy.drop(['Axy','Log VeDBA','StdNorm'],axis=1,inplace=True)
    df_GPS_RUNNING = df_GPS_RUNNING = df_copy.loc[df_copy['Behavior']=='RunningGPS',:]
    df_GPS_RUNNING.iloc[:,1] = 'Running'

    df_RUNNING =  df_copy[df_copy['Behavior']=='Running']

    df_copy = df_copy[df_copy['Behavior']!='RunningGPS']
    df_copy = df_copy[df_copy['Behavior']!='Running']
    df_copy = df_copy[df_copy['Behavior']!='Others']

    x=df_copy.iloc[:,4:]  # Features
    y=df_copy['Behavior'].values  # Labels

    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.35,random_state=42)
    X_train =  np.concatenate((X_train, df_GPS_RUNNING.iloc[:,4:].to_numpy()), axis = 0)
    y_train = np.concatenate([y_train,df_GPS_RUNNING['Behavior'].to_numpy()],axis=0)


    X_test =  np.concatenate((X_test, df_RUNNING.iloc[:,4:].to_numpy()), axis = 0)
    y_test = np.concatenate([y_test,df_RUNNING['Behavior'].to_numpy()],axis=0)
    return X_train, X_test, y_train, y_test,df_copy


#Determing which Function to run
if RunningEnough==False:
    X_train, X_test, y_train, y_test,df_copy =NotEnoughRunning(df)
else:
    X_train, X_test, y_train, y_test,df_copy =EnoughRunning(df)

#Training the model and saving it as a pickle formated model file
#Outputs a confusion matrix with labels and prints a classification report
def train_rf(X_train, X_test, y_train, y_test):

    Scaler = StandardScaler()
    clf=RandomForestClassifier(n_estimators=150, n_jobs=-1, random_state=42)
    X_train = Scaler.fit_transform(X_train)
    clf.fit(X_train,y_train)

    X_test = Scaler.transform(X_test)
    y_pred=clf.predict(X_test)

    print("Accuracy:",accuracy_score(y_test, y_pred))

    plt.figure(dpi=250)
    cf_matrix = confusion_matrix(y_test, y_pred,normalize='true')
    ax = sns.heatmap(cf_matrix, annot=True, cmap='Blues')

    ax.set_title('Random Forest Confusion Matrix with labels \n\n');
    ax.set_xlabel('\nPredicted Values')
    ax.set_ylabel('Actual Values ');

    ## Ticket labels - List must be in alphabetical order
    ax.xaxis.set_ticklabels(sorted(np.unique(y_train)))
    ax.yaxis.set_ticklabels(sorted(np.unique(y_train)))
    #plt.tight_layout()
    plt.show()


    print(classification_report(y_test, y_pred))

    pipeline = make_pipeline(StandardScaler(),RandomForestClassifier(n_estimators=150, n_jobs=-1, random_state=42) )
    x=df_copy.iloc[:,4:]  # Features
    y=df_copy['Behavior'].values  # Labels
    pipeline.fit(x, y)
    joblib.dump(pipeline, '/media/amlan/Data/Thesis Data/Processed Data/RF_model.mod')

train_rf(X_train, X_test, y_train, y_test)
