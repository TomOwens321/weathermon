#!/usr/bin/env python3
"""Listen for UDP JSON datagrams, print them, and send measurements to MQTT/InfluxDB."""

import argparse
import json
import socket
import sys
from datetime import datetime, timezone

import lib.conversions as conv
from lib.influxdb import Influxdb
from lib.mqtt import Mqtt
from lib.udp_json import listen_udp_json

MQTT_TOPIC = "sun-chaser/weather"
MQTT_HOST = "rpi4b-1.ourhouse"
INFLUX_HOST = "knode.ourhouse"
INFLUX_PORT = "8086"
INFLUX_DB = "weather_data"
INFLUX_RP = "one_year"
SENSOR_LOCATION = "Bob's Garage"
SENSOR_TYPE = "UDP_JSON"

mq = Mqtt(MQTT_HOST)
db = Influxdb(host=INFLUX_HOST, port=INFLUX_PORT)
db_client = db.client()


def _as_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _find_value(payload, keys):
    """Return the first numeric value found for any key, checking nested dicts."""
    if not isinstance(payload, dict):
        return None
    for key in keys:
        if key in payload:
            value = _as_number(payload[key])
            if value is not None:
                return value
    for value in payload.values():
        if isinstance(value, dict):
            found = _find_value(value, keys)
            if found is not None:
                return found
    return None


def _get_tempc(payload):
    tempc = _find_value(
        payload, ("tempc", "temp_c", "temperature_c", "temperature", "temp")
    )
    if tempc is not None:
        return tempc
    tempf = _find_value(payload, ("tempf", "temp_f", "temperature_f"))
    if tempf is not None:
        return (tempf - 32) * 5 / 9
    return None


def _get_humidity(payload):
    return _find_value(payload, ("humidity", "hum", "rh", "relative_humidity"))


def _get_sensor_name(payload):
    """Return sensor name from payload hostname, falling back to local hostname."""
    if isinstance(payload, dict):
        hostname = payload.get("hostname")
        if isinstance(hostname, str) and hostname.strip():
            return hostname.strip()
    return socket.gethostname()


def build_measurements(payload, sensor_name=None):
    """Build InfluxDB/MQTT measurement dicts for temperature and humidity."""
    if sensor_name is None:
        sensor_name = _get_sensor_name(payload)
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    tags = {
        "sensorName": sensor_name,
        "sensorLocation": SENSOR_LOCATION,
        "sensorType": SENSOR_TYPE,
    }
    data = []

    tempc = _get_tempc(payload)
    if tempc is not None:
        reading = {
            "measurement": "temperature",
            "time": timestamp,
            "tags": tags.copy(),
            "fields": {
                "tempc": round(tempc, 2),
                "tempf": round(float(conv.c_to_f(tempc)), 2),
            },
        }
        data.append(reading)

    humidity = _get_humidity(payload)
    if humidity is not None:
        reading = {
            "measurement": "humidity",
            "time": timestamp,
            "tags": tags.copy(),
            "fields": {
                "humidity": round(humidity, 2),
            },
        }
        data.append(reading)

    return data


def main():
    parser = argparse.ArgumentParser(
        description="Listen on a UDP port and print any valid JSON received."
    )
    parser.add_argument(
        "port",
        type=int,
        nargs="?",
        default=4210,
        help="UDP port number to listen on (default: 4210)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Local address to bind to (default: 0.0.0.0)",
    )
    args = parser.parse_args()

    try:
        for message in listen_udp_json(args.port, host=args.host):
            print(message, flush=True)
            try:
                payload = json.loads(message)
            except (ValueError, TypeError):
                continue
            if not isinstance(payload, dict):
                continue

            data = build_measurements(payload)
            if not data:
                continue

            try:
                db_client.write_points(data, database=INFLUX_DB, retention_policy=INFLUX_RP)
            except Exception as exc:
                print(f"InfluxDB write error: {exc}", file=sys.stderr)

            for d in data:
                topic = MQTT_TOPIC + "/" + d["measurement"] + "/" + d["tags"]["sensorName"]
                try:
                    mq.send(topic, json.dumps(d))
                except Exception as exc:
                    print(f"MQTT send error: {exc}", file=sys.stderr)
    except KeyboardInterrupt:
        pass
    except OSError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
