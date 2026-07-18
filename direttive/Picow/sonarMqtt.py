from machine import Pin, time_pulse_us
import network
import time
import secretsLab
from umqtt_simple import MQTTClient

#############################################
# Attivare su PC qakdemo26\src\demomqttt.qak
#############################################
# ===== WIFI =====
SSID     = secretsLab.WIFI_SSID
PASSWORD = secretsLab.WIFI_PASSWORD
led      = machine.Pin("LED", machine.Pin.OUT)

def ledOnOff(N,DT):
    #while True:
    for _ in range(N): 
        led.toggle()
        time.sleep(DT)
    led.off()
    
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    while not wlan.isconnected():
        time.sleep(1)
        print("Connessione WiFi...")
    
    print("Connesso:", wlan.ifconfig())

# ===== MQTT =====
MQTT_BROKER = "192.168.1.132"   
MQTT_PORT   = 1883
CLIENT_ID   = "picosonar"
TOPIC       = b"mqttdemotopic"


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

##client = MQTTClient(CLIENT_ID, MQTT_BROKER)

# ===== SONAR =====
TRIG = Pin(3, Pin.OUT)
ECHO = Pin(2, Pin.IN)

def misura_distanza():
    TRIG.low()
    time.sleep_us(2)
    
    TRIG.high()
    time.sleep_us(10)
    TRIG.low()
    
    durata = time_pulse_us(ECHO, 1, 30000)
    
    if durata < 0:
        return None
    
    distanza = (durata / 2) / 29.1
    return distanza

# ===== MAIN =====
connect_wifi()
#client.connect()
client = connect_mqtt()
print("MQTT connesso")
ledOnOff(5,0.3)

while True:
    try:
        d = misura_distanza()
        
        if d is not None:
            #msg = "event(distance, sonar, %.2f)" % d
            d_int = round(d)
            #value = "sonardata(%.2f)" % d
            value  = "sonardata(%d)" % d_int
            print("Distance=", value)
            msg = "msg(sonardata,event,picow,none,"+value+",0)"
            print("Invio:", msg)
            client.publish(TOPIC, msg.encode() )
        else:
            print("Errore misura")
        
        time.sleep(1)
    
    except KeyboardInterrupt as e:
        print("Programma interrotto manualmente")
        break
    except Exception as e:
        print("È successo qualcosa di imprevisto:", type(e).__name__, e)
        
        
    