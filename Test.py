import datetime
import time, os

import Logfile
import requests

    

def readTempSuelo (nVerbose):

    szRootUrl = 'http://192.168.2.135'
    szUriParams = '/ReadTemp'
    url = szRootUrl+szUriParams
    s=requests.session()
    
    nHowManyTries=0
    
    Temp_Suelo=0
    
    while Temp_Suelo <= 1 and nHowManyTries < 6:
            if nHowManyTries > 0:
                Logfile.printError ('[Calefaccion] Temperatura Suelo Esperando 10 segundos para otro intento')
                time.sleep(10)
            
            nHowManyTries+=1
            
            try:
                response = s.get(url,stream=False, timeout=15)
            except requests.exceptions.RequestException as e:
                Logfile.printError ('[Calefaccion] Error conectando a OnOff Temp Suelo')
                pass
                
            Temp_Suelo = response.json()[0]
                 
    s.close()
    
    if nVerbose > 0:
        Logfile.printError ('[Calefaccion] Temperatura suelo: '+str(Temp_Suelo))
    
    return (Temp_Suelo)

               
        
def main():
    Temp_Suelo =0
    nVerbose =1
    
    Temp_Suelo = readTempSuelo (nVerbose)    
    print (str(Temp_Suelo))
    
if __name__ == "__main__":
    main()
    
    
    # Cron cada 15 min
    # Comprobar que cada temp es la de cada habitacion
    # fecha->nombre fichero. Cada dia uno
    # timestamp, t1, t2, t3, t4, t5, t6
    # If Airzone.error repetir ultimas T
