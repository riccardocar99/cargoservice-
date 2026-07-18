"""
tcp_client.py – MicroPython TCP client sulla porta 8010
Testato su ESP8266 / ESP32 con MicroPython >= 1.19
"""
#################################################
# Attivare su PC qakdemo26\src\demorequest.qak
#################################################
import network
import socket
import time
import secretsLab

# ─────────────────────────────────────────
#  Configurazione
# ─────────────────────────────────────────
WIFI_SSID     = secretsLab.WIFI_SSID
WIFI_PASSWORD = secretsLab.WIFI_PASSWORD

REMOTE_HOST = "192.168.1.132"   # IP del computer remoto
REMOTE_PORT = 8010

TIMEOUT_SEC = 10                # timeout socket in secondi
RECV_BUFFER = 1024              # dimensione buffer di ricezione


# ─────────────────────────────────────────
#  Connessione Wi-Fi
# ─────────────────────────────────────────
def connect_wifi(ssid: str, password: str) -> network.WLAN:
    """
    Connette il dispositivo alla rete Wi-Fi.
    Restituisce l'oggetto WLAN già connesso.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print(f"[WiFi] Connessione a '{ssid}' …")
        wlan.connect(ssid, password)

        deadline = time.time() + 20          # attesa massima 20 s
        while not wlan.isconnected():
            if time.time() > deadline:
                raise OSError("[WiFi] Timeout: impossibile connettersi.")
            time.sleep(0.5)

    ip = wlan.ifconfig()[0]
    print(f"[WiFi] Connesso – IP locale: {ip}")
    return wlan


# ─────────────────────────────────────────
#  Gestione connessione TCP
# ─────────────────────────────────────────
class TCPClient:
    """
    Client TCP semplice per MicroPython.

    Uso:
        client = TCPClient("192.168.1.32", 8010)
        client.connect()
        client.send("ciao server")
        risposta = client.receive()
        client.close()
    """

    def __init__(self, host: str, port: int, timeout: int = TIMEOUT_SEC):
        self.host    = host
        self.port    = port
        self.timeout = timeout
        self._sock   = None

    # ── connessione ──────────────────────
    def connect(self) -> None:
        """
        Apre la connessione TCP verso host:port.
        Solleva OSError in caso di errore.
        """
        addr = socket.getaddrinfo(self.host, self.port)[0][-1]
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(self.timeout)
        self._sock.connect(addr)
        print(f"[TCP] Connesso a {self.host}:{self.port}")

    # ── invio ────────────────────────────
    def send(self, messaggio: str, encoding: str = "utf-8") -> int:
        """
        Invia `messaggio` (stringa) al server.
        Restituisce il numero di byte effettivamente inviati.
        Aggiunge automaticamente '\\n' come terminatore di riga.
        """
        if self._sock is None:
            raise OSError("[TCP] Socket non connesso. Chiama prima connect().")

        payload = (messaggio + "\n").encode(encoding)
        inviati = self._sock.send(payload)
        print(f"[TCP] Inviati {inviati} byte: {messaggio!r}")
        return inviati

    # ── ricezione ────────────────────────
    def receive(self, bufsize: int = RECV_BUFFER, encoding: str = "utf-8") -> str:
        """
        Legge i dati in arrivo dal server.
        Restituisce la stringa decodificata (o "" se la connessione è chiusa).
        Blocca fino a TIMEOUT_SEC secondi in attesa di dati.
        """
        if self._sock is None:
            raise OSError("[TCP] Socket non connesso. Chiama prima connect().")

        try:
            raw = self._sock.recv(bufsize)
        except OSError as e:
            print(f"[TCP] Errore in ricezione: {e}")
            return ""

        if not raw:
            print("[TCP] Connessione chiusa dal server.")
            return ""

        messaggio = raw.decode(encoding).strip()
        print(f"[TCP] Ricevuti {len(raw)} byte: {messaggio!r}")
        return messaggio

    # ── ricezione riga per riga ──────────
    def receive_line(self, encoding: str = "utf-8") -> str:
        """
        Legge un carattere alla volta finché non trova '\\n'.
        Utile quando il server manda risposte line-by-line.
        """
        if self._sock is None:
            raise OSError("[TCP] Socket non connesso.")

        riga = b""
        while True:
            byte = self._sock.recv(1)
            if not byte or byte == b"\n":
                break
            riga += byte

        messaggio = riga.decode(encoding).strip()
        if messaggio:
            print(f"[TCP] Riga ricevuta: {messaggio!r}")
        return messaggio

    # ── chiusura ─────────────────────────
    def close(self) -> None:
        """Chiude il socket TCP."""
        if self._sock:
            self._sock.close()
            self._sock = None
            print("[TCP] Connessione chiusa.")

    # ── context manager ──────────────────
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *_):
        self.close()


# ─────────────────────────────────────────
#  Funzioni di utilità standalone
#  (usabili senza istanziare la classe)
# ─────────────────────────────────────────
_client_globale: TCPClient = None


def inizializza(host: str = REMOTE_HOST, port: int = REMOTE_PORT) -> TCPClient:
    """
    Crea e connette il client globale.
    Chiama questa funzione una volta prima di send() e receive().
    """
    global _client_globale
    _client_globale = TCPClient(host, port)
    _client_globale.connect()
    return _client_globale


def invia(messaggio: str) -> int:
    """Invia un messaggio usando il client globale."""
    if _client_globale is None:
        raise OSError("Client non inizializzato. Chiama prima inizializza().")
    return _client_globale.send(messaggio)


def ricevi(bufsize: int = RECV_BUFFER) -> str:
    """Riceve un messaggio usando il client globale."""
    if _client_globale is None:
        raise OSError("Client non inizializzato. Chiama prima inizializza().")
    return _client_globale.receive(bufsize)


def chiudi() -> None:
    """Chiude il client globale."""
    global _client_globale
    if _client_globale:
        _client_globale.close()
        _client_globale = None


# ─────────────────────────────────────────
#  Main – esempio di utilizzo
# ─────────────────────────────────────────
def main():
    # 1. Connessione Wi-Fi
    connect_wifi(WIFI_SSID, WIFI_PASSWORD)

    # 2a. Utilizzo tramite classe (consigliato con context manager)
    print("\n── Esempio con context manager ──")
    with TCPClient(REMOTE_HOST, REMOTE_PORT) as client:
        msg = "msg(r1,request,picow,called,r1(35),0)"
        client.send(msg)
        risposta = client.receive_line()
        print(f"Risposta server: {risposta}")
        time.sleep(1)
"""
    # 2b. Utilizzo tramite funzioni standalone
    print("\n── Esempio con funzioni standalone ──")
    inizializza(REMOTE_HOST, REMOTE_PORT)
    invia("Messaggio di test")
    msg = ricevi()
    print(f"Ricevuto: {msg}")
    chiudi()

    # 2c. Loop di echo (invia e aspetta risposta)
    print("\n── Loop echo (Ctrl+C per uscire) ──")
    with TCPClient(REMOTE_HOST, REMOTE_PORT) as client:
        messaggi = ["ping", "status", "temperatura", "fine"]
        for m in messaggi:
            client.send(m)
            risposta = client.receive_line()
            print(f"  → {m!r}  ←  {risposta!r}")
            time.sleep(1)
"""

if __name__ == "__main__":
    main()
