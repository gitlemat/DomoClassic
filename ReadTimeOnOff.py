import time, datetime
import sys, getopt
import Logfile

def setTimerOnOffState (dispositivo, szState, nVerbose):

    szFileName='CONFIG/TimerOnOff'
    
    try:
        with open(szFileName, 'r') as fd:
            lines = fd.readlines()
    except IOError:
        Logfile.printError ('[ReadTimer] Error leyendo CONFIG/TimerOnOff')
        pass
        
    nLine=0
    nLineMax=len(lines)
      
    while nLine<nLineMax:
        lines[nLine]=lines[nLine].rstrip()
        line= lines[nLine].split() 
        szDeviceTimer=line[0]
        
        if szDeviceTimer == dispositivo:
            
            # El segundo campo puede ser man/prog o las fechas
            # si es 'man' fuera con -1
            
            opmode = line[1]
            if opmode == 'Man' or opmode == 'Prog':
                lines[nLine] = szDeviceTimer + " " + szState
                
        nLine+=1
                
    try:
        with open(szFileName, 'w') as fd:
            fd.write('\n'.join(lines))
            fd.write('\n')
    except IOError:
        Logfile.printError ('[ReadTimer] Error leyendo CONFIG/TimerOnOff')
        pass


def readTimerOnOff (dispositivo, nVerbose):
    
    stateOnOff=-1

    dateToday = datetime.datetime.now()
    current_date=datetime.datetime.strptime (dateToday.strftime ("%Y-%m-%d"), "%Y-%m-%d")
    hour=dateToday.strftime ("%H")
    weekday=dateToday.strftime ("%w")
    szFileName='CONFIG/TimerOnOff'
        
    if weekday == '1':
        dayLetter="L"
    if weekday == '2':
        dayLetter="M"
    if weekday == '3':
        dayLetter="X"
    if weekday == '4':
        dayLetter="J"
    if weekday == '5':
        dayLetter="V"
    if weekday == '6':
        dayLetter="S"
    if weekday == '0':
        dayLetter="D"
        
    if nVerbose > 0:
        Logfile.printError ('[ReadTimer] Hora:' + hour)
        Logfile.printError ('[ReadTimer] Dia:' + dayLetter)
 
    try:
        with open(szFileName, 'r') as fd:
            lines = fd.readlines()
    except IOError:
        Logfile.printError ('[ReadTimer] Error leyendo CONFIG/TimerOnOff')
        pass
        
    nLine=0
    nLineMax=len(lines)
      
    while nLine<nLineMax:
        line= lines[nLine].split() 
        szDeviceTimer=line[0]
        
        if szDeviceTimer == dispositivo:
        
            if stateOnOff < 0:
                stateOnOff=0
            
            # El segundo campo puede ser man/prog o las fechas
            # si es 'man' fuera con -1
            
            opmode = line[1]
            if opmode == 'Man':
                stateOnOff=-1
                break
                
            if opmode == 'Prog':
                nLine+=1
                continue
            
            dates3=line[1]
            weekdays=line[2]
            
            dashPos=dates3.find('-')
            szDateInit=dates3[0:dashPos]
            szDateEnd=dates3[dashPos+1:]
            if szDateInit == "X":
                szDateInit = "19710101"
            if szDateEnd == "X":
                szDateEnd = "29710101"
            dateinit=datetime.datetime.strptime (szDateInit[:4]+"/"+szDateInit[4:6]+"/"+szDateInit[6:8], "%Y/%m/%d")    
            dateend=datetime.datetime.strptime (szDateEnd[:4]+"/"+szDateEnd[4:6]+"/"+szDateEnd[6:8], "%Y/%m/%d")
            
            if nVerbose > 0:
                Logfile.printError ('[ReadTimer] Program Dates:' + szDateInit + " - " + szDateEnd)
                
                
            if (current_date >= dateinit and current_date <= dateend):
                if nVerbose > 0:
                    Logfile.printError ('[ReadTimer] Program Weekdays:' + weekdays)
                if dayLetter in weekdays:
                    nWord=3
                    nWordMax=len(line)
                    while nWord<nWordMax:
                        hours=line[nWord]
                        hourinit=int(hours[:2])
                        hourend=int(hours[-2:])
                        if nVerbose > 0:
                            Logfile.printError ('[ReadTimer] Program Hours:' + str(hourinit) + ' - ' + str(hourend))
                        if int(hour) >= hourinit and int(hour) <= hourend:
                            if nVerbose > 0:
                                Logfile.printError ('[ReadTimer] Programa Activo')
                            stateOnOff=1
                        nWord=nWord+1
        nLine+=1

    nLine=0	
                
    if nVerbose > 0:
        Logfile.printError ('[ReadTimer] Resultado: ' + str(stateOnOff))
     
    print ("Stado: "+str(stateOnOff))
    return(stateOnOff)


if __name__ == "__main__":
    readTimerOnOff('SOJD1',1)
    #setTimerOnOffState ('SOJD1', 'Man', 1)  
