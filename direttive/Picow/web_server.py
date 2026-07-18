import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
import secretsHome
import rp2
import sys

## Browser on http://192.168.1.81:8030/

ssid     = secretsHome.WIFI_SSID
password = secretsHome.WIFI_PASSWORD

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        pico_led.on()
        sleep(0.5)
        pico_led.off()
        sleep(0.5)
        #sleep(1)
    print(wlan.ifconfig())
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 8030)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return connection

def webpage(temperature, state):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <form action="./lighton">
            <input type="submit" value="Light on" />
            </form>
            <form action="./lightoff">
            <input type="submit" value="Light off" />
            </form>
            <form action="./close">
            <input type="submit" value="Stop server" />
            </form>
            <p>LED is {state}</p>
            <p>Temperature is {temperature}</p>
            </body>
            </html>
            """    
    return str(html)

def serve(connection):
    #Start a web server
    state = 'OFF'
    pico_led.off()
    temperature = 0
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        #print(request)
        try:
            request = request.split()[1]
        except IndexError:
            print("pass") 
            pass
        print(request)
        if request == '/lighton?':
            pico_led.on()
        elif request =='/lightoff?':
            pico_led.off()
        elif request == '/close?':
            sys.exit()
        temperature = pico_temp_sensor.temp        
        html = webpage(temperature, state)        
        # PRIMA invia l'intestazione  
        client.send('HTTP/1.1 200 OK\n')
        client.send('Content-Type: text/html\n')
        client.send('Connection: close\n\n') # Il doppio \n indica la fine della busta
        # POI invia il contenuto vero e proprio (il file HTML)
        client.send(html)
        client.close()
    


ip=connect()
connection=open_socket(ip)
serve(connection)