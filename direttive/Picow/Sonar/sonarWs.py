import network
import asyncio
import ubinascii
import hashlib
from machine import Pin, time_pulse_us
from wifi import init_wifi
import time
#import secrets

#init_wifi()

# ---------------------------------------------------------------------------
# Configurazione sonar HC-SR04
# ---------------------------------------------------------------------------
TRIG_PIN      = 3
ECHO_PIN      = 2
SONAR_INTERVAL = 0.1   # secondi tra una lettura e l'altra

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)


def read_distance():
    """Legge la distanza in cm dal sonar HC-SR04."""
    trig.low()
    time.sleep_us(2)
    trig.high()
    time.sleep_us(10)
    trig.low()
    duration = time_pulse_us(echo, 1, 30000)  # timeout 30 ms
    if duration < 0:
        return -1   # timeout / nessun ostacolo
    return round((duration / 2) / 29.1, 1)

# ---------------------------------------------------------------------------
# Connessione Wi-Fi
# ---------------------------------------------------------------------------
"""
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
    print("Connessione Wi-Fi in corso", end="")
    timeout = 15
    while not wlan.isconnected() and timeout > 0:
        print(".", end="")
        time.sleep(1)
        timeout -= 1
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print(f"\nConnesso! IP: {ip}")
        return ip
    raise RuntimeError("Impossibile connettersi al Wi-Fi")
"""

# ---------------------------------------------------------------------------
# Utilità WebSocket (RFC 6455 — frame text minimali)
# ---------------------------------------------------------------------------
WS_MAGIC = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

async def ws_handshake(reader, writer):
    """Esegue l'upgrade HTTP -> WebSocket. Restituisce True se riuscito."""
    await reader.readline()          # GET / HTTP/1.1
    key = None
    while True:
        line = await reader.readline()
        if line in (b"\r\n", b"\n", b""):
            break
        if b"Sec-WebSocket-Key" in line:
            key = line.split(b": ")[1].strip()
    if key is None:
        return False
    accept = ubinascii.b2a_base64(
        hashlib.sha1(key + WS_MAGIC).digest()
    ).strip()
    writer.write(
        b"HTTP/1.1 101 Switching Protocols\r\n"
        b"Upgrade: websocket\r\n"
        b"Connection: Upgrade\r\n"
        b"Sec-WebSocket-Accept: " + accept + b"\r\n\r\n"
    )
    await writer.drain()
    return True

def ws_send(writer, message):
    """Costruisce e accoda un frame WebSocket text (non mascherato)."""
    data = message.encode("utf-8")
    n = len(data)
    header = bytes([0x81, n]) if n < 126 else bytes([0x81, 126, n >> 8, n & 0xFF])
    writer.write(header + data)

# ---------------------------------------------------------------------------
# Gestione client WebSocket
# ---------------------------------------------------------------------------
clients = []

async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    print(f"Connection from {addr}")

    if not await ws_handshake(reader, writer):
        writer.close()
        return

    clients.append(writer)
    print(f"WebSocket OK: {addr}  — client attivi: {len(clients)}")

    try:
        while True:
            header = await reader.read(2)
            if not header or (header[0] & 0x0F) == 8:   # frame di chiusura
                break
    except Exception:
        pass
    finally:
        if writer in clients:
            clients.remove(writer)
        writer.close()
        print(f"Disconnesso: {addr}  — client attivi: {len(clients)}")

# ---------------------------------------------------------------------------
# Loop sonar: legge e fa broadcast a tutti i client connessi
# ---------------------------------------------------------------------------
async def sonar_loop():
    led = Pin("LED", Pin.OUT)
    while True:
        dist = read_distance()
        if dist >= 0 and clients:
            msg = str(dist)
            dead = []
            for w in clients:
                try:
                    ws_send(w, msg)
                    await w.drain()
                except Exception:
                    dead.append(w)
            for w in dead:
                clients.remove(w)
            led.toggle()
        await asyncio.sleep(SONAR_INTERVAL)

# ---------------------------------------------------------------------------
# Avvio
# ---------------------------------------------------------------------------
async def main():
    #ip = connect_wifi()
    #print(f"Server WebSocket ->  ws://{ip}:81/")
    init_wifi()
    server = await asyncio.start_server(handle_client, "0.0.0.0", 81)
    await asyncio.gather(
        server.wait_closed(),
        sonar_loop()
    )

asyncio.run(main())