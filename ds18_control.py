import json
import requests
import datetime
import HandleDeviceConfig
import control_devices

import Logfile
import time

from websocket import create_connection

def GetTempWemos(szZonaId, ZonaTempDef, nVerbose):
    
    dataDevId = HandleDeviceConfig.GetUsageData (szZonaId,nVerbose)
    WemosIP =  dataDevId[0]['Address']
    szRootUrlWemos = 'http://' + WemosIP + '/'
        
        
    url = szRootUrlWemos + "ReadTempPrepare"
    
    if nVerbose > 0:
        szLogMsg = '[DS18] Wemos Preparando: ' + url + '....'
        Logfile.printError (szLogMsg)
        
        
    s=requests.session()
    try:
        response = s.get(url, stream=False, timeout=15)
    except requests.exceptions.RequestException as e:
        szLogMsg = '[DS18] Error leyendo ' + szZonaId
        Logfile.printError (szLogMsg)
        return()
        
    time.sleep(1)
    
    url = szRootUrlWemos + "ReadTempGet"
    
    if nVerbose > 0:
        szLogMsg = '[DS18] Wemos Get: ' + url + '....'
        Logfile.printError (szLogMsg)
    
    s=requests.session()
    try:
        response = s.get(url, stream=False, timeout=15)
    except requests.exceptions.RequestException as e:
        szLogMsg = '[DS18] Error leyendo ' + szZonaId
        Logfile.printError (szLogMsg)
        return()
        
    data = response.json()
    
    for datum in data:
        if datum['room'] == 'Salon':
            ZonaTempDef[0] = str(datum ['temp'])
        if datum['room'] == 'Despacho':
            ZonaTempDef[1] = str(datum ['temp'])
        if datum['room'] == 'Cocina':
            ZonaTempDef[2] = str(datum ['temp'])
        if datum['room'] == 'Principal':
            ZonaTempDef[3] = str(datum ['temp'])
        if datum['room'] == 'Sofia':
            ZonaTempDef[4] = str(datum ['temp'])
        if datum['room'] == 'Alvaro':
            ZonaTempDef[5] = str(datum ['temp'])
                

def GetTemp2(RoomDataList, nVerbose):
    #####################################
    # General Params
    #####################################
    
    status = 0
    DevTermsList2 = []  # Aqui se agrupan por IP:
    # [{'Address': '192.168.2.131', 'Terms' : [{'devId': 'TempPrincipal', 'roomNumber': 4}, {'devId': 'TempSofia', 'roomNumber': 5}]}]
    for (RoomDict) in RoomDataList:
        TermostatosRoom = RoomDict['Terms']
        nTempMedia = 0
        nNumTerms = 0
        
        for (TermDict) in TermostatosRoom:
            szAddress = TermDict['Address']
            szDevId = TermDict['devId']
            
            Logfile.printError ('[DS18] Leyendo Termostato ' + szDevId + ' - ' + szAddress)
            
            
            
            response = control_devices.ReadUsageState('WIFI', szDevId, nVerbose, szAddress, 'on')
            
            #response = [{"devId": "TempSalon", "Status": 200, "State":27}]
            
            Logfile.printError ('[DS18] Respuesta: ' + str(response))
            
            if response[0]['Status'] != 200:
                return (-1)
            
            TermDict['Value'] = response[0]['State']
            
            try:
                tempTest = float (response[0]['State'])   # Esto es solo para comprobar que s un numero
                if tempTest > 10 and tempTest < 60:
                    nTempMedia += tempTest
                    nNumTerms += 1
            except:
                Logfile.printError ('[DB18] Error leyendo DB18: ' + str(response))
                                            
        if nNumTerms > 0:
            nTempMedia = nTempMedia / nNumTerms
        else:
            nTempMedia = -127
            status = -1
            
        RoomDict['Temp2'] = str(int(nTempMedia*100)/100)
                         
    return (status) 
            
    """
            # Lo de consolidar de momento lo dejamos
            
            # Consolidamos para hacer solo 1 request por IP
            
            foundit=0
            for (tmp) in DevTermsList2:
                if tmp.get('Address') == szAddress:
                    tmp['Terms'].append({'devId':szDevId,'roomNumber':RoomDict['roomNumber']})
                    foundit = 1
            if foundit == 0:
                tmp = [{'devId':szDevId,'roomNumber':RoomDict['roomNumber']}]
                DevTermsList2.append({'Address':szAddress,'Terms' : tmp})
            
    for (devHW) in DevTermsList2:
        url = "http://"+devHW['Address']+"/ReadTemp?"
        ndevNum = 0
        for (devTerm) in devHW['Terms']:
            url = url + "&devId" + str(ndevNum) + "=" + devTerm['devId']
            ndevNum = ndevNum + 1
                    
        Logfile.printError ('[DS18] ' + url)
        
        
        response = [{'devId':'TempPrincipal','Temp':23.1},{'devId':'TempSofia','Temp':23.2},{'devId':'TempAlvaro','Temp':23.3}]
                

        # Actualizamos RoomDataList
    
        for (devTermsResp) in response:
            szdevIdResp = devTermsResp['devId']
            for (RoomDict) in RoomDataList:
                TermostatosRoom = RoomDict['Terms']
                for (TermDict) in TermostatosRoom:
                    szDevId = TermDict['devId']
                    if szDevId == szdevIdResp:
                        TermDict['Value'] = devTermsResp['Temp']
                        
    """

        
    
            

def GetTemp(ZonaTempDef, nVerbose):
    #####################################
    # General Params
    #####################################
    
    szDevIdWemosBaja = 'SO4CAL1'
    szDevIdWemosHabitaciones = 'SO4CAL2'
    
    GetTempWemos(szDevIdWemosBaja, ZonaTempDef, nVerbose)
    GetTempWemos(szDevIdWemosHabitaciones, ZonaTempDef, nVerbose)
    
    if nVerbose > 0:
        szLogMsg = '[DS18] Salon: ' + ZonaTempDef[0]
        Logfile.printError (szLogMsg)
        szLogMsg = '[DS18] Despacho: ' + ZonaTempDef[1]
        Logfile.printError (szLogMsg)
        szLogMsg = '[DS18] Cocina: ' + ZonaTempDef[2]
        Logfile.printError (szLogMsg)
        szLogMsg = '[DS18] Principal: ' + ZonaTempDef[3]
        Logfile.printError (szLogMsg)
        szLogMsg = '[DS18] Sofia: ' + ZonaTempDef[4]
        Logfile.printError (szLogMsg)
        szLogMsg = '[DS18] Alvaro: ' + ZonaTempDef[5]
        Logfile.printError (szLogMsg)
    
    
if __name__ == "__main__":
    ZonaTempDef = ['Null' for i in range(6)]

    GetTemp(ZonaTempDef, 1)
    print (ZonaTempDef)
    