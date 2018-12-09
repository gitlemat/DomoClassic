import requests
import Logfile
import mysql.connector as mariadb

# GetHWTypesList(szSortBy,nVerbose)
# GetTypesList(szSortBy,nVerbose)
# GetUsagesListAll(szSortBy, nVerbose)
# GetDeviceHWListAll(szSortBy, nVerbose)
# GetUsageListAllOn(szSortBy, nVerbose)
# GetUsageListTypeOn(szTypeReq, nVerbose)

# GetRoomFromDevId(devId, nVerbose)

# AddDeviceHWDB(szAddress, variablesDict, nVerbose)
#     UpdateDeviceHWDB(szAddress, variablesDict, nVerbose)
#     UpdateUsageToHWDB(szAddress, bAddDelete, numInputsDelta, numOutputsDelta , nVerbose)
# DeleteDeviceHWDB (szAddress, nVerbose)

# AddUpdateUsageConfig(szDevId, variablesDict, nVerbose)
#     AddUsageDB(szDevId, variablesDict, nVerbose)     #### No llamar , solo interna
# DeleteUsageDB (szDevId, nVerbose)


# UpdateDeviceState(szAddress, szState, nVerbose)


# ReadIfDeviceHWExists(szField, szValue, nVerbose)
# ReadIfUsageExists(szField, szValue, nVerbose)


###################################################################################################
###################################################################################################
#
# Funciones to GET
#
###################################################################################################
###################################################################################################

def GetHWTypesList(szSortBy,nVerbose): 

    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    szMysqlReq="SELECT HWType, maxUsages, maxInputs, maxOutputs, modbus from HW_TYPES"
    
    if (szSortBy != ""):
        szMysqlReq += " ORDER BY " + szSortBy

    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))

    mariadb_connection.close()
        
    szTypesList=[]
    
    for (HWType, maxUsages, maxInputs, maxOutputs, modbus) in cursor:
        szTypesList.append({'HWType':HWType, 'maxUsages':maxUsages, 'maxInputs':maxInputs, 'maxOutputs':maxOutputs, 'modbus':modbus})

    return (szTypesList)

def GetTypesList(szSortBy,nVerbose): 

    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    szMysqlReq="SELECT devType, devType from DEVTYPES"
    
    if (szSortBy != ""):
        szMysqlReq += " ORDER BY " + szSortBy

    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))

    mariadb_connection.close()
        
    szTypesList=[]
    
    for (devType, ddd) in cursor:
        szTypesList.append({'devType':devType})

    return (szTypesList)


def GetUsagesListAll(szSortBy, nVerbose): 

    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    szMysqlReq="SELECT devType, devId, roomNumber, numButton, AddrType, Address, Description from DEVICES"
    
    if (szSortBy != ""):
        szMysqlReq += " ORDER BY " + szSortBy

    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))

    mariadb_connection.close()
        
    szDeviceList=[]
    
    for (devType, devId, roomNumber, numButton, AddrType, Address, Description) in cursor:
        szDeviceList.append({'devType':devType, 'roomNumber':roomNumber, 'numButton':numButton,'devId':devId,'Address':Address,'Description':Description})

    return (szDeviceList)

def GetDeviceHWListAll(szSortBy, nVerbose): 

    
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    szMysqlReq="SELECT HWType, numUsages, AddrType, Address, State from DEVICES_HW"
    
    if (szSortBy != ""):
        szMysqlReq += " ORDER BY " + szSortBy
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))

    mariadb_connection.close()
        
    szDeviceList=[]
    
    for (HWType, numUsages, AddrType, Address, State) in cursor:
        szDeviceList.append({'HWType':HWType,'numUsages':numUsages,'AddrType':AddrType,'Address':Address,'State':State})

    return (szDeviceList)
        
def GetUsageListAllOn(szSortBy, nVerbose): 

    
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    #szMysqlReq="SELECT devType, devId, numButton, AddrType, Address, State, Description from DEVICES where State = 'on'"
    
    szMysqlReq="SELECT us.devType, us.devId, us.numButton, hw.AddrType, hw.Address, hw.State, us.Description from DEVICES AS us INNER JOIN DEVICES_HW AS hw  ON us.Address = hw.address where hw.State = 'on'"
    
    
    if (szSortBy != ""):
        szMysqlReq += " ORDER BY " + szSortBy
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))

    mariadb_connection.close()
        
    szDeviceList=[]
    
    for (devType, devId, numButton, AddrType, Address, State, Description) in cursor:
        szDeviceList.append({'devType':devType,'numButton':numButton,'devId':devId,'Address':Address,'State':State,'Description':Description})

    return (szDeviceList)
    
def GetHWUsagesListTreeAll(nVerbose):
    
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    szMysqlReq="SELECT hw.Address, hw.mbAddress ,hw.State, hw.HWtype, typ.maxUsages, typ.maxInputs, typ.maxOutputs, us.devType, us.devId, us.numButton, us.numOutputs, us.pinInput1, us.pinInput2, us.pinInput3, us.pinInput4, us.pinOutput1, us.pinOutput2, us.pinOutput3, us.pinOutput4, us.Description from DEVICES AS us INNER JOIN DEVICES_HW AS hw  ON us.Address = hw.address INNER JOIN HW_TYPES AS typ ON typ.HWtype = hw.HWtype ORDER by Address"
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
        
    szDeviceList=[]
    szDeviceListEnd=[]
    szHWList = []
    
    szAddress = ""
    nMbAddress = 0
    szState = ""
    szHWType = ""
    nMaxUsages = 0
    nMaxInputs = 0
    nMaxOutputs = 0
    
    
    
    for (Address, mbAddress, State, HWType, maxUsages, maxInputs, maxOutputs, devType, devId, numButton, numOutputs, pinInput1, pinInput2, pinInput3, pinInput4, pinOutput1, pinOutput2, pinOutput3, pinOutput4, Description) in cursor:
        if (szAddress != Address and szAddress != ""):
            szHWList.append({'Address':szAddress,'mbAddress':nMbAddress,'State':szState,'HWType':szHWType,'maxUsages':nMaxUsages,'maxInputs':nMaxInputs,'maxOutputs':nMaxOutputs,'usage':szDeviceList})
            szDeviceList=[]
        szDeviceList.append({'devId':devId,'numButton':numButton,'numOutputs':numOutputs,'pinInput1':pinInput1,'pinInput2':pinInput2,'pinInput3':pinInput3,'pinInput4':pinInput4,'pinOutput1':pinOutput1,'pinOutput2':pinOutput2,'pinOutput3':pinOutput3,'pinOutput4':pinOutput4,'devType':devType,'Description':Description})
        szAddress = Address
        nMbAddress = mbAddress
        szHWType = HWType
        szState = State
        nMaxUsages = maxUsages
        nMaxInputs = maxInputs
        nMaxOutputs = maxOutputs
    
    # Ahora el ultimo    
    szHWList.append({'Address':szAddress,'mbAddress':nMbAddress,'State':szState,'HWType':szHWType,'maxUsages':nMaxUsages,'maxInputs':nMaxInputs,'maxOutputs':nMaxOutputs,'usage':szDeviceList})
       
    # Ahora los que no tienen DEVICE
    cursor = mariadb_connection.cursor()                   
                    
    szMysqlReq="SELECT hw.Address, hw.mbAddress ,hw.State, hw.HWtype, typ.maxUsages, typ.maxInputs, typ.maxOutputs from DEVICES_HW AS hw INNER JOIN HW_TYPES AS typ ON typ.HWtype = hw.HWtype where hw.numUsages = 0"
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))

    mariadb_connection.close()
    
    for (Address, mbAddress, State, HWType, maxUsages, maxInputs, maxOutputs) in cursor:
        szHWList.append({'Address':Address,'mbAddress':mbAddress,'State':State,'HWType':HWType,'maxUsages':maxUsages,'maxInputs':maxInputs,'maxOutputs':maxOutputs,'usage':szDeviceListEnd})    
    
    return (szHWList)
    


def GetUsageListTypeOn(szTypeReq, nVerbose): 

    
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    szMysqlReq="SELECT us.devType, us.devId, us.numButton, hw.AddrType, hw.Address, us.Description from DEVICES AS us INNER JOIN DEVICES_HW AS hw  ON us.Address = hw.address where hw.State = 'on' and devType = '"+szTypeReq+"'"
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))

    mariadb_connection.close()
        
    szDeviceList=[]
    
    for (devType, devId, numButton, AddrType, Address, Description) in cursor:
        szDeviceList.append({'devType':devType,'numButton':numButton,'devId':devId,'Address':Address,'Description':Description})

    return (szDeviceList)
    

def GetUsageData(szDevId, nVerbose): 

    
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    szMysqlReq="SELECT us.devType, us.devId, us.nUsage, us.numButton, us.numOutputs, hw.AddrType, hw.Address, us.Description from DEVICES AS us INNER JOIN DEVICES_HW AS hw  ON us.Address = hw.address where devId = '"+szDevId+"'"
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))

    mariadb_connection.close()
        
    szDeviceList=[]
    
    for (devType, devId, nUsage, numButton, numOutputs, AddrType, Address, Description) in cursor:
        szDeviceList.append({'devType':devType,'nUsage':nUsage,'numButton':numButton,'numOutputs':numOutputs,'devId':devId,'Address':Address,'Description':Description})

    return (szDeviceList)
    
def GetRoomFromDevId(szDevId, nVerbose):

    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    szMysqlReq="select rc.roomID, rc.plantaID from ROOM_CONF as rc INNER JOIN DEVICES as us ON us.`roomNumber` = rc.`roomNumber` where devId = '"+szDevId+"'"
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))

    mariadb_connection.close()
            
    row = cursor.fetchone()
    
    if (cursor.rowcount < 0):
        return(-1)
    
    szRoom = row[0]
    szPlanta = row[1]
    
    szRoomInfo = []
    szRoomInfo.append({'roomID':szRoom, 'plantaID':szPlanta})

    return (szRoomInfo)
    

###################################################################################################
###################################################################################################
#
# Funciones to ADD
#
###################################################################################################
###################################################################################################


def AddDeviceHWDB(szAddress, variablesDict, nVerbose): 

    # Añade linea de DEVICE_HW (nuevo dispositivo HW)

    # /Device/Subscribe?devType=sonoff&devId=SOJD1&numUsages=2&Address=192%2E168%2E2%2E135
    
    szMbAddress = ""
    szAddrType = ""
    szHWType = ""
    szState = ""
    
    nMBAddress = -1
        
    if (variablesDict.get('HWtype')):
        szHWtype = variablesDict['HWtype'][0]
        if (CheckIfModBUS (szHWtype) > 0):
            nMBAddress = ObtainFreeModBusAddress()
            szAddrType = "IP+MB"
        else:
            szAddrType = "IP"

    if (variablesDict.get('AddrType')):
        szAddrType = variablesDict['AddrType'][0]

    
    szState = 'on'
    
    db_data = {
        'Address': szAddress,
        'mbAddress': nMBAddress,
        'AddrType': szAddrType,
        'HWtype': szHWtype,
        'State': szState,
        'numUsages' : 0,
        'numInputs' : 0,
        'numOutputs' : 0,
    }
            
    bExists = ReadIfDeviceHWExists('Address',szAddress, nVerbose)
    
    if (bExists >= 0):
        if (nVerbose > 0):
            Logfile.printError ('[HandleDeviceConfig] El DeviceHW:' + szAddress + ' ya existe')
        return
    
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
        
    szMysqlReq="INSERT INTO DEVICES_HW (Address, mbAddress, AddrType, HWtype, State, numUsages, numInputs, numOutputs) VALUES (%(Address)s,%(mbAddress)s,%(AddrType)s,%(HWtype)s,%(State)s,%(numUsages)s,%(numInputs)s,%(numOutputs)s)"
        
    if (nVerbose > 0):
        Logfile.printError ('[HandleDeviceConfig] Add DeviceHW:' + szMysqlReq + ', szAddress = ' + szAddress)
        
    try:
        cursor.execute(szMysqlReq, db_data)    
        mariadb_connection.commit()
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))

    mariadb_connection.close()

    return (nMBAddress)


    
def AddUsageDB(szDevId, variablesDict, nVerbose): 

    # Añade un Usage a la tabla de Usages
    # A su vez llama a la de actualizar DEVICE_HW
    # No se debería llamar desde fuera
    
    bADDUSAGE = 1
    bDELETEUSAGE = 0 
    
    nUsage = 0
    nPinInput1 = 0
    nPinInput2 = 0
    nPinInput3 = 0
    nPinInput4 = 0
    nPinOutput1 = 0
    nPinOutput2 = 0
    nPinOutput3 = 0
    nPinOutput4 = 0
    
    szDevType = ""
    szAddress = ""
    szDescription = ""
    nNumButton = 0
    nNumOutputs = 0
        
    if (variablesDict.get('devType')):
        szDevType = variablesDict['devType'][0]

    if (variablesDict.get('Address')):
        szAddress = variablesDict['Address'][0]
        
    if (variablesDict.get('numButton')):
        nNumButton = int(variablesDict['numButton'][0])
        
    if (variablesDict.get('numOutputs')):
        nNumOutputs = int(variablesDict['numOutputs'][0])
        
    if (variablesDict.get('nUsage')):
        nUsage = int(variablesDict['nUsage'][0])
        
    if (variablesDict.get('Description')):
        szDescription = variablesDict['Description'][0]
                   
    db_data = {
        'devID': szDevId,
        'devType': szDevType,
        'Address': szAddress,
        'nUsage' : nUsage,
        'numButton' : nNumButton,
        'numOutputs' : nNumOutputs,
        'Description' : szDescription,
    } 
            
    bExists = ReadIfUsageExists('devID',szDevId, nVerbose)
            
    if (bExists >= 0):
        return (-2)
    
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
        
    szMysqlReq="INSERT INTO DEVICES (devType, devId, nUsage, numButton, numOutputs, Address, Description) VALUES (%(devType)s,%(devID)s, %(nUsage)s,%(numButton)s,%(numOutputs)s,%(Address)s, %(Description)s)"
    
    if (nVerbose > 0):
        Logfile.printError ('[HandleDeviceConfig] Add Usage:' + szMysqlReq + ', szId = ' + szDevId)
        
    try:
        cursor.execute(szMysqlReq, db_data)    
        mariadb_connection.commit()
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
        return (-1)

    mariadb_connection.close()
    
    # Ahora hay que añadir el devId al DEVICES_HW

    result = UpdateUsageToHWDB(szAddress, bADDUSAGE, nNumButton, nNumOutputs , nVerbose) 
    
    if (result < 0):
        return (result)

    
    return (0)
    

###################################################################################################
###################################################################################################
#
# Funciones to UPDATE
#
###################################################################################################
###################################################################################################

def UpdateDeviceHWDB(szAddress, variablesDict, nVerbose): 

    bAddressChange = False
    szAddrType = ""
    szHWType = ""
    szAddressNew = ""
    szMbAddress = ""
    returndata = 0
     
    if (variablesDict.get('AddressNew')):
        szAddressNew=variablesDict['AddressNew'][0]
        if (szAddressNew != szAddress):
            bAddressChange = True
    else:
        szAddressNew=szAddress    
    
    szMysqlReq="UPDATE DEVICES_HW SET Address = %(AddressNew)s, "
    
    
    if (variablesDict.get('AddrType')):
        szAddrType=variablesDict['AddrType'][0]
        szMysqlReq += "AddrType = %(AddrType)s, "
        
    if (variablesDict.get('HWtype')):
        szHWType=variablesDict['HWtype'][0]
        szMysqlReq += "HWtype = %(HWtype)s, "
        
    if (variablesDict.get('mbAddress')):
        szMbAddress=variablesDict['mbAddress'][0]
        szMysqlReq += "mbAddress = %(mbAddress)s, "
        
    szMysqlReq += "Address = %(AddressNew)s WHERE Address = %(Address)s"
    
    if (nVerbose > 0):
        Logfile.printError ('[HandleDeviceConfig] ' + szMysqlReq + ". Address = " + szAddress)
        
    db_data = {
        'Address': szAddress,
        'AddressNew': szAddressNew,
        'AddrType': szAddrType,
        'HWtype' : szHWType,
        'mbAddress' : szMbAddress,
    } 
    
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()

    try:
        cursor.execute(szMysqlReq, db_data)    
        mariadb_connection.commit()
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
        returndata = -1        
        
    # Hay que cambiar la IP al resto de slaves
    
    if (bAddressChange == True):
        szMysqlReq="UPDATE DEVICES SET Address = %(AddressNew)s WHERE Address = %(Address)s"

        if (nVerbose > 0):
            Logfile.printError ('[HandleDeviceConfig] ' + szMysqlReq + ", Address = " + szAddress)
    
        try:
            cursor.execute(szMysqlReq,db_data)
            mariadb_connection.commit()
            returndata=0 
        except mariadb.Error as error:
            Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
            returndata=-1
                
    mariadb_connection.close()
    
    return (returndata)

def UpdateUsageToHWDB(szAddress, bAddDelete, numInputsDelta, numOutputsDelta , nVerbose): 

    # Añade Usage a una linea de DEVICE_HW (dispositivo HW que ya existe)
    # Bsicamente actualiza los numeros
    # bAddDelete = 0 -> Borrar
    # bAddDelete = 1 -> Añadir
    
    numUsagesNew = 0
    numInputsNew = 0
    numOutputsNew = 0
        
    
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    # SELECT numUsages, numInputs, numOutputs from DEVICES_HW where Address = 
    szMysqlReq="SELECT hw.HWtype, hw.numUsages, hw.numInputs, hw.numOutputs, typ.maxUsages, typ.maxInputs, typ.maxOutputs from DEVICES_HW AS hw INNER JOIN HW_TYPES AS typ ON hw.HWtype = typ.HWtype WHERE Address = '" + szAddress + "'"
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
        
    szInfoList=[] 
    
    for (HWtype, numUsages, numInputs, numOutputs, maxUsages, maxInputs, maxOutputs) in cursor:
        szInfoList.append({'HWtype':HWtype, 'numUsages':numUsages, 'numInputs':numInputs, 'numOutputs':numOutputs, 'maxUsages':maxUsages, 'maxInputs':maxInputs, 'maxOutputs':maxOutputs})
        
    if (len(szInfoList) < 1):
        return (-2)
        
    if (bAddDelete == 1):
        numUsagesNew = int(szInfoList[0]['numUsages']) + 1
        numInputsNew = int(szInfoList[0]['numInputs']) + numInputsDelta
        numOutputsNew = int(szInfoList[0]['numOutputs']) + numOutputsDelta
    else:
        numUsagesNew = int(szInfoList[0]['numUsages']) - 1
        numInputsNew = int(szInfoList[0]['numInputs']) - numInputsDelta
        numOutputsNew = int(szInfoList[0]['numOutputs']) - numOutputsDelta
    
    # Compribar si supero máximo
    
    if (numUsagesNew < 0 or numUsagesNew > szInfoList[0]['maxUsages']):
        Logfile.printError ('[HandleDeviceConfig] Numero erroneo de Usages')
        return (-1)
        
    if (numInputsNew < 0 or numInputsNew > szInfoList[0]['maxInputs']):
        Logfile.printError ('[HandleDeviceConfig] Numero erroneo de Inputs')
        return (-1)
        
    if (numOutputsNew < 0 or numOutputsNew > szInfoList[0]['maxOutputs']):
        Logfile.printError ('[HandleDeviceConfig] Numero erroneo de Outputs')
        return (-1)
            
    # devId1
    # UPDATE DEVICES SET AddrType = %s, Address = %s WHERE Address = %s
        
    db_data = {
        'Address': szAddress,
        'numInputs' : numInputsNew,
        'numOutputs' : numOutputsNew,
        'numUsages' : numUsagesNew,
    } 
    
    cursor = mariadb_connection.cursor()
    szMysqlReq="UPDATE DEVICES_HW SET numUsages = %(numUsages)s, numInputs = %(numInputs)s, numOutputs = %(numOutputs)s WHERE Address = %(Address)s"
    
    try:
        cursor.execute(szMysqlReq, db_data)    
        mariadb_connection.commit()
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
        
    mariadb_connection.close()

    
    return (0)
    
def UpdateSyncHWDB(szAddress, nVerbose): 

    # Añade Usage a una linea de DEVICE_HW (dispositivo HW que ya existe)
    # Bsicamente mira los numeros y actualiza en HW
    # Puede sustituir a la anterior
    
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    # SELECT numUsages, numInputs, numOutputs from DEVICES_HW where Address = 
    szMysqlReq="SELECT NumButton, NumOutputs from DEVICES WHERE Address = '" + szAddress + "'"
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
        
    szInfoList=[] 
    nTotalButton = 0
    nTotalOutputs = 0
    nTotalUsages = 0 
    
    for (NumButton, NumOutputs) in cursor:
        szInfoList.append({'NumButton':NumButton, 'NumOutputs':NumOutputs})
        nTotalButton += NumButton
        nTotalOutputs += NumOutputs
        nTotalUsages += 1
            
    # devId1
    # UPDATE DEVICES SET AddrType = %s, Address = %s WHERE Address = %s
        
    db_data = {
        'Address': szAddress,
        'numInputs' : nTotalButton,
        'numOutputs' : nTotalOutputs,
        'numUsages' : nTotalUsages,
    } 
    
    cursor = mariadb_connection.cursor()
    szMysqlReq="UPDATE DEVICES_HW SET numUsages = %(numUsages)s, numInputs = %(numInputs)s, numOutputs = %(numOutputs)s WHERE Address = %(Address)s"
    
    try:
        cursor.execute(szMysqlReq, db_data)    
        mariadb_connection.commit()
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
        
    mariadb_connection.close()

    
    return (0)
    
        
def AddUpdateUsageConfig(szDevId, variablesDict, nVerbose): 

    returndata = 0
    
    szDevIdNew = ""
    szDevType = ""
    nUsage = 0
    nNumButton = 0
    nNumOutputs = 0
    nPinInput1 = 0
    nPinInput2 = 0
    nPinInput3 = 0
    nPinInput4 = 0
    nPinOutput1 = 0
    nPinOutput2 = 0
    nPinOutput3 = 0
    nPinOutput4 = 0
    szDescription = ""
    
    bExists = ReadIfUsageExists('devID',szDevId, nVerbose)
            
    if (bExists < 0):
        AddUsageDB(szDevId, variablesDict, nVerbose)
    
    # Primero leo la config actual
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    if (variablesDict.get('devIdNew')):
        szDevIdNew=variablesDict['devIdNew'][0]
    else:
        szDevIdNew=szDevId    
        
    szMysqlReq="UPDATE DEVICES SET pinInput1 = null, pinInput2 = null, pinInput3 = null, pinInput4 = null, pinOutput1 = null, pinOutput2 = null, pinOutput3 = null, pinOutput4 = null WHERE devId = '" + szDevId + "'"
    
    try:
        cursor.execute(szMysqlReq)    
        mariadb_connection.commit()
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
        returndata = -1
    
    szMysqlReq="UPDATE DEVICES SET devId = %(devIdNew)s, ";
    
    if (variablesDict.get('devType')):
        szDevType=variablesDict['devType'][0]
        szMysqlReq += "devType = %(devType)s, "
        
    if (variablesDict.get('nUsage')):
        nUsage=variablesDict['nUsage'][0]
        szMysqlReq += "nUsage = %(nUsage)s, "
        
    if (variablesDict.get('pinInput1')):
        nPinInput1 = int(variablesDict['pinInput1'][0])
        szMysqlReq += "pinInput1 = %(pinInput1)s, "
        nNumButton += 1
        
    if (variablesDict.get('pinInput2')):
        nPinInput2 = int(variablesDict['pinInput2'][0])
        szMysqlReq += "pinInput2 = %(pinInput2)s, "
        nNumButton += 1
        
    if (variablesDict.get('pinInput3')):
        nPinInput3 = int(variablesDict['pinInput3'][0])
        szMysqlReq += "pinInput3 = %(pinInput3)s, "
        nNumButton += 1
        
    if (variablesDict.get('pinInput4')):
        nPinInput4 = int(variablesDict['pinInput4'][0])
        szMysqlReq += "pinInput4 = %(pinInput4)s, "
        nNumButton += 1
        
    if (variablesDict.get('pinOutput1')):
        nPinOutput1 = int(variablesDict['pinOutput1'][0])
        szMysqlReq += "pinOutput1 = %(pinOutput1)s, "
        nNumOutputs += 1
        
    if (variablesDict.get('pinOutput2')):
        nPinOutput2 = int(variablesDict['pinOutput2'][0])
        szMysqlReq += "pinOutput2 = %(pinOutput2)s, "
        nNumOutputs += 1
        
    if (variablesDict.get('pinOutput3')):
        nPinOutput3 = int(variablesDict['pinOutput3'][0]) 
        szMysqlReq += "pinOutput3 = %(pinOutput3)s, "
        nNumOutputs += 1
         
    if (variablesDict.get('pinOutput4')):
        nPinOutput4 = int(variablesDict['pinOutput4'][0])
        szMysqlReq += "pinOutput4 = %(pinOutput4)s, "
        nNumOutputs += 1
    
    '''    
    if (variablesDict.get('numButton')):
        nNumButton=variablesDict['numButton'][0]
        szMysqlReq += "numButton = %(numButton)s, "
        
    if (variablesDict.get('numOutputs')):
        nNumOutputs=variablesDict['numOutputs'][0]
        szMysqlReq += "numOutputs = %(numOutputs)s, "
    '''
    if (nNumOutputs > 0 or nNumButton > 0):
        szMysqlReq += "numButton = %(numButton)s, numOutputs = %(numOutputs)s, "
        
    if (variablesDict.get('Description')):
        szDescription=variablesDict['Description'][0]
        szMysqlReq += "Description = %(Description)s, "
        
    szMysqlReq += "devId = %(devIdNew)s WHERE devID = %(devID)s"
        
    if (nVerbose > 0):
        Logfile.printError ('[HandleDeviceConfig] ' + szMysqlReq + ", szId = " + szDevId)
        
    db_data = {
        'devID': szDevId,
        'devIdNew': szDevIdNew,
        'devType': szDevType,
        'nUsage' : nUsage,
        'numButton' : nNumButton,
        'numOutputs' : nNumOutputs,
        'pinInput1' : nPinInput1,
        'pinInput2' : nPinInput2,
        'pinInput3' : nPinInput3,
        'pinInput4' : nPinInput4,
        'pinOutput1' : nPinOutput1,
        'pinOutput2' : nPinOutput2,
        'pinOutput3' : nPinOutput3,
        'pinOutput4' : nPinOutput4,
        'Description' : szDescription,
    } 

    try:
        cursor.execute(szMysqlReq, db_data)    
        mariadb_connection.commit()
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
        returndata = -1
        
    mariadb_connection.close()
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor(buffered=True)
            
    szMysqlReq = "SELECT Address FROM DEVICES where devId = '" + szDevId + "'"
    
    try:
        cursor.execute(szMysqlReq)    
        mariadb_connection.commit()
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DBBB: {}'.format(error))
        returndata = -1
    
    row = cursor.fetchone()
    
    mariadb_connection.close()
    
    szAddress = row[0]
            
    UpdateSyncHWDB(szAddress, nVerbose)
     
    return (returndata)
    

def UpdateDeviceState(szAddress, szState, nVerbose): 

    returndata=0
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
        
    szMysqlReq="UPDATE DEVICES_HW SET State = '"+szState+"' WHERE Address = '"+szAddress+"'"
    
    try:
        cursor.execute(szMysqlReq)
        mariadb_connection.commit()
        returndata=0 
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
        returndata=-1
        
            
    mariadb_connection.close()
            
    return (returndata)
    
###################################################################################################
###################################################################################################
#
# Funciones to DELETE
#
###################################################################################################
###################################################################################################

def DeleteDeviceHWDB (szAddress, nVerbose):

    returndata=0
            
    bExists = ReadIfDeviceHWExists('Address',szAddress, nVerbose)
            
    if (bExists < 0):
        return (-2)
            
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor(buffered=True)
    
    szMysqlReq="DELETE FROM DEVICES WHERE Address = '" + szAddress +"'"

    if (nVerbose > 0):
        Logfile.printError ('[HandleDeviceConfig] ' + szMysqlReq )

    try:
        cursor.execute(szMysqlReq)
        mariadb_connection.commit()
        returndata=0 
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
        returndata=-1
        return (returndata)
    
    szMysqlReq="DELETE FROM DEVICES_HW WHERE Address = '" + szAddress +"'"


    if (nVerbose > 0):
        Logfile.printError ('[HandleDeviceConfig] ' + szMysqlReq )

    try:
        cursor.execute(szMysqlReq)
        mariadb_connection.commit()
        returndata=0 
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
        returndata=-1
        return (returndata)        
    
    return (returndata)
    

def DeleteUsageDB (szDevId, nVerbose):

    returndata=0
    bADDUSAGE = 1
    bDELETEUSAGE = 0 
            
    bExists = ReadIfUsageExists('devID',szDevId, nVerbose)
            
    if (bExists < 0):
        return (-2)
    
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor(buffered=True)
    
    szMysqlReq="SELECT devId, Address, NumButton, NumOutputs from DEVICES where devId = '" + szDevId +"'"
    
    if (nVerbose > 0):
        Logfile.printError ('[HandleDeviceConfig] ' + szMysqlReq )

    try:
        cursor.execute(szMysqlReq)
        mariadb_connection.commit()
        returndata=0 
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
        returndata=-1
        return (returndata)
        
    row = cursor.fetchone()
    
    if (cursor.rowcount < 0):
        return(-1)
    
    szAddress = row[1]
    nNumButton = row[2]
    nNumOutputs = row[3]
        
    szMysqlReq="DELETE FROM DEVICES WHERE devId = '" + szDevId +"'"

    if (nVerbose > 0):
        Logfile.printError ('[HandleDeviceConfig] ' + szMysqlReq )

    try:
        cursor.execute(szMysqlReq)
        mariadb_connection.commit()
        returndata=0 
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
        returndata=-1
        return (returndata)
        
            
    mariadb_connection.close()
    
    result = UpdateUsageToHWDB(szAddress, bDELETEUSAGE, nNumButton, nNumOutputs , nVerbose) 
    
    if (result < 0):
        return (result)
            
    return (returndata)
    
###################################################################################################
###################################################################################################
#
# Funciones to CHECK
#
###################################################################################################
###################################################################################################

def ObtainFreeModBusAddress():
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    szMysqlReq="SELECT HW_Index FROM DEVICES_HW WHERE mbAddress = 1"
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
    
    row = cursor.fetchone()
    
    # -1 no existe
    # 0 existe
    
    if (cursor.rowcount < 0):
        return (1)
        
    szMysqlReq="SELECT (t.mbAddress + 1) mbAddress FROM DEVICES_HW as t LEFT JOIN DEVICES_HW s ON s.mbAddress = (t.mbAddress + 1) WHERE s.mbAddress IS NULL AND t.mbAddress IS NOT NULL ORDER BY t.mbAddress LIMIT 1"
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
    
    row = cursor.fetchone()
    
    mbAddress = row[0]
    
    mariadb_connection.close()
    
    return (mbAddress)
    
def CheckIfModBUS (szHWtype):

    # SELECT modbus FROM HW_TYPES where HWtype = 'Domo4ch';
    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    szMysqlReq="SELECT modbus FROM HW_TYPES where HWtype = '"+szHWtype+"'"
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))
    
    row = cursor.fetchone()
    
    if (cursor.rowcount < 0):
        mbEnabled = 0
    else:
        mbEnabled = row[0]
    
    mariadb_connection.close()
    
    return (mbEnabled)
    
    
def ReadIfDeviceHWExists(szField, szValue, nVerbose): 

    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    szMysqlReq="SELECT State from DEVICES_HW where "+szField+" = '"+szValue+"'"
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))

    mariadb_connection.close()
    
    row = cursor.fetchone()
    
    # -1 no existe
    # 0 existe
            
    return (cursor.rowcount)

def GetAdressesFromDevId (szDevId, nVerbose): 

    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    szMysqlReq="SELECT hw.Address, hw.mbAddress, us.nUsage FROM DEVICES_HW AS hw INNER JOIN DEVICES as us ON hw.Address = us.Address where devId='"+szDevId+"'"
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))

    mariadb_connection.close()
    
    szDeviceList=[]
    
    for (Address, mbAddress, nUsage) in cursor:
        szDeviceList.append({'Address':Address,'mbAddress':mbAddress,'nUsage':nUsage})

    return (szDeviceList)
    
def ReadIfUsageExists(szField, szValue, nVerbose): 

    mariadb_connection = mariadb.connect(user='root', password='licaoasi', database='domotica17')
    cursor = mariadb_connection.cursor()
    
    szMysqlReq="SELECT devId from DEVICES where "+szField+" = '"+szValue+"'"
    
    try:
        cursor.execute(szMysqlReq)    
    except mariadb.Error as error:
        Logfile.printError ('[HandleDeviceConfig] Error DB: {}'.format(error))

    mariadb_connection.close()
    
    row = cursor.fetchone()
    
    # -1 no existe
    # 0 existe
            
    return (cursor.rowcount)
    
                
def main():

    #a=GetTypesList("", 1)
    #print (a)
    #UpdateUsageToHWDB('192.168.2.150', 'SASD', 2, 2 , 1)
    
    variablesDict = {
        'devType': ['tLuz'],
        'Address': ['192.168.2.150'],
        #'AddressNew': ['192.168.2.136'],
        'nUsage' : [1],
        'numButton' : [1],
        'numOutputs' : [1],
        'pinInput1' : [1],
        'pinOutput1' : [2],
        'Description' : ['Prueba222'],
    }
    
    #AddUpdateUsageConfig('SODU2', variablesDict, 1)
    #AddUsageDB('SODU2', variablesDict, 1)
    #DeleteUsageDB ('SODU2', 1)
    #UpdateDeviceHWDB('192.168.2.135', variablesDict, 1)
    #address = ObtainFreeModBusAddress()
    #print (address)
    
    #address = CheckIfModBUS ('Domo4ch')
    
    #addr = GetAdressesFromDevId ('SOAN1', 1)
    #addr = GetHWUsagesListTreeAll ( 1)
    data = GetUsageData ('SO4CAL1',1)
    print (data)
    #print (addr[0]['Address'])
       
if __name__ == "__main__":
    main()
