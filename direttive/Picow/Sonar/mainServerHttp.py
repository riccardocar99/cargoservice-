# ---------------------------------------------------------------------------
# Server HTTP — serve la pagina HTML
# ---------------------------------------------------------------------------
HTML_FILE = "indexSonarWs.html"   # deve essere caricata sul Pico W

async def handle_http(reader, writer):
    await reader.readline()          # GET / HTTP/1.1
    while True:                      # consuma gli header
        line = await reader.readline()
        if line in (b"\r\n", b"\n", b""):
            break
    try:
        with open(HTML_FILE, "r") as f:
            body = f.read()
        writer.write(
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/html\r\n"
            b"Connection: close\r\n\r\n"
        )
        writer.write(body.encode("utf-8"))
    except OSError:
        writer.write(b"HTTP/1.1 404 Not Found\r\n\r\nFile not found")
    await writer.drain()
    writer.close()

# ---------------------------------------------------------------------------
# Avvio — tre task in parallelo
# ---------------------------------------------------------------------------
async def main():
    ip = connect_wifi()
    print(f"Pagina HTML   ->  http://{ip}/")
    print(f"Server WS     ->  ws://{ip}:81/")

    http_server = await asyncio.start_server(handle_http,    "0.0.0.0", 80)
    ws_server   = await asyncio.start_server(handle_client,  "0.0.0.0", 81)

    await asyncio.gather(
        http_server.wait_closed(),
        ws_server.wait_closed(),
        sonar_loop()
    )