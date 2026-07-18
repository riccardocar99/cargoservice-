from machine import Pin, time_pulse_us
import time

# Configurazione pin
TRIG = Pin(0, Pin.OUT)               # Invertito (GP0)
ECHO = Pin(2, Pin.IN, Pin.PULL_DOWN)  # Invertito (GP2)

print("--- AVVIO TEST DI DEBUG SONAR ---")

while True:
    # Impulso di trigger
    TRIG.low()
    time.sleep_us(2)
    TRIG.high()
    time.sleep_us(10)
    TRIG.low()
    
    # Misura durata
    durata = time_pulse_us(ECHO, 1, 30000)
    
    # Stampa dettagliata del codice di errore
    print("DEBUG | Durata grezza: %d" % durata)
    
    if durata > 0:
        d = (durata / 2) / 29.1
        print("➔ Distanza calcolata: %.2f cm" % d)
    elif durata == -2:
        print("➔ ERRORE: Il pin ECHO non è mai andato a 1 (Timeout avvio impulso). Verifica il filo di TRIG o alimentazione.")
    elif durata == -1:
        print("➔ ERRORE: Il pin ECHO è andato a 1 ma non è mai tornato a 0 (Timeout fine impulso). Possibile corto o tensione errata.")
    else:
        print("➔ ERRORE generico di misura.")
        
    time.sleep(0.5)