#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains all the classes used in order to analyze trace
of experiments.

For instance we analyze PCAP by defaults but it would be completely acceptable
to have some log analyzer code here.
"""

from collections import defaultdict
from csv import DictWriter, DictReader
from itertools import product
from multiprocessing import Pool
from multiprocessing.dummy import Pool as dummy_pool
import fnmatch
import json
import os
import re
import subprocess
from math import sqrt
from os.path import join as PJ
import networkx as nx
from networkx.readwrite import json_graph
import numpy as np
from numpy import std, mean
import logging

log = logging.getLogger("Pwet")
BINS = 100


def pcap_stats(stat, output_path):
    with open(output_path, "w") as output_file:
        command = ["tshark", "-q",
                   "-z", stat,
                   "-r", "output.pcap"]
        log.debug(str(command))
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output_file.write(stdout)
        return stdout


def io():
    log_file = "io.log"

    stat = ["io", "stat", str(BINS), "udp", "icmpv6.type==155",
            "icmpv6.type==128||icmpv6.type==129", "coap",
            "data.data == 42",
            "data.data == 52"]
    # RPL packets
    # ICMPV6 PING PACKETS
    pcap_stats(
        stat=",".join(stat),
        output_path=log_file)

    io2csv(input_path=log_file,
           output_path="io.csv")


def distance(x1, x2, y1, y2):
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def powertracker_to_csv(powertracker_log):
    """
    format :
    Sky_2 MONITORED 9898083 us
    Sky_2 ON 180565 us 1,82 %
    Sky_2 TX 83860 us 0,85 %
    Sky_2 RX 2595 us 0,03 %
    Sky_2 INT 907 us 0,01 %

    sky_tx_cost: Transmitting during 1 us
    sky_rx_cost: Reception during 1 us
    sky_on_cost: Only CPU on during 1 us
    sky_int_cost: Idle mode during 1 us

    NO GARANTY IF FORMAT IS DIFFERENT
    """

    # We have the result from powertracker in us
    # (mA * µs) => (A * h) to fit Claude Chaudet slides
    sky_tx_cost = (17.4 * 10 ** -3) / (3600 * 10 ** 6)
    sky_rx_cost = (19.7 * 10 ** -3) / (3600 * 10 ** 6)
    sky_on_cost = (365 * 10 ** -6) / (3600 * 10 ** 6)
    sky_int_cost = (19.7 * 10 ** -3) / (3600 * 10 ** 6)

    with open(powertracker_log) as powertracker_file:
        powertracker_logs = powertracker_file.read()

        monitored_iterable = re.finditer(
            "^Sky_(?P<mote_id>\d+) MONITORED (?P<monitored_time>\d+)",
            powertracker_logs, re.MULTILINE)
        on_iterable = re.finditer(
            "^Sky_(?P<mote_id>\d+) ON (?P<on_time>\d+)",
            powertracker_logs, re.MULTILINE)
        tx_iterable = re.finditer(
            "^Sky_(?P<mote_id>\d+) TX (?P<tx_time>\d+)",
            powertracker_logs, re.MULTILINE)
        rx_iterable = re.finditer(
            "^Sky_(?P<mote_id>\d+) RX (?P<rx_time>\d+)",
            powertracker_logs, re.MULTILINE)
        int_iterable = re.finditer(
            "^Sky_(?P<mote_id>\d+) INT (?P<int_time>\d+)",
            powertracker_logs, re.MULTILINE)

        all_iterable = zip(monitored_iterable, on_iterable, tx_iterable, rx_iterable, int_iterable)

        fields = ["mote_id", "monitored_time",
                  "tx_time", "rx_time", "on_time", "int_time",
                  "energy_consumed"]
        final_energy = {}
        with open("powertracker.csv", "w") as csv_output:
            writer = DictWriter(csv_output, delimiter=',', fieldnames=fields)
            writer.writeheader()

            for matches in all_iterable:
                row = {}
                for match in matches:
                    all(m.groupdict()["mote_id"] == matches[0].groupdict()["mote_id"]
                        for m in matches)
                    row.update((k, int(v))
                               for k, v in match.groupdict().items())
                    row["energy_consumed"] = sky_tx_cost * row.get("tx_time", 0)
                    row["energy_consumed"] += sky_rx_cost * row.get("rx_time", 0)
                    row["energy_consumed"] += sky_on_cost * row.get("on_time", 0)
                    row["energy_consumed"] += sky_int_cost * row.get("int_time", 0)
                # Passing the result from us to s
                row["monitored_time"] = float(row["monitored_time"]) / (10 ** 6)
                row["tx_time"] = float(row["tx_time"]) / (10 ** 6)
                row["rx_time"] = float(row["rx_time"]) / (10 ** 6)
                row["on_time"] = float(row["on_time"]) / (10 ** 6)
                row["int_time"] = float(row["int_time"]) / (10 ** 6)
                writer.writerow(row)

                # Final energy
                final_energy[row["mote_id"]] = row["energy_consumed"]

        # with open(self.powertracker_csv.replace(".csv", "_final.csv"), "w") as f:
        #     writer = DictWriter(f, ["mote_id", "energy_consumed"])
        #     writer.writeheader()
        #     for mote_id, energy_consumed in final_energy.items():
        #         writer.writerow({"mote_id": mote_id,
        #                          "energy_consumed": energy_consumed})
def rpl_tree():
    """
    Produce the RPL tree.
    """
    rpl_dag = nx.DiGraph()
    with open("serial.log") as log_file:
        lines = log_file.readlines()
        pattern = ["^(?P<time>\d+)",
                   "ID:(?P<node>\d+)",
                   "(P(?P<p>\d+)|(?P<root>created a new RPL dag))"]
        matcher = "\s+".join(pattern)
        for line in lines:
            m = re.search(matcher, line)
            if m:
                data = m.groupdict()
                node = int(data["node"]) if data["node"] else 0
                # route_in = int(data["route_in"]) if data["route_in"] else 0
                # route_out = int(data["route_out"]) if data["route_out"] else 0
                p = int(data["p"]) if data["p"] else 0
                root = data["root"]
                parent, child = None, None
                # 1190170 ID:8 created a new RPL dag
                if root:
                    rpl_dag.add_node(node, root=True)
                    rpl_dag.graph["root"] = node

                # 241189330 ID:8 route: 2 via 4
                # Warning: Accurate to only one hop
                # if route_in and route_out:
                #     log.info("%s via %s" % (route_in, route_out))
                #     rpl_dag.add_node(node, root=True)
                #     rpl_dag.graph["root"] = node
                #     parent = route_out
                #     child = route_in

                # 900379320 ID:7 P3
                if p and node:
                    parent = p
                    child = node

                if child and parent:
                    if child == parent:
                        parent = rpl_dag.graph["root"]
                    rpl_dag.add_nodes_from([child, parent])
                    for old_parent in rpl_dag.successors(child):
                        rpl_dag.remove_edge(child, old_parent)
                    rpl_dag.add_edge(child, parent)

                    log.info(
                        "%d preferred parent => %d" % (child, parent))

        log.info("%s" % rpl_dag.nodes(data=True))
        log.info("%s" % rpl_dag.edges(data=True))

        # Adding depth if available
        for node in rpl_dag.nodes():
            if "root" in rpl_dag.graph:
                log.info(rpl_dag.nodes(data=True))
                if nx.has_path(rpl_dag, node, rpl_dag.graph["root"]):
                    # noinspection PyArgumentList
                    depth = nx.shortest_path_length(rpl_dag,
                                                    source=node,
                                                    target=rpl_dag.graph["root"])
                    rpl_dag.add_node(node, depth=depth)

        # Saving to rpl_tree.json
        with open("rpl_tree.json", "w") as rpl_tree_f:
            rpl_tree_f.write(json_graph.dumps(rpl_dag,
                                              indent=4, sort_keys=True))


def message():
    """
    Extract from the serial logs all the message.

    IMPORTANT: We only extract the message received from the root or send by
    the root.

    186572 ID:2 DATA send to 1 'Hello 1'
    187124 ID:8 DATA recv 'Hello 1' from 2
    197379 ID:8 REPLY send to 7 'Reply 1'
    197702 ID:7 REPLY recv 'Reply 1' from 8

    TODO: Pass all times to seconds.
    """
    # Arrivals to root
    a_root = "^(?P<time>\d+)\s+ID:(?P<mote_id>\d+)\s+DATA recv '(?P<message>.*)' from (?P<source>\d+)"
    # Departures from root
    d_root = "^(?P<time>\d+)\s+ID:(?P<mote_id>\d+)\s+REPLY send to (?P<destination>\d+) '(?P<message>.*)'"
    # Battery recalibration
    b_recalibration = "^(?P<time>\d+)\s+ID:(?P<mote_id>\d+)\s+B$"
    fieldnames = ["time", "mote_id", "message", "message_type", "source",
                  "destination"]

    with open("serial.log") as serial_file:
        lines = serial_file.read()

        with open("messages.csv", "w") as output_file:
            writer = DictWriter(output_file, fieldnames)
            writer.writeheader()
            for match in re.finditer(a_root, lines, re.MULTILINE):
                d = match.groupdict()
                d["message_type"] = "data"
                d["time"] = float(d["time"]) / (10 ** 6)
                writer.writerow(d)
            for match in re.finditer(d_root, lines, re.MULTILINE):
                d = match.groupdict()
                d["message_type"] = "reply"
                d["time"] = float(d["time"]) / (10 ** 6)
                writer.writerow(d)
            for match in re.finditer(b_recalibration, lines, re.MULTILINE):
                d = match.groupdict()
                d["message_type"] = "battery_recalibration"
                d["time"] = float(d["time"]) / (10 ** 6)
                writer.writerow(d)


def radio_tree():
    """
    Compute the radio graph
    """
    radio_net = nx.Graph()
    with open("graph.json") as f:
        nodes = json.loads(f.read())
        for node in nodes:
            radio_net.add_node(node["mote_id"],
                               mote_type=node["mote_type"],
                               x=node["x"], y=node["y"])

        nodes_product = product(radio_net.nodes(data=True), radio_net.nodes(data=True))
        for (a, d_a), (b, d_b) in nodes_product:
            d = distance(d_a["x"], d_b["x"], d_a["y"], d_b["y"])
            if d < 42:
                radio_net.add_edge(a, b)
    with open("radio_tree.json", "w") as f:
        f.write(json_graph.dumps(radio_net, sort_keys=True,
            indent=4))


def depth_energy():
    """
    Energy consumed by depth
    """
    depth, powertracker, mean_d, std_d, result = {
    }, {}, {}, {}, defaultdict(list)
    # Gathering energy consumed by each nodes
    with open("powertracker.csv") as powertracker_file:
        powertracker_reader = DictReader(powertracker_file)
        powertracker = {row["mote_id"]: float(row["energy_consumed"])
                        for row in powertracker_reader}

    # Gathering depth of each nodes
    with open("depth.csv") as depth_file:
        depth_reader = DictReader(depth_file)
        depth = {row["mote_id"]: row["depth"]
                 for row in depth_reader}

    # Joining depth and energy consumed
    for node, energy_consumed in powertracker.items():
        if node in depth:
            result[depth[node]].append(energy_consumed)

    for node_depth, energy_consumed in result.items():
        mean_d[node_depth] = mean(energy_consumed)
        std_d[node_depth] = std(energy_consumed)

    # Export to CSV
    with open("depth_energy.csv", "w") as f:
        writer = DictWriter(f, ["depth", "mean_energy", "std_energy"])
        writer.writeheader()
        # sorted to have all depth in the right order
        for depth in sorted(mean_d):
            writer.writerow({"depth": depth,
                             "mean_energy": mean_d[depth],
                             "std_energy": std_d[depth]})

        return result


def io2csv(input_path, output_path):
    """
    """
    with open(input_path) as input_file, open(output_path, "w") as csv_out:
        fields = ["bin_start", "bin_end", "total_bytes",
                  "udp_bytes", "rpl_bytes", "ping_bytes", "coap_bytes",
                  "battery_bytes", "rplinfo_bytes"]
        writer = DictWriter(csv_out, delimiter=",", fieldnames=fields)
        writer.writeheader()
        result = []
        for line in input_file:
            if "<>" in line:
                split_line = line.split("|")
                d = {"bin_start": float(split_line[1].split("<>")[0]),
                     "bin_end": float(split_line[1].split("<>")[1]),
                     "total_bytes": float(split_line[3]),
                     "udp_bytes": float(split_line[5]),
                     "rpl_bytes": float(split_line[7]),
                     "ping_bytes": float(split_line[9]),
                     "coap_bytes": float(split_line[11]),
                     "battery_bytes": float(split_line[13]),
                     "rplinfo_bytes": float(split_line[15])}
                result.append(d)
                writer.writerow(d)
        return result


def rx_cost(message_size):
    """
    Energy consumed in Ah for L bytes received.

    ( 6,055 . L/250 + 7,9 ).10 -9 Ah
    """
    return (6.055 * message_size / 250 + 7.9) * 10 ** -9


def tx_cost(message_size):
    """
    Energy consumed in Ah for L bytes transmitted.

    ( 5,417 . L/250 + 7,5 ).10 -9 Ah
    """
    return (5.417 * message_size / 250 + 7.5) * 10 ** - 9


def custom_mean(s):
    """
    Mean that adapt to the amount of component available
    """
    res = []
    for i in range(max([len(vector) for vector in s])):
        res.append(np.mean([vector[i]
                            for vector in s
                            if len(vector) > i]))
    return res


def custom_std(s):
    """
    Std that adapt to the amount of component available
    """
    res = []
    for i in range(max([len(vector) for vector in s])):
        res.append(np.std([vector[i]
                           for vector in s
                           if len(vector) > i]))
    return res


class Analyze():
    """
    Analyze a PCAP file for every node and every instance

    Output all the information to the good folder of the
    experiment (CSV folder) (the label of the CSV helps for building
    the graph)

    Execute the defined task.
    """

    def __init__(self, result_dir):
        """
        Initialize a Analyze class
        """
        log.info(result_dir)
        self.result_dir = result_dir
        motes = range(1, 16)
        self.hosts = [(int(node["mote_id"]),
                       node_address(int(node["mote_id"])))
                      for node in motes]

        self.serial = PJ(self.result_dir, "serial.log")
        self.message_csv = PJ(self.result_dir, "message.csv")
        self.mac_json = PJ(self.result_dir, "mac.json")
        self.packet_loss_csv = PJ(self.result_dir, "packet_loss.csv")

        # Graph output
        self.graph_json = PJ(self.result_dir, "graph.json")
        self.rpl_tree_json = PJ(self.result_dir, "rpl_tree.json")
        self.radio_tree_json = PJ(self.result_dir, "radio.json")
        self.depth_csv = PJ(self.result_dir, "depth.csv")

        # Estimators
        self.overhead_csv = PJ(self.result_dir, "overhead.csv")

        # Energy
        self.powertracker_log = PJ(self.result_dir, "powertracker.log")
        self.powertracker_csv = PJ(self.result_dir, "powertracker.csv")
        self.depth_energy_csv = PJ(self.result_dir, "depth_energy.csv")

        # PCAP stats
        self.pcap = PJ(self.result_dir, "output.pcap")
        self.pcap_csv = PJ(self.result_dir, "pcap.csv")

        self.tasks_to_do = []

    def __call__(self):
        serial_tasks = [self.mac, self.message, self.packet_loss]
        graph_tasks = [self.rpl_tree, self.radio_tree, self.depth2csv]
        powertracker_tasks = [self.powertracker_to_csv, self.depth_energy]
        pcap_tasks = [self.pcap2csv, self.overhead, self.io]
        pcap_stats_tasks = [self.pcap_stats_udp, self.pcap_stats_ipv6, self.pcap_stats_hosts]

        # Set up like this to be commented easily
        # WARNING: Look at the order of the commands
        self.tasks_to_do.extend(serial_tasks)
        self.tasks_to_do.extend(graph_tasks)
        self.tasks_to_do.extend(powertracker_tasks)
        self.tasks_to_do.extend(pcap_tasks)
        self.tasks_to_do.extend(pcap_stats_tasks)

        p = dummy_pool(2)
        p.map(self.run_task, self.tasks_to_do)
        log.info("All analyze done for %s" % self.result_dir)

    def run_task(self, task):
        try:
            log.info("Starting %s" % task)
            task()
            log.info("Done with %s" % task)
        except Exception as e:
            log.warning(e)
            raise e

    def overhead(self):
        with open(self.pcap_csv) as pcap_csv_f:
            with open(self.overhead_csv, "w") as estimator_overhead_csv_f:
                reader = DictReader(pcap_csv_f)
                fieldnames = ["time", "other", "battery", "rplinfo"]
                writer = DictWriter(estimator_overhead_csv_f, fieldnames)
                writer.writeheader()
                accu = {"battery": 0, "rplinfo": 0, "other": 0, "time": 0}

                for row in reader:
                    if row["data.data"] == "52":
                        accu["rplinfo"] += 1
                        accu["time"] = row["frame.time_relative"]
                        writer.writerow(accu)
                    if row["data.data"] == "42":
                        accu["battery"] += 1
                        accu["time"] = row["frame.time_relative"]
                        writer.writerow(accu)
                    if row["data.data"] not in ["42", "52"]:
                        accu["other"] += 1
                        accu["time"] = row["frame.time_relative"]
                        writer.writerow(accu)


    def mac(self):
        """
        Extract from serial logs all the mac addresses.

        format:
        361 ID:8 MAC 00:12:74:08:00:08:08:08
        """
        pattern = "^(?P<time>\d+)\s+ID:(?P<mote_id>\d+)\s+MAC (?P<mac>\S*)\s+"
        result = {}
        with open(self.serial) as log_file:
            lines = log_file.read()
            for match in re.finditer(pattern, lines, re.MULTILINE):
                d = match.groupdict()
                result[int(d["mote_id"])] = d["mac"]
        with open(self.mac_json, "w") as f:
            f.write(
                json_graph.dumps(
                    result, indent=4, sort_keys=True))


    def depth2csv(self):
        """
        Depth of a node
        """
        with open(self.rpl_tree_json) as rpl_f:
            tree = json_graph.loads(rpl_f.read())

            with open(self.depth_csv, "w") as depth_f:
                writer = DictWriter(depth_f, ["node", "depth"])
                writer.writeheader()
                # sorted to have all depth in the right order
                for node, data in sorted(tree.nodes(data=True)):
                    if "depth" in data:
                        writer.writerow(
                            {"node": node,
                             "depth": data["depth"]})

    def packet_loss(self):
        """
        Compute packet loss ratio by parsing serial log file.
        """
        send_pattern = "^(?P<time>\d+) ID:(?P<node>\d+) D(?P<sender>\d+)"
        received_pattern = "^(?P<time>\d+) ID:(?P<node>\d+) DATA recv (.)* from (?P<sender>\d+)"
        sent, received = defaultdict(float), defaultdict(float)
        with open(self.serial) as serial_file:

            with open(self.packet_loss_csv, "w") as output_file:
                fieldnames = ["time", "node", "avg", "ratio"]
                writer = DictWriter(output_file, fieldnames=fieldnames)
                writer.writeheader()
                for line in serial_file:

                    reception_match = re.search(received_pattern, line)
                    # We trigger the CSV writing only when we received.
                    if reception_match:
                        node = reception_match.group('sender')
                        received[node] += 1.0
                        if received[node] and sent[node]:
                            l = [received[n] / sent[n]
                                 for n in received
                                 if sent[n]]
                            avg = sum(l) / len(l)
                            writer.writerow({
                                "time": reception_match.group("time"),
                                "node": node,
                                "ratio": received[node] / sent[node],
                                "avg": avg})

                    send_match = re.search(send_pattern, line)
                    if send_match:
                        sent[send_match.group('node')] += 1.0


    def pcap_stats_udp(self):
        log_file = PJ(self.result_dir, "exchanges_udp.log")
        self.pcap_stats(stat="conv,udp", output_path=log_file)
        exchanges_to_csv(input_path=log_file,
                         output_path=PJ(self.result_dir, "exchanges_udp.csv"))

    def pcap_stats_ipv6(self):
        log_file = PJ(self.result_dir, "exchanges_ipv6.log")
        self.pcap_stats(stat="conv,ipv6",
                        output_path=log_file)
        exchanges_to_csv(input_path=log_file,
                         output_path=PJ(self.result_dir, "exchanges_ipv6.csv"))

    def pcap_stats_hosts(self):
        result_by_host = {}

        for host_id, host_ip in self.hosts:
            host_ip = "".join(["::", host_ip.split("::")[1]])
            stat = [
                "io", "stat", str(
                    BINS), "udp && ipv6.addr == %s" % host_ip,
                "icmpv6.type==155 && ipv6.addr == %s" % host_ip,
                "( icmpv6.type==128 || icmpv6.type==129 ) && ipv6.addr == %s" % host_ip,
                "coap && ipv6.addr == %s" % host_ip]
            # RPL packets
            # ICMPV6 PING PACKETS
            result_by_host[host_ip] = self.pcap_stats(
                stat=",".join(stat),
                output_path=PJ(self.result_dir, "io_%s.log" % host_ip))

    def pcap2csv(self):
        """
        Execute a simple filter on PCAP and count
        """
        log.info("start pcap2csv")
        with open(self.pcap_csv, "w") as output_file:
            command = ["tshark",
                       "-T", "fields",
                       "-E", "header=y",
                       "-E", "separator=,",
                       "-e", "frame.number",
                       "-e", "frame.time_relative",
                       "-e", "frame.len",
                       "-e", "6lowpan.src",
                       "-e", "6lowpan.dst",
                       "-e", "wpan.src64",
                       "-e", "wpan.dst64",
                       "-e", "icmpv6.type",
                       "-e", "ipv6.src",
                       "-e", "ipv6.dst",
                       "-e", "icmpv6.code",
                       "-e", "udp.srcport",
                       "-e", "udp.dstport",
                       "-e", "coap.tid",
                       "-e", "data.data",
                       "-r", self.pcap]
            log.debug(str(command))
            process = subprocess.Popen(command, stdout=subprocess.PIPE)
            stdout, stderr = process.communicate()
            output_file.write(stdout)


def run(sim_folder):
    step = Analyze(sim_folder)
    step()


if __name__ == '__main__':
    powertracker_to_csv("powertracker.log")
    message()
    depth_energy()
    rpl_tree()
    radio_tree()
    io()
