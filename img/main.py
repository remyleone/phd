#!/usr/bin/env python

import os
from csv import DictReader
from matplotlib import pyplot as plt
import numpy as np
from itertools import product

io_to_do = {
        10: "/home/sieben/Dropbox/results_estimators/meta_10/io.csv",
        25: "/home/sieben/Dropbox/results_estimators/meta_25/io.csv",
        50: "/home/sieben/Dropbox/results_estimators/meta_50/io.csv"
        }


def divergence():
    """
    TODO: Make them share some axis.
    """
    exp_root = "/home/sieben/sim/results/sim_25_100_100_123456/"
    nodes = range(7)
    result = {"noinfo": {n + 1: {"time": [], "estimation": [], "powertracker": []} for n in nodes},
              "route": {n + 1: {"time": [], "estimation": [], "powertracker": []} for n in nodes},
              "radio": {n + 1: {"time": [], "estimation": [], "powertracker": []} for n in nodes},
        }
    for key, d in result.items():
        for node, res in d.items():
                try:
                    with open(os.path.join(exp_root, "%s_%s.csv" % (node, key))) as f:
                        reader = DictReader(f)
                        time, estimation, powertracker = [], [], []
                        for row in reader:
                            time.append(float(row["time"]))
                            estimation.append(float(row["estimation"]))
                            powertracker.append(float(row["powertracker"]))
                        result[key][node]["time"] = time
                        result[key][node]["estimation"] = estimation
                        result[key][node]["powertracker"] = powertracker
                except IOError as e:
                    print(e)

    estimator_name = ["noinfo", "route", "radio"]
    estimator = range(3)
    f, axarr = plt.subplots(7, 3)
    for (node, estimator) in product(nodes, estimator):
        axarr[node, estimator].plot(result[estimator_name[estimator]][node + 1]["time"], result[estimator_name[estimator]][node + 1]["estimation"])
        axarr[node, estimator].plot(result[estimator_name[estimator]][node + 1]["time"], result[estimator_name[estimator]][node + 1]["powertracker"])
        axarr[node, estimator].legend(loc='lower right')
        if node == 6:
            axarr[node, estimator].set_xlabel('T (s)')
            #axarr[node, estimator].set_xticklabels(visible=False)
        if not estimator:
            axarr[node, estimator].set_ylabel('E (Ah)')
        if not node:
            axarr[node, estimator].set_title(estimator_name[estimator])

    for ax in plt.gcf().axes:
        try:
            ax.label_outer()
        except:
            pass
        #axarr[node, estimator].set_yticklabels(visible=False)
    #axarr[0, 0].plot(x, y)
    #axarr[0, 1].scatter(x, y)
    #axarr[1, 0].plot(x, y ** 2)
    #axarr[1, 1].scatter(x, y ** 2)
    # Fine-tune figure; hide x ticks for top plots and y ticks for right plots
    #plt.setp([a.get_xticklabels() for a in axarr[6, :]], visible=False)
    #plt.setp([a.get_yticklabels() for a in axarr[:, 1]], visible=False)
    plt.savefig("divergence.png")
    plt.show()

def overhead():
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)

    ax1.set_title('repartition protocol')
    ax1.set_ylabel('repartition (%)')
    ax1.set_xlabel('time (s)')

    for cbr_rate, io_path in sorted(io_to_do.items()):

        with open(io_path) as io_f:
            reader = DictReader(io_f)
            bin_start, ratio  = [], []
            for row in reader:
                if float(row["mean_total_bytes"]):
                    bin_start.append(float(row["bin_start"]))
                    ratio.append((float(row["mean_rplinfo_bytes"]) + float(row["mean_battery_bytes"]))/float(row["mean_total_bytes"]))

        ax1.plot(bin_start, ratio, label="CBR: %d" % cbr_rate)

        plt.legend()
        plt.tight_layout()
        plt.savefig("overhead.png")

def protocol_repartition():

    color = {"coap": "red", "rpl": "blue", "ping":
            "green", "udp": "yellow",
            "rplinfo": "cyan", "battery": "magenta"}

    for cbr_rate, io_path in sorted(io_to_do.items()):

        fig1 = plt.figure()
        ax1 = fig1.add_subplot(111)
        ax1.set_title("Protocol repartition")
        ax1.set_ylabel("Bytes")
        ax1.set_xlabel("Time (s)")
        ax1.set_xlim([0, 2750])

        with open(io_path) as csv_file:
            reader = DictReader(csv_file)

            # Hack to avoid duplicate label in legend
            label_first = {"rpl": True,
                    "udp": True, "battery": True,
                    "rplinfo": True}
            for row in reader:
                row = {k: float(v) for k, v in row.iteritems()}
                width = (row["bin_end"] - row["bin_start"]) / 2
                bottom = 0.0

                # rpl
                if row["mean_rpl_bytes"]:
                    ax1.bar(row["bin_start"] + width, row["mean_rpl_bytes"],
                            color=color["rpl"], width=width, bottom=bottom,
                            label="rpl" if label_first["rpl"] else "")
                    bottom += row["mean_rpl_bytes"]
                    label_first["rpl"] = False

                # udp
                if row["mean_udp_bytes"]:
                    ax1.bar(row["bin_start"] + width, row["mean_udp_bytes"],
                            color=color["udp"], width=width, bottom=bottom,
                            label='application' if label_first["udp"] else "")
                    bottom += row["mean_udp_bytes"]
                    label_first["udp"] = False

                # battery
                if row["mean_battery_bytes"]:
                    ax1.bar(row["bin_start"] + width, row["mean_battery_bytes"],
                            color=color["battery"], width=width, bottom=bottom,
                            label="battery" if label_first["battery"] else "")
                    bottom += row["mean_battery_bytes"]
                    label_first["battery"] = False

                # rplinfo
                if row["mean_rplinfo_bytes"]:
                    ax1.bar(row["bin_start"] + width, row["mean_rplinfo_bytes"],
                            color=color["rplinfo"], width=width, bottom=bottom,
                            label="rplinfo" if label_first["rplinfo"] else "")
                    bottom += row["mean_rplinfo_bytes"]
                    label_first["rplinfo"] = False

        plt.legend()

        plt.savefig("repartition_protocol_%d.png" % cbr_rate)

def traffic_impact():
    cbr_to_do = {
        10: "/home/sieben/Dropbox/results_estimators/sim_10_100_100_123456/results/4_radio.csv",
        25: "/home/sieben/Dropbox/results_estimators/sim_25_100_100_123456/results/4_radio.csv",
        50: "/home/sieben/Dropbox/results_estimators/sim_50_100_100_123456/results/4_radio.csv"}

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)

    ax1.set_title('repartition protocol')
    ax1.set_ylabel('Erreur (%)')
    ax1.set_xlabel('time (s)')

    for cbr, p in cbr_to_do.items():
        with open(p) as f:
            reader = DictReader(f)
            time, diff = [], []
            for row in reader:
                time.append(float(row["time"]))
                diff.append(abs(float(row["estimation"]) - float(row["powertracker"]))/float(row["powertracker"]))
            ax1.plot(time, diff, label="CBR: %d" % cbr)
    plt.legend()
    plt.tight_layout()
    plt.savefig("traffic_impact.png")

def recalibration_impact():
    recalibration_to_do = {
        100: "/home/sieben/Dropbox/results_estimators/sim_10_100_100_123456/results/4_radio.csv",
        250: "/home/sieben/Dropbox/results_estimators/sim_10_250_100_123456/results/4_radio.csv",
        500: "/home/sieben/Dropbox/results_estimators/sim_10_500_100_123456/results/4_radio.csv"}

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)

    ax1.set_title('Recalibration impact')
    ax1.set_ylabel('Erreur (%)')
    ax1.set_xlabel('time (s)')

    for recalibration, p in recalibration_to_do.items():
        with open(p) as f:
            reader = DictReader(f)
            time, diff = [], []
            for row in reader:
                time.append(float(row["time"]))
                diff.append(abs(float(row["estimation"]) - float(row["powertracker"]))/float(row["powertracker"]))
            ax1.plot(time, diff, label="Recalibration: %d" % cbr)
    plt.legend()
    plt.tight_layout()
    plt.savefig("recalibration_impact.png")


if __name__ == "__main__":
    divergence()
    protocol_repartition()
    overhead()
    traffic_impact()
    recalibration_impact()
