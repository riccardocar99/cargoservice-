import machine
import time
import network
import uasyncio as asyncio
from umqtt_simple import MQTTClient

# Try importing secrets, fallback to defaults if not found
try:
    import secrets
    WIFI_SSID = secrets.WIFI_SSID
    WIFI_PASSWORD = secrets.WIFI_PASSWORD
    MQTT_BROKER = secrets.MQTT_BROKER
except Exception:
    WIFI_SSID = "Your_WiFi_SSID"
    WIFI_PASSWORD = "Your_WiFi_Password"
    MQTT_BROKER = "192.168.1.100" # Replace with your PC IP where MQTT Broker runs

# Pin Configuration (standard BCM equivalent for Pico W)
# TRIG: GP17, ECHO: GP27, LED: GP25 (or 'LED' for Pico W onboard LED)
TRIG_PIN = 17
ECHO_PIN = 27
LED_PIN = "LED" # Use 'LED' for onboard Pico W LED, or a GP number (e.g. 25) for external LED

# Global variables for LED control
led = machine.Pin(LED_PIN, machine.Pin.OUT)
led_mode = "off" # "off", "on", "blink"

# Setup Sonar Pins
trig = machine.Pin(TRIG_PIN, machine.Pin.OUT)
echo = machine.Pin(ECHO_PIN, machine.Pin.IN)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("WiFi | Connecting to", WIFI_SSID)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        # Wait up to 10 seconds
        for _ in range(20):
            if wlan.isconnected():
                break
            time.sleep(0.5)
    if wlan.isconnected():
        print("WiFi | Connected! IP:", wlan.ifconfig()[0])
    else:
        print("WiFi | Connection failed")

def read_sonar():
    # Trigger pulse
    trig.low()
    time.sleep_us(2)
    trig.high()
    time.sleep_us(10)
    trig.low()

    # Wait for echo to start
    pulse_start = 0
    pulse_end = 0
    timeout = 20000 # 20ms timeout
    start_time = time.ticks_us()
    
    while echo.value() == 0:
        pulse_start = time.ticks_us()
        if time.ticks_diff(pulse_start, start_time) > timeout:
            return 999.0 # Timeout

    while echo.value() == 1:
        pulse_end = time.ticks_us()
        if time.ticks_diff(pulse_end, start_time) > timeout:
            return 999.0 # Timeout

    pulse_duration = time.ticks_diff(pulse_end, pulse_start)
    # Distance in cm = (duration * speed of sound (34300 cm/s)) / 2
    distance = (pulse_duration * 0.0343) / 2
    return round(distance, 1)

# MQTT callback to receive LED state updates
def mqtt_callback(topic, msg):
    global led_mode
    topic_str = topic.decode('utf-8')
    msg_str = msg.decode('utf-8')
    print("MQTT | Received topic:", topic_str, "msg:", msg_str)
    
    if topic_str == "cargoservice/pico/led":
        if msg_str in ["off", "on", "blink"]:
            led_mode = msg_str

# Async loop to handle Led blinking/on/off without blocking
async def led_control_loop():
    global led_mode
    while True:
        if led_mode == "off":
            led.off()
            await asyncio.sleep(0.1)
        elif led_mode == "on":
            led.on()
            await asyncio.sleep(0.1)
        elif led_mode == "blink":
            led.on()
            await asyncio.sleep(0.25)
            led.off()
            await asyncio.sleep(0.25)

# Async loop to periodically publish Sonar distance to MQTT
async def sonar_mqtt_loop(client):
    while True:
        try:
            d = read_sonar()
            client.publish("cargoservice/pico/sonar", str(d))
            print("MQTT | Published distance:", d, "cm")
        except Exception as e:
            print("Sonar Loop | Error:", e)
        await asyncio.sleep(0.25) # Publish 4 times per second

# Async loop to check for incoming MQTT messages
async def mqtt_check_loop(client):
    while True:
        try:
            client.check_msg()
        except Exception as e:
            print("MQTT Check | Error:", e)
        await asyncio.sleep(0.1)

async def main():
    connect_wifi()
    
    # Setup MQTT Client
    client = MQTTClient("pico_client", MQTT_BROKER)
    client.set_callback(mqtt_callback)
    
    try:
        client.connect()
        client.subscribe("cargoservice/pico/led")
        print("MQTT | Connected & Subscribed to cargoservice/pico/led")
    except Exception as e:
        print("MQTT | Initial connection failed:", e)

    # Launch concurrent async loops
    await asyncio.gather(
        led_control_loop(),
        sonar_mqtt_loop(client),
        mqtt_check_loop(client)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program stopped")
