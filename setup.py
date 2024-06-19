import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine

ssid = 'SPACE_INVADERS'
password = 'SmartHome'
light = machine.Pin(4, machine.Pin.OUT)

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
        
    ip = wlan.ifconfig()[0]
    print(f"Connected as {ip}")
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def web_page(temperature, state):
    # the page to be served up
    page = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                </head>
                <body>
                <form action="./lighton">
                <input type="submit" value="Light on" />
                </form>
                <form action="./lightoff">
                <input type="submit" value="Light off" />
                </form>
                <p>LED is {state}</p>
                <p>Temperature is {temperature}</p>
                </body>
                </html>
            """    
    return str(page)

def serve(connection):
    #Start a web server
    state = 'OFF'
    pico_led.off()
    light.off()
    temperature = 0
    
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        # print(request)
        
        try:
            command = request.split()[1]
        except IndexError:
            print("no command")
            
        if command == '/lighton?':
            pico_led.on()
            light.on()
            state = 'ON'
        elif command == '/lightoff?':
            pico_led.off()
            light.off()
            state = 'OFF'
        
        temperature = pico_temp_sensor.temp
        html = web_page(temperature, state)
        client.send(html)
        client.close()
    
try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()