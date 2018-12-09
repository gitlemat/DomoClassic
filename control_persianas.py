import gpio_api
import os, sys, getopt, time
import Logfile
import threading


def persiana_control(szPersiana, szNivel, szVerbose):

    if szPersiana== '0':
        #persiana('1', szNivel, szVerbose)
        #persiana('2', szNivel, szVerbose)
        #persiana('3', szNivel, szVerbose)
        t_persianas1 = threading.Thread(name='persianas', target=persiana, args=('1', szNivel, szVerbose,))
        t_persianas2 = threading.Thread(name='persianas', target=persiana, args=('2', szNivel, szVerbose,))
        t_persianas3 = threading.Thread(name='persianas', target=persiana, args=('3', szNivel, szVerbose,))
        t_persianas1.start()
        t_persianas2.start()
        t_persianas3.start()
    else:
        persiana(szPersiana, szNivel, szVerbose)


def persiana(szPersiana, szNivel, szVerbose):
    pin_base=35
    pin=35
    ntime=1
    nVerbose=int(szVerbose)

    Logfile.printError ('[GPIO_Persianas] Persiana: '+szPersiana)
    
    if szPersiana == '1':
        pin_base=32
    if szPersiana == '2':
        pin_base=35
    if szPersiana == '3':
        pin_base=37   

                
    if szNivel=='1':
        pin=pin_base
        pin_contrario=pin_base+1
        ntime=42
    if szNivel=='2':
        pin=pin_base
        pin_contrario=pin_base+1
        ntime=33
    if szNivel=='3':
        pin=pin_base+1
        pin_contrario=pin_base
        ntime=33
    if szNivel=='4':
        pin=pin_base+1
        pin_contrario=pin_base
        ntime=42
        
    if szNivel=='0':
        gpio_api.gpio_control(pin_base, 0, str(0), nVerbose)
        gpio_api.gpio_control(pin_base+1, 0, str(0), nVerbose)
    else:
        state=gpio_api.gpio_control(pin, 3, str(0), nVerbose)
        if state == 1:                 # Si ya está en movimiento, no tocar
            return()
            
        state_contrario=gpio_api.gpio_control(pin_contrario, 3, str(0), nVerbose)
        if state_contrario == 1:             # Si el contrario está en marcha, se para, sleep (1) y se pone en marcha
            gpio_api.gpio_control(pin_contrario, 0, str(0), nVerbose) #Primero dejamos a 0 el relé del movimiento contrario
            time.sleep(1)
        gpio_api.gpio_control(pin, 2, str(ntime), nVerbose)

if __name__ == "__main__":
    persiana_control(sys.argv[1], sys.argv[2], sys.argv[3])
    
    # 32: Persianas 1 Up
    # 33: Persianas 1 Down
    # 35: Persianas 2 Up
    # 36: Persianas 2 Down
    # 37: Persianas 3 Up
    # 38: Persianas 3 Down
