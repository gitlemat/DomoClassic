import datetime
import time, os
import AirzoneAPI
import Analysis2
import Alarms
import Aemet
import ReadConsigna3
import control_caldera
import control_rooms
import mysql.connector as mariadb
import Logfile
import requests
import ds18_control

'''

[{'roomID': 'Salon', 
  'roomNumber': 1, 
  'Consigna': 0, 
  'Temp1': 'NULL'},
  'Temp2': 'NULL', 
  'Terms': [{'Address': '192.168.2.130', 
             'devId': 'TempSalon', 
             'Value': 23.1}], 
  'Valvs': [{'Address': '192.168.2.130', 
             'devId': 'ValvSalon_1', 
             'Value': 0}, 
            {'Address': '192.168.2.130', 
             'devId': 'ValvSalon_2', 
             'Value': 0}], 
  'Caldera': 'NULL',
 
  
 {'roomID': 'Despacho', 
  'roomNumber': 2, 
  'Consigna': 0.5, 
  'Temp1': 'NULL',
  'Temp2': 'NULL', 
  'Terms': [{'Address': '192.168.2.130', 
             'devId': 'TempDespacho', 
             'Value': 23.1}], 
  'Valvs': [{'Address': '192.168.2.130', 
             'devId': 'ValvDespacho', 
             'Value': 0}], 
  'Caldera': 'NULL'}]
'''

def GetValvulaState (szRoom, nVerbose):
    
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()

    #select * from temps order by timedate desc limit 3;
    
    szValvula = 'cal_' + szRoom
    
    szMysqlReq="SELECT " + szValvula + " from temps ORDER BY fecha DESC LIMIT 1"
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[Calefaccion] Error DB: {}'.format(error))

    mariadb_connection.close()
    
    row = cursor.fetchone()
    
    if (cursor.rowcount < 0):
        return(-1)
        
    if (row[0] == 'off'):
        ret_val = 0
        
    if (row[0] == 'on'):
        ret_val = 1

    return (ret_val)
    
def GetRoomList (nVerbose):
        
    szRoomList=control_rooms.GetRoomList(nVerbose)
    
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    # añadimos termostatos y valvulas a cada habitacion
    
    for roomDict in szRoomList:
        TermsList = []
        ValvsList = []
        
        szMysqlReq="SELECT us.devId, us.devType, us.roomNumber, us.address FROM DEVICES as us WHERE roomNumber = " + str(roomDict['roomNumber'])
        try:
            cursor.execute(szMysqlReq)    
        except mariadb.Error as error:
            Logfile.printError ('[Calefaccion] Error DB: {}'.format(error))
            
        for (devId, devType, roomNumber, address) in cursor:
            if devType == 'tTempDS18':
                TermsList.append({'devId':devId,'Address':address,'Value':0})
            if devType == 'tValvulaCal':
                ValvsList.append({'devId':devId,'Address':address,'Value':0})
        
        roomDict.update({'Terms':TermsList,'Valvs':ValvsList})
        
        
    mariadb_connection.close()

    return (szRoomList)
    

    return ()
    
def GetRoomListTreeTemps (nVerbose):
    # Devuelve lista de rooms con ultimas temps y con caldera de la DB
        
    szPlantaList=control_rooms.GetRoomListTree(nVerbose)
    
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    # añadimos termostatos y valvulas a cada habitacion
    
    for plantaDict in szPlantaList:
        roomsPlanta = plantaDict['rooms']
        print (roomsPlanta)
        for roomDict in roomsPlanta:
            szTId = 't_' + roomDict['roomID']
            szTId2 = 't_' + roomDict['roomID'] + '_ds'
            szCons = 'tc_' + roomDict['roomID']
            szCal = 'cal_' + roomDict['roomID']
            
            szMysqlReq = "SELECT fecha, " + szTId + ", " + szTId2 + ", " + szCons + ", " + szCal + " from temps ORDER BY fecha DESC LIMIT 1"
            
            try:
                cursor.execute(szMysqlReq)    
            except mariadb.Error as error:
                Logfile.printError ('[Calefaccion] Error DB: {}'.format(error))
                
            cons1 = ReadConsigna3.readConsignaRoom(roomDict['roomNumber'], nVerbose)
                
            for (fecha, temp1, temp2, cons, cald) in cursor:
                roomDict.update({'Temp1':temp1,'Temp2':temp2,'Consigna':cons1,'Caldera':cald})
        
    mariadb_connection.close()

    return (szPlantaList)
    

    return ()
    
def readLineasDB_AemetLast (TempAemet, CieloAemet):

    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()

    #select * from temps order by timedate desc limit 3;
    
    try:
        cursor.execute("SELECT fecha, aemet_Temp, aemet_Cielo from temps ORDER BY fecha DESC LIMIT 3")    
    except mariadb.Error as error:
        Logfile.printError ('[Calefaccion] Error DB: {}'.format(error))

    mariadb_connection.close()
    
    nIter=0
    for (date1, a1, a2) in cursor:
        TempAemet[nIter] = str(a1)
        CieloAemet[nIter] = str(a2)
        Logfile.printError ('[Calefaccion] Fallo en AEMET. Leyendo viejo. Temp numero '+str(nIter)+' : ' + TempAemet[nIter])
        Logfile.printError ('[Calefaccion] Fallo en AEMET. Leyendo viejo. Cielo numero '+str(nIter)+' : ' + CieloAemet[nIter])

        nIter+=1
      
def readLineasDB (RoomDataList):

    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()

    #select * from temps order by timedate desc limit 3;
    
    szMysqlReq="SELECT fecha"
    
    for (room) in RoomDataList:
        KeyTemp1 = 't_'+room['roomID']
        KeyTemp2 = 't_'+room['roomID']+'_DS'
        szMysqlReq += ", " + KeyTemp1 + ", " + KeyTemp2
        
    szMysqlReq += " from temps ORDER BY fecha DESC LIMIT 1"
    
    Logfile.printError ('[Calefaccion] Leyendo ultimas Temp despues de fallo en lectura:' + szMysqlReq)
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[Calefaccion] Error DB: {}'.format(error))

    mariadb_connection.close()
    
    response = cursor.fetchall()
    
    nResponse = 0
    
    # Miramos si hay alguna medida fallida en alguna habitacion e intentamos recuperar
    
        
    for (room) in RoomDataList:
    
        prevTemp1 = 0
        prevTemp2 = 0
        prevTemp1_OK = True
        prevTemp2_OK = True
    
        tempLeida1 = -127
        tempLeida2 = -127
        tempLeida1_OK = True
        tempLeida2_OK = True
    
        # Miramos las temp anteriores ( y ver si son validas)
        
        try:
            prevTemp1 = float (response[0][2*nResponse+1])   # Esto es solo para comprobar que s un numero
        except:   # esto no debería pasar nunca
            prevTemp1_OK = False
            Logfile.printError ('[Calefaccion] Error Datos previos Airzone: ' + str(response))
            prevTemp1  = 22   
            
        try:
            prevTemp2 = float (response[0][2*nResponse+2])   # Esto es solo para comprobar que s un numero
        except:   # esto no debería pasar nunca
            prevTemp2_OK = False
            Logfile.printError ('[Calefaccion] Error Datos previos DS18: ' + str(response))
            prevTemp2 = 22   
        
        # Comprobamos las temperaturas leidas  
                
        try:
            tempLeida1 = float(room['Temp1'])
        except:
            tempLeida1 = -127
            tempLeida1_OK = False
            
        if tempLeida1 < 10 or tempLeida1 > 60:
            tempLeida1_OK = False
            
        try:
            tempLeida2 = float(room['Temp2'])
        except:
            tempLeida2 = -127
            tempLeida2_OK = False
            
        if tempLeida2 < 10 or tempLeida2 > 60:
            tempLeida2_OK = False
             
        # Vemos que hacemos si Temp1 es NOK
        
        if tempLeida1_OK == False:
            if prevTemp1_OK == True and prevTemp2_OK == True and tempLeida2_OK == True:
                tempLeida1 = prevTemp1 + (tempLeida2 - prevTemp2)
                Logfile.printError ('[Calefaccion] Recuperamos ' + room['roomID'] + ' Temp1 = ' + str(prevTemp1) + ' + (' + str(tempLeida2) + ' - ' + str(prevTemp2) + ')')

            else:
                tempLeida1 = 22
                Logfile.printError ('[Calefaccion] Recuperamos ' + room['roomID'] + ' Temp1 = 22 por decreto')
                
        if tempLeida2_OK == False:
            if prevTemp2_OK == True and prevTemp1_OK == True and tempLeida1_OK == True:
                tempLeida2 = prevTemp2 + (tempLeida1 - prevTemp1)
                Logfile.printError ('[Calefaccion] Recuperamos ' + room['roomID'] + ' Temp2 = ' + str(prevTemp2) + ' + (' + str(tempLeida1) + ' - ' + str(prevTemp1) + ')')
            else:
                tempLeida2 = 22
                Logfile.printError ('[Calefaccion] Recuperamos ' + room['roomID'] + ' Temp2 = 22 por decreto')
                
        room['Temp1'] = str(tempLeida1)
        room['Temp2'] = str(tempLeida2)    
            
        nResponse +=1
        
        
def writeToMariaDB (RoomDataList, TempAemet0, CieloAemet0):
    
    date1=datetime.datetime.now().strftime ("%Y-%m-%d %H:%M:%S")
        
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    db_data = {'fecha': date1}
    
    szMysqlReq="INSERT INTO temps (fecha"
    
    for (room) in RoomDataList:
        KeyTemp1 = 't_'+room['roomID']
        KeyTemp2 = 't_'+room['roomID']+'_DS'
        KeyConsig = 'tc_'+room['roomID']
        KeyCal = 'cal_'+room['roomID']
        szMysqlReq += ", " + KeyTemp1 + ", " + KeyTemp2 + ", " + KeyConsig + ", " + KeyCal
        
        db_data.update({KeyTemp1:room['Temp1'],KeyTemp2:room['Temp2'],KeyConsig:room['Consigna'],KeyCal:room['Caldera']})
        
    db_data.update({'aemet_Temp' : float(TempAemet0),'aemet_Cielo' : CieloAemet0 })
    
    szMysqlReq += ", aemet_Temp, aemet_Cielo) VALUES (%(fecha)s"
    
    for (room) in RoomDataList:
        ValTemp1 = '%(t_'+room['roomID']+')s'
        ValTemp2 = '%(t_'+room['roomID']+'_DS)s'
        ValConsig = '%(tc_'+room['roomID']+')s'
        ValCal = '%(cal_'+room['roomID']+')s'
        szMysqlReq += ", " + ValTemp1 + ", " + ValTemp2 + ", " + ValConsig + ", " + ValCal
        
    szMysqlReq += ", %(aemet_Temp)s, %(aemet_Cielo)s)"

    try: 
        cursor.execute(szMysqlReq, db_data)      
    except mariadb.Error as error: 
        Logfile.printError ('[Calefaccion] Error: {}'.format(error)) 

    Logfile.printError ('[Calefaccion] ' + str(db_data))    

    mariadb_connection.commit()
    mariadb_connection.close()

def readTemps(RoomDataList, nVerbose):

    nErrorLecturas = 0
    

    ########################################        
    # Ahora leemos los DS18.
        
    response = ds18_control.GetTemp2(RoomDataList, nVerbose)
            
    if response < 0:  # Alguno ha fallado
        Logfile.printError ('[Calefaccion] Leyendo DS alguno ha fallado')
        nErrorLecturas -= 1
    
    ########################################        
    # Ahora leemos de Airzone.
    
    nHowManyTries=0
    errorAirzone = 'TRUE'
    
    Logfile.printError ('[Calefaccion] Lectura Airzone')
    
    while errorAirzone == 'TRUE' and nHowManyTries < 3:
        if nHowManyTries > 0:
            Logfile.printError ('[Calefaccion] Airzone esperando para proximo intento')
            time.sleep(120)
        
        nHowManyTries+=1
        
        input_params = ['AirzoneAPI.py', 'gettemps']
        
        try:
            result = AirzoneAPI.airzoneControl(input_params, 1, nVerbose)
            if (result['status'] == 0):
                errorAirzone = 'FALSE'
        except:
            Logfile.printError ('[Calefaccion] Error en lectura Airzone')
            pass
            
    if errorAirzone == 'TRUE': # Fallo las 3 veces
        Logfile.printError ('[Calefaccion] Error en lectura Airzone tres veces')
        Alarms.writeAlarmToMariaDB (101, 1, "NULL", nVerbose)  # Activo Alarma Airzone
        nErrorLecturas -= 1
    else:
        Alarms.writeAlarmToMariaDB (101, 0, "NULL", nVerbose)  # Apago Alarma   
        
    # Da igual que haya fallo, copiamos lo que tenga. Si es fallo tengo NULL
         
    for (RoomDict) in RoomDataList:
        if RoomDict['roomID'] in result['temps']:
            RoomDict['Temp1'] = result['temps'][RoomDict['roomID']]
            
    ########################################        
    # Si errores, intentamos recuperar
                
    if nErrorLecturas < 0: # Error en Airzone o DS18
        # El fallo es, o NULL, o -127 o fuera de rango
        Logfile.printError ('[Calefaccion] Intentamos recuperar por algn error')
        readLineasDB (RoomDataList) 
                


def Calefaccion_control(nVerbose):
    szInstalation='Sergio'
    
    RoomDataList = GetRoomList (nVerbose)
    TempAemet = ['Null' for i in range(7)]
    CieloAemet = ['Null' for i in range(7)]
    
    
    for (RoomDict) in RoomDataList:
        RoomDict.update({'Temp1':'NULL','Temp2':'NULL','Consigna':'NULL','Caldera':'NULL'}) 
                           
    try:
        readTemps(RoomDataList, nVerbose)
        pass
    except:
        Logfile.printError ('[Calefaccion] Error general en lectura Temperaturas')
        Alarms.writeAlarmToMariaDB (101, 1, "NULL", nVerbose)  # Activo Alarma Airzone
        return  
        
    try:
        Aemet.GetTempAEMET(TempAemet, CieloAemet, nVerbose)
    except:
        Logfile.printError ('[Calefaccion] Error general en lectura AEMET')
        Alarms.writeAlarmToMariaDB (102, 1, "NULL", nVerbose)  # Activo Alarma AEMET
        return
      
    if TempAemet[0].find ('Null') >= 0:
        Alarms.writeAlarmToMariaDB (102, 1, "NULL", nVerbose)  # Activo Alarma AEMET
        readLineasDB_AemetLast (TempAemet, CieloAemet)
    else:
        Alarms.writeAlarmToMariaDB (102, 0, "NULL", nVerbose)  # Apago Alarma
        
    try:
        ReadConsigna3.readConsigna3(RoomDataList, nVerbose)

    except:
        Logfile.printError ('[Calefaccion] Error general en lectura Consignas')
        Alarms.writeAlarmToMariaDB (104, 1, "NULL", nVerbose)  # Activo Alarma
        return
    else:
        Alarms.writeAlarmToMariaDB (104, 0, "NULL", nVerbose)  # Apago Alarma
    
    try:
        pass
        Analysis2.mainControl(RoomDataList, TempAemet, CieloAemet, nVerbose)
    except:
        Logfile.printError ('[Calefaccion] Error general en Analisis')
        Alarms.writeAlarmToMariaDB (103, 1, "NULL", nVerbose)  # Activo Alarma
        return
    else:
        Alarms.writeAlarmToMariaDB (103, 0, "NULL", nVerbose)  # Apago Alarma
        
            
    # Ahora hay que llamar a la API que active el rele si es necesario
    try:
        control_caldera.caldera2(RoomDataList, nVerbose)
    except:
        Logfile.printError ('[Calefaccion] Error general controlando caldera')
        Alarms.writeAlarmToMariaDB (106, 1, "NULL", nVerbose)  # Activo Alarma
        return
    else:
        Alarms.writeAlarmToMariaDB (106, 0, "NULL", nVerbose)  # Apago Alarma
    
    try:
        writeToMariaDB (RoomDataList, TempAemet[0], CieloAemet[0])    
        pass
    except:
        Logfile.printError ('[Calefaccion] Error general escribiendo en MariaDB')
        return
               
        
def main():

    Calefaccion_control(1)
    
if __name__ == "__main__":
    main()
    
    
    # Cron cada 15 min
    # Comprobar que cada temp es la de cada habitacion
    # fecha->nombre fichero. Cada dia uno
    # timestamp, t1, t2, t3, t4, t5, t6
    # If Airzone.error repetir ultimas T
