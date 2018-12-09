import time, datetime
import sys, getopt
import Logfile

# Son solo menos de 100 lineas. Subirlas a memoria no es un gran gasto

def SetTempManual (szTemp, nVerbose):
    
    szFileName='CONFIG/Temp_Consigna2'
    if nVerbose > 0:
        Logfile.printError ('[ReadConsigna] Set Consigna Manual:' + szTemp)
 
    try:
        with open(szFileName, 'r') as fd:
            lines_orig = fd.readlines()
    except IOError:
        Logfile.printError ('[ReadConsigna] Error leyendo CONFIG/Temp_Consigna')
        pass
        
    # Tengo que buscar la linea de consigna manual
    # Sin comentarios es la 1
    
    nLine = 0
    nLinePosOrig = 1
    
    lines = []
    while nLine <= nLinePosOrig:
        line = lines_orig[nLine]
        if (line[0] == "\n" or line[0] == "#"):
            nLinePosOrig = nLinePosOrig + 1
        nLine += 1
               
    lines_orig[nLinePosOrig] =  szTemp + " Null\n"
       
    try:
        with open(szFileName, 'w') as fd:
            fd.writelines(lines_orig)
    except IOError:
        Logfile.printError ('[ReadConsigna] Error Escribiendo CONFIG/Temp_Consigna2')
        pass
    
    
def SetOpMode (szOpMode, nVerbose):

    if (szOpMode != "Prog" and szOpMode != "Man" and szOpMode != "Off"):
        Logfile.printError ('[ReadConsigna] Error SetMode:' + szOpMode)
        return
    
    szFileName='CONFIG/Temp_Consigna2'
    if nVerbose > 0:
        Logfile.printError ('[ReadConsigna] Set Op Mode:' + szOpMode)
 
    try:
        with open(szFileName, 'r') as fd:
            lines_orig = fd.readlines()
    except IOError:
        Logfile.printError ('[ReadConsigna] Error leyendo CONFIG/Temp_Consigna2')
        pass
       
    # Tengo que buscar la linea de consigna manual
    # Sin comentarios es la 0
    
    nLine = 0
    nLinePosOrig = 0
    
    lines = []
    while nLine <= nLinePosOrig:
        line = lines_orig[nLine]
        if (line[0] == "\n" or line[0] == "#"):
            nLinePosOrig = nLinePosOrig + 1
        nLine += 1
               
    lines_orig[nLinePosOrig] =  szOpMode + " # Off/Man/Prog\n"
       
    try:
        with open(szFileName, 'w') as fd:
            fd.writelines(lines_orig)
    except IOError:
        Logfile.printError ('[ReadConsigna] Error Escribiendo CONFIG/Temp_Consigna2')
        pass
    

def SetOffsetRoom (szRoomNum, szTemp, nVerbose):

    nRoom = int(szRoomNum)
    
    szFileName='CONFIG/Temp_Consigna2'
    if nVerbose > 0:
        Logfile.printError ('[ReadConsigna] Set Room Offset. Room:' + szRoomNum + " .Offset: " + szTemp)
 
    try:
        with open(szFileName, 'r') as fd:
            lines_orig = fd.readlines()
    except IOError:
        Logfile.printError ('[ReadConsigna] Error leyendo CONFIG/Temp_Consigna2')
        pass
       
    # Tengo que buscar la linea de consigna manual
    # Sin comentarios es la 2
    
    nLine = 0
    nLinePosOrig = 2
    
    lines = []
    while nLine <= nLinePosOrig:
        line = lines_orig[nLine]
        if (line[0] == "\n" or line[0] == "#"):
            nLinePosOrig = nLinePosOrig + 1
        nLine += 1
        
    line = lines_orig[nLinePosOrig].split()
    line [nRoom] = szTemp
    lines_orig[nLinePosOrig] =  ' '.join(line) + "\n"
       
    try:
        with open(szFileName, 'w') as fd:
            fd.writelines(lines_orig)
    except IOError:
        Logfile.printError ('[ReadConsigna] Error Escribiendo CONFIG/Temp_Consigna2')
        pass


def readConsignaMode (nVerbose):

    szFileName='CONFIG/Temp_Consigna2'
 
    try:
        with open(szFileName, 'r') as fd:
            lines_orig = fd.readlines()
    except IOError:
        Logfile.printError ('[ReadConsignaMode] Error leyendo CONFIG/Temp_Consigna2')
        pass
        
    nLine=0
    nLineMax=len(lines_orig)
    
    lines = []
    while nLine<nLineMax:
        line = lines_orig[nLine]
        if (line[0] == "\n" or line[0] == "#"):
            pass
        else:
            lines.append(line)
        
        nLine += 1
 
    line=lines[0].split()
    opmode = line[0]
    
    return(opmode)
    

def readConsignaRoom (nRoomReq, nVerbose):
    tempConsigna = ['Null' for x in range (7)] #inicializando
    tempConsignaDiff = ['Null' for x in range (6)] #inicializando

    dateToday = datetime.datetime.now()
    current_date=datetime.datetime.strptime (dateToday.strftime ("%Y-%m-%d"), "%Y-%m-%d")
    hour=dateToday.strftime ("%H")
    weekday=dateToday.strftime ("%w")
    szFileName='CONFIG/Temp_Consigna2'
        
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
            lines_orig = fd.readlines()
    except IOError:
        Logfile.printError ('[ReadConsigna] Error leyendo CONFIG/Temp_Consigna2')
        pass
        
    nLine=0
    nLineMax=len(lines_orig)
    
    lines = []
    while nLine<nLineMax:
        line = lines_orig[nLine]
        if (line[0] == "\n" or line[0] == "#"):
            pass
        else:
            lines.append(line)
        
        nLine += 1
 
    line=lines[0].split()
    opmode = line[0]
    
    if nVerbose > 0:
        Logfile.printError ('[ReadConsigna] ' + opmode)

    # Luego los prog default
    
    
        
    if opmode == 'Prog':
        line=lines[2].split();
        tempConsigna = float(line[0])
    if opmode == 'Man':
        line=lines[1].split();
        tempConsigna = float(line[0])
    if opmode == 'Off':
        tempConsigna = 0
        
      
    nLine = 3 	
    nLineMax = len(lines)
    
    while nLine < nLineMax and opmode == 'Prog':
        line= lines[nLine].split()
        nLine = nLine + 1
        if not str(nRoomReq) in line [2]: 
            continue
          
        datedays = line[0]
        if datedays == "X-X":
            dateinit = datetime.datetime(1974, 1, 1, 0, 0)
            dateend = datetime.datetime(2200, 1, 1, 0, 0) 
        else:
            dateinit=datetime.datetime.strptime (datedays[:4]+"/"+datedays[4:6]+"/"+datedays[6:8], "%Y/%m/%d")
            dateend=datetime.datetime.strptime (datedays[9:13]+"/"+datedays[13:15]+"/"+datedays[15:17], "%Y/%m/%d")
            
        if (current_date >= dateinit and current_date <= dateend):
            weekdays=line[1]
            if dayLetter in weekdays:
                nWord=3
                nWordMax=len(line)
                while nWord<nWordMax:
                    hours=line[nWord]
                    hourinit=int(hours[:2])
                    hourend=int(hours[-2:])
                    if int(hour) >= hourinit and int(hour) <= hourend:
                        tempConsigna = float(line[nWord+1])
                    nWord=nWord+2
                 
        
    if nVerbose > 0:
        Logfile.printError ('[ReadConsigna] ' + str(tempConsigna))
        
    return(tempConsigna)

def readConsigna3 (RoomDataList, nVerbose):

    for (RoomDict) in RoomDataList:
        RoomDict['Consigna'] = readConsignaRoom(RoomDict['roomNumber'], nVerbose)

    
        
def main():
    #Consignas = ['Null' for i in range(7)]
    #Consignas = readConsigna(1)
    #print (Consignas)
    #SetOpMode("Man", 1)
    print (readConsignaRoom (6, 1))
    
if __name__ == "__main__":
    main()
