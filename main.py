import os
import sys
import time
import board
import requests
import logging
import adafruit_mpl3115a2

URL_IP = "http://ipinfo.io/json"
URL_LOCATION = "https://geolocation-db.com/json/{0}&position=true"
METEO_URL = "https://api.openweathermap.org/data/2.5/weather?lat={0}&lon={1}&appid={2}"


def get_ip():
    try:
        ip = requests.get(URL_IP).json()['ip']
        logging.info(f"My public IP: {ip}")
        return ip
    except Exception:
        logging.fatal("Can't retrieve IP")


def get_localitsation(ip):
    try:
        location = requests.get(URL_LOCATION.format(ip)).json()
        longitude = location['longitude']
        latitude = location['latitude']
        logging.info(f'Longitude: {longitude}, Latitude: {latitude}')
        return longitude, latitude
    except Exception:
        logging.fatal("Can't retrieve location")


def get_atmospheric_pressure(longitude, latitude, apikey):
    try:
        data = requests.get(METEO_URL.format(longitude, latitude, apikey)).json()
        maindata = data['main']
        logging.info(f'Data: {maindata}')
        return data['main']['pressure']
    except Exception:
        logging.fatal("Can't retrieve atmospheric pressure")


def getAltimeter(sealevel_pressure):
    i2c = board.I2C()
    sensor = adafruit_mpl3115a2.MPL3115A2(i2c)
    sensor.sealevel_pressure = sealevel_pressure * 100
    while True:
        pressure =sensor.pressure
        logging.info("Pressure: {0:0.3f} pascals".format(pressure))
        altitude = sensor.altitude
        logging.info("Altitude: {0:0.3f} meters".format(altitude))
        temperature = sensor.temperature
        logging.info("Temperature: {0:0.3f} degrees celsius".format(temperature))
        time.sleep(1.0)


def main(apikey):
    ip = get_ip()
    longitude, latitude = get_localitsation(ip)
    lon = int(round(longitude, 0))
    lat = int(round(latitude, 0))
    logging.info(f'Round longitude: {lon}, round Latitude: {lat}')
    pressure = get_atmospheric_pressure(lon, lat, apikey)
    getAltimeter(pressure)


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    try:
        apikey = os.environ['API_KEY']
        sys.exit(main(apikey))
    except KeyError:
        logging.fatal("API_KEY is missing")
