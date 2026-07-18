from machine import Pin, time_pulse_us
import time

# Pin
TRIG = Pin(3, Pin.OUT)
ECHO = Pin(2, Pin.IN)

def misura_distanza():
    # Reset trigger
    TRIG.low()
    time.sleep_us(2)
    
    # Impulso 10us
    TRIG.high()
    time.sleep_us(10)
    TRIG.low()
    
    # Legge durata impulso echo
    durata = time_pulse_us(ECHO, 1, 30000)  # timeout 30ms
    
    if durata < 0:
        return None
    
    # Conversione in cm
    distanza = (durata / 2) / 29.1
    return distanza

# Loop principale
while True:
    d = misura_distanza()
    if d is not None:
        print("Distanza: %.2f cm" % d)
    else:
        print("Errore misura")
    
    time.sleep(1)