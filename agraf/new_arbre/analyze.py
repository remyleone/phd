#!/usr/bin/env python3

from itertools import product
from csv import DictReader
from matplotlib import pyplot as plt

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

def time_per_message(tx, rx, ms):
    folders = ["%s/%d" % (kind, size) for (kind, size) in product(kinds, sizes)]
    for kind in kinds:
        avg_rx_receiver, avg_rx_sender, avg_tx_receiver, avg_tx_sender = [], [], [], []
        for size in sizes:
            serial_path = ("/").join([kind, str(size), "serial.log"])
            p_path = ("/").join([kind, str(size), "powertracker_stripped.csv"])
            if ms[serial_path]:
                avg_tx_sender.append(tx[p_path]["sender"] / ms[serial_path])
                avg_tx_receiver.append(tx[p_path]["receiver"] / ms[serial_path])
                avg_rx_sender.append(rx[p_path]["sender"] / ms[serial_path])
                avg_rx_receiver.append(rx[p_path]["receiver"] / ms[serial_path])
                #print("AVG(TX/msg)(SENDER) for %d => %f" % (size, avg_tx_sender))
                #print("AVG(TX/msg)(RECEIVER) for %d => %f" % (size, avg_tx_receiver))
                #print("AVG(RX/msg)(SENDER) for %d => %f" % (size, avg_rx_sender))
                #print("AVG(RX/msg)(RECEIVER) for %d => %f" % (size, avg_rx_receiver))
            else:
                avg_tx_sender.append(None)
                avg_tx_receiver.append(None)
                avg_rx_sender.append(None)
                avg_rx_receiver.append(None)

        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_title("tx per message for %s" % kind)
        ax1.set_xlabel("Size of payload")
        ax1.set_ylabel("TX_TIME/#messages")
        print(avg_rx_sender)
        ax1.plot(sizes, avg_tx_sender, label="tx sender")
        ax1.plot(sizes, avg_rx_sender, label="rx sender")
        ax1.plot(sizes, avg_tx_receiver, label="tx receiver")
        ax1.plot(sizes, avg_rx_receiver, label="rx receiver")

        ax1.legend()
        fig.savefig("%s.pdf" % kind, format="pdf")

time_per_message(tx, rx, ms)
