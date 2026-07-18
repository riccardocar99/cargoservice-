import network
import socket
import time
from secretsLab2 import secrets

# --- CONFIGURAZIONE WIFI ---
SSID     = secrets.ssid
PASSWORD = secrets.pw
PORT     = 8012
led      = machine.Pin("LED", machine.Pin.OUT)

def ledOnOff(N,DT):
    #while True:
    for _ in range(N): 
        led.toggle()
        time.sleep(DT)
    led.off()
    
# 1. Connessione al Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

print("Connessione al Wi-Fi...")
while not wlan.isconnected():
    time.sleep(1)
    print(".")

ip_pico = wlan.ifconfig()[0]
print(f"Connesso! Indirizzo IP del PicoW: {ip_pico}")

ledOnOff(5,0.3)

# 2. Configurazione Server TCP
# Creiamo il socket (AF_INET = IPv4, SOCK_STREAM = TCP)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Leghiamo il socket all'indirizzo IP e alla porta 8012
# Usiamo '' per indicare che deve ascoltare su tutte le interfacce
s.bind(('', PORT))

# Mettiamo il server in ascolto (massimo 1 connessione in coda)
s.listen(1)
print(f"Server in ascolto sulla porta {PORT}...")

while True:
    try:
        # Il programma si ferma qui finché qualcuno non si connette
        client, addr = s.accept()
        print(f"Connessione ricevuta da: {addr}")
        
        # Riceviamo i dati inviati dal PC (max 1024 bytes)
        request = client.recv(1024).decode('utf-8')
        print(f"Messaggio ricevuto: {request}")
        
        # Rispondiamo al client
        risposta = "Messaggio ricevuto, grazie PC!\n"
        client.send(risposta.encode('utf-8'))
        
        ledOnOff(3,0.8)
        
        # Chiudiamo la sessione con questo client
        client.close()
        
    except Exception as e:
        print("Errore durante la gestione della connessione:", e)
        client.close()