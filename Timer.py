import os
import datetime
import ReadTimeOnOff
import requests
import Logfile
import HandleDeviceConfig
import control_devices
        
def TimerDispositivos(nVerbose): 

    sortBy = ""

    deviceList = HandleDeviceConfig.GetUsageListAllOn(sortBy, nVerbose)
    
    for device in deviceList:
        szIP='http://'+device['Address']
        szDevId=device['devId']
        szDevType=device['devType']
        
        response=ReadTimeOnOff.readTimerOnOff(szDevId,nVerbose)
        
        if nVerbose>0:
            Logfile.printError ('[Timer] ' + szDevType+" - "+szIP+" - "+str(response))
        
        # -1 si no hay programa para ese device
        if response > -1:
            control_devices.UpdateUsageState('WIFI', szDevId, response, nVerbose)
            
    return
            

def main():

    TimerDispositivos(1);
       
if __name__ == "__main__":
    main()
