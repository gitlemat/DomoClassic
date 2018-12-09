import os
import smtplib
import requests
import datetime
import Logfile
import HandleDeviceConfig


from email.mime.text import MIMEText
    
def sendMailGoogle (objeto, objetoState):
    import smtplib
    fromaddr = 'domocasa5566@gmail.com'
    toaddrs  = 'sibanezc@gmail.com'
    username = 'domocasa5566@gmail.com'
    password = 'monkey......123'

    msg = "\r\n".join([
        "From: " + fromaddr,
        "To:" + toaddrs,
        "Subject: [Domotica] - " + objeto + " ha cambiado a " + objetoState,
        "",
        objeto + " ha cambiado a " + objetoState
    ])

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()
    
def MonitorPing(nVerbose): 

    # Cada 5 min hace ping a los wemos
    # Si no responden pone rojo
    
    # Leemos fichero de estados actuales
    # Lo que haya en DEVICES_LIST
    
    szSortBy = ""
    deviceList = HandleDeviceConfig.GetDeviceHWListAll(szSortBy, nVerbose)
    
    for device in deviceList:
        szSonOffStateOld=device['State']
        szAddress = device['Address']
        szURL='http://' + szAddress
        #szDevId=device['devId']
        
        s=requests.session()
        try:
            response = s.get(szURL,stream=False, timeout=5)
            statuscode = response.status_code
        except requests.exceptions.RequestException as e:
            Logfile.printError ('[MonitorPing] Error conectando a device '+device['Address'])
            statuscode = -1
            pass 
            
        s.close()
    
        if statuscode == 200:
            szSonOffStateNew = "on"
        else:
            szSonOffStateNew = "off"
            
        if szSonOffStateNew != szSonOffStateOld:
            Logfile.printError ('[MonitorPing] ATENCION: '+ szAddress + 'ahora: ' + szSonOffStateNew)
            HandleDeviceConfig.UpdateDeviceState(szAddress, szSonOffStateNew, nVerbose)
            #sendMailGoogle(szDevId, szSonOffStateNew)
                
def main():

    MonitorPing(1);
       
if __name__ == "__main__":
    main()
