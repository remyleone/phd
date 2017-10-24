#!/usr/bin/env python3

from itertools import product
from csv import DictReader

# [10, 20, 30, 40, 50]
sizes = range(10, 60, 10)
kinds = ["contikimac", "nullmac"]

def extract_message_sent(pathes):
    messages_sent = {path: 0 for path in pathes}
    for path in pathes:
        with open(path) as f:
            for line in f:
                if "DATA recv" in line:
                    messages_sent[path] += 1.0
    print(messages_sent)
    return messages_sent

def extract_powertracker(pathes):
    tx_time = {path: {"sender": 0, "receiver": 0} for path in pathes}
    rx_time = {path: {"sender": 0, "receiver": 0} for path in pathes}
    for path in pathes:
        with open(path) as f:

            print(path)

            reader = DictReader(f)
            for row in reader:
                if row["mote_id"] == "1":
                    tx_time[path]["sender"], rx_time[path]["sender"] = float(row["tx_time"]), float(row["rx_time"])
                if row["mote_id"] == "2":
                    tx_time[path]["receiver"], rx_time[path]["receiver"] = float(row["tx_time"]), float(row["rx_time"])

    print("=== TX ===")
    for path, data in sorted(tx_time.items()):
        print(path, data)
    print("=== RX ===")
    for path, data in sorted(rx_time.items()):
        print(path, data)
    return tx_time, rx_time

ms = extract_message_sent(["%s/%d/serial.log" % (kind, size) for (kind, size)in product(kinds, sizes)])
tx, rx = extract_powertracker(["%s/%d/powertracker_stripped.csv" % (kind, size) for (kind, size) in product(kinds, sizes)])

def tx_per_message(tx, ms):
    folders = ["%s/%d" % (kind, size) for (kind, size) in product(kinds, sizes)]
    for folder in folders:
        serial_path = folder + "/serial.log"
        p_path = folder + "/powertracker_stripped.csv"
        if ms[serial_path]:
            avg_sender = tx[p_path]["sender"] / ms[serial_path]
            avg_receiver = tx[p_path]["receiver"] / ms[serial_path]
            print("AVG(TX/msg)(SENDER) for %s => %f" % (folder, avg_sender))
            print("AVG(TX/msg)(RECEIVER) for %s => %f" % (folder, avg_receiver))
        else:
            print('NO messages in ', serial_path)

def rx_per_message(tx, ms):
    folders = ["%s/%d" % (kind, size) for (kind, size) in product(kinds, sizes)]
    for folder in folders:
        serial_path = folder + "/serial.log"
        p_path = folder + "/powertracker_stripped.csv"
        if ms[serial_path]:
            avg_sender = rx[p_path]["sender"] / ms[serial_path]
            avg_receiver = rx[p_path]["receiver"] / ms[serial_path]
            print("AVG(RX/msg)(SENDER) for %s => %f" % (folder, avg_sender))
            print("AVG(RX/msg)(RECEIVER) for %s => %f" % (folder, avg_receiver))
        else:
            print('NO messages in ', serial_path)

tx_per_message(tx, ms)
rx_per_message(rx, ms)

def plot():
    pass
