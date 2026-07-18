import time
import sys
import threading
try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("Error: paho-mqtt library not found. Please install it using: pip install paho-mqtt")
    sys.exit(1)

MQTT_BROKER = sys.argv[1] if len(sys.argv) > 1 else "localhost"
MQTT_PORT = 1883

led_state = "off"
current_distance = 15.0  # Default idle state (no container, no failure)

def on_connect(client, userdata, flags, rc):
    print(f"Emulator | Connected to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT} (Result code {rc})")
    client.subscribe("cargoservice/pico/led")
    print("Emulator | Subscribed to: cargoservice/pico/led")

def on_message(client, userdata, msg):
    global led_state
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    if topic == "cargoservice/pico/led":
        led_state = payload
        print(f"\n[LED UPDATE] LED is now: {led_state.upper()}")

def distance_publisher_loop(client):
    global current_distance
    while True:
        try:
            # Continuously publish the current distance every 500ms to allow
            # the QAK Sonar actor to correctly measure presence/failure duration.
            client.publish("cargoservice/pico/sonar", f"{current_distance:.1f}")
            time.sleep(0.5)
        except Exception as e:
            time.sleep(1)

def console_input_loop(client):
    global current_distance
    print("\n=======================================================")
    print("Pico W Emulator - Console Control")
    print("Enter a distance (in cm) to publish to cargoservice:")
    print("  - Enter < 10 (e.g., 5) to simulate container presence at IOPort")
    print("  - Enter > 20 (e.g., 30) to simulate Sonar failure (Out of Service)")
    print("  - Enter between 10 and 20 (e.g., 15) to simulate normal idle state")
    print("=======================================================\n")
    
    while True:
        try:
            val = input("Enter distance (cm) -> ").strip()
            if not val:
                continue
            d = float(val)
            current_distance = d
            print(f"-> Selected distance: {d} cm (now streaming to MQTT...)")
        except ValueError:
            print("Invalid number. Please enter a valid distance.")
        except KeyboardInterrupt:
            break

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"Error: Could not connect to MQTT Broker: {e}")
        print("Please make sure your MQTT broker (e.g. Mosquitto) is running locally on port 1883.")
        sys.exit(1)

    # Start MQTT loop in a background thread
    mqtt_thread = threading.Thread(target=client.loop_forever)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    # Start continuous distance publisher in a background thread
    pub_thread = threading.Thread(target=distance_publisher_loop, args=(client,))
    pub_thread.daemon = True
    pub_thread.start()

    # Run console input loop in main thread
    try:
        console_input_loop(client)
    except KeyboardInterrupt:
        print("\nEmulator stopped.")

if __name__ == "__main__":
    main()
