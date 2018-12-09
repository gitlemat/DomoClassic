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


def readConsigna (nVerbose):
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
        
    tempConsigna[0]=opmode
    tempConsigna[2]=tempConsigna[1]+tempConsignaDiff[1]
    tempConsigna[3]=tempConsigna[1]+tempConsignaDiff[2]
    tempConsigna[4]=tempConsigna[1]+tempConsignaDiff[3]
    tempConsigna[5]=tempConsigna[1]+tempConsignaDiff[4]
    tempConsigna[6]=tempConsigna[1]+tempConsignaDiff[5]
      
    nLine=3	
    nLineMax=len(lines)
    
    while nLine<nLineMax and opmode == 'Prog':
        line= lines[nLine]
        dates3=line[:3]
        if dates3 == "X-X":
            line= lines[nLine].split()
            weekdays=line[1]
            if dayLetter in weekdays:
                nWord=3
                nWordMax=len(line)
                while nWord<nWordMax:
                    hours=line[nWord]
                    hourinit=int(hours[:2])
                    hourend=int(hours[-2:])
                    if int(hour) >= hourinit and int(hour) <= hourend:
                        for nRoom in line[2]:
                            tempConsigna[int(nRoom)]=float(line[nWord+1])
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
                    nWord=3
                    nWordMax=len(line)
                    while nWord<nWordMax:
                        hours=line[nWord]
                        hourinit=int(hours[:2])
                        hourend=int(hours[-2:])
                        if int(hour) >= hourinit and int(hour) <= hourend:
                            for nRoom in line[2]:
                                tempConsigna[int(nRoom)]=float(line[nWord+1])
                        nWord=nWord+2
        nLine+=1          
        
    if nVerbose > 0:
        Logfile.printError ('[ReadConsigna] ' + str(tempConsigna[0]) + ' ' + str(tempConsigna[1]) + ' ' + str(tempConsigna[2]) + ' ' + str(tempConsigna[3]) + ' ' + str(tempConsigna[4]) + ' ' 	+ str(tempConsigna[5]) )
    return(tempConsigna)

def readConsigna2 (RoomDataList, nVerbose):

    # Esto es una ñapa-wrapper, pero hay que actualizar para que el numero de rooms sea dinamico
    Consignas = ['Null' for i in range(7)]
    Consignas=readConsigna(nVerbose)

    #Consignas[0] es el modo de operacion. Lo quitamos
    #si mas adelante lo quiero se deja
    del Consignas[0]
    for (RoomDict) in RoomDataList:
        if RoomDict['roomNumber'] == 1:
            RoomDict['Consigna'] = Consignas[0]
        if RoomDict['roomNumber'] == 2:
            RoomDict['Consigna'] = Consignas[1]
        if RoomDict['roomNumber'] == 3:
            RoomDict['Consigna'] = Consignas[2]
        if RoomDict['roomNumber'] == 4:
            RoomDict['Consigna'] = Consignas[3]
        if RoomDict['roomNumber'] == 5:
            RoomDict['Consigna'] = Consignas[4]
        if RoomDict['roomNumber'] == 6:
            RoomDict['Consigna'] = Consignas[5]
    
    
        
def main():
    #Consignas = ['Null' for i in range(7)]
    #Consignas = readConsigna(1)
    #print (Consignas)
    #SetOpMode("Man", 1)
    SetOffsetRoom ("2", "-1.5",1)
    
if __name__ == "__main__":
    main()
