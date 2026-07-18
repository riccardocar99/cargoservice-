"""
tcp_client_async.py – MicroPython TCP client asincrono sulla porta 8010
Usa uasyncio per non bloccare il loop principale durante send/receive.
Testato su ESP8266 / ESP32 con MicroPython >= 1.19
"""

import network
import uasyncio as asyncio
import time

# ─────────────────────────────────────────
#  Configurazione
# ─────────────────────────────────────────
WIFI_SSID     = secretsLab.WIFI_SSID
WIFI_PASSWORD = secretsLab.WIFI_PASSWORD

REMOTE_HOST = "192.168.1.132"   # IP del computer remotoREMOTE_PORT = 8010

RECV_BUFFER = 1024


# ─────────────────────────────────────────
#  Connessione Wi-Fi (sincrona, solo all'avvio)
# ─────────────────────────────────────────
def connect_wifi(ssid: str, password: str) -> None:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"[WiFi] Connessione a '{ssid}' …")
        wlan.connect(ssid, password)
        deadline = time.time() + 20
        while not wlan.isconnected():
            if time.time() > deadline:
                raise OSError("[WiFi] Timeout: impossibile connettersi.")
            time.sleep(0.5)
    print(f"[WiFi] Connesso – IP locale: {wlan.ifconfig()[0]}")


# ─────────────────────────────────────────
#  Client TCP asincrono
# ─────────────────────────────────────────
class AsyncTCPClient:
    """
    Client TCP non bloccante basato su uasyncio.StreamReader / StreamWriter.

    Tutte le operazioni di I/O sono coroutine: vanno chiamate con `await`.
    La ricezione può essere avviata come task indipendente che gira in
    parallelo al loop principale.

    Uso tipico
    ----------
        client = AsyncTCPClient("192.168.1.100", 8010)
        await client.connect()

        # ricezione in background – il callback viene chiamato ad ogni messaggio
        asyncio.create_task(client.receive_loop(on_message=mia_funzione))

        # invio dal loop principale senza bloccarsi
        await client.send("ciao server")
    """

    def __init__(self, host: str, port: int):
        self.host    = host
        self.port    = port
        self._reader = None
        self._writer = None
        self._connected = False

    # ── connessione ──────────────────────
    async def connect(self) -> None:
        """Apre la connessione TCP in modo asincrono."""
        self._reader, self._writer = await asyncio.open_connection(self.host, self.port)
        self._connected = True
        print(f"[TCP] Connesso a {self.host}:{self.port}")

    # ── invio ────────────────────────────
    async def send(self, messaggio: str, encoding: str = "utf-8") -> None:
        """
        Invia `messaggio` al server senza bloccare il loop.
        Aggiunge '\\n' come terminatore di riga.
        """
        if not self._connected:
            raise OSError("[TCP] Non connesso. Chiama prima await connect().")
        payload = (messaggio + "\n").encode(encoding)
        self._writer.write(payload)
        await self._writer.drain()          # attende svuotamento buffer (non bloccante)
        print(f"[TCP] Inviati {len(payload)} byte: {messaggio!r}")

    # ── ricezione singola (coroutine) ────
    async def receive(self, bufsize: int = RECV_BUFFER,
                      encoding: str = "utf-8") -> str:
        """
        Attende un singolo blocco di dati dal server.
        Restituisce la stringa decodificata.
        Non blocca il loop: cede il controllo agli altri task mentre aspetta.
        """
        if not self._connected:
            raise OSError("[TCP] Non connesso.")
        raw = await self._reader.read(bufsize)
        if not raw:
            print("[TCP] Connessione chiusa dal server.")
            self._connected = False
            return ""
        messaggio = raw.decode(encoding).strip()
        print(f"[TCP] Ricevuti {len(raw)} byte: {messaggio!r}")
        return messaggio

    # ── ricezione riga per riga (coroutine) ──
    async def receive_line(self, encoding: str = "utf-8") -> str:
        """
        Attende una riga completa (terminata da '\\n') dal server.
        Non blocca il loop: cede il controllo agli altri task mentre aspetta.
        """
        if not self._connected:
            raise OSError("[TCP] Non connesso.")
        raw = await self._reader.readline()
        if not raw:
            print("[TCP] Connessione chiusa dal server.")
            self._connected = False
            return ""
        messaggio = raw.decode(encoding).strip()
        print(f"[TCP] Riga ricevuta: {messaggio!r}")
        return messaggio

    # ── loop di ricezione in background ──
    async def receive_loop(self, on_message=None, use_readline: bool = True) -> None:
        """
        Task da lanciare con asyncio.create_task().
        Rimane in ascolto continuo; per ogni messaggio ricevuto chiama
        `on_message(messaggio)` se fornita, altrimenti stampa il messaggio.

        Parametri
        ---------
        on_message   : callable(str) oppure coroutine(str) – callback invocato
                       ad ogni messaggio in arrivo. Può essere sia una normale
                       funzione che una coroutine (async def).
        use_readline : se True usa readline() (attende '\\n'),
                       altrimenti usa read() su buffer fisso.
        """
        print("[TCP] Loop di ricezione avviato.")
        while self._connected:
            try:
                if use_readline:
                    msg = await self.receive_line()
                else:
                    msg = await self.receive()

                if not msg:
                    break                   # connessione chiusa

                if on_message:
                    # supporta sia callback normali che coroutine
                    result = on_message(msg)
                    if hasattr(result, "send"):  # è una coroutine?
                        await result
                else:
                    print(f"[RX] {msg}")

            except OSError as e:
                print(f"[TCP] Errore nel loop di ricezione: {e}")
                break

        self._connected = False
        print("[TCP] Loop di ricezione terminato.")

    # ── chiusura ─────────────────────────
    async def close(self) -> None:
        """Chiude il socket in modo pulito."""
        self._connected = False
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None
            self._reader = None
            print("[TCP] Connessione chiusa.")

    # ── context manager asincrono ────────
    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *_):
        await self.close()


# ─────────────────────────────────────────
#  Esempi di utilizzo
# ─────────────────────────────────────────

# Esempio 1 – ricezione in background, invio periodico dal main
# ------------------------------------------------------------
async def esempio_background():
    """
    Il task di ricezione gira in parallelo al loop di invio.
    Il main non si blocca mai aspettando dati.
    """
    messaggi_ricevuti = []

    def on_message(msg: str):
        """Callback chiamato ad ogni riga ricevuta dal server."""
        messaggi_ricevuti.append(msg)
        print(f"[CALLBACK] Messaggio arrivato: {msg!r}")

    async with AsyncTCPClient(REMOTE_HOST, REMOTE_PORT) as client:
        # avvia la ricezione come task indipendente
        rx_task = asyncio.create_task(
            client.receive_loop(on_message=on_message, use_readline=True)
        )

        # loop principale: invia un messaggio ogni 2 secondi
        for i in range(5):
            await client.send(f"messaggio #{i}")
            print(f"[MAIN] Sto facendo altro lavoro… (ricevuti finora: {len(messaggi_ricevuti)})")
            await asyncio.sleep(2)          # cede il controllo → rx_task può ricevere

        # chiudi il task di ricezione prima di uscire
        rx_task.cancel()
        try:
            await rx_task
        except asyncio.CancelledError:
            pass

    print(f"[MAIN] Totale messaggi ricevuti: {len(messaggi_ricevuti)}")


# Esempio 2 – callback asincrono (async def)
# ------------------------------------------
async def esempio_callback_async():
    """
    Il callback stesso è una coroutine: può fare await al suo interno
    (es. rispondere al server, aggiornare un display, ecc.).
    """
    async def on_message_async(msg: str):
        print(f"[ASYNC CB] Elaboro: {msg!r}")
        await asyncio.sleep(0)              # cede il controllo se necessario
        # qui puoi fare altre operazioni async, es. aggiornare un display

    async with AsyncTCPClient(REMOTE_HOST, REMOTE_PORT) as client:
        rx_task = asyncio.create_task(
            client.receive_loop(on_message=on_message_async)
        )
        await client.send("start")
        await asyncio.sleep(10)
        rx_task.cancel()
        try:
            await rx_task
        except asyncio.CancelledError:
            pass


# Esempio 3 – receive singola in una coroutine (request/response)
# ---------------------------------------------------------------
async def esempio_request_response():
    """
    Mostra come usare send + receive come coppia request/response
    senza un loop di ricezione permanente.
    """
    async with AsyncTCPClient(REMOTE_HOST, REMOTE_PORT) as client:
        await client.send("ping")
        risposta = await client.receive_line()
        print(f"[RR] Risposta al ping: {risposta!r}")

        await client.send("temperatura")
        risposta = await client.receive_line()
        print(f"[RR] Temperatura: {risposta!r}")


# ─────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────
async def main():
    connect_wifi(WIFI_SSID, WIFI_PASSWORD)

    print("\n── Esempio 1: ricezione in background ──")
    await esempio_background()

    # decommenta per gli altri esempi:
    # print("\n── Esempio 2: callback asincrono ──")
    # await esempio_callback_async()

    # print("\n── Esempio 3: request/response ──")
    # await esempio_request_response()


asyncio.run(main())
