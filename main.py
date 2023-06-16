import board, microcontroller
import os
import time
import busio
import ipaddress, wifi, socketpool
import json
import re
import adafruit_requests


UART_TX = microcontroller.pin.GPIO0
UART_RX = microcontroller.pin.GPIO1

SENSOR_ID = 1        # needs to be unique per sensor
DESTINATION = 'http://192.168.1.4:5300/sensors'
UPDATE_INTERVAL = 5 * 60    # in seconds

uart = None
pool = requests = None


def initialise_wifi():
    global pool, requests

    connected_ok = False

    ipv4 =  ipaddress.IPv4Address("192.168.1.101")
    netmask =  ipaddress.IPv4Address("255.255.255.0")
    gateway =  ipaddress.IPv4Address("192.168.1.1")
    while not connected_ok:
        wifi.radio.set_ipv4_address(ipv4=ipv4, netmask=netmask, gateway=gateway)
        wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
        time.sleep(0.25)
        if wifi.radio.ipv4_address is None:
            # Connection failed
            time.sleep(10)
        else:
            connected_ok = True
    print(f":::: connected to {os.getenv('CIRCUITPY_WIFI_SSID')} ::::\n")

    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool)
    print(f":::: requests object initialised ::::\n")


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


def parse_response(key, response):
    m = re.search(f"{key}=([0-9.]+)", response)
    if m:
        return float(m.group(1))

    return 0


def tmh(uart):
    set_LED(uart, True)
    uart.write(bytearray("twh"))
    response = uart.read(30)
    set_LED(uart, False)

    temp = parse_response("t", response)
    moisture = parse_response("w", response)
    humidity = parse_response("h", response)

    return {
        "temp": temp, "moisture": moisture, "humidity": humidity
    }


def set_LED(uart, is_on):
    if is_on:
        uart.write(bytearray("L"))
    else:
        uart.write(bytearray("l"))


def send_sensor_data(uart):
    data = tmh(uart)
    data["sensor_id"] = SENSOR_ID
    print(f"Sending data {data} ...")
    resp = requests.post(url=DESTINATION, json=data)
    print(f"... response code was {resp.status_code}")


def start_main_loop(uart):
    while True:
        print(f"Getting sensor data & sending to {DESTINATION}")
        send_sensor_data(uart)
        print(f"Sleeping for {UPDATE_INTERVAL} seconds")
        time.sleep(UPDATE_INTERVAL)


def main():
    global uart

    print("\n --> Startup\n")
    initialise_wifi()
    print(" --> Network interface is UP\n")
    uart = initialise_sensor()
    set_LED(uart, False)
    print(" --> Sensors initialised\n")
    start_main_loop(uart)


main()

