"""
mqtt_firefly.py  –  MicroPython / Pico W
Sottoscrive la topic MQTT "ff_0_0" e accende il LED onboard
quando il payload ricevuto vale "1".

Dipendenze: libreria umqtt.simple (inclusa in MicroPython standard)
"""

import time
from machine import Pin
import network
import time
import secretsLab
from umqtt_simple import MQTTClient

# ── Configurazione ────────────────────────────────────────────────────────────

WIFI_SSID     = secretsLab.WIFI_SSID
WIFI_PASSWORD = secretsLab.WIFI_PASSWORD

MQTT_BROKER   = "192.168.1.132"   # IP del broker (es. il pc che esegue Mosquitto)
MQTT_PORT     = 1883
MQTT_CLIENT_ID= "picow"
MQTT_TOPIC    = b"ff_0_0"       # bytes, non str

# ── LED onboard del Pico W ────────────────────────────────────────────────────
# Sul Pico W il LED è collegato al chip CYW43 tramite "LED" o Pin("LED")
led = Pin("LED", Pin.OUT)

# ── Connessione Wi-Fi ─────────────────────────────────────────────────────────

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Connessione Wi-Fi in corso", end="")
    for _ in range(20):                        # timeout ~10 s
        if wlan.isconnected():
            break
        time.sleep(0.5)
        print(".", end="")
    if not wlan.isconnected():
        raise RuntimeError("Wi-Fi: connessione fallita")
    print("\nConnesso –", wlan.ifconfig())

# ── Callback MQTT ─────────────────────────────────────────────────────────────

def on_message(topic, msg):
    """Chiamata dal client ogni volta che arriva un messaggio sulla topic."""
    print(f"Topic: {topic}  Payload: {msg}")
    if msg == b"1":
        led.on()
        print("LED ON")
    elif msg == b"0":
        led.off()
        print("LED OFF")
    # altri valori vengono ignorati

def connect_mqtt():
    client = MQTTClient(
        client_id = MQTT_CLIENT_ID,
        server    = MQTT_BROKER,
        port      = MQTT_PORT,
        keepalive = 60
    )
    client.connect()
    client.set_callback(on_message)
    print(f"Connesso al broker MQTT: {MQTT_BROKER}:{MQTT_PORT}")
    return client

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    connect_wifi()
    
    client = connect_mqtt()
    client.subscribe(MQTT_TOPIC.decode())
    print(f"Sottoscritto a '{MQTT_TOPIC.decode()}'  –  in attesa di messaggi...")

    try:
        while True:
            # check_msg() è non-bloccante: restituisce subito se non ci sono msg
            #client.check_msg()
            client.wait_msg()
            time.sleep_ms(100)
    except KeyboardInterrupt:
        print("Interruzione utente")
    finally:
        led.off()
        client.disconnect()
        print("Disconnesso.")

main()