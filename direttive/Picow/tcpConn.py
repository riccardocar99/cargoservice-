import network
import socket
import time

# --- CONFIGURAZIONE ---
ssid     = ' '
password = ' '

SERVER_IP = "192.168.1.132" # Metti l'IP del tuo PC qui
PORT      = 8010

# 1. Connessione al Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

print("Connessione al Wi-Fi in corso...")
while not wlan.isconnected():
    time.sleep(1)
    print(".")

print("Connesso! IP del Pico:", wlan.ifconfig()[0])

# 2. Creazione del Socket TCP
try:
    # Creiamo il "tubo" per la comunicazione
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Ci connettiamo al PC
    print(f"Tentativo di connessione a {SERVER_IP}:{PORT}...")
    s.connect((SERVER_IP, PORT))
    
    # Inviamo il messaggio
    messaggio = "msg(msg2,dispatch,sender,receiver,msg2(picow),0)"
    s.send(messaggio.encode('utf-8'))
    print("Messaggio inviato con successo!")

    time.sleep(1)

    # Chiudiamo la connessione
    s.close()
    print("Connessione chiusa.")

except Exception as e:
    print("Errore durante la connessione:", e)