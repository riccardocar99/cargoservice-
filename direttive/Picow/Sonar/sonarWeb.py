from wifi import init_wifi
import socket
from machine import Pin
import time

init_wifi()

# ultrasonic sensor pins and functions
trigger = Pin(3, Pin.OUT)
echo    = Pin(2, Pin.IN)

d  = 10

def ultrasonicMock():
    global d
    d = d + 1
    return d

def ultrasonic():
    trigger.low()
    time.sleep_us(1)
    trigger.high()
    time.sleep_us(10)
    trigger.low()
    while echo.value() == 0:
        signaloff = time.ticks_us()
    while echo.value() == 1:
        signalon = time.ticks_us()
    timepassed = signalon - signaloff
    distance = (timepassed * 0.0340) / 2
    return distance

# Function to load in html page

def get_html(html_name, distance):
    # open html_name (index.html), 'r' = read-only as variable 'file'
    with open(html_name, 'r') as file:
        html    = file.read()
    content = html #replace("<h2 id=\"ultrasonic\"></h2>", f"<h2 id=\"ultrasonic\">{distance}cm</h2>")
    #print(html)
    return content

def get_referer(req):
    # Cerchiamo la riga che inizia con "Referer: "
    for line in req.split('\r\n'):
        if line.startswith("Referer: "):
            return line.replace("Referer: ", "").strip()
    return None # Se non viene trovato

# HTTP server with socket
addr = socket.getaddrinfo('0.0.0.0', 8010)[0][-1]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #riusa indirizzo anche se occupato
try:
    s.bind(addr)
    #s.bind(('',8030))
    s.listen(1)

    print('Listening on', addr)

    # Listen for connections
    while True:
        try:
            cl, addr = s.accept()
            print('Client connected from', addr)
            request = cl.recv(1024).decode('utf-8')
            request = get_referer(request)
            print(request)  
            risposta = "HTTP/1.1 200 OK\n"
            risposta += "Content-Type: text/html\n"
            risposta += "Access-Control-Allow-Origin: *\n" # <--- CORS
            risposta += "\n"
            #print (""+request.find('/data'))
            #if (request.find('/data') > -1):
            if( request != None ) :
                #if string is found, respond with data.
                print("found /data")
                risposta += str(ultrasonic())
            else:
                print("NOT found /data")
                risposta += get_html('indexSonar.html', ultrasonic())
            #print(risposta)
            cl.send(risposta.encode('utf-8'))
            #response = get_html('indexSonar.html', 
            
            #cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n Access-Control-Allow-Origin: *\n"')
            #cl.send(response)
            cl.close()

        except OSError as e:
            cl.close()
            print('OSError ' + e)
            break
        
        except KeyboardInterrupt as e:
            print("Programma interrotto manualmente")
            cl.close()
            break

finally:
    # Questo codice viene eseguito SEMPRE, anche dopo il break o un crash
    s.close()
    print("close the socket")
