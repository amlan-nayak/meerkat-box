#Home directory, mention the main directory as a string
DIRECTORY = '/media/amlan/Data/Thesis Data/'


#This File sets the multiple parameters needed for running the code

GROUPS = ['NQ_2021_1','ZU_2021_1','RW_2021_1','ZU_2021_2']

#For GPS_Extraction.py
MainPath = DIRECTORY + 'Raw Data/' #Directory 
SavePath = DIRECTORY + 'Processed Data/' 
AddPath = '/COLLAR/GPS/' #For my database structure, this was need. 



#For ACC_Extraction.py
FREQUENCY =  [50,10,10,50] #Frequency of the ACC files



#For Boris Processing.py
BorisPath = DIRECTORY + 'BORIS Data/'
BorisAddPath = '/Event Data/'

#For Model_Training.py
#Do you have atleast 50 instances running data? If yes, set following variable as True. If not, set variable as False
RunningEnough=False


