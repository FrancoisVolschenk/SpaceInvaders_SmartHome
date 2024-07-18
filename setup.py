import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
from machine import Pin

ssid = 'SPACE_INVADERS'
password = 'SmartHome'
lights = dict()

lights["kitchen_green"] = Pin(15, Pin.OUT)
lights["kitchen_yellow"] = Pin(14, Pin.OUT)
lights["kitchen_red"] = Pin(13, Pin.OUT)
lights["kitchen_blue"] = Pin(12, Pin.OUT)

lights["bedroom_blue"] = Pin(0, Pin.OUT)
lights["bedroom_green"] = Pin(1, Pin.OUT)
lights["bedroom_white"] = Pin(2, Pin.OUT)
lights["bedroom_yellow"] = Pin(3, Pin.OUT)

rave1 = [lights["kitchen_red"], lights["kitchen_blue"], lights["bedroom_blue"], lights["bedroom_green"]]
rave2 = [lights["kitchen_yellow"], lights["kitchen_green"], lights["bedroom_white"], lights["bedroom_yellow"]]

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    
    pico_led.on()
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
                <style>
                    body {{
                        background-color: black;
                        color: white; 
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }}

                    .card {{
                        background-color: #1c1c1c;
                        border: 1px solid white; 
                        border-radius: 10px;
                        padding: 20px;
                        box-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
                        text-align: center;
                    }}

                    form {{
                        margin: 10px 0;
                    }}

                    input[type="submit"] {{
                        background-color: #a0a0a0; 
                        color: white;
                        border: none; 
                        border-radius: 5px; 
                        padding: 10px 20px; 
                        cursor: pointer; 
                        font-size: 16px; 
                    }}

                    input[type="submit"]:hover {{
                        background-color: #909090; 
                    }}
                </style>
            </head>
            <body>
                <div class="card">
                    <form action="./lumos">
                        <input type="submit" value="Light on" />
                    </form>
                    <form action="./nox">
                        <input type="submit" value="Light off" />
                    </form>
                    <form action="./francois_mode">
                        <input type="submit" value="Red Lights On" />
                    </form>
                    <form action="./rave_mode">
                        <input type="submit" value="RAVE" />
                    </form>
                    <p>LED is {state}</p>
                    <p>Temperature is {temperature}</p>
                </div>
            </body>
            </html>
            """    
    return str(page)

def serve(connection):
    #Start a web server
    state = 'OFF'
    temperature = 0
    
    try:
        while True:
            client = connection.accept()[0]
            request = client.recv(1024)
            request = str(request)
            # print(request)
            
            try:
                command = request.split()[1]
            except IndexError:
                print("no command")
                
            
            if "lumos" in command:
                for light in list(lights.values()):
                    light.on()
                    state = 'ON'
                    
            if "nox" in command:
                for light in list(lights.values()):
                    light.off()
                    state = 'OFF'
                    
            if "francois_mode" in command:
                lights["kitchen_red"].on()
                state = "ON FOR REAL"
                
            
            if 'rave_mode' in command:
                times = 5
                while(times > 0):
                    times -= 1
                    for light in rave1:
                        light.on()
                    sleep(0.5)
                    for light in rave1:
                        light.off()
                    
                    for light in rave2:
                        light.on()
                    sleep(0.5)
                    for light in rave2:
                        light.off()
            
            temperature = pico_temp_sensor.temp
            html = web_page(temperature, state)
            client.send(html)
            client.close()
    except KeyboardInterrupt:
        machine.reset()
    
try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()