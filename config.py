#This File sets the multiple parameters needed for running the code

GROUPS = ['NQ_2021_1','ZU_2021_1','RW_2021_1','ZU_2021_2']

#For GPS_Extraction.py
MainPath = '/media/amlan/Data/Thesis Data/Raw Data/' #Directory 
SavePath = '/media/amlan/Data/Thesis Data/Processed Data/' 
AddPath = '/COLLAR/GPS/' #For my database structure, this was need. 



#For ACC_Extraction.py
FREQUENCY =  10 #Frequency of the ACC files
WINDOW_SIZE = 20 #If frequency is n, window size can be n, 2n , 3n etc. Leave at 0 if you want no overlap


#For Boris Processing.py
BorisPath = '/media/amlan/Data/Thesis Data/BORIS Data/'
BorisAddPath = '/Event Data/'




