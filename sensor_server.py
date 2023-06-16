#!/usr/bin/env python3

from flask import Flask, request
import os, time, json


app = Flask(__name__)

# Just to check that the server is up
@app.route("/", methods=["GET"])
def hw():
    return "Hello world"


@app.route("/sensors", methods=["POST"])
def write_sensor_data():
    data = json.loads(request.data)

    epoch = int(time.time())
    now = time.asctime(time.localtime(epoch))
    temp = data.get("temp")
    moisture = data.get("moisture")
    humidity = data.get("humidity")
    sensor_id = data.get("sensor_id")

    data_file = f"{os.getenv('HOME')}/data/plants_{sensor_id}.csv"
    with open(data_file, 'a') as recorded_data:
        print(f"{now},{epoch},{temp},{humidity},{moisture}", file=recorded_data)

    # return what we are sent, along with timestamp decoration
    return {"timestamp": now, "epoch": epoch,
            "temp": temp, "humidity": humidity, "moisture": moisture,
            "sensor_id": sensor_id}



if __name__ == "__main__":
    app.run()

