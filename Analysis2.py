import time, datetime
import sys, getopt
import mysql.connector as mariadb
import Logfile

# Son solo menos de 100 lineas. Subirlas a memoria no es un gran gasto
def readLineasDB (RoomsLocalAnalisys, nVerbose):

    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()

    #select * from temps order by timedate desc limit 3;
    
    #szMysqlReq="SELECT fecha, t_Salon, t_Despacho, t_Cocina, t_Principal, t_Sofia, t_Alvaro, cal_Salon, cal_Despacho, cal_Cocina, cal_Principal, cal_Sofia, Cal_Alvaro from temps ORDER BY fecha DESC LIMIT 4"
    szMysqlReq="SELECT fecha"
    
    for (room) in RoomsLocalAnalisys:
        datTemp1 = 't_'+room['roomID']
        datTemp2 = 't_'+room['roomID']+'_ds'
        datCal = 'cal_'+room['roomID']
        szMysqlReq += ", " + datTemp1 + ", " + datTemp2 + ", " + datCal
        
    szMysqlReq += " from temps ORDER BY fecha DESC LIMIT 1"
    
    if nVerbose > 0:
        Logfile.printError ('[Analisis] MySQL: ' + szMysqlReq)
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[Analisis] Error DB: {}'.format(error))

    mariadb_connection.close()
    
    response = cursor.fetchall()
    
    if nVerbose > 0:
        Logfile.printError ('[Analisis] MySQL Response: ' + str(response))
    
    nRoom = 0
        
    for (room) in RoomsLocalAnalisys:
        room['DatePrev'] = response[0][0]
        nTemps = 0
        tempPrev = 0
        try:
            tempPrev1 = float(response[0][3*nRoom+1])
            if tempPrev1 > 10 and tempPrev1 < 70:
                nTemps += 1
                tempPrev += tempPrev1
        except:
            Logfile.printError ('[Analisis] Error Datos previos: ' + str(response))
            
        '''  De momento no usamos los DS
        try:
            tempPrev2 = float(response[0][3*nRoom+2])
            if tempPrev2 > 10 and tempPrev2 < 70:
                nTemps += 1
                tempPrev += tempPrev2
        except:
            Logfile.printError ('[Analisis] Error Datos previos: ' + str(response))
        '''         
        if nTemps > 0:
            room['TempPrev'] = tempPrev / nTemps
        else:
            room['TempPrev'] = 22
        nRoom +=1


def factorcorreccion (RoomsLocalAnalisys, TempAemet, CieloAemet, nVerbose):

    # Todo esto puede que haya que replantearlo.
    # La pendiente probablemente ya tiene todo esto en cuenta
    # La unica diferencia es que las condiciones externas cambien
    # El factor mas importante es la temperatura del suelo
    # y esto se puede intuir calculando hace cuanto que esta encendida/apagada la cale
    #
    # Otro punto de vista es que el cambio fundamental es que se encienda o apague la cale
    # Y esto si que va a cambiar la pendiente
    # Y en realidad este factor solo va a modificar la inercia, que solo se usa cuando cambio
    # el estado de la cale, con lo cual todo esto si que sirve
    
    dateToday = datetime.datetime.now()
    
    FactorSol = [0 for i in range(100)]
    #Sol
    #Correccion 1
    # Valor AEMET = 11
    FactorSol[11]=1
    
    #Sol y nubes
    #Correccion 0.7
    # Valor AEMET = 12,13,14,17
    
    FactorSol[12]=0.7
    FactorSol[13]=0.7
    FactorSol[14]=0.7
    FactorSol[17]=0.7
    
    #Sol y nubes, y lluvia
    #Correccion 0.4
    # Valor AEMET = 43, 44, 23, 24, 33, 34, 71, 72, 51, 52, 61, 62
    
    FactorSol[43]=0.4
    FactorSol[44]=0.4
    FactorSol[23]=0.4
    FactorSol[24]=0.4
    FactorSol[33]=0.4
    FactorSol[34]=0.4
    FactorSol[71]=0.4
    FactorSol[72]=0.4
    FactorSol[51]=0.4
    FactorSol[52]=0.4
    FactorSol[61]=0.4
    FactorSol[62]=0.4
    
    # Cubierto Nubes
    # Sin correccion
    # Valor AEMET = 15,16
    
    # Cubierto y Lluvia (o tormenta)
    # Sin correccion
    # Valor AEMET = 45, 25, 35, 73, 53, 54, 63, 64
    
    # Horas que afecta el Sol. Hora/mes
    
    HorasAfeccion = [[0 for x in range(24)] for y in range(13)] #inicializando
    # 01: 10,13,14,15,16,17
    # 02: 10,12,13,14,15,16,17,18
    # 03: 09,10,12,13,14,15,16,17,18
    # 04: 09,10,12,13,14,15,16,17,18,19
    # 05: 08,09,10,12,13,14,15,16,17,18,19
    # 06: 08,09,10,12,13,14,15,16,17,18,19,20
    # 07: 08,09,10,12,13,14,15,16,17,18,19,20
    # 08: 09,10,12,13,14,15,16,17,18,19
    # 09: 09,10,12,13,14,15,16,17,18,19
    # 10: 09,10,12,13,14,15,16,17,18
    # 11: 10,13,14,15,16,17,18
    # 12: 10,13,14,15,16,17
    # Horas           00,01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16,17,18,19,20,21,22,23
    HorasAfeccion[1]= [0,0,0,0,0,0,0,0,0,0,1,0,0,1,1,1,1,1,0,0,0,0,0,0]
    HorasAfeccion[2]= [0,0,0,0,0,0,0,0,0,0,1,0,1,1,1,1,1,1,1,0,0,0,0,0]
    HorasAfeccion[3]= [0,0,0,0,0,0,0,0,0,1,1,0,1,1,1,1,1,1,1,0,0,0,0,0]
    HorasAfeccion[4]= [0,0,0,0,0,0,0,0,0,1,1,0,1,1,1,1,1,1,1,1,0,0,0,0]
    HorasAfeccion[5]= [0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,1,1,1,1,1,0,0,0,0]
    HorasAfeccion[6]= [0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,1,1,1,1,1,1,0,0,0]
    HorasAfeccion[7]= [0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,1,1,1,1,1,1,0,0,0]
    HorasAfeccion[8]= [0,0,0,0,0,0,0,0,0,1,1,0,1,1,1,1,1,1,1,1,0,0,0,0]
    HorasAfeccion[9]= [0,0,0,0,0,0,0,0,0,1,1,0,1,1,1,1,1,1,1,1,0,0,0,0]
    HorasAfeccion[10]=[0,0,0,0,0,0,0,0,0,1,1,0,1,1,1,1,1,1,1,0,0,0,0,0]
    HorasAfeccion[11]=[0,0,0,0,0,0,0,0,0,0,1,0,0,1,1,1,1,1,1,0,0,0,0,0]
    HorasAfeccion[12]=[0,0,0,0,0,0,0,0,0,0,1,0,0,1,1,1,1,1,0,0,0,0,0,0]
    
    nMes=dateToday.month
    nHour=dateToday.hour

    try:
        nSol=int(CieloAemet[0])
    except ValueError:
        nSol=0
    
    # Ahora a corregir con respecto a la temperatura exterior

    # Si el exterior está 17 grados más frio o mas, se considera que el sol no caliente
    # Si el exterior esta a 6 grados o menos, considero que no calienta
    # Si el exterior esta a 17 grados o más, ya calienta al máximo
    
    TempExterior = float(TempAemet[0])
    if TempExterior < 6:
        TempExterior = 6
    if TempExterior > 17:
        TempExterior = 17
        
    FactorTempExterior = (TempExterior -6)/11
    
    # Otro factor puede ser hace cuanto que está la caldera encendida o apagado
    # Nos puede dar una idea de la temperatura del suelo
    
    # Calculamos el factor total. Entre 0 (inercia lenta al calor) y 1 (inercia rápida al calor)
    
    FactorTotal=FactorSol[nSol]*HorasAfeccion[nMes][nHour]*FactorTempExterior

    if nVerbose > 0:
            Logfile.printError ('[Analisis] Mes: '+str(nMes))
            Logfile.printError ('[Analisis] Hora: '+str(nHour))
            Logfile.printError ('[Analisis] Temp Ext: '+TempAemet[0])
            Logfile.printError ('[Analisis] Cielo: '+CieloAemet[0])
            Logfile.printError ('[Analisis] Cielo Array: '+str(nSol))
            Logfile.printError ('[Analisis] FactorSol: '+str(FactorSol[nSol]))
            Logfile.printError ('[Analisis] Horas Affeccion: '+str(HorasAfeccion[nMes][nHour]))
            Logfile.printError ('[Analisis] FactorTempExt: '+str(FactorTempExterior))
            Logfile.printError ('[Analisis] FactorTotal: '+str(FactorTotal))
    return(FactorTotal)

def analisis(RoomsLocalAnalisys, TempAemet, CieloAemet, nVerbose):

    # Estos factores tendremos que ajustarlos segun más cosas (temperatura exterior...)
    inercia_subida=1200 # tiempo que consideramos que va a seguir subiendo despues de apagado (aunque es más bien un factor de calculo)
    inercia_bajada=1200 # tiempo que sigue bajando temperatura si pongo ahora la caldera (aunque es más bien un factor de calculo)

    # El factor de correccion va a ajustar las inercias dependiendo del sol, epoca del año, hora y temperatura exterior
    FactorCorreccion = factorcorreccion (RoomsLocalAnalisys, TempAemet, CieloAemet, nVerbose)
        
    nIter=0
    
    for (room) in RoomsLocalAnalisys:    #Vamos sobre todas las habitaciones
        # Analisis basico de diferencia de dos ultimas temperaturas
        
        timeDifference = room['Date'] - room['DatePrev']
        nSeconds = timeDifference.total_seconds() # Segundos entre las dos ultimas medidas
        tempIter0=room['Temp']
        tempIter1=room['TempPrev']
        nDiffConsigna=tempIter0-room['Consigna']               # Negativo: hay que calentar
        nVariacionTemp = (tempIter0 - tempIter1)
        nPendiente = nVariacionTemp/nSeconds+0.000001      # Evitar division por 0
    
        if nDiffConsigna <0: # Hace mas frio
            nSegundosConvergencia=nDiffConsigna/nPendiente*(-1) # el -1 es porque la diff es negativa y la convergencia es solo con Pendiente positiva
            if nSegundosConvergencia>inercia_subida or nVariacionTemp<0: # Si con esta convergencia no llego en x tiempo
                room['Caldera'] = 'on'
                #szCalderaOnOff[0][nIter]='on'
            else:
                room['Caldera'] = 'off'
                #szCalderaOnOff[0][nIter]='off'
                
        if nDiffConsigna >=0:  # Hace mas calor o igual
            nSegundosConvergencia=nDiffConsigna/nPendiente*(-1) # Por lo mismo pero al contrario
            if nSegundosConvergencia<inercia_bajada and nPendiente<0: # Si estoy reduciendo temperatura muy rapido
                room['Caldera'] = 'on'
                #szCalderaOnOff[0][nIter]='on'
            else:
                room['Caldera'] = 'off'
                #szCalderaOnOff[0][nIter]='off'
    
        if nVerbose > 0:
            Logfile.printError ('[Analisis] Para habitacion '+ room['roomID'])
            Logfile.printError ('[Analisis] -----------------')
            Logfile.printError ('[Analisis] Temp consigna: '+ str(room['Consigna']))
            Logfile.printError ('[Analisis] Temp actual: '+ str(room['Temp']))
            Logfile.printError ('[Analisis] Temp anterior: '+ str(room['TempPrev']))
            Logfile.printError ('[Analisis] Seconds: '+str(nSeconds))
            Logfile.printError ('[Analisis] Delta Temp: '+str(nVariacionTemp))
            Logfile.printError ('[Analisis] Velocidad Variacion: '+str(nPendiente)) 
            Logfile.printError ('[Analisis] Diff consigna: '+str(nDiffConsigna))
            Logfile.printError ('[Analisis] Segundos Convergencia1: '+str(nSegundosConvergencia))
            Logfile.printError ('[Analisis] Caldera: ' + str(room['Caldera']))
            Logfile.printError ('[Analisis]  ')
        nIter+=1

        
def mainControl(RoomDataList, TempAemet, CieloAemet, nVerbose):

    # Vamos a usar solo las medidas actuales y la anterior    
    
    dateToday = datetime.datetime.now()
    dateInit = datetime.datetime.fromordinal(730920)
    
    RoomsLocalAnalisys = []
    
    for (RoomDict) in RoomDataList:
        # Temp1 es Airzone
        # Temp2 es la media de lo otros
        numTemps = 0
            
        tempRoom = 0
                            
        if RoomDict['Temp1'] != 'NULL':
            
            tempRoom += float(RoomDict['Temp1'])
            numTemps += 1
        # De momento no usamos DS hasta ver qué le pasa a la cocina   
        #if RoomDict['Temp2'] != 'NULL':
        #    tempRoom += float(RoomDict['Temp2'])
        #    numTemps += 1
                    
        if (numTemps > 0):
            tempRoom = int (tempRoom / numTemps *100) / 100   
        else:
            tempRoom  = 22
            
        RoomData = {'Date':dateToday, 'Temp': tempRoom, 'DatePrev':dateInit, 'TempPrev': 0, 'Caldera': 'off', 'roomID' : RoomDict['roomID'], 'Consigna': RoomDict['Consigna']} 
        RoomsLocalAnalisys.append(RoomData)
            
    readLineasDB(RoomsLocalAnalisys, nVerbose)
        
    analisis(RoomsLocalAnalisys, TempAemet, CieloAemet, nVerbose)
    
    # Una lista se hizo con respecto a la otra por lo que los indices coinciden
    
    nRoom = 0
    for (RoomDict) in RoomDataList:
        RoomDict['Caldera'] = RoomsLocalAnalisys[nRoom]['Caldera']
        nRoom +=1
    
    return

def main():

    TempAemet = ['Null' for i in range(7)]
    CieloAemet = ['Null' for i in range(7)]

    TempAemet[0] ='12.5'
    TempAemet[1] ='6'
    TempAemet[2] ='5'

    CieloAemet[0]='11'
    CieloAemet[1]='11'
    CieloAemet[2]='11'
    
    RoomDataList = [{'Caldera': 'NULL', 'roomNumber': 4, 'Consigna': -0.5, 'Terms': [{'devId': 'TempPrincipal', 'Value': 23.1, 'Address': '192.168.2.131'}], 'Temp1': 'NULL', 'Valvs': [{'devId': 'ValvPrincipal_1', 'Value': 0, 'Address': '192.168.2.131'}, {'devId': 'ValvPrincipal_2', 'Value': 0, 'Address': '192.168.2.131'}], 'roomID': 'Principal', 'Temp2': 'NULL'}, {'Caldera': 'NULL', 'roomNumber': 5, 'Consigna': -0.5, 'Terms': [{'devId': 'TempSofia', 'Value': 23.2, 'Address': '192.168.2.131'}], 'Temp1': 'NULL', 'Valvs': [{'devId': 'ValvSofia', 'Value': 0, 'Address': '192.168.2.132'}], 'roomID': 'Sofia', 'Temp2': 'NULL'}, {'Caldera': 'NULL', 'roomNumber': 6, 'Consigna': -0.5, 'Terms': [{'devId': 'TempAlvaro', 'Value': 23.3, 'Address': '192.168.2.131'}], 'Temp1': 'NULL', 'Valvs': [{'devId': 'ValvAlvaro', 'Value': 0, 'Address': '192.168.2.131'}], 'roomID': 'Alvaro', 'Temp2': 'NULL'}]
    
    mainControl(RoomDataList, TempAemet, CieloAemet, 1)
    print (RoomDataList)


if __name__ == "__main__":
    main()
