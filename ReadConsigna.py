import time, datetime
import sys, getopt
import Logfile

# Son solo menos de 100 lineas. Subirlas a memoria no es un gran gasto
def readConsigna (nVerbose):
    tempConsigna = ['Null' for x in range (7)] #inicializando
    tempConsignaDiff = ['Null' for x in range (6)] #inicializando

    dateToday = datetime.datetime.now()
    current_date=datetime.datetime.strptime (dateToday.strftime ("%Y-%m-%d"), "%Y-%m-%d")
    hour=dateToday.strftime ("%H")
    weekday=dateToday.strftime ("%w")
    szFileName='CONFIG/Temp_Consigna'
        
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
        Logfile.printError ('[ReadConsigna] ' + hour)
 
    try:
        with open(szFileName, 'r') as fd:
            lines = fd.readlines()
    except IOError:
        Logfile.printError ('[ReadConsigna] Error leyendo CONFIG/Temp_Consigna')
        pass
 
    line=lines[0].split()
    opmode = line[0]
    
    if nVerbose > 0:
        Logfile.printError ('[ReadConsigna] ' + opmode)

    # Luego los prog default

    line=lines[2].split();
    tempConsignaDiff[1]=float(line[1])
    tempConsignaDiff[2]=float(line[2])
    tempConsignaDiff[3]=float(line[3])
    tempConsignaDiff[4]=float(line[4])
    tempConsignaDiff[5]=float(line[5])
        
    if opmode == 'Prog':
        tempConsigna[1]=float(line[0])
    if opmode == 'Man':
        line=lines[1].split();
        tempConsigna[1]=float(line[0])
    if opmode == 'Off':
        tempConsigna[1]=0
          
        
    nLine=3	
    nLineMax=len(lines)
    
    while nLine<nLineMax and opmode == 'Prog':
        line= lines[nLine]
        dates3=line[:3]
        if dates3 == "X-X":
            line= lines[nLine].split()
            weekdays=line[1]
            if dayLetter in weekdays:
                nWord=2
                nWordMax=len(line)
                while nWord<nWordMax:
                    hours=line[nWord]
                    hourinit=int(hours[:2])
                    hourend=int(hours[-2:])
                    if int(hour) >= hourinit and int(hour) <= hourend:
                        tempConsigna[1]=float(line[nWord+1])
                    nWord=nWord+2
        nLine+=1

    nLine=3	
    
    while nLine<nLineMax and opmode == 'Prog':
        line= lines[nLine]
        dates3=line[:3]
        if dates3 != "X-X":
            line= lines[nLine].split()
            datedays=line[0]
            dateinit=datetime.datetime.strptime (datedays[:4]+"/"+datedays[4:6]+"/"+datedays[6:8], "%Y/%m/%d")
            dateend=datetime.datetime.strptime (datedays[9:13]+"/"+datedays[13:15]+"/"+datedays[15:17], "%Y/%m/%d")
            if (current_date >= dateinit and current_date <= dateend):
                weekdays=line[1]
                if dayLetter in weekdays:
                    nWord=2
                    nWordMax=len(line)
                    while nWord<nWordMax:
                        hours=line[nWord]
                        hourinit=int(hours[:2])
                        hourend=int(hours[-2:])
                        if int(hour) >= hourinit and int(hour) <= hourend:
                            tempConsigna[1]=float(line[nWord+1])
                        nWord=nWord+2
        nLine+=1          
  
    tempConsigna[2]=tempConsigna[1]+tempConsignaDiff[1]
    tempConsigna[3]=tempConsigna[1]+tempConsignaDiff[2]
    tempConsigna[4]=tempConsigna[1]+tempConsignaDiff[3]
    tempConsigna[5]=tempConsigna[1]+tempConsignaDiff[4]
    tempConsigna[6]=tempConsigna[1]+tempConsignaDiff[5]
    tempConsigna[0]=opmode
        
    if nVerbose > 0:
        Logfile.printError ('[ReadConsigna] ' + str(tempConsigna[0]) + ' ' + str(tempConsigna[1]) + ' ' + str(tempConsigna[2]) + ' ' + str(tempConsigna[3]) + ' ' + str(tempConsigna[4]) + ' ' 	+ str(tempConsigna[5]) )
    return(tempConsigna)


if __name__ == "__main__":
    readConsigna(1)
        
