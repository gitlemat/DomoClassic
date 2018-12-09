import multiprocessing
import time

# bar
def bar():
    for i in range(100):
        print ("Tick"+str(i))
        time.sleep(1)


def control ():
    p = multiprocessing.Process(target=bar)

    p.start()
    
    # Wait for 10 seconds or until process finishes
    p.join(10)
    
    # If thread is still active
    if p.is_alive():
        print ("running... let's kill it...")
    
        # Terminate
        p.terminate()
        p.join()

if __name__ == '__main__':
    # Start bar as a process
    
    for i in range(20):
        time.sleep(3)
        p = multiprocessing.Process(target=bar)

        p.start()
        
        # Wait for 10 seconds or until process finishes
        p.join(3)
        
        # If thread is still active
        if p.is_alive():
            print ("running... let's kill it...")
        
            # Terminate
            p.terminate()
            p.join()
    