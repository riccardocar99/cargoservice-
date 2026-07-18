import network
import time
import secretsLab
from umqtt_simple import MQTTClient

#############################################
# Attivare su PC LabWork26\griddisplay
#############################################
# ===== WIFI =====
SSID     = secretsLab.WIFI_SSID
PASSWORD = secretsLab.WIFI_PASSWORD

led      = machine.Pin("LED", machine.Pin.OUT)
 
# ===== MQTT =====
MQTT_BROKER = "192.168.1.132"   
MQTT_PORT   = 1883
CLIENT_ID   = "ff00"
TOPIC       = b"grid"

# ===== Messages =====
ledOn_ev    = "msg(cellstate,event,picow,none,cellstate(0,0,1),1)"
ledOff_ev   = "msg(cellstate,event,picow,none,cellstate(0,0,0),1)"

    
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    while not wlan.isconnected():
        time.sleep(1)
        print("Connessione WiFi...")
    
    print("Connesso:", wlan.ifconfig())


def connect_mqtt():
    client = MQTTClient(
        client_id = CLIENT_ID,
        server    = MQTT_BROKER,
        port      = MQTT_PORT,
        keepalive = 60
    )
    client.connect()
    print(f"Connesso al broker MQTT: {MQTT_BROKER}:{MQTT_PORT}")
    return client

 

# ===== MAIN =====
connect_wifi()
#client.connect()
client = connect_mqtt()
print("MQTT connesso")
 

while True:
    try:
        time.sleep(1.0)
        print("on")
        led.on()
        client.publish( TOPIC, ledOn_ev.encode() )
        time.sleep(1.0)
        print("off")
        led.off()
        client.publish( TOPIC, ledOff_ev.encode() )
    except KeyboardInterrupt as e:
        print("Programma interrotto manualmente")
        break
    except Exception as e:
        print("È successo qualcosa di imprevisto:", type(e).__name__, e)
        
        
    