import gpio_api
import requests
import Logfile
import json
import HandleDeviceConfig

def control_wemos2(RoomDataList, nVerbose):

    # Lo deberia llevar a control_devices.UpdateUsageState y a tomar por culo.

    DevTermsList2 = []  # Aqui se agrupan por IP:
    # [{'Address': '192.168.2.131', 'Valvs' : [{'devId': 'TempPrincipal', 'roomNumber': 4}, {'devId': 'TempSofia', 'roomNumber': 5}]}]
    for (RoomDict) in RoomDataList:
        ValvulasRoom = RoomDict['Valvs']
        for (ValvDict) in ValvulasRoom:
            szAddress = ValvDict['Address']
            szDevId = ValvDict['devId']
            szValue = RoomDict['Caldera']
            
            # Consolidamos para hacer solo 1 request por IP
            
            foundit=0
            for (tmp) in DevTermsList2:
                if tmp.get('Address') == szAddress:
                    tmp['Valvs'].append({'devId':szDevId,'State':szValue})
                    foundit = 1
            if foundit == 0:
                tmp = [{'devId':szDevId,'State':szValue}]
                DevTermsList2.append({'Address':szAddress,'Valvs' : tmp})
            
    for (devHW) in DevTermsList2:
        url = "http://"+devHW['Address']+"/Update?"
        ndevNum = 0
        for (devTerm) in devHW['Valvs']:
            url = url + "&devId" + str(ndevNum) + "=" + devTerm['devId']
            url = url + "&State" + str(ndevNum) + "=" + devTerm['State']
            ndevNum = ndevNum + 1
        if nVerbose > 0:
            Logfile.printError ('[GPIO_Caldera] Accediendo a ' + url)
            
        s=requests.session()
        try:
            response = s.get(url,stream=False)
        except requests.exceptions.RequestException as e:
            Logfile.printError ('[GPIO_Caldera] Error accediendo a ' + url)
            return()
        s.close()
            
def control_valvulaCentral2(RoomDataList, nVerbose):
    nValvulas=0
    for (RoomDict) in RoomDataList:
        if RoomDict['Caldera']=='on':
            nValvulas+=1
    
    # Pin caldera general:29
    if nVerbose > 0:
        Logfile.printError ('[GPIO_Caldera] Valvula General: ' + str(nValvulas))
        
    if nValvulas > 0:
        gpio_api.gpio_control(29, 1, 0, nVerbose)  # cambiar a 1
    else:
        gpio_api.gpio_control(29, 0, 0, nVerbose)
                    
def control_wemos(szCalderaOnOff, nVerbose):
    
    szDevIdWemosBaja = 'SO4CAL1'
    szDevIdWemosHabitaciones = 'SO4CAL2'
    
    dataDevId = HandleDeviceConfig.GetUsageData (szDevIdWemosBaja,nVerbose)
    WemosIP =  dataDevId[0]['Address']
    szRootUrlWemosBaja = 'http://' + WemosIP + '/'
        
    dataDevId = HandleDeviceConfig.GetUsageData (szDevIdWemosHabitaciones,nVerbose)
    WemosIP =  dataDevId[0]['Address']
    szRootUrlWemosHabitaciones = 'http://' + WemosIP + '/'
    
    szUriParamsBaja = "Update?"
    szUriParamsHabitaciones = "Update?"
    
    if szCalderaOnOff[0]=='on':   # De momento solo cuento el salon para encender la caldera
        szUriParamsBaja += "Salon=ON"
    else:
        szUriParamsBaja += "Salon=OFF"
        
    if szCalderaOnOff[1]=='on':
        szUriParamsBaja += "&Despacho=ON"
    else:
        szUriParamsBaja += "&Despacho=OFF"
    
    if szCalderaOnOff[2]=='on':
        szUriParamsBaja += "&Cocina=ON"
    else:
        szUriParamsBaja += "&Cocina=OFF"
        
    if szCalderaOnOff[3]=='on':
        szUriParamsHabitaciones += "&Principal=ON"
    else:
        szUriParamsHabitaciones += "&Principal=OFF"
        
    if szCalderaOnOff[4]=='on':
        szUriParamsHabitaciones += "&Sofia=ON"
    else:
        szUriParamsHabitaciones += "&Sofia=OFF"
        
    if szCalderaOnOff[5]=='on':
        szUriParamsHabitaciones += "&Alvaro=ON"
    else:
        szUriParamsHabitaciones += "&Alvaro=OFF"
        
    url = szRootUrlWemosBaja+szUriParamsBaja
    
    if nVerbose > 0:
        Logfile.printError ('[GPIO_Caldera] Accediendo a ' + url)
    
    s=requests.session()
    try:
        response = s.get(url,stream=False)
    except requests.exceptions.RequestException as e:
        Logfile.printError ('[GPIO_Caldera] Error accediendo a ' + url)
        return()
    s.close()
    
    url = szRootUrlWemosHabitaciones+szUriParamsHabitaciones
    
    if nVerbose > 0:
        Logfile.printError ('[GPIO_Caldera] Accediendo a ' + url)
    
    s=requests.session()
    try:
        response = s.get(url,stream=False)
    except requests.exceptions.RequestException as e:
        Logfile.printError ('[GPIO_Caldera] Error accediendo a ' + url)
        return()
    s.close()
    
def control_valvulaCentral(szCalderaOnOff, nVerbose):
    nValvulas=0
    if szCalderaOnOff[0]=='on':   # De momento solo cuento el salon para encender la caldera
        nValvulas+=1
    if szCalderaOnOff[1]=='on':
        nValvulas+=1
    if szCalderaOnOff[2]=='on':
        nValvulas+=1
    if szCalderaOnOff[3]=='on':
        nValvulas+=1
    if szCalderaOnOff[4]=='on':
        nValvulas+=1
    if szCalderaOnOff[5]=='on':
        nValvulas+=1
    
    # Pin caldera general:29
    if nVerbose > 0:
        Logfile.printError ('[GPIO_Caldera] Valvula General: ' + str(nValvulas))
        
    if nValvulas > 0:
        gpio_api.gpio_control(29, 1, 0, nVerbose)
    else:
        gpio_api.gpio_control(29, 0, 0, nVerbose)
        
def caldera(szCalderaOnOff, nVerbose):
    control_valvulaCentral(szCalderaOnOff, nVerbose)
    control_wemos(szCalderaOnOff, nVerbose)
    
def caldera2(RoomDataList, nVerbose):
    control_wemos2(RoomDataList, nVerbose)
    control_valvulaCentral2(RoomDataList, nVerbose)


if __name__ == "__main__":
    szCalderaOnOff = ['off' for i in range(6)]
    szCalderaOnOff[0]='off' # Salon
    szCalderaOnOff[1]='off' # Despacho
    szCalderaOnOff[2]='off' # Cocina
    szCalderaOnOff[3]='off' # Principal
    szCalderaOnOff[4]='off' # Sofia
    szCalderaOnOff[5]='off' # Alvaro
    
    control_valvulaCentral(szCalderaOnOff, 1)
    control_wemos(szCalderaOnOff, 1)
    
    