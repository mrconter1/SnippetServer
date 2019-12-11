from datetime import datetime
import time
import os

maxFiles = 4*10
freqInMin = 60*6

def backupFile(fileName, folderName):

    #Create folder if not exists
    if not os.path.exists(folderName):
        os.system("mkdir " + folderName)

    #Generate timestamp
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")

    if "." in fileName:
        dt_string += "." + fileName.split(".")[-1]

    #Save database to folder
    if os.path.isfile(fileName):
        os.system("cp " + fileName + " " + folderName + "/" + fileName)
        os.system("mv " + folderName + "/" + fileName + " " + folderName + "/" + dt_string)
    
    #Remove oldest file if more than x files 
    list_of_files = os.listdir(folderName)
    full_path = [folderName + "/{0}".format(x) for x in list_of_files]

    if len([name for name in list_of_files]) > maxFiles:
        oldest_file = min(full_path, key=os.path.getctime)
        os.remove(oldest_file)

while True:
    print("Backing up data..")
    backupFile("data.db", "backup")
    time.sleep(freqInMin*60) 
