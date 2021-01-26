import subprocess
import time 
import requests
import json
import RPi.GPIO as GPIO
GPIO.setwarnings(False)



printLevel=1

timeToWakeUp=120
numberOfRetries=3
timeToNextPing=2
timeBetweenRetries=2
firstWait=5
resetWait=5
#logFile="C:/Users/70018928/Documents/GitHub/RouterRebooter/rebootRouter.log"
logFile="/home/pi/Project/RelayCtrl/rebootReouter.log"

def Reset(rebootOk):
    GPIO.setmode(GPIO.BCM)
    Relay1_GPIO=4
    print(" :: ",rebootOk)
    GPIO.setup(Relay1_GPIO, GPIO.OUT)
    print(" Turn Off ")
    GPIO.output(Relay1_GPIO, GPIO.LOW)
    time.sleep(2)
    GPIO.output(Relay1_GPIO, GPIO.HIGH)
    GPIO.cleanup()
    print(" Turn On ")
    rebootOk=1
    return rebootOk


def printDbg(level, arg):
    if(level>=printLevel):
        print(arg)
    return None

def runPing():
    
    pingS=[]
    pingResponse=subprocess.Popen(["ping","-c4","8.8.8.8"],stdout=subprocess.PIPE).stdout.read()

    pingResponse=pingResponse.decode('utf-8')
    #print(' ==> ',pingResponse)
    pingS.append(pingResponse.find("2 received"))
    pingS.append(pingResponse.find("3 received"))
    pingS.append(pingResponse.find("4 received"))

    if(pingS[0]>0 or pingS[1]>0 or pingS[2]>0):
        print(' :: ', pingS[0], ',' , pingS[1], ',', pingS[2])
    else:
        print(' No internet Connection')
    pingSuccessful=-1
    for n in pingS:
        if(n>0):
            pingSuccessful=n
    print("Out : ",pingSuccessful)
    return pingSuccessful

def logToFile(line, appendNewLine=0, logFilePath=logFile):
    currentDate=time.strftime("%Y-%m-%d %H:%M:%S")
    head="[%s]>>%s"%(currentDate, line, )
    if(appendNewLine==1):
        head+="\n"
    with open(logFilePath,"a") as file:
        file.write(head)
    return None
    

if(__name__=="__main__"):
    logToFile("+++++++",1)
    logToFile("Application Started",1)
    #time.sleep(firstWait)

    while(True):

        pingSuccessful=runPing()
        #print(" :: ",pingSuccessful)

        if(pingSuccessful>0):
            printDbg(0,"Ping Successful")
            time.sleep(timeToNextPing)
            continue
    
        for i in range(0,numberOfRetries):
            time.sleep(timeBetweenRetries)
            pingSuccessful=runPing()
            if(pingSuccessful>0):
                break
            printDbg(0,"Ping Unsuccessful, retry %d/%d"% (i+1,numberOfRetries,))
            
        if(pingSuccessful==-1):
            printDbg(0,"Rebooting Router")
            logToFile("Rebooting Router ...",1)
            rebootOk=0
            ### Reboot Router
            rebootOk=Reset(rebootOk)
            if(rebootOk==1):
                printDbg(0, "Waiting ofr router to wake up")
                time.sleep(timeToWakeUp)
 
    
        