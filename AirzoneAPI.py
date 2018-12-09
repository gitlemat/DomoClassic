import json
import ssl
import websocket
import random
import requests
import datetime
import Logfile
import sys

from websocket import create_connection

def CreateTokenFile():
    szFileName='AirzoneToken'

    fd = open(szFileName, 'w') # el mismo fichero
    fd.write ('\n')
        
    fd.close()
    
def readTokenFile(nVerbose, webPython): 

    # Cada 5 min hace ping a los wemos
    # Si no responden pone rojo
    
    # Leemos fichero de estados actuales
    # Lo que haya en DEVICES_LIST

    szFileName='AirzoneToken'
    
    try:
        with open(szFileName, 'r') as fd:
            linesToken = fd.readlines()
    except IOError:
        Logfile.printErrorAPI ('[AirzoneAPI] Error leyendo fichero. Recreamos.', webPython)
        CreateTokenFile()
        result_php = {'status': -1}
        # Send it to stdout (to PHP)
        return(result_php)

    fd.close()

    lineSplit=linesToken[0].split(',')
    
    if (len (lineSplit)<2):
        result_php = {'status': -1}
        # Send it to stdout (to PHP)
        return(result_php)
    
    szToken = lineSplit[0]
    szDevice = lineSplit[1]
    
    result_php = {'status': 0, 'token': szToken, 'DeviceID': szDevice}

    # Send it to stdout (to PHP)
    # print (json.dumps(result_php))
    
    return  (result_php)



    
def sortTempsAirzone(ZonaName, ZonaTemp, ZonaTempDef):
    #########################
    # Consideramos que no tienen que estar en orden (casi siempre lo estan)
    # Orden definitivo:
    # SALON DESPACHO COCINA PRINCIPAL SOFIA ALVARO
    nInit = 0
    while nInit < 6:
        if ZonaName[nInit].find ('SALON') >= 0:
            ZonaTempDef[0]=ZonaTemp[nInit].strip()
        if ZonaName[nInit].find ('DESPACHO') >= 0:
            ZonaTempDef[1]=ZonaTemp[nInit].strip()
        if ZonaName[nInit].find ('COCINA') >= 0:
            ZonaTempDef[2]=ZonaTemp[nInit].strip()
        if ZonaName[nInit].find ('PRINCIPAL') >= 0:
            ZonaTempDef[3]=ZonaTemp[nInit].strip()
        if ZonaName[nInit].find ('SOFIA') >= 0:
            ZonaTempDef[4]=ZonaTemp[nInit].strip()
        if ZonaName[nInit].find ('ALVARO') >= 0:
            ZonaTempDef[5]=ZonaTemp[nInit].strip()
        nInit+=1
        
        
        
        
        
        
def GetInitData(nVerbose, webPython):
    #####################################
    # General Params
    #####################################
    
    szRootUrl = 'https://www.airzonecloud.com'
    szRootWSUrl = 'wss://www.airzonecloud.com'
    szUserEmail='sibanezc@gmail.com'
    szUserPsw='licaoasi'
    
    ZonaName = ['Null' for i in range(7)]
    ZonaTemp = ['Null' for i in range(7)]
    
#    context = ssl._create_unverified_context()
    
    #####################################
    # Homepage sock1
    #####################################
    
    if nVerbose > 0:
        Logfile.printErrorAPI ('[AirzoneAPI] Load homepage......', webPython)
        
    s=requests.session()
    
    headers = {'Cookie': 'SERVERID=Server_2'}
    url = szRootUrl
    try:
        response = s.get(url, headers=headers, stream=False, timeout=5)
    except requests.exceptions.RequestException as e:
        Logfile.printErrorAPI ('[AirzoneAPI] Error leyendo Homepage', webPython)
        result_php = {'status': -1}
        # Send it to stdout (to PHP)
        return(result_php)
 
    #####################################
    # Sign in sock1
    #####################################
    
    if nVerbose > 0:
        Logfile.printErrorAPI ('[AirzoneAPI] Signing in......', webPython)
    
    data = {'email': szUserEmail, 'password' : szUserPsw}
    #headers = {'Content-Type': 'application/json', 'Cookie': 'SERVERID=Server_2'}
    headers = {'Content-Type': 'application/json;charset=UTF-8', 'Origin': 'https://www.airzonecloud.com', 'Accept': 'application/json, text/plain, */*', 'Accept-Encoding':'gzip, deflate, br', 'Accept-Language':'en-US,en;q=0.8,es;q=0.6', 'Referer':'https://www.airzonecloud.com/', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 'X-Requested-With':'XMLHttpRequest'}

    url = szRootUrl+'/users/sign_in'
    try:
        response = s.post(url, headers=headers, json=data, stream=False, timeout=10)
    except requests.exceptions.RequestException as e:
        Logfile.printErrorAPI ('[AirzoneAPI] Error Signing in..', webPython)
        result_php = {'status': -1}
        return(result_php)
        
    if (response.status_code > 299):
        Logfile.printErrorAPI ('[AirzoneAPI] Error leyendo User Data', webPython)
        result_php = {'status': -1}
        return(result_php)
        
 
    data = response.json()
        
    szToken = data['user']['authentication_token']
    szId = data['user']['id']
    
    #####################################
    # Request User data sock1
    #####################################
    
    if nVerbose > 0:
        Logfile.printErrorAPI ('[AirzoneAPI] Request User Data......', webPython)
    
    szUriParams = 'format=json&user_email='+szUserEmail+'&user_token='+szToken
    #headers = {'Cookie': 'SERVERID=Server_2'}
    headers = {'Content-Type': 'application/json;charset=UTF-8', 'Origin': 'https://www.airzonecloud.com', 'Accept': 'application/json, text/plain, */*', 'Accept-Encoding':'gzip, deflate, br', 'Accept-Language':'en-US,en;q=0.8,es;q=0.6', 'Referer':'https://www.airzonecloud.com/', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 'X-Requested-With':'XMLHttpRequest'}

    url = szRootUrl+'/device_relations/?'+szUriParams
    try: 
        response = s.get(url, headers=headers, stream=False, timeout=10)
    except requests.exceptions.RequestException as e:
        Logfile.printErrorAPI ('[AirzoneAPI] Error leyendo User Data', webPython)
        result_php = {'status': -1}
        return(result_php)

    if (response.status_code > 299):
        Logfile.printErrorAPI ('[AirzoneAPI] Error leyendo User Data', webPython)
        result_php = {'status': -1}
        return(result_php)
 
    if nVerbose > 1:
        Logfile.printErrorAPI ('[AirzoneAPI] ' + url, webPython)
        Logfile.printErrorAPI ('[AirzoneAPI] ' + str(response.status_code), webPython)

    s.close()

    data = response.json()
    
    szDeviceId = data['device_relations'][0]['device']['id']
    
    szFileName='AirzoneToken'

    fd = open(szFileName, 'w') # el mismo fichero
    fd.write (szToken+','+szDeviceId)
        
    fd.close()
        
    result_php = {'status': 0, 'token': szToken, 'DeviceID': szDeviceId}

    # Send it to stdout (to PHP)
    # print (json.dumps(result_php))
    
    return  (result_php)







def GetSystemsData(szToken, szDeviceId, nVerbose, webPython):
    #####################################
    # General Params
    #####################################
    
    szRootUrl = 'https://www.airzonecloud.com'
    szUserEmail='sibanezc@gmail.com'
    
    #    context = ssl._create_unverified_context()
    
    # {"systems":[{"id":"5a7c803d84e2e21302002089",
     #             "device_id":"5810d30470696e3570050000",
     #             "name":"PLANTA BAJA",
     #             "eco":"0",
     #             "eco_color":"5",
     #             "velocity":null,
     #             "has_velocity":false,
     #             "has_air_flow":false,
     #             "mode":"1",
     #             "modes":"111111100",
     #             "setup_type":null,
     #             "max_limit":null,
     #             "min_limit":null,
     #             "power":false,"zones_ids":["5a7c803d84e2e2130200208a","5a7c803d84e2e2130200208b","5a7c803d84e2e2130200208c"],
     #             "class":"System",
     #             "updated_at":1532099136,
     #             "system_number":"1",
     #             "last_update":1532099130,
     #             "firm_ws":"",
     #             "scene":null,
     #             "auto":false,
     #             "temperature_unit":false,
     #             "autochange_differential":null,
     #             "config_ZBS_visible_environment":null,
     #             "system_fw":null},
     #            {"id":"5a7c803d84e2e2130200208d","device_id":"5810d30470696e3570050000","name":"PLANTA 1","eco":"0","eco_color":"5","velocity":null,"has_velocity":false,"has_air_flow":false,"mode":"1","modes":"110110100","setup_type":null,"max_limit":null,"min_limit":null,"power":false,"zones_ids":["5a7c803d84e2e21302002092","5a7c803d84e2e21302002093","5a7c803d84e2e21302002094"],"class":"System","updated_at":1532099143,"system_number":"2","last_update":1532099130,"firm_ws":"","scene":null,"auto":false,"temperature_unit":false,"autochange_differential":null,"config_ZBS_visible_environment":null,"system_fw":null}]}
 
    
    #####################################
    # Request User data sock1
    #####################################
    
    #Request URL:https://www.airzonecloud.com/systems/?device_id=5810d30470696e3570050000
    #                                             &format=json
    #                                             &user_email=sibanezc@gmail.com
    #                                             &user_token=9fEz7ldoZhAzTFBcxs6TKKYzDAixT5-SKZheqQ4GuJs
    
    if nVerbose > 0:
        Logfile.printErrorAPI ('[AirzoneAPI] Request System and Zone Data......', webPython)
    
    szUriParams = 'device_id='+szDeviceId+'&format=json&user_email='+szUserEmail+'&user_token='+szToken
    headers = {'Content-Type': 'application/json;charset=UTF-8', 'Origin': 'https://www.airzonecloud.com', 'Accept': 'application/json, text/plain, */*', 'Accept-Encoding':'gzip, deflate, br', 'Accept-Language':'en-US,en;q=0.8,es;q=0.6', 'Referer':'https://www.airzonecloud.com/', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 'X-Requested-With':'XMLHttpRequest'}
    url = szRootUrl+'/systems/?'+szUriParams
    
    s=requests.session()
    try: 
        response = s.get(url, headers=headers, stream=False, timeout=10)
    except requests.exceptions.RequestException as e:
        Logfile.printErrorAPI ('[AirzoneAPI] Error leyendo System Data', webPython)
        result_php = {'status': -1}
        # Send it to stdout (to PHP)
        return(result_php)

    data = response.json()
     
    if nVerbose > 1:
        Logfile.printErrorAPI ('[AirzoneAPI] ' + url, webPython)
        Logfile.printErrorAPI ('[AirzoneAPI] ' + str(response.status_code), webPython)
        
    if (response.status_code > 299):
        Logfile.printErrorAPI ('[AirzoneAPI] Error leyendo System Data', webPython)
        result_php = {'status': -1}
        return(result_php)
        

    
    Index0 = 0
    Index1 = 1
        
    szSystemNum1 = data['systems'][0]['system_number']
    szSystemNum2 = data['systems'][1]['system_number']
    
    if int(szSystemNum1) == 1:
        Index0 = 0
        Index1 = 1
    else:
        Index0 = 1
        Index1 = 0
        
    szSystemNum1 = data['systems'][Index0]['system_number']
    szSystemNum2 = data['systems'][Index1]['system_number']
    
    szSystemMode1 = data['systems'][Index0]['mode']
    szSystemMode2 = data['systems'][Index1]['mode']
    
    szSystemPower1 = data['systems'][Index0]['power']
    szSystemPower2 = data['systems'][Index1]['power']
    
    szSystemId1 = data['systems'][Index0]['id']
    szSystemId2 = data['systems'][Index1]['id']
    
    resultZone1 = GetZoneData(s, szToken, szDeviceId, szSystemId1, nVerbose, webPython)
    resultZone2 = GetZoneData(s, szToken, szDeviceId, szSystemId2, nVerbose, webPython)
    
    s.close()
        
    result_php = {"status" : 0, "Systems": [{"System_Id" : szSystemId1, "System_Number" : szSystemNum1, "Mode" : szSystemMode1, "Power" : szSystemPower1, "Zones" : resultZone1['zones']}, {"System_Id" : szSystemId2, "System_Number" : szSystemNum2, "Mode" : szSystemMode2, "Power" : szSystemPower2, "Zones" : resultZone2['zones']}]}

    # Send it to stdout (to PHP)
    # print (json.dumps(result_php))
            
    return (result_php)
        
    # {"status": 0, "Systems": [{"Mode": "1", "System_Number": "1", "Zones": [{"Sleep": "0", "Consign": "27.5", "State": "0", "Temp": "27.9", "Zone_Number": "3"}, {"Sleep": "0", "Consign": "27.5", "State": "0", "Temp": "28.4", "Zone_Number": "2"}, {"Sleep": "0", "Consign": "27.5", "State": "0", "Temp": "29.5", "Zone_Number": "1"}], "System_Id": "5a7c803d84e2e21302002089", "Power": false}, {"Mode": "1", "System_Number": "2", "Zones": [{"Sleep": "0", "Consign": "28.0", "State": "0", "Temp": "30.1", "Zone_Number": "3"}, {"Sleep": "0", "Consign": "27.5", "State": "0", "Temp": "30.0", "Zone_Number": "1"}, {"Sleep": "0", "Consign": "28.5", "State": "0", "Temp": "30.3", "Zone_Number": "2"}], "System_Id": "5a7c803d84e2e2130200208d", "Power": false}]}
    
    
def GetZoneData(s, szToken, szDeviceId, szSystemId, nVerbose, webPython):
    #####################################
    # General Params
    #####################################
    
    szRootUrl = 'https://www.airzonecloud.com'
    szUserEmail='sibanezc@gmail.com'
    
    #    context = ssl._create_unverified_context()
    
 
    
    #####################################
    # Request User data sock1
    #####################################
    
    #Request URL:https://www.airzonecloud.com/zones/?format=json
    #                                               &system_id=581e0d3869dba749830003b5
    #                                               &user_email=sibanezc@gmail.com
    #                                               &user_token=22zofe9gYzpA2MiygzfjuB9jBzrNg0fVFG7WAZVCRik
    
    if nVerbose > 0:
        Logfile.printErrorAPI ('[AirzoneAPI] Request System and Zone Data......', webPython)
    
    szUriParams = 'format=json&system_id='+szSystemId+'&user_email='+szUserEmail+'&user_token='+szToken
    headers = {'Content-Type': 'application/json;charset=UTF-8', 'Origin': 'https://www.airzonecloud.com', 'Accept': 'application/json, text/plain, */*', 'Accept-Encoding':'gzip, deflate, br', 'Accept-Language':'en-US,en;q=0.8,es;q=0.6', 'Referer':'https://www.airzonecloud.com/', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 'X-Requested-With':'XMLHttpRequest'}
    url = szRootUrl+'/zones/?'+szUriParams
    try: 
        response = s.get(url, headers=headers, stream=False, timeout=10)
    except requests.exceptions.RequestException as e:
        Logfile.printErrorAPI ('[AirzoneAPI] Error leyendo Zone Data', webPython)
        result_php = {'status': -1}
        # Send it to stdout (to PHP)
        return(result_php)
 
    if nVerbose > 1:
        Logfile.printErrorAPI ('[AirzoneAPI] ' + url, webPython)
        Logfile.printErrorAPI ('[AirzoneAPI] ' + str(response.status_code), webPython)
        
    if (response.status_code > 299):
        Logfile.printErrorAPI ('[AirzoneAPI] Error leyendo Zone Data', webPython)
        result_php = {'status': -1}
        return(result_php)
        
    data = response.json()
    
    Index0 = 0
    Index1 = 1
    Index2 = 2
        
    szZoneNum0 = data['zones'][0]['zone_number']
    szZoneNum1 = data['zones'][1]['zone_number']
    szZoneNum2 = data['zones'][2]['zone_number']
    
    if int(szZoneNum0) == 1:
        Index0 = 0
        if int(szZoneNum1) == 2:
            Index1 = 1 
            Index2 = 2
        else:
            Index1 = 2
            Index2 = 1
    
    if int(szZoneNum1) == 1:
        Index0 = 1
        if int(szZoneNum0) == 2:
            Index1 = 0 
            Index2 = 2
        else:
            Index1 = 2
            Index2 = 0
            
    if int(szZoneNum2) == 1:
        Index0 = 2
        if int(szZoneNum0) == 2:
            Index1 = 0 
            Index2 = 1
        else:
            Index1 = 1
            Index2 = 0
    
    szZoneNum1 = data['zones'][Index0]['zone_number']
    szZoneNum2 = data['zones'][Index1]['zone_number']
    szZoneNum3 = data['zones'][Index2]['zone_number']
    
    szZoneState1 = data['zones'][Index0]['state']
    szZoneState2 = data['zones'][Index1]['state']
    szZoneState3 = data['zones'][Index2]['state']

    
    szZoneConsign1 = data['zones'][Index0]['consign']
    szZoneConsign2 = data['zones'][Index1]['consign']
    szZoneConsign3 = data['zones'][Index2]['consign']
    
    szZoneTemp1 = data['zones'][Index0]['temp']
    szZoneTemp2 = data['zones'][Index1]['temp']
    szZoneTemp3 = data['zones'][Index2]['temp']
    
    szZoneSleep1 = data['zones'][Index0]['sleep']
    szZoneSleep2 = data['zones'][Index1]['sleep']
    szZoneSleep3 = data['zones'][Index2]['sleep']
    
    result_php = {"status" : 0, "zones" : [{"Zone_Number" : szZoneNum1, "State" : szZoneState1, "Consign" : szZoneConsign1, "Temp" : szZoneTemp1, "Sleep" : szZoneSleep1}, {"Zone_Number" : szZoneNum2, "State" : szZoneState2, "Consign" : szZoneConsign2, "Temp" : szZoneTemp2, "Sleep" : szZoneSleep2}, {"Zone_Number" : szZoneNum3, "State" : szZoneState3, "Consign" : szZoneConsign3, "Temp" : szZoneTemp3, "Sleep" : szZoneSleep3}]}

    # Send it to stdout (to PHP)
    # print (json.dumps(result_php))
    
    return (result_php)


def SetSystemMode(szToken, szDeviceId, nSystemNum, szOption, nValue, nVerbose, webPython):
    #####################################
    # General Params
    #####################################
    
    szRootUrl = 'https://www.airzonecloud.com'
    szUserEmail='sibanezc@gmail.com'
    
    #szRootUrl = 'http://www.google.com'
    #szUserEmail='sssss@gmail.com'
    #    context = ssl._create_unverified_context()
    
 
    
    #####################################
    # Request User data sock1
    #####################################
    
    #Request URL:https://www.airzonecloud.com/events/?user_email=sibanezc@gmail.com
    #                                                &user_token=9fEz7ldoZhAzTFBcxs6TKKYzDAixT5-SKZheqQ4GuJs
    
    # {"event":{"cgi":"modsistema","system_number":"1","option":"mode","value":1,"device_id":"5810d30470696e3570050000"}}

    if nVerbose > 0:
        Logfile.printErrorAPI ('[AirzoneAPI] Updating System mode......', webPython)
        
    
    data = {'event':{'cgi':'modsistema','system_number':str(nSystemNum),"option":szOption,"value":str(nValue),"device_id":szDeviceId}}

    szUriParams = 'user_email='+szUserEmail+'&user_token='+szToken
    headers = {'Content-Type': 'application/json;charset=UTF-8', 'Origin': 'https://www.airzonecloud.com', 'Accept': 'application/json, text/plain, */*', 'Accept-Encoding':'gzip, deflate, br', 'Accept-Language':'en-US,en;q=0.8,es;q=0.6', 'Referer':'https://www.airzonecloud.com/', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 'X-Requested-With':'XMLHttpRequest'}
    url = szRootUrl+'/events/?'+szUriParams
    
    s=requests.session()
    
    try:
        response = s.post(url, headers=headers, json=data, stream=False, timeout=10)
    except requests.exceptions.RequestException as e:
        Logfile.printErrorAPI ('[AirzoneAPI] Error Changing System mode state..', webPython)
        result_php = {'status': -1}
        return(result_php)
        
    s.close()
 
    if nVerbose > 1:
        Logfile.printErrorAPI ('[AirzoneAPI] URL: ' + url, webPython)
        Logfile.printErrorAPI ('[AirzoneAPI] JSON: ' + json.dumps(data), webPython)
        Logfile.printErrorAPI ('[AirzoneAPI] Resp: ' + str(response.status_code), webPython)
                

    if response.status_code > 299:
        result_php = {'status': -1}
    else:
        result_php = {'status': 0}
        
    return(result_php)
    
    
    
    
      
    
def SetZoneState(szToken, szDeviceId, nSystemNum, nZoneNum, szOption, nValue, nVerbose, webPython):
    #####################################
    # General Params
    #####################################
    
    szRootUrl = 'https://www.airzonecloud.com'
    szUserEmail='sibanezc@gmail.com'
    
    #szRootUrl = 'http://www.google.com'
    #szUserEmail='sssss@gmail.com'
    #    context = ssl._create_unverified_context()
    
 
    
    #####################################
    # Request User data sock1
    #####################################
    
    #Request URL:https://www.airzonecloud.com/events/?user_email=sibanezc@gmail.com
    #                                                &user_token=9fEz7ldoZhAzTFBcxs6TKKYzDAixT5-SKZheqQ4GuJs
    
    # {"event":{"cgi":"modzona","system_number":"1","zone_number":"3","option":"state","value":"1","device_id":"5810d30470696e3570050000"}}

    if nVerbose > 0:
        Logfile.printErrorAPI ('[AirzoneAPI] Updating zone state......', webPython)
        
    if szOption == "consign":
        szValue = "{:.1f}".format(nValue)
    else:
        szValue = str(nValue)
    
    data = {'event':{'cgi':'modzona','system_number':str(nSystemNum),"zone_number":str(nZoneNum),"option":szOption,"value":szValue,"device_id":szDeviceId}}
	
    szUriParams = 'user_email='+szUserEmail+'&user_token='+szToken
    headers = {'Content-Type': 'application/json;charset=UTF-8', 'Origin': 'https://www.airzonecloud.com', 'Accept': 'application/json, text/plain, */*', 'Accept-Encoding':'gzip, deflate, br', 'Accept-Language':'en-US,en;q=0.8,es;q=0.6', 'Referer':'https://www.airzonecloud.com/', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 'X-Requested-With':'XMLHttpRequest'}
    url = szRootUrl+'/events/?'+szUriParams
    
    s=requests.session()
    
    try:
        response = s.post(url, headers=headers, json=data, stream=False, timeout=10)
    except requests.exceptions.RequestException as e:
        Logfile.printErrorAPI ('[AirzoneAPI] Error Changing state..', webPython)
        result_php = {'status': -1}
        return(result_php)
 
    s.close()
    
    if nVerbose > 1:
        Logfile.printErrorAPI ('[AirzoneAPI] URL: ' + url, webPython)
        Logfile.printErrorAPI ('[AirzoneAPI] JSON: ' + json.dumps(data), webPython)
        Logfile.printErrorAPI ('[AirzoneAPI] Resp: ' + str(response.status_code), webPython)
                

    if response.status_code > 299:
        result_php = {'status': -1}
    else:
        result_php = {'status': 0}

    return(result_php)
    
    
    
    
      
    
    
def GetTemps(szToken, szDeviceId, nVerbose, webPython):

    szRootUrl = 'https://www.airzonecloud.com'
    szRootWSUrl = 'wss://www.airzonecloud.com'
    szUserEmail='sibanezc@gmail.com'
    
    ZonaName = ['Null' for i in range(7)]    
    ZonaTemp = ['Null' for i in range(7)]
    ZonaTempDef = ['Null' for i in range(6)]

    #####################################
    # Open websocket sock2
    #####################################
    # wss://www.airzonecloud.com/websocket?user_token=m0QehCHYEaxw6mbcE22fVFVGXgT7QFBTFg670hA-Ueo&user_email=sibanezc@.com
    
    szUriParams = 'user_token='+szToken+'&user_email='+szUserEmail
    try:
        ws = create_connection(szRootWSUrl+"/websocket?"+szUriParams, sslopt={"cert_reqs": ssl.CERT_NONE})
    except Exception as e:
        Logfile.printErrorAPI ('[AirzoneAPI] Error empezando websocket', webPython)
        result_php = {'status': -1}
        return(result_php)

    if nVerbose > 0:
        Logfile.printErrorAPI ('[AirzoneAPI] Create Websocket......', webPython)
    
    result =  ws.recv()
    if nVerbose > 2:
        Logfile.printErrorAPI ('[AirzoneAPI] <<<< '+result, webPython)
    
    if result.find ('ping')>=0:
        idRandom=random.randrange(150000) 
        dataPong = '["websocket_rails.pong",{"id":' + str(idRandom) + ',"data":{}}]'
        ws.send(dataPong)
        if nVerbose > 2:
            Logfile.printErrorAPI ('[AirzoneAPI] >>>> '+dataPong, webPython)
    
    idRandom=random.randrange(150000) 
    data = '["websocket_rails.subscribe",{"id":' + str(idRandom) + ',"data":{"channel":"'+szDeviceId+'"}}]'
    ws.send(data)
    if nVerbose > 2:
        Logfile.printErrorAPI ('[AirzoneAPI] >>>> '+data, webPython)
    
    #####################################
    # Mandar POST raro1 sock3
    #####################################
    #{"event":{"cgi":"infosistema2","system_number":"1","option":null,"value":null,"device_id":"5810d30470696e3570050000"}}
    
    if nVerbose > 0:
        Logfile.printErrorAPI ('[AirzoneAPI] Sending event to CGI, Sistema1......', webPython)
    
    data2 = '{"event":{"cgi":"infosistema2","system_number":"1","option":null,"value":null,"device_id":"'+szDeviceId+'"}}'
    databytes = data2.encode('ascii')	
    
    headers = {'Content-Type': 'application/json;charset=UTF-8', 'Origin': 'https://www.airzonecloud.com', 'Accept': 'application/json, text/plain, */*', 'Accept-Encoding':'gzip, deflate, br', 'Accept-Language':'en-US,en;q=0.8,es;q=0.6', 'Referer':'https://www.airzonecloud.com/', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 'X-Requested-With':'XMLHttpRequest'}
    szUriParams = 'user_email='+szUserEmail+'&user_token='+szToken
    url = szRootUrl+'/events/?'+szUriParams
    
    s3=requests.session()

    try: 
        response = s3.post(url, headers=headers, data=databytes, stream=False, timeout=10)
    except requests.exceptions.RequestException as e:
        Logfile.printErrorAPI ('[AirzoneAPI] Error mandando POST 1', webPython)
        result_php = {'status': -1}
        return(result_php)
 
 
    if nVerbose > 1:
        Logfile.printErrorAPI ('[AirzoneAPI] ' + url, webPython)
        Logfile.printErrorAPI ('[AirzoneAPI] ' + str(response.status_code), webPython)
        
    if response.status_code > 299:
        Logfile.printErrorAPI ('[AirzoneAPI] Error mandando POST 1', webPython)
        result_php = {'status': -1} 
        return(result_php)
    
    #####################################
    # Mandar POST raro2 sock3
    #####################################
    #{"event":{"cgi":"infosistema2","system_number":"1","option":null,"value":null,"device_id":"5810d30470696e3570050000"}}
    
    if nVerbose > 0:
        Logfile.printErrorAPI ('[AirzoneAPI] Sending event to CGI, Sistema2......', webPython)
    
    data2 = '{"event":{"cgi":"infosistema2","system_number":"2","option":null,"value":null,"device_id":"'+szDeviceId+'"}}'
    databytes = data2.encode('ascii')	
    
    headers = {'Content-Type': 'application/json;charset=UTF-8', 'Origin': 'https://www.airzonecloud.com', 'Accept': 'application/json, text/plain, */*', 'Accept-Encoding':'gzip, deflate, br', 'Accept-Language':'en-US,en;q=0.8,es;q=0.6', 'Referer':'https://www.airzonecloud.com/', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 'X-Requested-With':'XMLHttpRequest'}
    szUriParams = 'user_email='+szUserEmail+'&user_token='+szToken
    url = szRootUrl+'/events/?'+szUriParams
    try:
        response = s3.post(url, headers=headers, data=databytes, stream=False, timeout=10)
    except requests.exceptions.RequestException as e:
        Logfile.printErrorAPI ('[AirzoneAPI] Error mandando POST 2', webPython)
        result_php = {'status': -1}
        return(result_php)
 
    if nVerbose > 1:
        Logfile.printErrorAPI ('[AirzoneAPI] ' + url, webPython)
        Logfile.printErrorAPI ('[AirzoneAPI] ' + str(response.status_code), webPython)
        
    if response.status_code > 299:
        result_php = {'status': -1}
        return(result_php)
    
    #####################################
    # Handle websocket (vaya basura de codigo, hay que hacer un thread aparte)
    #####################################
    
    initLoopZones = 0
    initLoopPings = 0
    zonesFilled = [0] * 6
    
    while sum (zonesFilled) < 6 and initLoopPings < 5:
        result =  ws.recv()
        if nVerbose > 2:
            Logfile.printErrorAPI ('[AirzoneAPI] <<<< '+result, webPython)
        if result.find ('consign') >= 0:
            initLoopZones+=1
            if nVerbose > 0:
                Logfile.printErrorAPI ('[AirzoneAPI] Getting Zone '+str(initLoopZones)+'....', webPython)
            data = json.loads(result) 
            systemnumber = int(data[0][1]['data']['system_number']) - 1
            indexnumber = systemnumber*3 + int(data[0][1]['data']['zone_number']) - 1
            zonesFilled[indexnumber] = 1;
            ZonaTemp[indexnumber] = data[0][1]['data']['temp']
            ZonaName[indexnumber] = data[0][1]['data']['name']
            if nVerbose > 0:
                Logfile.printErrorAPI ('[AirzoneAPI] Nombre:'+ZonaName[indexnumber], webPython)
                Logfile.printErrorAPI ('[AirzoneAPI] Index:'+str(indexnumber), webPython)
                Logfile.printErrorAPI ('[AirzoneAPI] Temp:'+ZonaTemp[indexnumber], webPython)
        if result.find ('ping') >= 0:
            idRandom=random.randrange(150000) 
            dataPong = '["websocket_rails.pong",{"id":' + str(idRandom) + ',"data":{}}]'
            ws.send(dataPong)
            initLoopPings+=1
            if nVerbose > 2:
                Logfile.printErrorAPI ('[AirzoneAPI] >>>> '+dataPong, webPython)
    
    #####################################
    # Close Socket
    #####################################
    #["websocket_rails.unsubscribe", {id: 92397, data: {channel: "5810d30470696e3570050000"}}]
    
    if nVerbose > 0:
        Logfile.printErrorAPI ('[AirzoneAPI] Close websocket......', webPython)
    
    data = '["websocket_rails.unsubscribe",{"id":' + str(idRandom) + ',"data":{"channel":"'+szDeviceId+'"}}]'
    ws.send(data)
    if nVerbose > 2:
        Logfile.printErrorAPI ('[AirzoneAPI] >>>> '+data, webPython)
    
    ws.close()
    s3.close()
    
    sortTempsAirzone(ZonaName, ZonaTemp, ZonaTempDef)
    
    Logfile.printErrorAPI ('[AirzoneAPI] SALON:     '+ZonaTempDef[0]+'C', webPython)
    Logfile.printErrorAPI ('[AirzoneAPI] DESPACHO:  '+ZonaTempDef[1]+'C', webPython)
    Logfile.printErrorAPI ('[AirzoneAPI] COCINA:    '+ZonaTempDef[2]+'C', webPython)
    Logfile.printErrorAPI ('[AirzoneAPI] PRINCIPAL: '+ZonaTempDef[3]+'C', webPython)
    Logfile.printErrorAPI ('[AirzoneAPI] SOFIA:     '+ZonaTempDef[4]+'C', webPython)
    Logfile.printErrorAPI ('[AirzoneAPI] ALVARO:    '+ZonaTempDef[5]+'C', webPython)
    
    result_php = {'status': 0, 'temps' : {'Salon': ZonaTempDef[0], 'Despacho': ZonaTempDef[1], 'Cocina': ZonaTempDef[2], 'Principal': ZonaTempDef[3], 'Sofia': ZonaTempDef[4], 'Alvaro': ZonaTempDef[5]}}

    # Send it to stdout (to PHP)
    #print (json.dumps(result_php))
    
    return(result_php)
    
    
    
    
    
def Logout(szToken, nVerbose, webPython):
    
    #####################################
    # Sign out.... 
    #####################################
    
    if nVerbose > 0:
        Logfile.printErrorAPI ('[AirzoneAPI] Signing out......', webPython)
    
    szRootUrl = 'https://www.airzonecloud.com'
    szUserEmail='sibanezc@gmail.com'
    
    data = {}
    
    szUriParams = 'user_email='+szUserEmail+'&user_token='+szToken
    headers = {'Content-Type': 'application/json', 'Cookie': 'SERVERID=Server_2'}
    url = szRootUrl+'/users/sign_out?'+szUriParams
    
    s3=requests.session()
    
    try:
        response = s3.delete(url, headers=headers, json=data, stream=False, timeout=10)
    except requests.exceptions.RequestException as e:
        Logfile.printErrorAPI ('[AirzoneAPI] Error Signing out', webPython)
        result_php = {'status': -1}
        return(result_php)
        
    s3.close()
    
    if nVerbose > 1:
        Logfile.printErrorAPI ('[AirzoneAPI] ' + url, webPython)
        Logfile.printErrorAPI ('[AirzoneAPI] ' + str(response.status_code), webPython)
        
    result_php = {'status': 0}

    return(result_php)   
        
        

def airzoneControl(input_options, webPython, nVerbose):

    # Modos:
    # 
    # gettemps
    # getstatedata
    # setzonestate nSystemNum nZoneNum szOption nValue
    
    # webPython:
    #     0 -> Desde web
    #     1 -> Desde Pyhton
        
    if len (input_options) < 2:
        print ("Wrong params. Usage:")
        print ("python3 AirzoneAPI.py mode params ...")
        print ("    mode: gettemps, getstatedata, setzonestate, setsystemmode")
        return 
    szRequestType = input_options[1]
    if szRequestType == 'setzonestate':
        if len (input_options) < 6:
            print ("Wrong params. Usage:")
            print ("python3 AirzoneAPI.py setzonestate nSystemNum nZoneNum szOption nValue")
            return 
        nSystemNum = int(input_options[2])
        if nSystemNum < 1 or nSystemNum > 2:
            print ("Wrong params. Usage:")
            print ("python3 AirzoneAPI.py setzonestate nSystemNum nZoneNum szOption nValue")
            print ("")
            print ("El valor SystemNum debe ser entre 1 y 2")
            return 
        nZoneNum = int(input_options[3])
        if nZoneNum < 1 or nZoneNum > 3:
            print ("Wrong params. Usage:")
            print ("python3 AirzoneAPI.py setzonestate nSystemNum nZoneNum szOption nValue")
            print ("")
            print ("El valor ZoneNum debe ser entre 1 y 3")
            return 
        szOption = input_options[4]
        nValue = float(input_options[5])
        if szOption != "state" and szOption != "sleep" and szOption != "consign":
            print ("Wrong params. Usage:")
            print ("python3 AirzoneAPI.py setzonestate nSystemNum nZoneNum szOption nValue")
            print ("")
            print ("El valor szOption debe ser state, consign o sleep")
            return 
        if szOption == "state" and (nValue < 0 or nValue >1):
            print ("Wrong params. Usage:")
            print ("python3 AirzoneAPI.py setzonestate nSystemNum nZoneNum szOption nValue")
            print ("")
            print ("El valor nValue para la opcion state debe ser entre 0 y 1")
            return 
        if szOption == "sleep" and (nValue < 0 or nValue >3):
            print ("Wrong params. Usage:")
            print ("python3 AirzoneAPI.py setzonestate nSystemNum nZoneNum szOption nValue")
            print ("")
            print ("El valor nValue para la opcion sleep debe ser entre 0 y 3")
            return 
            
        if szOption == "consign" and (nValue < 22 or nValue >30):
            print ("Wrong params. Usage:")
            print ("python3 AirzoneAPI.py setzonestate nSystemNum nZoneNum szOption nValue")
            print ("")
            print ("El valor nValue para la opcion consign debe ser entre 22 y 30")
            return 
    if szRequestType == 'setsystemmode':
        if len (input_options) < 5:
            print ("Wrong params. Usage:")
            print ("python3 AirzoneAPI.py setsystemmode nSystemNum szOption nValue")
            return 
        nSystemNum = int(input_options[2])
        if nSystemNum < 1 or nSystemNum > 2:
            print ("Wrong params. Usage:")
            print ("python3 AirzoneAPI.py setsystemmode nSystemNum szOption nValue")
            print ("")
            print ("El valor SystemNum debe ser entre 1 y 2")
            return 
        szOption = input_options[3]
        nValue = int(input_options[4])
        if szOption != "mode":
            print ("Wrong params. Usage:")
            print ("python3 AirzoneAPI.py setsystemmode nSystemNum szOption nValue")
            print ("")
            print ("El valor szOption debe ser mode")
            return 
        if szOption == "mode" and (nValue < 0 or nValue >1):
            print ("Wrong params. Usage:")
            print ("python3 AirzoneAPI.py setsystemmode nSystemNum szOption nValue")
            print ("")
            print ("El valor nValue para la opcion mode debe ser entre 0 y 1")
            return 
        
    
    result = readTokenFile(nVerbose, webPython)
    
    if (result['status']<0):
        Logfile.printErrorAPI ('Token fail', webPython)
        result = GetInitData(nVerbose, webPython)
    
    szToken = result['token']
    szDeviceId = result['DeviceID']
    
    
    if szRequestType == 'gettemps':
        result = GetTemps(szToken, szDeviceId, nVerbose, webPython)
        if (result['status']<0):
            Logfile.printErrorAPI  ('[AirzoneAPI] Token fail-2', webPython)
            result = GetInitData(nVerbose, webPython)
            szToken = result['token']
            szDeviceId = result['DeviceID']
            result = GetTemps(szToken, szDeviceId, nVerbose, webPython)

    if szRequestType == 'getstatedata':
        result = GetSystemsData(szToken, szDeviceId, nVerbose, webPython)
        if (result['status']<0):
            Logfile.printErrorAPI  ('[AirzoneAPI] Token fail-2', webPython)
            result = GetInitData(nVerbose, webPython)
            szToken = result['token']
            szDeviceId = result['DeviceID']
            result = GetSystemsData(szToken, szDeviceId, nVerbose, webPython)
        

    if szRequestType == 'setzonestate':
        result = SetZoneState(szToken, szDeviceId, nSystemNum, nZoneNum, szOption, nValue, nVerbose, webPython)
        if (result['status']<0):
            Logfile.printErrorAPI  ('[AirzoneAPI] Token fail-2', webPython)
            result = GetInitData(nVerbose, webPython)
            szToken = result['token']
            szDeviceId = result['DeviceID']
            result = SetZoneState(szToken, szDeviceId, nSystemNum, nZoneNum, szOption, nValue, nVerbose, webPython)
            
    if szRequestType == 'setsystemmode':
        result = SetSystemMode(szToken, szDeviceId, nSystemNum, szOption, nValue, nVerbose, webPython)
        if (result['status']<0):
            Logfile.printErrorAPI  ('[AirzoneAPI] Token fail-2', webPython)
            result = GetInitData(nVerbose, webPython)
            szToken = result['token']
            szDeviceId = result['DeviceID']
            result = SetSystemMode(szToken, szDeviceId, nSystemNum, szOption, nValue, nVerbose, webPython)
            
    #Logout(szToken, nVerbose, webPython)
    if (webPython == 0):    
        print (json.dumps(result))
    else:
        return (result)


    
#####################################
# Main
#####################################    
if __name__ == "__main__":
#    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

    # Modos:
    # 
    # gettemps
    # getstatedata
    # setzonestate nSystemNum nZoneNum szOption nValue
    
    # webPython:
    #     0 -> Desde web
    #     1 -> Desde Pyhton
    airzoneControl(sys.argv, 0, 1)    
    

