import datetime
import time, os
import Airzone
import Analysis
import Alarms
import Aemet
import ReadConsigna2
import control_caldera
import mysql.connector as mariadb
import Logfile
import requests
import ds18_control


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
      
def readLineasDB (ZonaTempDef):

    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()

    #select * from temps order by timedate desc limit 3;
    
    try:
        cursor.execute("SELECT fecha, t_Salon, t_Despacho, t_Cocina, t_Principal, t_Sofia, t_Alvaro  from temps ORDER BY fecha DESC LIMIT 1")    
    except mariadb.Error as error:
        Logfile.printError ('[Calefaccion] Error DB: {}'.format(error))

    mariadb_connection.close()
    
    nIter=1
    for (date1, t1, t2, t3, t4, t5, t6) in cursor:
        ZonaTempDef[0] = t1
        ZonaTempDef[1] = t2
        ZonaTempDef[2] = t3
        ZonaTempDef[3] = t4
        ZonaTempDef[4] = t5
        ZonaTempDef[5] = t6
        nIter+=1
        
        
def writeToMariaDB (Consignas, ZonaTempDef, ZonaTempDef_DS, szCalderaOnOff, TempAemet0, CieloAemet0, Temp_Suelo):
    
    date1=datetime.datetime.now().strftime ("%Y-%m-%d %H:%M:%S")
        
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    db_data = {
        'fecha': date1,
        't_Salon': float(ZonaTempDef[0]),
        't_Salon_DS': float(ZonaTempDef_DS[0]),
        'tc_Salon': float(Consignas[0]),
        't_Despacho' : float(ZonaTempDef[1]),
        't_Despacho_DS' : float(ZonaTempDef_DS[1]),
        'tc_Despacho' : float(Consignas[1]),
        't_Cocina' : float(ZonaTempDef[2]),
        't_Cocina_DS' : float(ZonaTempDef_DS[2]),
        'tc_Cocina' : float(Consignas[2]),
        't_Principal' : float(ZonaTempDef[3]),
        't_Principal_DS' : float(ZonaTempDef_DS[3]),
        'tc_Principal' : float(Consignas[3]),
        't_Sofia' : float(ZonaTempDef[4]),
        't_Sofia_DS' : float(ZonaTempDef_DS[4]),
        'tc_Sofia' : float(Consignas[4]),
        't_Alvaro' : float(ZonaTempDef[5]),
        't_Alvaro_DS' : float(ZonaTempDef_DS[5]),
        'tc_Alvaro' : float(Consignas[5]),
        'cal_Salon' : szCalderaOnOff[0],
        'cal_Despacho' : szCalderaOnOff[1],
        'cal_Cocina' : szCalderaOnOff[2],
        'cal_Principal' : szCalderaOnOff[3],
        'cal_Sofia' : szCalderaOnOff[4],
        'cal_Alvaro' : szCalderaOnOff[5],
        'aemet_Temp' : float(TempAemet0),
        'aemet_Cielo' : CieloAemet0,
        't_SueloTest' : Temp_Suelo,
    } 
    
    szMysqlReq = "INSERT INTO temps (fecha, t_Salon, t_Salon_DS, tc_Salon, t_Despacho, t_Despacho_DS, tc_Despacho, t_Cocina, t_Cocina_DS, tc_Cocina, \
                                     t_Principal, t_Principal_DS, tc_Principal, t_Sofia, t_Sofia_DS, tc_Sofia, t_Alvaro, t_Alvaro_DS, tc_Alvaro, \
                                     cal_Salon, cal_Despacho, cal_Cocina, cal_Principal, cal_Sofia, cal_Alvaro, \
                                     aemet_Temp, aemet_Cielo, t_SueloTest) \
                             VALUES (%(fecha)s,%(t_Salon)s,%(t_Salon_DS)s, %(tc_Salon)s,%(t_Despacho)s,%(t_Despacho_DS)s,%(tc_Despacho)s,%(t_Cocina)s, %(t_Cocina_DS)s, %(tc_Cocina)s, \
                                     %(t_Principal)s, %(t_Principal_DS)s, %(tc_Principal)s, %(t_Sofia)s, %(t_Sofia_DS)s, %(tc_Sofia)s, %(t_Alvaro)s, %(t_Alvaro_DS)s, %(tc_Alvaro)s, \
                                     %(cal_Salon)s, %(cal_Despacho)s, %(cal_Cocina)s, %(cal_Principal)s, %(cal_Sofia)s, %(cal_Alvaro)s, \
                                     %(aemet_Temp)s, %(aemet_Cielo)s, %(t_SueloTest)s)"
    

    try: 
        #cursor.execute("INSERT INTO temps VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)", (date1, float(ZonaTempDef[0]),float(Consignas[0]),float(ZonaTempDef[1]),float(Consignas[1]),float(ZonaTempDef[2]),float(Consignas[2]),float(ZonaTempDef[3]),float(Consignas[3]),float(ZonaTempDef[4]),float(Consignas[4]),float(ZonaTempDef[5]),float(Consignas[5]),szCalderaOnOff[0],szCalderaOnOff[1],szCalderaOnOff[2],szCalderaOnOff[3],szCalderaOnOff[4],szCalderaOnOff[5],float(TempAemet0),CieloAemet0, Temp_Suelo))
        cursor.execute(szMysqlReq, db_data)      
    except mariadb.Error as error: 
        Logfile.printError ('[Calefaccion] Error: {}'.format(error)) 

    Logfile.printError ('[Calefaccion] ' + ZonaTempDef[0]+' '+ZonaTempDef[1]+' '+ZonaTempDef[2]+' '+ZonaTempDef[3]+' '+ZonaTempDef[4]+' '+ZonaTempDef[5]+' '+szCalderaOnOff[0]+' '+szCalderaOnOff[1]+' '+szCalderaOnOff[2]+' '+szCalderaOnOff[3]+' '+szCalderaOnOff[4]+' '+szCalderaOnOff[5]+' '+TempAemet0+' '+CieloAemet0)    

    mariadb_connection.commit()
    mariadb_connection.close()
    
def readTempSuelo (nVerbose):

    szRootUrl = 'http://192.168.2.135'
    szUriParams = '/ReadTemp'
    url = szRootUrl+szUriParams
    s=requests.session()
    
    nHowManyTries=0
    Temp_Suelo=0
    
    while Temp_Suelo <= 1 and nHowManyTries < 6:
            if nHowManyTries > 0:
                Logfile.printError ('[Calefaccion] Temperatura Suelo Esperando 10 segundos para otro intento')
                time.sleep(10)
            
            nHowManyTries+=1
            
            try:
                response = s.get(url,stream=False, timeout=15)
            except requests.exceptions.RequestException as e:
                Logfile.printError ('[Calefaccion] Error conectando a OnOff Temp Suelo')
                pass
                
            Temp_Suelo = response.json()[0]
                 
    s.close()
    
    if nVerbose > 0:
        Logfile.printError ('[Calefaccion] Temperatura suelo: '+str(Temp_Suelo))
    
    return (Temp_Suelo)

def readTemps(ZonaTempDef, ZonaTempDef_DS, szInstalation, nVerbose):
    nHowManyTries=0
    
    if szInstalation == 'Sergio':
    
        # Primero leemos de Airzone.
        # Luego decidimos si esto se quita
        
        while ZonaTempDef[5].find ('Null') >= 0 and nHowManyTries < 3:
            if nHowManyTries > 0:
                Logfile.printError ('[Calefaccion] Airzone esperando para proximo intento')
                time.sleep(120)
            
            nHowManyTries+=1
            
            try:
                Airzone.GetTemp(ZonaTempDef, nVerbose)
            except:
                Logfile.printError ('[Calefaccion] Error en lectura Airzone')
                pass
                
        if ZonaTempDef[5].find ('Null') >= 0:   # Fallo las 3 veces
            Logfile.printError ('[Calefaccion] Error en lectura Airzone tres veces')
            Alarms.writeAlarmToMariaDB (101, 1, "NULL", nVerbose)  # Activo Alarma Airzone
            readLineasDB (ZonaTempDef)          # leo ultima referencia para tener algo
        else:
            Alarms.writeAlarmToMariaDB (101, 0, "NULL", nVerbose)  # Apago Alarma
            
        # Ahora leemos los del DS de 4ch
        
        nHowManyTries=0
        
        while ZonaTempDef_DS[5].find ('Null') >= 0 and nHowManyTries < 3:
            if nHowManyTries > 0:
                Logfile.printError ('[Calefaccion] DS18 esperando para proximo intento')
                time.sleep(30)
            
            nHowManyTries+=1
            
            try:
                ds18_control.GetTemp(ZonaTempDef_DS, nVerbose) 
            except:
                Logfile.printError ('[Calefaccion] Error en lectura DS18')
                pass
                
        if ZonaTempDef_DS[5].find ('Null') >= 0:   # Fallo las 3 veces
            Logfile.printError ('[Calefaccion] Error en lectura DS18 tres veces')
            Alarms.writeAlarmToMariaDB (107, 1, "NULL", nVerbose)  # Activo Alarma Airzone
            #readLineasDB (ZonaTempDef)          # leo ultima referencia para tener algo
        else:
            Alarms.writeAlarmToMariaDB (107, 0, "NULL", nVerbose)  # Apago Alarma
                        
        
    if szInstalation == 'Ruben':
        # Aqui viene lo de Ruben
        pass
           
def Calefaccion_control(nVerbose):
    szInstalation='Sergio'
        
    ZonaTempDef = ['Null' for i in range(6)]
    ZonaTempDef_DS = ['Null' for i in range(6)]

    Consignas = ['Null' for i in range(7)]
    TempAemet = ['Null' for i in range(7)]
    CieloAemet = ['Null' for i in range(7)]
    szCalderaOnOff = ['Null' for x in range (6)]
    Temp_Suelo = 0
    
                
    try:
        readTemps(ZonaTempDef, ZonaTempDef_DS,  szInstalation, nVerbose)
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
        Consignas=ReadConsigna2.readConsigna(nVerbose)
        #Consignas[0] es el modo de operacion. Lo quitamos
        #si mas adelante lo quiero se deja
        del Consignas[0]
    except:
        Logfile.printError ('[Calefaccion] Error general en lectura Consignas')
        Alarms.writeAlarmToMariaDB (104, 1, "NULL", nVerbose)  # Activo Alarma
        return
    else:
        Alarms.writeAlarmToMariaDB (104, 0, "NULL", nVerbose)  # Apago Alarma
    

    try:
        szCalderaOnOff=Analysis.mainControl(Consignas, ZonaTempDef, TempAemet, CieloAemet, nVerbose)
    except:
        Logfile.printError ('[Calefaccion] Error general en Analisis')
        Alarms.writeAlarmToMariaDB (103, 1, "NULL", nVerbose)  # Activo Alarma
        return
    else:
        Alarms.writeAlarmToMariaDB (103, 0, "NULL", nVerbose)  # Apago Alarma
    
    # Ahora hay que llamar a la API que active el rele si es necesario
    try:
        control_caldera.caldera(szCalderaOnOff, nVerbose)
    except:
        Logfile.printError ('[Calefaccion] Error general controlando caldera')
        Alarms.writeAlarmToMariaDB (106, 1, "NULL", nVerbose)  # Activo Alarma
    else:
        Alarms.writeAlarmToMariaDB (106, 0, "NULL", nVerbose)  # Apago Alarma
        
    try:
        Temp_Suelo = readTempSuelo (nVerbose)
    except:
        Logfile.printError ('[Calefaccion] Error general leyendo temperatura suelo')
        Temp_Suelo = 22
    
    try:
        writeToMariaDB (Consignas, ZonaTempDef, ZonaTempDef_DS, szCalderaOnOff, TempAemet[0], CieloAemet[0], Temp_Suelo)
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
