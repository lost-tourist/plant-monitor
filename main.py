import board, microcontroller, digitalio
import os
import time
import busio
import ipaddress, wifi
import socketpool
import json
from adafruit_httpserver import Server, Request, Response


UART_TX = microcontroller.pin.GPIO0
UART_RX = microcontroller.pin.GPIO1

uart = None
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)


def initialise_wifi():
    connected_ok = False

    ipv4 =  ipaddress.IPv4Address("192.168.1.101")
    netmask =  ipaddress.IPv4Address("255.255.255.0")
    gateway =  ipaddress.IPv4Address("192.168.1.1")
    while not connected_ok:
        wifi.radio.set_ipv4_address(ipv4=ipv4, netmask=netmask, gateway=gateway)
        wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
        time.sleep(0.25)
        if wifi.radio.ipv4address = None:
            # Connection failed
            time.sleep(10)
        else:
            connected_ok = True


def initialise_sensor():
    return busio.UART(UART_TX, UART_RX, baudrate=9600)


def _sensor_response(cmd):
    uart.write(bytearray(cmd))
    response = uart.read(10)
    return float(response[2:-2])


def temperature(uart):
    return _sensor_response("t")


def moisture(uart):
    return _sensor_response("w")


def humidity(uart):
    return _sensor_response("h")


def set_LED(uart, is_on):
    if is_on:
        uart.write(bytearray("L"))
    else:
        uart.write(bytearray("l"))


def start_web_server():
    server.serve_forever(str(wifi.radio.ipv4_address))


@server.route("/")
def base(request: Request):
    """
    Serve a default static plain text message.
    """
    return Response(request, "Hello from the CircuitPython HTTP Server!")


@server.route("/sensors")
def sensor_data(request: Request):
    set_LED(uart, True)
    info = {
        'temperature': temperature(uart),
        'humidity': humidity(uart),
        'moisture': moisture(uart)
    }
    set_LED(uart, False)

    return Response(request, json.dumps(info))


def main():
    global uart

    print("\n --> Startup\n")
    initialise_wifi()
    print(" --> Network interface is UP\n")
    uart = initialise_sensor()
    set_LED(uart, False)
    print(" --> Sensors initialised\n")
    start_web_server()
    print(" --> Web server running\n")


main()

