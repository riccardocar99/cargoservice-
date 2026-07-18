import network
import time
from umqtt_simple import MQTTClient
from machine import Pin, ADC
import ujson
import secretsLab

# ---------------------------------------------------------------------------
# Configurazione Wi-Fi
# ---------------------------------------------------------------------------
WIFI_SSID     = secretsLab.WIFI_SSID
WIFI_PASSWORD = secretsLab.WIFI_PASSWORD

# ---------------------------------------------------------------------------
# Configurazione MQTT
# ---------------------------------------------------------------------------
MQTT_BROKER   = "192.168.1.132"   # IP del broker locale nella tua rete
MQTT_PORT     = 1883
MQTT_CLIENT   = "pico_w_sensor"
MQTT_TOPIC    = b"sensor/temperature"
MQTT_INTERVAL = 5                  # secondi tra una pubblicazione e l'altra

# ---------------------------------------------------------------------------
# Sensore: lettura temperatura interna del chip RP2040
# (sostituisci con il tuo sensore se necessario)
# ---------------------------------------------------------------------------
sensor_temp = ADC(4)              # sensore interno al Pico W
CONVERSION_FACTOR = 3.3 / 65535

def read_temperature():
    """Legge la temperatura interna del RP2040 in gradi Celsius."""
    raw = sensor_temp.read_u16() * CONVERSION_FACTOR
    temperature = 27 - (raw - 0.706) / 0.001721
    return round(temperature, 2)

# ---------------------------------------------------------------------------
# Connessione Wi-Fi
# ---------------------------------------------------------------------------
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Connessione Wi-Fi in corso", end="")
    timeout = 15
    while not wlan.isconnected() and timeout > 0:
        print(".", end="")
        time.sleep(1)
        timeout -= 1
    if wlan.isconnected():
        print(f"\nConnesso! IP: {wlan.ifconfig()[0]}")
    else:
        raise RuntimeError("Impossibile connettersi al Wi-Fi")
    return wlan

# ---------------------------------------------------------------------------
# Connessione MQTT
# ---------------------------------------------------------------------------
def connect_mqtt():
    client = MQTTClient(
        client_id = MQTT_CLIENT,
        server    = MQTT_BROKER,
        port      = MQTT_PORT,
        keepalive = 60
    )
    client.connect()
    print(f"Connesso al broker MQTT: {MQTT_BROKER}:{MQTT_PORT}")
    return client

# ---------------------------------------------------------------------------
# Loop principale
# ---------------------------------------------------------------------------
def main():
    led = Pin("LED", Pin.OUT)     # LED verde sul Pico W

    wlan   = connect_wifi()
    client = connect_mqtt()

    print(f"Pubblicazione su topic '{MQTT_TOPIC.decode()}' ogni {MQTT_INTERVAL}s\n")

    while True:
        try:
            # Riconnessione automatica se il Wi-Fi cade
            if not wlan.isconnected():
                print("Wi-Fi perso, riconnessione...")
                wlan = connect_wifi()
                client = connect_mqtt()

            # Lettura sensore e costruzione payload JSON
            temp = read_temperature()
            payload = ujson.dumps({
                "device":      MQTT_CLIENT,
                "temperature": temp,
                "unit":        "C",
                "timestamp":   time.time()
            })

            # Pubblicazione
            client.publish(MQTT_TOPIC, payload)
            print(f"Pubblicato: {payload} on {MQTT_TOPIC.decode()}")

            # Lampeggio LED per feedback visivo
            led.on()
            time.sleep(0.1)
            led.off()

        except OSError as e:
            print(f"Errore di rete: {e} — riprovo tra 5s")
            time.sleep(5)
            try:
                client = connect_mqtt()
            except Exception:
                pass

        time.sleep(MQTT_INTERVAL)

main()