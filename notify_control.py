import requests
import Logfile

import ast



############################################################################################
############################################################################################
#
# Handle Devices HW Config
#
############################################################################################
############################################################################################

def NotifyControl(szAddress, variablesDict, nVerbose): 
    
    # http://192.168.2.135/UpdateHW?AddressNew=192.168.2.136&mbAddress=34&HWtype=Sonoff
    
    if (variablesDict.get('devId')):    
        szdevId = variablesDict['devId'][0]
    if (variablesDict.get('HWId')):    
        szdevId = variablesDict['HWId'][0]
    if (variablesDict.get('Mensaje')):    
        szMensaje = variablesDict['Mensaje'][0]
        
    Logfile.printError ('[Event] :' + szdevId + ' - ' + szMensaje)
    
               
    return (returndata)	
    
 
                
def main():
    #ReadUsageStateWiFi('Luz_JardinD_1', 'NULL', 'NULL', 1)
    pass 
       
if __name__ == "__main__":
    main()
