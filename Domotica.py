import threading
import multiprocessing
import datetime
import time
import Calefaccion2
import MonitorPing
import Timer
import TimerAirzone
import Logfile
import webServer


def AirzoneTimer_loop(): 

    # Cada 15 min mira los timers de airzone (para el aire)
    
    while True:
        try:
            TimerAirzone.TimerAirzone(3)
        except:
            Logfile.printError ('[Domotica] Error en Airzone Timer')
            pass
    
        time.sleep (900)
        
def Timer_loop(): 

    # Cada 15 min mira los timers
    
    while True:
        try:
            Timer.TimerDispositivos(1)
        except:
            Logfile.printError ('[Domotica] Error en Timer')
            pass
    
        time.sleep (900)
             
def Monitor_loop(): 

    # Cada 5 min hace ping a los wemos
    # Si no responden pone rojo
    
    while True:
        try:
            MonitorPing.MonitorPing(1)
        except:
            Logfile.printError ('[Domotica] Error en Ping')
            pass
    
        time.sleep (305)  

def llamadaCalefaccion():
    try:
        Calefaccion2.Calefaccion_control(1)
    except:
        Logfile.printError ('[Domotica] Error en Calefaccion')
        pass
            
def Calefaccion_loop():
    
    while True:        
            
        # Esta parte es para que se ejecute cada hora 05, 20, 35 y 50 mins
        
        dateToday = datetime.datetime.now()
        szMinutenow=dateToday.strftime ("%M")
        minutenow=int(szMinutenow)
        if (minutenow >=5 and minutenow < 20):
            minutewait=20-minutenow
            
        if (minutenow >=20 and minutenow < 35):
            minutewait=35-minutenow
        
        if (minutenow >=35 and minutenow < 50):
            minutewait=50-minutenow
        
        if (minutenow >=50 and minutenow < 60):
            minutewait=65-minutenow
            
        if (minutenow < 5):
            minutewait=5-minutenow
            
        szMensaje='[Domotica] Proximo ciclo calefaccion en ' + str(minutewait) + ' minutos'
            
        Logfile.printError (szMensaje)
        time.sleep (minutewait*60)
        
        # Ahora se ejecuta
        
        p = multiprocessing.Process(target=llamadaCalefaccion())

        p.start()
        
        # Wait for 10 minutes or until process finishes
        p.join(600)
        Logfile.printError ('[Domotica] Proceso Calefaccion finalizado o timeout..')
        
        # If thread is still active
        if p.is_alive():
            Logfile.printError ('[Domotica] Calefaccion parece que se ha quedado bloqueado. Killin it...')
        
            # Terminate
            p.terminate()
            p.join()
        
def webServerDomo_loop():

    webServer.webServerDomo()
    
        
def main():

    t_calefaccion = threading.Thread(name='calefaccion', target=Calefaccion_loop)
    t_monitor = threading.Thread(name='monitor', target=Monitor_loop)
    t_timer = threading.Thread(name='timer', target=Timer_loop)
    t_timerAirzone = threading.Thread(name='timerAirzone', target=AirzoneTimer_loop)
    t_webServerDomo = threading.Thread(name='webServerDomo', target=webServerDomo_loop)


    t_calefaccion.start();
    t_monitor.start();
    t_timer.start();
    t_timerAirzone.start();
    t_webServerDomo.start();
    
if __name__ == "__main__":
    main()
    
    
    # Cron cada 15 min
    # Comprobar que cada temp es la de cada habitacion
    # fecha->nombre fichero. Cada dia uno
    # timestamp, t1, t2, t3, t4, t5, t6
    # If Airzone.error repetir ultimas T
