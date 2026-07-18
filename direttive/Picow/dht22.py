from machine import Pin
import dht

# ultrasonic sensor pins and functions
dht22 = dht.DHT22(Pin(16))

try:
    
    dht22.measure()             #per aggiornare i dati interni
    temp = dht22.temperature()  # Restituisce i gradi Celsius (float)
    hum  = dht22.humidity()     # Restituisce l'umidità relativa (float)

    print("Temperatura: {}°C, Umidità: {}%".format(temp, hum))
except OSError as e:
    print("Errore di lettura dal sensore:", e)