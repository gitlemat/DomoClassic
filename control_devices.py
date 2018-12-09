import requests
import Logfile
import serial
import sys
import mysql.connector as mariadb
import HandleDeviceConfig

import ast

import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu

PORT = '/dev/ttyUSB1'
WIFI_COIL = 0
MB_COMMAND_READ = 0
MB_COMMAND_WRITE = 1



############################################################################################
############################################################################################
#
# Handle Devices HW Config
#
############################################################################################
############################################################################################

def UpdateHWFirmware(szAddress, variablesDict, nVerbose): 
    
    # http://192.168.2.135/UpdateHW?AddressNew=192.168.2.136&mbAddress=34&HWtype=Sonoff
    
    szURL = 'http://'+szAddress+'/UpdateHW?'
    
    szURLparams = ""
    
    returndata=0   
        
    # Actualizamos lo que he pillado con lo que me viene a modificar
    
    if (variablesDict.get('AddressNew')):
        szURLparams+='&AddressNew='+variablesDict['AddressNew'][0]
    if (variablesDict.get('mbAddress')):
        szURLparams+='&mbAddress='+variablesDict['mbAddress'][0]
    if (variablesDict.get('HWtype')):
        szURLparams+='&HWtype='+variablesDict['HWtype'][0]
     
    szURL = szURL + szURLparams

    if (nVerbose > 0):
        Logfile.printError ('[ControlDevices] Update HW config: ' + szURL)

    s=requests.session()
    try:
        response = s.get(szURL,stream=False, timeout=10)
        returndata = response.text
    except requests.exceptions.RequestException as e:
        Logfile.printError ('[ControlDevices] Error leyendo estado device: '+szId)
        returndata = -1
        pass 
                
    s.close()
               
    return (returndata)	
    
def DeleteFullFirmware(szAddress, nVerbose): 

    # http://192.168.2.135/deInitAll
    
    szURL = 'http://'+szAddress+'/deInitAll'
        
    returndata=0   
        
    if (nVerbose > 0):
        Logfile.printError ('[ControlDevices] Request a Device: ' + szURL)

    s=requests.session()
    try:
        response = s.get(szURL,stream=False, timeout=10)
        returndata = response.status_code
    except requests.exceptions.RequestException as e:
        Logfile.printError ('[ControlDevices] Error leyendo estado device: '+szId)
        returndata = -1
        pass 
                
    s.close()
               
    return (returndata)	
    
############################################################################################
############################################################################################
#
# Handle Usages Config via WiFi
#
############################################################################################
############################################################################################

def AddModifyUsageFirmware(szAddress, szId, variablesDict, nVerbose): 

    # http://192.168.2.135/AddModifyUsage?devId=TMP234&devIdNew=SOAN1&devType=tLuz&pinInput1=4&pinInput2=5&pinOutput1=11&pinOutput2=13&Description=Teas%20Test
    
    szURL = 'http://'+szAddress+'/AddModifyUsage?devId='+szId
    
    szURLparams = ""
    
    returndata=0   
        
    # Actualizamos lo que he pillado con lo que me viene a modificar
    
    if (variablesDict.get('devIdNew')):
        szURLparams+='&devIdNew='+variablesDict['devIdNew'][0]
    if (variablesDict.get('devType')):
        szURLparams+='&devType='+variablesDict['devType'][0]
    if (variablesDict.get('pinInput1')):
        szURLparams+='&pinInput1='+variablesDict['pinInput1'][0]
    if (variablesDict.get('pinInput2')):
        szURLparams+='&pinInput2='+variablesDict['pinInput2'][0]
    if (variablesDict.get('pinInput3')):
        szURLparams+='&pinInput3='+variablesDict['pinInput3'][0]
    if (variablesDict.get('pinInput4')):
        szURLparams+='&pinInput4='+variablesDict['pinInput4'][0]
    if (variablesDict.get('pinOutput1')):
        szURLparams+='&pinOutput1='+variablesDict['pinOutput1'][0]
    if (variablesDict.get('pinOutput2')):
        szURLparams+='&pinOutput2='+variablesDict['pinOutput2'][0]
    if (variablesDict.get('pinOutput3')):
        szURLparams+='&pinOutput3='+variablesDict['pinOutput3'][0]
    if (variablesDict.get('pinOutput4')):
        szURLparams+='&pinOutput4='+variablesDict['pinOutput4'][0]
    if (variablesDict.get('Description')):
        szURLparams+='&Description='+variablesDict['Description'][0]
     
    szURL = szURL + szURLparams

    if (nVerbose > 0):
        Logfile.printError ('[ControlDevices] Request a Device: ' + szURL)

    s=requests.session()
    try:
        response = s.get(szURL,stream=False, timeout=10)            # responde el nUsage
        returndata = response.text
    except requests.exceptions.RequestException as e:
        Logfile.printError ('[ControlDevices] Error leyendo estado device: '+szId)
        returndata = -1
        pass 
                
    s.close()
               
    return (returndata)	 # devuelve el nUsage

def DeleteUsageFirmware(szAddress, szId, nVerbose): 

    # http://192.168.2.135/Initialize?devId=TMP234&szMaster=FALSE&devId=SOAN1&ip=192.168.2.135&type=tLuz&Description=Teas%20Test
    
    szURL = 'http://'+szAddress+'/deleteUsage?devId='+szId
    
    szURLparams = ""
    
    returndata=0   
        
    if (nVerbose > 0):
        Logfile.printError ('[ControlDevices] Request a Device: ' + szURL)

    s=requests.session()
    try:
        response = s.get(szURL,stream=False, timeout=10)
        returndata = response.status_code
    except requests.exceptions.RequestException as e:
        Logfile.printError ('[ControlDevices] Error leyendo estado device: '+szId)
        returndata = -1
        pass 
                
    s.close()
               
    return (returndata)	
    
    
############################################################################################
############################################################################################
#
# Handle HW WiFi ON/OFF via MODBUS
#
############################################################################################
############################################################################################

def DeviceWiFiSate(mbAddress, nWiFiState, nVerbose): 
    
    try:
        master = modbus_rtu.RtuMaster(
            serial.Serial(port=PORT, baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0)
        ) 
        master.set_timeout(5.0)
    
        result = master.execute(mbAddress, cst.WRITE_SINGLE_COIL, WIFI_COIL, output_value=nWiFiState)
        
    except modbus_tk.modbus.ModbusError as exc:
        Logfile.printError ('[ControlDevices] Error Modbus %s- Code=%d', exc, exc.get_exception_code())
        
    print (result)
        
    
############################################################################################
############################################################################################
#
# Handle Usages states
#
############################################################################################
############################################################################################

def ReadUsageState(szCommType, szId, nVerbose, szAddress = 'NULL', szStatus = 'NULL'): 
    
    if (szCommType.upper() == "MODBUS"):
        pass
    
    if (szCommType.upper() == "WIFI"):
        returndata = ReadUsageStateWiFi(szId, szAddress, szStatus, nVerbose)
        
    try:
        returndata = ast.literal_eval(returndata)
    except:
        returndata = [{"Status": 503}]
        
    return (returndata)
    
def UpdateUsageState(szCommType, szId, nState, nVerbose, szAddress = 'NULL', szStatus = 'NULL'):

    if (szCommType.upper() == "MODBUS"):
        pass
    
    if (szCommType.upper() == "WIFI"):
        returndata = UpdateUsageStateWiFi(szId, nState, szAddress, szStatus, nVerbose)
                
    return (returndata)

def ReadUsageStateMODBUS(szDevId, nVerbose): 

    AddressList = HandleDeviceConfig.GetAdressesFromDevId (szDevId, nVerbose)
    
    mbAddress = AddressList[0]['mbAddress']
    nUsage = AddressList[0]['nUsage']
    
    try:
        master = modbus_rtu.RtuMaster(
            serial.Serial(port=PORT, baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0)
        ) 
        master.set_timeout(5.0)
    
        result = master.execute(mbAddress, cst.READ_HOLDING_REGISTERS, nUsage , 1)
        
    except modbus_tk.modbus.ModbusError as exc:
        Logfile.printError ('[ControlDevices] Error Modbus %s- Code=%d', exc, exc.get_exception_code())
        
    return (result[0])

def UpdateUsageStateWiFi(szId, nState, szAddress, szStatus, nVerbose):

    if (szAddress == 'NULL' or szStatus == 'NULL'):
        mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
        cursor = mariadb_connection.cursor()
    
        szMysqlReq="SELECT AddrType, Address, State from DEVICES where devId = '"+szId+"'"
    
        try:
            cursor.execute(szMysqlReq)    
        except mariadb.Error as error:
            Logfile.printError ('[ControlDevices] Error DB: {}'.format(error))

        mariadb_connection.close()
            
        row = cursor.fetchone()
    
        szAddrType = row[0]
        szAddress = row[1]
        szStatus = row[2]
    
    if szStatus == 'off':
        return (-1)
        
    # http://192.168.2.135/Update?devId=DEV&State=0
    
    szURL = 'http://'+szAddress+'/Update?devId='+szId+'&State='+str(nState)
    
    Logfile.printError ('[ControlDevices]'+szURL)
    
    s=requests.session()
    try:
        response = s.get(szURL,stream=False, timeout=10)
        returndata = response.text
    except requests.exceptions.RequestException as e:
        Logfile.printError ('[ControlDevices] Error lanzando update a device: '+szId)
        returndata = -1
        pass 
                
    s.close()
            
    return (returndata)
    
def ReadUsageStateWiFi(szId, szAddress, szStatus, nVerbose): 

    returndatafail = "[{\"devId\": \"NULL\", \"Status\": 503, \"State\":0}]"
    if (szAddress == 'NULL' or szStatus == 'NULL'):
        mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
        cursor = mariadb_connection.cursor()
    
        szMysqlReq="SELECT AddrType, Address, State from DEVICES where devId = '"+szId+"'"
    
        try:
            cursor.execute(szMysqlReq)    
        except mariadb.Error as error:
            Logfile.printError ('[ControlDevices] Error DB: {}'.format(error))

        mariadb_connection.close()
            
        row = cursor.fetchone()
        
        if (cursor.rowcount < 0):
            return(returndatafail)
    
        szAddrType = row[0]
        szAddress = row[1]
        szStatus = row[2]
    
    if szStatus == 'off':
        
        return (returndatafail)
    
    szURL = 'http://'+szAddress+'/Read?devId='+szId
    
    s=requests.session()
    try:
        response = s.get(szURL,stream=False, timeout=10)
        returndata = response.text         
    except requests.exceptions.RequestException as e:
        Logfile.printError ('[ControlDevices] Error leyendo estado device: '+szId)
        returndata = returndatafail
        pass 
                        
    s.close()
                
    return (returndata)

def UpdateUsageStateMODBUS(szDevId, nState, szAddress, szStatus, nVerbose): 

    AddressList = HandleDeviceConfig.GetAdressesFromDevId (szDevId, nVerbose)
    
    mbAddress = AddressList[0]['mbAddress']
    nUsage = AddressList[0]['nUsage']
    
    try:
        master = modbus_rtu.RtuMaster(
            serial.Serial(port=PORT, baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0)
        ) 
        master.set_timeout(5.0)
    
        master.execute(mbAddress, cst.WRITE_SINGLE_REGISTER, nUsage , nState)
        
    except modbus_tk.modbus.ModbusError as exc:
        Logfile.printError ('[ControlDevices] Error Modbus %s- Code=%d', exc, exc.get_exception_code())
        
    return (0)    
                
def main():
    #ReadUsageStateWiFi('Luz_JardinD_1', 'NULL', 'NULL', 1)
    print (ReadUsageStateWiFi('Luz_JardinD_1', 'NULL', 'NULL', 1))
    pass 
       
if __name__ == "__main__":
    main()
