import json
import ssl
import websocket
import random
import requests
import datetime
import Logfile

from websocket import create_connection
    
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
        
def GetTemp(ZonaTempDef, nVerbose):
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
        Logfile.printError ('[Airzone] Load homepage......')
    
    headers = {'Cookie': 'SERVERID=Server_2'}
    url = szRootUrl
    s=requests.session()
    try:
        response = s.get(url, headers=headers, stream=False, timeout=15)
    except requests.exceptions.RequestException as e:
        Logfile.printError ('[Airzone] Error leyendo Homepage')
        return()
 
    #####################################
    # Sign in sock1
    #####################################
    
    if nVerbose > 0:
        Logfile.printError ('[Airzone] Signing in......')
        
    data = {}
    #headers = {'Content-Type': 'application/json, text/plain, */*', 'Cookie': 'SERVERID=Server_2', 'X-Requested-With':'XMLHttpRequest'}
    headers = {'Content-Type': 'application/json;charset=UTF-8', 'Origin': 'https://www.airzonecloud.com', 'Accept': 'application/json, text/plain, */*', 'Accept-Encoding':'gzip, deflate, br', 'Accept-Language':'en-US,en;q=0.8,es;q=0.6', 'Referer':'https://www.airzonecloud.com/', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 'X-Requested-With':'XMLHttpRequest'}
    
    url = szRootUrl+'/browsers/?format=json'

    try:
        response = s.post(url, headers=headers, json=data, stream=False, timeout=10)
    except requests.exceptions.RequestException as e:
        Logfile.printError ('[Airzone] Error Signing in..')
        return()
            
    data = {'email': szUserEmail, 'password' : szUserPsw}
    #headers = {'Content-Type': 'application/json', 'Cookie': 'SERVERID=Server_2', 'X-Requested-With':'XMLHttpRequest'}
    headers = {'Content-Type': 'application/json;charset=UTF-8', 'Origin': 'https://www.airzonecloud.com', 'Accept': 'application/json, text/plain, */*', 'Accept-Encoding':'gzip, deflate, br', 'Accept-Language':'en-US,en;q=0.8,es;q=0.6', 'Referer':'https://www.airzonecloud.com/', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 'X-Requested-With':'XMLHttpRequest'}

    url = szRootUrl+'/users/sign_in'

    try:
        response = s.post(url, headers=headers, json=data, stream=False, timeout=10)
    except requests.exceptions.RequestException as e:
        Logfile.printError ('[Airzone] Error Signing in..')
        return()
         
    data = response.json()
    
    szToken = data['user']['authentication_token']
    szId = data['user']['id']
    
    #####################################
    # Request User data sock1
    #####################################
    
    if nVerbose > 0:
        Logfile.printError ('[Airzone] Request User Data......')
    
    szUriParams = 'format=json&user_email='+szUserEmail+'&user_token='+szToken
    #headers = {'Cookie': 'SERVERID=Server_2'}
    headers = {'Content-Type': 'application/json;charset=UTF-8', 'Origin': 'https://www.airzonecloud.com', 'Accept': 'application/json, text/plain, */*', 'Accept-Encoding':'gzip, deflate, br', 'Accept-Language':'en-US,en;q=0.8,es;q=0.6', 'Referer':'https://www.airzonecloud.com/', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 'X-Requested-With':'XMLHttpRequest'}

    url = szRootUrl+'/device_relations/?'+szUriParams
    
    try: 
        response = s.get(url, headers=headers, stream=False, timeout=10)
    except requests.exceptions.RequestException as e:
        Logfile.printError ('[Airzone] Error leyendo User Data')
        return()
 
    data = response.json()
    
    szDeviceId = data['device_relations'][0]['device']['id']
    
    #####################################
    # Open websocket sock2
    #####################################
    # wss://www.airzonecloud.com/websocket?user_token=m0QehCHYEaxw6mbcE22fVFVGXgT7QFBTFg670hA-Ueo&user_email=sibanezc@.com
    
    szUriParams = 'user_token='+szToken+'&user_email='+szUserEmail
    try:
        ws = create_connection(szRootWSUrl+"/websocket?"+szUriParams, sslopt={"cert_reqs": ssl.CERT_NONE})
    except Exception as e:
        Logfile.printError ('[Airzone] Error empezando websocket')
        return()

    if nVerbose > 0:
        Logfile.printError ('[Airzone] Create Websocket......')
    
    result =  ws.recv()
    if nVerbose > 2:
        Logfile.printError ('[Airzone] <<<< '+result)
    
    if result.find ('ping')>=0:
        idRandom=random.randrange(150000) 
        dataPong = '["websocket_rails.pong",{"id":' + str(idRandom) + ',"data":{}}]'
        ws.send(dataPong)
        if nVerbose > 2:
            Logfile.printError ('[Airzone] >>>> '+dataPong)
    
    idRandom=random.randrange(150000) 
    data = '["websocket_rails.subscribe",{"id":' + str(idRandom) + ',"data":{"channel":"'+szDeviceId+'"}}]'
    ws.send(data)
    if nVerbose > 2:
        Logfile.printError ('[Airzone] >>>> '+data)
    
    #####################################
    # Mandar POST raro1 sock3
    #####################################
    #{"event":{"cgi":"infosistema2","system_number":"1","option":null,"value":null,"device_id":"5810d30470696e3570050000"}}
    
    if nVerbose > 0:
        Logfile.printError ('[Airzone] Sending event to CGI, Sistema1......')
    
    data2 = '{"event":{"cgi":"infosistema2","system_number":"1","option":null,"value":null,"device_id":"'+szDeviceId+'"}}'
    databytes = data2.encode('ascii')	
    
    headers = {'Content-Type': 'application/json;charset=UTF-8', 'Origin': 'https://www.airzonecloud.com', 'Accept': 'application/json, text/plain, */*', 'Accept-Encoding':'gzip, deflate, br', 'Accept-Language':'en-US,en;q=0.8,es;q=0.6', 'Referer':'https://www.airzonecloud.com/', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 'X-Requested-With':'XMLHttpRequest'}
    szUriParams = 'user_email='+szUserEmail+'&user_token='+szToken
    url = szRootUrl+'/events/?'+szUriParams
    s3=requests.session()
    try: 
        response = s3.post(url, headers=headers, data=databytes, stream=False, timeout=10)
    except requests.exceptions.RequestException as e:
        Logfile.printError ('[Airzone] Error mandando POST 1')
        return()
 
    if nVerbose > 1:
        Logfile.printError ('[Airzone] ' + url)
    if nVerbose > 1:
        Logfile.printError ('[Airzone] ' + str (response.status_code))
    
    #####################################
    # Mandar POST raro2 sock3
    #####################################
    #{"event":{"cgi":"infosistema2","system_number":"1","option":null,"value":null,"device_id":"5810d30470696e3570050000"}}
    
    if nVerbose > 0:
        Logfile.printError ('[Airzone] Sending event to CGI, Sistema2......')
    
    data2 = '{"event":{"cgi":"infosistema2","system_number":"2","option":null,"value":null,"device_id":"'+szDeviceId+'"}}'
    databytes = data2.encode('ascii')	
    
    headers = {'Content-Type': 'application/json;charset=UTF-8', 'Origin': 'https://www.airzonecloud.com', 'Accept': 'application/json, text/plain, */*', 'Accept-Encoding':'gzip, deflate, br', 'Accept-Language':'en-US,en;q=0.8,es;q=0.6', 'Referer':'https://www.airzonecloud.com/', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 'X-Requested-With':'XMLHttpRequest'}
    szUriParams = 'user_email='+szUserEmail+'&user_token='+szToken
    url = szRootUrl+'/events/?'+szUriParams
    try:
        response = s3.post(url, headers=headers, data=databytes, stream=False, timeout=10)
    except requests.exceptions.RequestException as e:
        Logfile.printError ('[Airzone] Error mandando POST 2')
        return()
 
    if nVerbose > 1:
        Logfile.printError ('[Airzone] ' + url)
        Logfile.printError ('[Airzone] ' + str (response.status_code))
    
    #####################################
    # Handle websocket (vaya basura de codigo, hay que hacer un thread aparte)
    #####################################
    
    initLoopZones = 0
    initLoopPings = 0
    zonesFilled = [0] * 6
    
    while sum (zonesFilled) < 6 and initLoopPings < 5:
        result =  ws.recv()
        if nVerbose > 2:
            Logfile.printError ('[Airzone] <<<< '+result)
        if result.find ('consign') >= 0:
            initLoopZones+=1
            if nVerbose > 0:
                Logfile.printError ('[Airzone] Getting Zone '+str(initLoopZones)+'....')
            data = json.loads(result) 
            systemnumber = int(data[0][1]['data']['system_number']) - 1
            indexnumber = systemnumber*3 + int(data[0][1]['data']['zone_number']) - 1
            zonesFilled[indexnumber] = 1;
            ZonaTemp[indexnumber] = data[0][1]['data']['temp']
            ZonaName[indexnumber] = data[0][1]['data']['name']
            if nVerbose > 0:
                Logfile.printError ('[Airzone] Nombre:'+ZonaName[indexnumber])
                Logfile.printError ('[Airzone] Index:'+str(indexnumber))
                Logfile.printError ('[Airzone] Temp:'+ZonaTemp[indexnumber])
        if result.find ('ping') >= 0:
            idRandom=random.randrange(150000) 
            dataPong = '["websocket_rails.pong",{"id":' + str(idRandom) + ',"data":{}}]'
            ws.send(dataPong)
            initLoopPings+=1
            if nVerbose > 2:
                Logfile.printError ('[Airzone] >>>> '+dataPong)
    
    #####################################
    # Close Socket
    #####################################
    #["websocket_rails.unsubscribe", {id: 92397, data: {channel: "5810d30470696e3570050000"}}]
    
    if nVerbose > 0:
        Logfile.printError ('[Airzone] Close websocket......')
    
    data = '["websocket_rails.unsubscribe",{"id":' + str(idRandom) + ',"data":{"channel":"'+szDeviceId+'"}}]'
    ws.send(data)
    if nVerbose > 2:
        Logfile.printError ('[Airzone] >>>> '+data)
    
    ws.close()
    
    #####################################
    # Sign out.... 
    #####################################
    
    if nVerbose > 0:
        Logfile.printError ('[Airzone] Signing out......')
    
    data = {}
    szUriParams = 'user_email='+szUserEmail+'&user_token='+szToken
    headers = {'Content-Type': 'application/json', 'Cookie': 'SERVERID=Server_2'}
    url = szRootUrl+'/users/sign_out?'+szUriParams
    try:
        response = s3.delete(url, headers=headers, json=data, stream=False, timeout=10)
    except requests.exceptions.RequestException as e:
        Logfile.printError ('[Airzone] Error Signing out')
        return()

    s.close()
    s3.close()
    
    if nVerbose > 1:
        Logfile.printError ('[Airzone] ' + url)
        Logfile.printError ('[Airzone] ' + str(response.status_code))
        
    sortTempsAirzone(ZonaName, ZonaTemp, ZonaTempDef)

def main():
    ZonaTempDef = ['Null' for i in range(6)]

    GetTemp(ZonaTempDef, 1)
    print (ZonaTempDef)
    Logfile.printError ('[Airzone] SALON:     '+ZonaTempDef[0]+'C')
    Logfile.printError ('[Airzone] DESPACHO:  '+ZonaTempDef[1]+'C')
    Logfile.printError ('[Airzone] COCINA:    '+ZonaTempDef[2]+'C')
    Logfile.printError ('[Airzone] PRINCIPAL: '+ZonaTempDef[3]+'C')
    Logfile.printError ('[Airzone] SOFIA:     '+ZonaTempDef[4]+'C')
    Logfile.printError ('[Airzone] ALVARO:    '+ZonaTempDef[5]+'C')
    
#####################################
# Main
#####################################    
if __name__ == "__main__":
    main()
    

