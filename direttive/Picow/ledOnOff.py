import machine
import time
#RPI_PICO_W-20260406-v1.28.0.uf2
led = machine.Pin("LED", machine.Pin.OUT) # Nota: "LED" funziona solo su Pico W

def ledOnOff():
    #while True:
    for _ in range(7): 
        led.toggle()
        time.sleep(0.3)
    led.off()

print("ledonoff")
ledOnOff()
    
