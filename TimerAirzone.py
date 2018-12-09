import os
import datetime
import ReadTimeOnOff
import requests
import Logfile
import AirzoneAPI

def recrear_Fichero(nVerbose):
    fline=['1','2','3','4','5','6']
    fline[0]='off,20170707,1631,20170707,1716\n'
    fline[1]='off,20170707,1749,20170707,1934\n'
    fline[2]='off,20170707,1655,20170707,1655\n'
    fline[3]='off,20170707,1631,20170707,1716\n'
    fline[4]='off,20170807,1946,20170807,2202\n'
    fline[5]='off,20170707,1631,20170707,1716\n'
    
    with open("CONFIG/AirzoneTimer", "w") as fd:
        for item in fline:
            fd.write("%s" % item)
    fd.close()

def control_Airzone(szDateOn, szHourOn, szDateOff, szHourOff, nZone, nMaquina, nVerbose):
    dateToday = datetime.datetime.now()
    
    dateinit=datetime.datetime.strptime (szDateOn+" "+szHourOn, "%Y%m%d %H%M")
    dateend =datetime.datetime.strptime (szDateOff+" "+szHourOff, "%Y%m%d %H%M")
    
    if (dateend < dateToday):
        arguments=['AirzoneAPI.py','setzonestate',nMaquina, nZone, 'state', 0]
        AirzoneAPI.airzoneControl(arguments, 1, 3)
        return('off')
        
    if (dateinit > dateToday):
        return('on')
        
    if (dateend > dateToday and dateinit < dateToday):
        arguments=['AirzoneAPI.py','setzonestate',nMaquina, nZone, 'state', 1]
        AirzoneAPI.airzoneControl(arguments, 1, 3)
        return('on')
        
def TimerAirzone(nVerbose): 

    szFileName='CONFIG/AirzoneTimer'

    try:
        with open(szFileName, 'r') as fd:
            Programs = fd.readlines()
    except IOError:
        Logfile.printError ('[AirzoneTimer] Error leyendo fichero AirzoneTimer.')
        recrear_Fichero(0)
    fd.close()
    
    nLine=0
    nZone=0
    nMaquina=1
    
    for line in Programs:
        nLine+=1
        nZone+=1
        if nZone > 3:
            nZone=1
            nMaquina+=1
            
        lineSplit=line.split(',')
        szMode=lineSplit[0].rstrip()
        szDateOn=lineSplit[1].rstrip()
        szHourOn=lineSplit[2].rstrip()
        szDateOff=lineSplit[3].rstrip()
        szHourOff=lineSplit[4].rstrip()

        if nVerbose>0:
            Logfile.printError ('[AirzoneTimer] Mode: ' + szMode)
            
        if (szMode == 'off'):
            continue
            
        returnmode=control_Airzone (szDateOn, szHourOn, szDateOff, szHourOff, nZone, nMaquina, nVerbose)
        Programs[nLine-1]=returnmode+","+szDateOn+","+szHourOn+","+szDateOff+","+szHourOff+"\n"
        
    with open("CONFIG/AirzoneTimer", "w") as fd:
        for item in Programs:
            fd.write("%s" % item)
    fd.close()

def main():

    TimerAirzone(1);
       
if __name__ == "__main__":
    main()