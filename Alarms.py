import datetime
import time, os
import mysql.connector as mariadb
import Logfile

      
def GetAlarmDefMariaDB (idAlarma, nVerbose):

    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    szMysqlReq="SELECT id, System, Subsystem, Severity, devId, Description from ALARMS where id = " + str(idAlarma)
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[Alarms] Error DB: {}'.format(error))

    mariadb_connection.close()
    
    szAlarmDefList=[]
    
    for (id, System, Subsystem, Severity, devId, Description) in cursor:
        szAlarmDefList.append({'id':id,'System':System,'Subsystem':Subsystem,'Severity':Severity,'devId':devId,'Description':Description})

    return (szAlarmDefList)
    
def readAlarmsMariaDB (variablesList, nVerbose):

    szParams = ""
    szSystem = ""
    if (variablesList.get('System')):
        szSystem = variablesList['System'][0]   
        szParams += " and adef.System = '" + szSystem + "'"
    szSubsystem = ""
    if (variablesList.get('Subsystem')):
        szSubsystem = variablesList['Subsystem'][0]
        szParams += " and adef.Subsystem = '" + szSubsystem + "'"
    szSeverity = ""
    if (variablesList.get('Severity')):
        szSeverity = variablesList['Severity'][0]
        szParams += " and adef.Severity = " + szSeverity
    szDevId = ""
    if (variablesList.get('devId')):
        szDevId = variablesList['devId'][0]
        szParams += " and adef.devId = '" + szDevId + "'"

    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    # SELECT al.`AlarmId`, al.`Timestamp`, al.`DevId`, adef.`System`, adef.`Subsystem`, adef.`Severity`, adef.`Description` FROM ALARMS_ACTIVE AS al INNER JOIN ALARMS AS adef ON al.`AlarmId` = adef.`id`;
    # SELECT al.`AlarmId`, al.`Timestamp`, al.`DevId`, adef.`System`, adef.`Subsystem`, adef.`Severity`, adef.`Description` FROM ALARMS_ACTIVE AS al INNER JOIN ALARMS AS adef ON al.`AlarmId` = adef.`id` AND al.`AlarmId` = 102;
    # SELECT al.`AlarmId`, al.`Timestamp`, al.`DevId`, adef.`System`, adef.`Subsystem`, adef.`Severity`, adef.`Description` FROM ALARMS_ACTIVE AS al INNER JOIN ALARMS AS adef ON al.`AlarmId` = adef.`id` AND adef.`System` = 'Calefaccion';
    
    
    szMysqlReq="SELECT al.`AlarmId`, DATE_FORMAT(al.Timestamp, '%Y-%m-%d %H:%i:%s') Timestamp, al.`DevId`, adef.`System`, adef.`Subsystem`, adef.`Severity`, adef.`Description` FROM ALARMS_ACTIVE AS al INNER JOIN ALARMS AS adef ON al.`AlarmId` = adef.`id`" + szParams
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[Alarms] Error DB: {}'.format(error))

    mariadb_connection.close()
    
    szAlarmList=[]
    
    for (AlarmId, Timestamp, DevId, System, Subsystem, Severity, Description) in cursor:
        szAlarmList.append({'AlarmId':AlarmId,'Timestamp':Timestamp,'DevId':DevId,'System':System,'Subsystem':Subsystem,'Severity':Severity,'Description':Description})

    return (szAlarmList)

        
def writeAlarmToMariaDB (idAlarma, bActive, szDevId, nVerbose):

    date1=datetime.datetime.now().strftime ("%Y-%m-%d %H:%M:%S")
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    db_data = {
        'AlarmId': idAlarma,
        'DevId': szDevId,
        'DateTime': date1,
    }
    
    if (bActive):
                
        if (szDevId != "NULL"):
            szMysqlReq="INSERT INTO ALARMS_ACTIVE (Timestamp, AlarmId, DevId) VALUES (%(DateTime)s,%(AlarmId)s,%(DevId)s)"
        else:
            szMysqlReq="INSERT INTO ALARMS_ACTIVE (Timestamp, AlarmId) VALUES (%(DateTime)s,%(AlarmId)s)"
        
        if (nVerbose > 0):
            Logfile.printError ('[Alarms] ' + szMysqlReq)
            
    
    else:
        szMysqlReq="DELETE FROM ALARMS_ACTIVE WHERE AlarmId = %(AlarmId)s"
        
        if (szDevId != "NULL"):
            szMysqlReq = szMysqlReq + " and DevId = %(DevId)s"
        else:
            szMysqlReq = szMysqlReq + " and DevId IS NULL"
        
        
        if (nVerbose > 0):
            Logfile.printError ('[Alarms] ' + szMysqlReq)
            
            
    try:
        cursor.execute(szMysqlReq, db_data)    
        mariadb_connection.commit()
    except mariadb.Error as error:
        Logfile.printError ('[Alarms] Error DB: {}'.format(error))
        
                
    mariadb_connection.close()
            
    return 
    
def main():

    #variablesList = {'Severity' : ['1']}
    #variablesList = {}
    #nVerbose = 1
    #szAlarms = readAlarmsMariaDB(variablesList, nVerbose)
    #print (szAlarms);
    writeAlarmToMariaDB (101, 1, 'NULL', 1)
    #print (GetAlarmDefMariaDB (101, 1))
    
    
if __name__ == "__main__":
    main()
