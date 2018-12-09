# RESTAPI


# /Alarms/GetAlarms

# /Rooms/GetRoomList

# /Calefaccion/Update
# /Calefaccion/GetConsignas
# /Calefaccion/GetConsignaMode
# /Calefaccion/GetRoomListTreeTemps    // Devuelve lista de habitaciones con temps y con caldera
# /Calefaccion/GetTemp?room=Sofia     
#                      room=all
# /Calefaccion/GetValvulaState?devId1=ValvSofia&devId2=ValvAlvaro     

# /Calefaccion/SetTempManual?Temp=22.5
# /Calefaccion/SetOffsetRoom
# /Calefaccion/SetOpMode?Mode=Prog



# /Update/Persianas/nPersiana/nNivel

# /TimerOnOff/Read?devId=SOJD1
# /TimerOnOff/Setmode?devId=SOJD1&Mode=Prog


##########################################
##      Devices                        ###
##########################################
# Get Info
#
# /Device/GetList?type=tipo_luz
# /Device/GetListAll?sortBy=Address       [Parametro de sortBy opcional]
# /Device/GetListAllTree
# /Device/GetHWListAll
# /Device/GetTypesList
# /Device/GetHWTypesList

##########################################
# Notifications
# 
# /Device/Notify?devId=SOAN1
# /Device/Notify?HWId=SOAN1

##########################################
# Actuaciones
#
# /Device/Read?devId=SOAN1
# /Device/Actuate?devId=SOAN1&State=2  ->  Actuador/Rele

##########################################
# Paraguas
#
# /Device/Config/ModifyHW?Address=192.168.2.167&AddressNew=192.168.2.189&mbAddress=2&HWtype=Sonoff
# /Device/Config/DeleteHW?Address=192.168.1.165
# /Device/Config/AddModifyUsage?devId=TMP554&Address=192.168.1.165&devType=tPersiana&numButton=2&numOutputs=2&pinInput1=0&pinInput2=1&pinOutput1=0&pinOutput2=1&Description=Pruebassss
# /Device/Config/DeleteUsage?devId=TMP554&Address=192.168.1.166

##########################################
# Solo DB
#
# /Device/Config/AddHWDB?HWtype=Domo4ch&Address=192.168.1.165
#      Return: nMBAddress para que lo grabe el arduino
# /Device/Config/ModifyHWDB?HWtype=Domo4ch&Address=192.168.1.135&mbAddress=9
# /Device/Config/DeleteHWDB?Address=192.168.1.165 
#
# /Device/Config/AddModifyUsageDB?devId=TMP554&Address=192.168.1.166&numButton=3&pinInput1=0&pinInput2=2&pinOutput1=0&Description=Pruebassssttt
# /Device/Config/DeleteUsageDB?devId=TMP554

##########################################
# Solo FW
#
# /Device/Config/AddModifyUsageFirmware?Address=192.168.2.167&devId=TMP554&devIdNew=SOAN1devType=tLuz&pinInput1=4&pinInput2=5&pinOutput1=11&pinOutput2=13&Description=Teas%20Test     devID es obligatorio
# /Device/Config/DeleteUsageFirmware?devId=TMP554                                          devID es obligatorio


from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
import multiprocessing
import threading
import random
import Calefaccion
import Calefaccion2
import Logfile
import time
import re
import datetime
import control_persianas
import control_devices
import control_rooms
import ReadTimeOnOff
import ReadConsigna2
import ReadConsigna3
import HandleDeviceConfig
import Alarms


hostName = "192.168.2.129"
hostPort = 9000

class MyServer(BaseHTTPRequestHandler):

    def log_request(self, code='-', size='-'):
        # Override para evitar que escriba al stdout
        pass
        
    def do_GET(self):

        nVerbose = 1
        # import os.path
        # from urllib.parse import urlparse
        # 
        # o = urlparse('http://www.cwi.nl:80/%7Eguido/Python?variable=1&ip=192%2E168%2E2%2E8')
        # o2 = parse_qs(o.query)
        # o2
        # {'ip': ['192.168.2.8'], 'variable': ['1']}
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        parsed_path = urlparse(self.path)
        realPath = parsed_path.path
        variablesAll = parsed_path.query
        variablesList = parse_qs (variablesAll)
        
        messageWeb = "No Command Found"

        if nVerbose > 0:
            Logfile.printError ('[Webserver] Request: '+self.path)
    

        if (realPath.startswith  ('/Calefaccion')):
            messageWeb = self.CalefaccionHandle (realPath, variablesList, 1)
            
        if (realPath.startswith ('/Update/Persianas')):
            t_persianas = threading.Thread(name='persianas', target=self.Persianas_loop, args=(realPath, 1,))
            messageWeb = "Persianas Update ....\n"
            t_persianas.start()
            
        if (realPath.startswith ('/TimerOnOff')):
            messageWeb = self.timeronoff_loop (realPath, variablesList, 1)
            
        if (realPath.startswith ('/Rooms')):
            messageWeb = self.RoomsHandle (realPath, variablesList, 1)
            
        if (realPath.startswith ('/Device')):
            messageWeb = self.DeviceHandle (realPath, variablesList, 1)
            
        if (realPath.startswith ('/Alarms')):
            messageWeb = self.AlarmsHandle (realPath, variablesList, 1)
        
        if (realPath.startswith ('/Status')) or (realPath == "/"):
            messageWeb = self.Status_Parse (realPath)
                    
        
        #self.wfile.write(bytes("<html><head><title>Domotica Web Sever</title></head>\n", "utf-8"))
        #self.wfile.write(bytes("<body style=\"font-family:'lucida console'\">", "utf-8"))

        #self.wfile.write(bytes("<p style=\"font-size:20px;\">Domotica Web Server</p>\n", "utf-8"))
        #self.wfile.write(bytes("<p style=\"font-size:20px;\">-------------------</p>\n", "utf-8"))

        self.wfile.write(bytes(str(messageWeb), "utf-8"))
        
        Logfile.printError ('[Webserver] Respuesta: ' + messageWeb)
        #self.wfile.write(bytes("</body></html>", "utf-8"))

    def Persianas_loop(self, realPath, nVerbose):     
        Logfile.printError ('[Webserver] Proceso Persinanas iniciado..')
        
        pathList = realPath.split('/')
        
        nPersiana = pathList [3]
        nNivel = pathList [4]
        
        control_persianas.persiana_control(str(nPersiana), nNivel, str(nVerbose))
        
    def CalefaccionHandle(self, realPath, variablesList, nVerbose):
        # /Calefaccion/Update
        # /Calefaccion/GetConsignas
        # /Calefaccion/GetConsignaMode
        # /Calefaccion/SetTempManual?Temp=22.5
        # /Calefaccion/SetOffsetRoom
        # /Calefaccion/SetOpMode?Mode=Prog
        # /Calefaccion/GetValvulaState?devId1=ValvSofia&devId2=ValvAlvaro 
        
        messageWeb = "404"    

    
        if (realPath == "/Calefaccion/Update"): 
            t_calefaccion = threading.Thread(name='calefaccion', target=self.Calefaccion_loop)
            messageWeb = "Calefaccion Update ....\n"
            t_calefaccion.start()
            
        if (realPath == "/Calefaccion/GetConsignas"): 
            consignas = ReadConsigna2.readConsigna(nVerbose)
            messageWeb = json.dumps(consignas)
            
        if (realPath == "/Calefaccion/GetConsignaMode"): 
            consignaMode = ReadConsigna3.readConsignaMode(nVerbose)
            messageWeb = json.dumps(consignaMode)
            
        if (realPath == "/Calefaccion/GetRoomListTreeTemps"): 
            # /Calefaccion/GetRoomsListTreeTemps
            rooms = Calefaccion2.GetRoomListTreeTemps(nVerbose)
            messageWeb = json.dumps(rooms)
            
        if (realPath == "/Calefaccion/SetTempManual"): 
            szTemp = ""
            if (variablesList.get('Temp')):
                szTemp = variablesList['Temp'][0]
                ReadConsigna2.SetTempManual (szTemp, nVerbose)
                messageWeb = "0"
         
        if (realPath == "/Calefaccion/SetOpMode"): 
            szOpMode = ""
            if (variablesList.get('Mode')):
                szOpMode = variablesList['Mode'][0]
                ReadConsigna2.SetOpMode (szOpMode, nVerbose)
                messageWeb = "0"
                
        if (realPath == "/Calefaccion/SetOffsetRoom"): 
            szRoom = ""
            if (variablesList.get('Room') and variablesList.get('Temp')):
                szRoom = variablesList['Room'][0]
                szTemp = variablesList['Temp'][0]
                ReadConsigna2.SetOffsetRoom (szRoom, szTemp, nVerbose)
                messageWeb = "0"
                
        if (realPath == "/Calefaccion/GetValvulaState"): 
            szCal = {}
            szReturn = {}
            for var,val in variablesList.items():
                devId_tmp = val[0]
                
                szRoomInfo = HandleDeviceConfig.GetRoomFromDevId(devId_tmp,nVerbose)
                szRoom = szRoomInfo[0]['roomID']
                szCal.update({val[0] : Calefaccion.GetValvulaState ( szRoom,nVerbose)})
                
            szReturn.update({'status' : 0})
            szReturn.update({'value' : szCal})
            messageWeb = str(szReturn)
                  
        return (messageWeb)
            
        
        
    def Calefaccion_loop(self):        
        Logfile.printError ('[Webserver] Proceso Calefaccion iniciado..')
    
        p = multiprocessing.Process(target=self.llamadaCalefaccion())
    
        p.start()
            
        # Wait for 10 minutes or until process finishes
        p.join(600)
        Logfile.printError ('[Webserver] Proceso Calefaccion finalizado o timeout..')
            
        # If thread is still active
        if p.is_alive():
            Logfile.printError ('[Webserver] Calefaccion parece que se ha quedado bloqueado. Killin it...')
            
            # Terminate
            p.terminate()
            p.join()
                     
    
    def llamadaCalefaccion(self):
        try:
            Calefaccion.Calefaccion_control(1)
        except:
            Logfile.printError ('[Webserver] Error en Calefaccion')
            pass        
    
    def AlarmsHandle (self, realPath, variablesList, nVerbose):
        
        messageWeb = "Device Handle Subcommand Command Found"
        if (realPath == "/Alarms/GetAlarms"): 
            AlarmsList = Alarms.readAlarmsMariaDB(variablesList, nVerbose);
            messageWeb = json.dumps(AlarmsList)
            
        return (messageWeb)
            
    def RoomsHandle (self, realPath, variablesList, nVerbose):
        messageWeb = "Room Handle Subcommand Command Found"
        
        if (realPath == "/Rooms/GetRoomList"): 
            # /Rooms/GetRoomList
            szSortBy = ""
            
            if (variablesList.get('sortBy')):
                szSortBy = variablesList['sortBy'][0]
            szRoomList=control_rooms.GetRoomList(nVerbose)
            
            messageWeb = json.dumps(szRoomList)
        
        return (messageWeb)
    
    def DeviceHandle (self, realPath, variablesList, nVerbose):
        
        messageWeb = "Device Handle Subcommand Command Found"
        
        if (realPath == "/Device/GetHWListAll"): 
            # /Device/GetListAll
            szSortBy = ""
            if (variablesList.get('sortBy')):
                szSortBy = variablesList['sortBy'][0]
            deviceList = HandleDeviceConfig.GetDeviceHWListAll(szSortBy,nVerbose)
            messageWeb = json.dumps(deviceList)
            
        if (realPath == "/Device/GetList"): 
            #/Device/GetList?type=tLuz
            szType = ""
            if (variablesList.get('type')):
                szType = variablesList['type'][0]
            deviceList = HandleDeviceConfig.GetUsageListTypeOn(szType, nVerbose)
            messageWeb = json.dumps(deviceList)
        
        if (realPath == "/Device/GetListAll"): 
            # /Device/GetListAll
            szSortBy = ""
            if (variablesList.get('sortBy')):
                szSortBy = variablesList['sortBy'][0]
            deviceList = HandleDeviceConfig.GetUsagesListAll(szSortBy,nVerbose)
            messageWeb = json.dumps(deviceList)
            
        if (realPath == "/Device/GetListAllTree"): 
            # /Device/GetListAllTree

            deviceList = HandleDeviceConfig.GetHWUsagesListTreeAll(nVerbose)
            messageWeb = json.dumps(deviceList)
            
        if (realPath == "/Device/GetTypesList"): 
            # /Device/GetTypesList
            szSortBy = ""
            if (variablesList.get('sortBy')):
                szSortBy = variablesList['sortBy'][0]
            deviceList = HandleDeviceConfig.GetTypesList(szSortBy,nVerbose)
            messageWeb = json.dumps(deviceList)
            
        if (realPath == "/Device/GetHWTypesList"): 
            # /Device/GetTypesList
            szSortBy = ""
            if (variablesList.get('sortBy')):
                szSortBy = variablesList['sortBy'][0]
            deviceList = HandleDeviceConfig.GetHWTypesList(szSortBy,nVerbose)
            messageWeb = json.dumps(deviceList)

        if (realPath == "/Device/Read"): 
            #/Device/Read?devId=SOAN1
            szId=variablesList['devId'][0]
            
            
            szCommType = 'WIFI'
            state = control_devices.ReadUsageState(szCommType, szId, nVerbose)
            
            messageWeb = str(json.dumps(state))
                
        if (realPath == "/Device/Actuate"): 
            #/Device/Update?devId=SOAN1&State=2
            if (variablesList.get('devId')):
                szId=variablesList['devId'][0]
            if (variablesList.get('State')):    
                szState=variablesList['State'][0]
                nState=int(szState)
                
            szCommType = 'WIFI'

            state = control_devices.UpdateUsageState(szCommType, szId, nState, nVerbose)
            messageWeb = str(state)
            
        ##########################################
        # Notifications  (PUT con json)
        # 
        # /Device/Notify?devId=SOAN1
        # /Device/Notify?HWId=SOAN1
        
        if (realPath == "/Device/Config/ModifyHW"):
            #/Device/Notify?devId=SOAN1  
                
            messageWeb = "0"
            
        ###################################################
        # Funciones Paraguas
            
        if (realPath == "/Device/Config/ModifyHW"):
            #/Device/Config/DeleteHW?Address=192.168.2.167
                
            if (variablesList.get('Address')):    
                szAddress=variablesList['Address'][0]
                
                returnData = control_devices.UpdateHWFirmware(szAddress, variablesList, nVerbose)

                HandleDeviceConfig.UpdateDeviceHWDB(szAddress, variablesList, nVerbose)   # Podiamos haber mandado devIdNew como devID pero da igual
                
                # Aqui no se debería cambiar la IP
                messageWeb = "0"   # Puede devolver 200, 4xx, 5xx, -1, -2
                
            else:
                messageWeb = "-2"
                
                
        if (realPath == "/Device/Config/DeleteHW"):
            #/Device/Config/ModifyHW?Address=192.168.2.167&AddressNew=192.168.2.189&mbAddress=2&HWtype=Sonoff
                
            if (variablesList.get('Address')):    
                szAddress=variablesList['Address'][0]
                
                returnData = control_devices.DeleteFullFirmware(szAddress, nVerbose)

                HandleDeviceConfig.DeleteDeviceHWDB(szAddress, nVerbose)   # Podiamos haber mandado devIdNew como devID pero da igual
                
                # Aqui no se debería cambiar la IP
                messageWeb = "0"   # Puede devolver 200, 4xx, 5xx, -1, -2
                
            else:
                messageWeb = "-2"
                
                      
        if (realPath == "/Device/Config/AddModifyUsage"):
            #/Device/Config/AddModifyUsage?devId=TMP554&Address=192.168.2.167&devIdNew=SOAN1&devType=tLuz&pinInput1=4&pinInput2=5&pinOutput1=11&pinOutput2=13&Description=Teas%20Test     devID es obligatorio

            if (variablesList.get('devId')):
                szDevId=variablesList['devId'][0]
                
            if (variablesList.get('Address')):    
                szAddress=variablesList['Address'][0]
                
                # Desde REST no indicamos el usage (no se sabe).
                # El Device nos lo devuelve, y lo metemos como dato en VariableList. 
                # Lo del append es porque el dato es una lista en si mismo
                
                nUsage = control_devices.AddModifyUsageFirmware(szAddress, szDevId, variablesList, nVerbose)
                
                nUsageList = []
                nUsageList.append(nUsage)
                
                variablesList['nUsage']=nUsageList

                HandleDeviceConfig.AddUpdateUsageConfig(szDevId, variablesList, nVerbose)   # Podiamos haber mandado devIdNew como devID pero da igual
                
                # Aqui no se debería cambiar la IP
                messageWeb = "0"   # Puede devolver 200, 4xx, 5xx, -1, -2
                
            else:
                messageWeb = "-2"
                
                
        if (realPath == "/Device/Config/DeleteUsage"): 
            #/Device/Config/DeleteUsageFirmware?devId=TMP554                           devID es obligatorio
            
            if (variablesList.get('devId')):
                szId=variablesList['devId'][0]
                
            if (variablesList.get('Address')):    
                szAddress=variablesList['Address'][0]
                
                response = control_devices.DeleteUsageFirmware(szAddress, szId, nVerbose)
                response = HandleDeviceConfig.DeleteUsageDB(szId, nVerbose)
                messageWeb = "0" # str(response)
            else:
                messageWeb = "-2" 
         
        ###################################################
        # Funciones DB par HW       
            
        if (realPath == "/Device/Config/AddHWDB"): 
            
            # /Device/Config/AddHWDB?HWtype=Domo4ch&Address=192%2E168%2E2%2E135    v3

            if (variablesList.get('Address')):
                szAddress=variablesList['Address'][0]
            else:
                messageWeb = "-1"
                return (messageWeb) 
                
            Logfile.printError ('[Webserver] Subscribe HW device: '+szAddress)
                        
            nMBAddress = HandleDeviceConfig.AddDeviceHWDB(szAddress, variablesList, nVerbose)
                                 
            messageWeb = str(nMBAddress)
        
        if (realPath == "/Device/Config/ModifyHWDB"): 
            #/Device/Config/ModifyHWDB?Address=192.168.1.135&AddressNew=192.168.1.135&HWtype=Domo4ch&mbAddress=9    devID es obligatorio
            
            if (variablesList.get('Address')):
                szAddress=variablesList['Address'][0]
                                    
                # Aqui no se debería cambiar la IP
                response = HandleDeviceConfig.UpdateDeviceHWDB(szAddress, variablesList, nVerbose)
                messageWeb = str(response)
                
            else:
                messageWeb = "-2" 
               
        if (realPath == "/Device/Config/DeleteHWDB"): 
            #/Device/Config/DeleteHWDB?Address=192.168.1.165                              address es obligatorio
            
            if (variablesList.get('Address')):
                szAddress=variablesList['Address'][0]
                
                if (nVerbose > 0):
                    Logfile.printError ('[Webserver] Delete HW: ' + szAddress)
                response = HandleDeviceConfig.DeleteDeviceHWDB(szAddress, nVerbose)
                messageWeb = str(response)
            else:
                messageWeb = "-2"  
        
        ###################################################
        # Funciones DB par Usages       
                
                
        if (realPath == "/Device/Config/AddModifyUsageDB"): 
            #/Device/Config/ModifyUsageDB?devId=TMP554&devIdNew=SOAN1&State=2     devID es obligatorio
            
            if (variablesList.get('devId')):
                szDevId=variablesList['devId'][0]
                                    
                # Aqui no se debería cambiar la IP
                response = HandleDeviceConfig.AddUpdateUsageConfig(szDevId, variablesList, nVerbose)
                messageWeb = str(response)
                
            else:
                messageWeb = "-2" 
                
        if (realPath == "/Device/Config/DeleteUsageDB"): 
            #/Device/Config/DeleteUsageDB?devId=TMP554                              devID es obligatorio
            
            if (variablesList.get('devId')):
                szId=variablesList['devId'][0]
                
                if (nVerbose > 0):
                    Logfile.printError ('[Webserver] Delete: ' + szId)
                response = HandleDeviceConfig.DeleteUsageDB(szId, nVerbose)
                messageWeb = str(response)
                
            else:
                messageWeb = "-2" 
                
        ###################################################
        # Funciones Firmware       
                
        if (realPath == "/Device/Config/AddModifyUsageFirmware"): 
            #/Device/Config/AddModifyUsageFirmware?Address=192.168.2.167&devId=TMP554&devIdNew=SOAN1devType=tLuz&pinInput1=4&pinInput2=5&pinOutput1=11&pinOutput2=13&Description=Teas%20Test     devID es obligatorio
            
            if (variablesList.get('devId')):
                szId=variablesList['devId'][0]
                
            if (variablesList.get('Address')):    
                szAddress=variablesList['Address'][0]
                response = control_devices.AddModifyUsageFirmware(szAddress, szId, variablesList, nVerbose)
                # Response es el nUsage que hay que meter en DB
                messageWeb = str(response)   # Puede devolver 200, 4xx, 5xx, -1, -2
            else:
                messageWeb = "-2" 
                
        if (realPath == "/Device/Config/DeleteUsageFirmware"): 
            #/Device/Config/DeleteUsageFirmware?devId=TMP554                           devID es obligatorio
            
            if (variablesList.get('devId')):
                szId=variablesList['devId'][0]
                
            if (variablesList.get('Address')):    
                szAddress=variablesList['Address'][0]
                response = control_devices.DeleteUsageFirmware(szAddress, szId, nVerbose)
                messageWeb = "0" # str(response)
            else:
                messageWeb = "-2" 
        
        return (messageWeb)


    def timeronoff_loop (self, realPath, variablesList, nVerbose):
        # /TimerOnOff/Read?devId=SOJD1
        # /TimerOnOff/Setmode?devId=SOJD1&Mode=Prog
        
        messageWeb = "TimerOnOff Subcommand Command Found"
        
        if (realPath == "/TimerOnOff/Read"): 
    
            szDevId=variablesList['devId'][0]
            
            try:
                nState = ReadTimeOnOff.readTimerOnOff(szDevId,nVerbose)
            except:
                Logfile.printError ('[Webserver] Error leyendo Timer '+szDevId)
                messageWeb = "-2"
                return
                     
            messageWeb = str(nState)

        if (realPath == "/TimerOnOff/Setmode"): 
    
            szDevId=variablesList['devId'][0]
            szMode=variablesList['Mode'][0]
            
            if szMode != 'Man' and szMode != 'Prog':
                Logfile.printError ('[Webserver] Error setting Timer '+szDevId+' to '+szMode)
                messageWeb = "-2"
                return (messageWeb)
            
            try:
                ReadTimeOnOff.setTimerOnOffState(szDevId,szMode,nVerbose)
            except:
                Logfile.printError ('[Webserver] Error setting Timer '+szDevId+' to '+szMode)
                messageWeb = "-2"
                return (messageWeb)
                            
            if szMode == 'Man':
                messageWeb = "-1"
            if szMode == 'Prog':
                messageWeb = "0"
            
        
        return (messageWeb)
                

    def Status_Parse (self, realPath):
    
        dateToday = datetime.datetime.now()            
        filedateString=dateToday.strftime ("%Y%m%d")
        szFileName='LOGS/' + filedateString + '_mainlog'
        
        szFileNameCalefaccionProgram='CONFIG/Temp_Consigna'
        szFileNameTimers='CONFIG/TimerOnOff'
        szFileNameTimersAirzone='CONFIG/AirzoneTimer'
        
        if (realPath == "/Status") or (realPath == "/"):
            messageWeb = "<p style=\"font-size:20px;\">Config Files</p>"
            messageWeb += "<p></p>"
            messageWeb += "<p style=\"font-size:11px;\"><a href=\"/Status/Config/Calefaccion\">Programa Calefaccion</a></p>"
            messageWeb += "<p style=\"font-size:11px;\"><a href=\"/Status/Config/Devices\">Lista Dispositivos</a></p>"
            messageWeb += "<p style=\"font-size:11px;\"><a href=\"/Status/Config/Timers\">Timers Dispositivos</a></p>"
            messageWeb += "<p style=\"font-size:11px;\"><a href=\"/Status/Config/TimersAirzone\">Timers Airzone</a></p>"
            messageWeb += "<p></p>"
            messageWeb += "<p style=\"font-size:20px;\">Logs</p>"
            messageWeb += "<p></p>"
            messageWeb += "<p style=\"font-size:11px;\"><a href=\"/Status/Logs/Domotica\">LOGS Domotica General</a></p>"
            messageWeb += "<p style=\"font-size:11px;\"><a href=\"/Status/Logs/CalefaccionLite\">LOGS Calefaccion Resumen</a></p>"
            messageWeb += "<p style=\"font-size:11px;\"><a href=\"/Status/Logs/Calefaccion\">LOGS Calefaccion Todo</a></p>"
            messageWeb += "<p style=\"font-size:11px;\"><a href=\"/Status/Logs/Monitor\">LOGS Monitor Ping</a></p>"
            messageWeb += "<p style=\"font-size:11px;\"><a href=\"/Status/Logs/Persianas\">LOGS Persianas</a></p>"
            messageWeb += "<p style=\"font-size:11px;\"><a href=\"/Status/Logs/Timer\">LOGS Timers</a></p>"
            messageWeb += "<p style=\"font-size:11px;\"><a href=\"/Status/Logs/Monitor\">LOGS Monitor Ping</a></p>"
            messageWeb += "<p style=\"font-size:11px;\"><a href=\"/Status/Logs/WebServer\">LOGS Web Server</a></p>"
    
        if (realPath == "/Status/Logs/Domotica"):
            messageWeb = "<p>Logs de Domotica General</p>"
        
            with open(szFileName) as origin_file:
                for line in origin_file:
                    if (line.find("[Domotica]") > -1):
                        messageWeb += "<p style=\"font-size:11px;\">"+line.strip()+"</p>"
        
        if (realPath == "/Status/Logs/CalefaccionLite"):
            messageWeb = "<p>Logs de Calefaccion Resumen</p>"
        
            with open(szFileName) as origin_file:
                for line in origin_file:
                    if (line.find("[Calefaccion]") > -1) or (line.find("[GPIO_Caldera]") > -1):
                        messageWeb += "<p style=\"font-size:11px;\">"+line.strip()+"</p>"                
        
        if (realPath == "/Status/Logs/Calefaccion"):
            messageWeb = "<p>Logs de Calefaccion Completos</p>"
        
            with open(szFileName) as origin_file:
                for line in origin_file:
                    if (line.find("[Calefaccion]") > -1) or (line.find("[GPIO_Caldera]") > -1)  or (line.find("[Analysis]") > -1)  or (line.find("[Airzone]") > -1)  or (line.find("[AEMET]") > -1)  or (line.find("[ReadConsigna]") > -1):
                        messageWeb += "<p style=\"font-size:11px;\">"+line.strip()+"</p>" 
        
        if (realPath == "/Status/Logs/Persianas"):
            messageWeb = "<p>Logs de persianas</p>"
        
            with open(szFileName) as origin_file:
                for line in origin_file:
                    if (line.find("[GPIO]") > -1) or (line.find("Persianas") > -1):
                        messageWeb += "<p style=\"font-size:11px;\">"+line.strip()+"</p>"
                        
        if (realPath == "/Status/Logs/Timer"):
            messageWeb = "<p>Logs de Timers</p>"
        
            with open(szFileName) as origin_file:
                for line in origin_file:
                    if (line.find("[Timer]") > -1):
                        messageWeb += "<p style=\"font-size:11px;\">"+line.strip()+"</p>"
        
        if (realPath == "/Status/Logs/Monitor"):
            messageWeb = "<p>Logs de Monitor Pings</p>"
        
            with open(szFileName) as origin_file:
                for line in origin_file:
                    if (line.find("[MonitorPing]") > -1):
                        messageWeb += "<p style=\"font-size:11px;\">"+line.strip()+"</p>"
        
        if (realPath == "/Status/Logs/WebServer"):
            messageWeb = "<p>Logs de Monitor Pings</p>"
        
            with open(szFileName) as origin_file:
                for line in origin_file:
                    if (line.find("[Webserver]") > -1):
                        messageWeb += "<p style=\"font-size:11px;\">"+line.strip()+"</p>"   
    
        if (realPath == "/Status/Config/Calefaccion"):
            messageWeb = "<p>Programa Calefaccion</p>"
        
            with open(szFileNameCalefaccionProgram) as origin_file:
                for line in origin_file:
                    messageWeb += "<p style=\"font-size:11px;\">"+line.strip()+"</p>"
                    
        if (realPath == "/Status/Config/Devices"):
            messageWeb = "<p>Configuracion Dispositivos</p>"
            
            deviceList = HandleDeviceConfig.GetUsagesListAll("" ,1)
    
            for device in deviceList:
                messageWeb += "<p style=\"font-size:11px;\">"+str(device)+"</p>"
                    
        if (realPath == "/Status/Config/Timers"):
            messageWeb = "<p>Timers Dispositivos</p>"
        
            with open(szFileNameTimers) as origin_file:
                for line in origin_file:
                    messageWeb += "<p style=\"font-size:11px;\">"+line.strip()+"</p>"
        
        if (realPath == "/Status/Config/TimersAirzone"):
            messageWeb = "<p>Timers Airzone</p>"
        
            with open(szFileNameTimersAirzone) as origin_file:
                for line in origin_file:
                    messageWeb += "<p style=\"font-size:11px;\">"+line.strip()+"</p>"         
       
        return (messageWeb)
        

def webServerDomo():
    myServer = HTTPServer((hostName, hostPort), MyServer)

    Logfile.printError ('[Webserver] WebServer Starts....')
    
    try:
        myServer.serve_forever()
    except KeyboardInterrupt:
        pass
    
    myServer.server_close()
    Logfile.printError ('[Webserver] WebServer Stops....')
    
if __name__ == '__main__':

    webServerDomo()
