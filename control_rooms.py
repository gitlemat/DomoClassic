import requests
import Logfile
import serial
import sys
import mysql.connector as mariadb

import ast



############################################################################################
############################################################################################
#
# Handle Devices HW Config
#
############################################################################################
############################################################################################

def GetRoomList (nVerbose):
    
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()

    #select * from temps order by timedate desc limit 3;

    szMysqlReq="SELECT DISTINCT rc.roomNumber, rc.`roomID`, rc.`plantaID` from ROOM_CONF AS rc INNER JOIN DEVICES as us ON us.`roomNumber` = rc.`roomNumber` where (us.`devType` = 'tValvulaCal' or us.`devType` = 'tTempDS18' or us.`devType` = 'tTempDHT') and rc.roomNumber < 100 ORDER by plantaID"
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[Calefaccion] Error DB: {}'.format(error))

    
    szRoomList=[]
    
    for (roomNumber, roomID, plantaID) in cursor:
        szRoomList.append({'roomNumber':roomNumber,'roomID':roomID, 'plantaID':plantaID})
        
    mariadb_connection.close()
    
    return (szRoomList)
    
def GetRoomListTree (nVerbose):
    
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()

    #select * from temps order by timedate desc limit 3;

    szMysqlReq="SELECT DISTINCT rc.roomNumber, rc.`roomID`, rc.`plantaID`, rc.`plantaNumber` from ROOM_CONF AS rc INNER JOIN DEVICES as us ON us.`roomNumber` = rc.`roomNumber` where (us.`devType` = 'tValvulaCal' or us.`devType` = 'tTempDS18' or us.`devType` = 'tTempDHT') and rc.roomNumber < 100 ORDER by plantaNumber, roomNumber"
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[Calefaccion] Error DB: {}'.format(error))

    szRoomList=[]
    szPlantasList = []
    
    szPlantaId = ""
    szRoomId = ""
    nRoomNumber = 0
    
    for (roomNumber, roomID, plantaID, plantaNumber) in cursor:
        if (szPlantaId != plantaID and szPlantaId != ""):
            szPlantasList.append({'plantaID':szPlantaId, 'plantaNumber': nPlantaNumber, 'rooms':szRoomList})
            szRoomList=[]
        szRoomList.append({'roomNumber':roomNumber,'roomID':roomID})
        szPlantaId = plantaID
        nPlantaNumber = plantaNumber
        szRoomId = roomID
        nRoomNumber = roomNumber
        
    # Ahora el ultimo 
    szPlantasList.append({'plantaID':szPlantaId, 'plantaNumber': nPlantaNumber, 'rooms':szRoomList})
        
    mariadb_connection.close()
    
    return (szPlantasList)
                    
def main():
    #ReadUsageStateWiFi('Luz_JardinD_1', 'NULL', 'NULL', 1)
    print (GetRoomListTree(1))
    pass 
       
if __name__ == "__main__":
    main()
