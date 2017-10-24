#!/usr/bin/env python

import csv
import itertools
import operator
import os
import networkx as nx
import scipy.interpolate
from networkx.readwrite import json_graph
import logging
from os.path import join as PJ
from analyze import tx_cost, rx_cost

log = logging.getLogger("estimators")


class Estimator(object):
    """
    General Estimator Workflow.
    """
    default_rx_rate = 30
    default_tx_rate = 30
    size = 100

    def __init__(self, radio_graph=None, rpl_graph=None, serial_logs=None, energy_csv=None):
        """


        :param radio_graph:
        :param rpl_graph:
        :param serial_logs:
        :type radio_graph:
        """

        ###################
        # Graph preparing #
        ###################

        # Caching all routes and interaction path.
        # Because we have a directed graph, all routes are unique.

        self.radio_graph = None
        with open(radio_graph) as f:
            self.radio_graph = json_graph.loads(f.read())
        self.rpl_graph = None
        with open(rpl_graph) as f:
            self.rpl_graph = json_graph.loads(f.read())
        self.nodes = self.radio_graph.nodes()
        self.route_path = {n: nx.shortest_path(self.rpl_graph, n,
                                               self.rpl_graph.graph["root"])
                           for n in self.rpl_graph.nodes()}

        # We use the route stored in self.route_path, for each node in the path
        # minus the final destination, we compute all the neighbors of a node.
        # This nodes will be the one over hearing when a transmission occurs.
        self.radio_path = {n: list(itertools.chain(*[self.radio_graph.neighbors(n_)
                                                     for n_ in self.route_path[n][:-1]]))
                           for n in self.route_path}

        self.root = self.rpl_graph.graph["root"]

        #####################
        # Message preparing #
        #####################

        # Preparing the list of power_tracker messages for each node
        self.power_tracker_rows = {n: [] for n in self.nodes}
        with open(energy_csv) as energy_f:
            for row in csv.DictReader(energy_f):
                mote_id = int(row["mote_id"])
                message = {"time": float(row["monitored_time"]),
                           "energy": float(row["energy_consumed"]),
                           "message_type": "energy"}
                self.power_tracker_rows[mote_id].append(message)

        # Preparing the list of serial messages for each nodes
        self.serial_logs = {n: [] for n in self.nodes}
        with open(serial_logs) as f:
            reader = csv.DictReader(f)
            for row in reader:
                row = {k: v for k, v in row.items() if v}
                message = {"message_type": row["message_type"],
                           "time": float(row["time"]),
                           "size": Estimator.size}

                # Beware of choosing the right node for the message
                node = None
                if "source" in row and message["message_type"] == "data":
                    message["source"] = int(row["source"])
                    message["destination"] = self.root
                    node = message["source"]

                if "destination" in row and message["message_type"] == "reply":
                    message["source"] = self.root
                    message["destination"] = int(row["destination"])
                    node = message["destination"]

                if message["message_type"] == "battery_recalibration":
                    message["source"] = int(row["mote_id"])
                    message["destination"] = self.root
                    node = message["source"]

                self.serial_logs[node].append(message)

        # Fusion power_tracker and serial
        # IMPORTANT: We sort messages by time
        self.messages = {n: sorted(list(itertools.chain(self.serial_logs[n],
                                                        self.power_tracker_rows[n])),
                                   key=operator.itemgetter("time"))
                         for n in self.nodes}

        ###########################
        # Interpolation of energy #
        ###########################

        # Create interpolated power_tracker to have a power_tracker
        # results event when no one is available.
        self.interpolated_power_tracker = {}
        for n in self.nodes:
            time = [x["time"] for x in self.messages[n] if x["message_type"] == "energy"]
            energy = [x["energy"] for x in self.power_tracker_rows[n]]
            f = scipy.interpolate.UnivariateSpline(time, energy)
            self.interpolated_power_tracker[n] = f

        ###########################
        # Recalculation preparing #
        ###########################

        # Bytes received/transmitted each seconds.
        # This is useful at the beginning of the run when no information
        # is available.
        self.default_rx_rate = {n: Estimator.default_rx_rate for n in self.nodes}
        self.default_tx_rate = {n: Estimator.default_tx_rate for n in self.nodes}

        # Derive of the energy consumption. Initialize to None
        # to avoid using a wrong derive.
        self.derivative = {n: {"time": [0.0], "derivative": [0.0]}
                           for n in self.nodes}

        # Note: Doesn't depend on estimators
        self.recalibration = {n: {"energy": [0.0], "time": [0.0]}
                              for n in self.nodes}

        ######################
        # Estimators logging #
        ######################

        for kind in ["noinfo", "route", "radio"]:
            setattr(self, kind, {n: {"energy": [0.0], "time": [0.0],
                                     "estimation": [0.0], "difference": [0.0]}
                                 for n in self.nodes})

    def trend(self, node, current_e, current_t):
        """
        current_e and current_t are Measured by power_tracker
        :param node:
        :param current_e:
        :param current_t:
        Take into account:

        - source and destination of a message.
        - Derivative of a energy consumption

        TODO: Beware of threshold to really change the trend
        """
        # Fetching the last exact value known
        last_e = self.recalibration[node]["energy"][-1]
        last_t = self.recalibration[node]["time"][-1]

        # Beware threshold
        #if current_t - last_t > threshold:
        self.recalibration[node]["time"].append(current_t)
        self.recalibration[node]["energy"].append(current_e)

        # Derivative
        # f1(x) = f(x0) + (x-x0) f '(x0)
        # estimated_e = last_e + (current_e - last_e) * (time - last_t) / (message_time - last_t)
        d = (last_e - current_e) / (last_t - current_t)
        return d

    def noinfo_estimation(self, message):
        """
        Simply account for source and destination
        :param message:
        """
        res = {n: 0.0 for n in self.nodes}
        res[message["source"]] = tx_cost(message["size"])
        res[message["destination"]] = rx_cost(message["size"])
        return res

    def route_estimation(self, message):
        """
        For a given message this will estimate the energy consumed by
        all nodes forwarding the message through the RPL tree.

        :param message:
        """
        res = {n: 0.0 for n in self.nodes}
        transmitters = self.route_path[message["source"]]
        # Forwarders of the message
        for n in transmitters[1: -1]:
            res[n] = rx_cost(message["size"]) + tx_cost(message["size"])
        res[message["source"]] += tx_cost(message["size"])
        res[message["destination"]] += rx_cost(message["size"])
        return res

    def radio_estimation(self, message):
        """
        For a given message, this will estimate the energy consumed by
        nodes that over hear the message transmission.
        """
        # Starting as route
        transmitters = self.route_path[message["source"]]
        res = {n: 0.0 for n in self.nodes}
        for n in transmitters[1: -1]:
            res[n] = rx_cost(message["size"]) + tx_cost(message["size"])

        res[message["source"]] += tx_cost(message["size"])
        res[message["destination"]] += rx_cost(message["size"])

        # Sending to all listener nodes a rx_cost. In particular
        # a same node could receive several time the same message.
        for listener in self.radio_path[message["source"]]:
            res[listener] += rx_cost(message["size"])

        return res

    def update_estimator(self, estimator, node, energy=None, time=None, estimation=None, difference=None):
        getattr(self, estimator)[node]["energy"].append(energy)
        getattr(self, estimator)[node]["estimation"].append(estimation)
        getattr(self, estimator)[node]["difference"].append(difference)
        getattr(self, estimator)[node]["time"].append(time)

    def estimate(self):
        """
        Estimation occurs here
        """
        for current_node in self.nodes:

            # self.messages contains power_tracker and serial messages.
            for message in self.messages[current_node]:

                current_t = message["time"]
                current_e = self.interpolated_power_tracker[current_node](current_t)

                if message["message_type"] == "battery_recalibration":

                    # We update all estimators with the last value
                    for estimator in ["noinfo", "route", "radio"]:
                        self.update_estimator(estimator, current_node,
                                              energy=current_e,
                                              estimation=current_e,
                                              difference=0.0,
                                              time=current_t)

                    # Compute the derivative
                    # Beware the trend can only be computed with real information
                    # otherwise we have an auto reference problem with each estimator.
                    d = self.trend(current_node, current_e, current_t)
                    self.derivative[current_node]["time"].append(current_t),
                    self.derivative[current_node]["derivative"].append(d)

                    # Update recalibration
                    # Beware of checking the derivative.
                    self.recalibration[current_node]["time"].append(current_t)
                    self.recalibration[current_node]["energy"].append(current_e)

                # If we miss any information about what's going on in the
                # network we simply add the trend computed by real information
                if message["message_type"] == "energy":
                    d = self.derivative[current_node]["derivative"][-1]
                    for estimator in ["noinfo", "route", "radio"]:
                        last_e = getattr(self, estimator)[current_node]["energy"][-1]
                        last_t = getattr(self, estimator)[current_node]["time"][-1]
                        estimation = last_e + d * (current_t - last_t)
                        diff = abs(estimation - current_e) / current_e
                        self.update_estimator(estimator, current_node,
                                              energy=current_e,
                                              estimation=estimation,
                                              difference=diff,
                                              time=current_t)

                # BEWARE: Right now we add the trend and the transaction
                # maybe we are counting the same thing twice.
                if message["message_type"] == "data":
                    for estimator in ["noinfo", "route", "radio"]:
                        transaction = getattr(self, "%s_estimation" % estimator)(message)
                        last_e = getattr(self, estimator)[current_node]["energy"][-1]
                        last_t = getattr(self, estimator)[current_node]["time"][-1]
                        for n, transaction_cost in transaction.items():
                            # Real is approach here
                            estimation = last_e + transaction_cost
                            # At the beginning, d is not defined
                            d = self.derivative[n]["derivative"][-1]
                            if d:
                                estimation += d * (current_t - last_t)
                            diff = abs(estimation - current_e) / current_e
                            self.update_estimator(estimator, current_node,
                                                  energy=current_e,
                                                  estimation=estimation,
                                                  difference=diff,
                                                  time=current_t)

    def save(self, simulation_folder=None):
        """

        :param simulation_folder:
        """
        log.info("Save sim: %s" % simulation_folder)
        grid = itertools.product(self.nodes, ["noinfo", "route", "radio"])
        for (node, target) in grid:
            path = PJ(simulation_folder, "%d_%s.csv" % (node, target))
            with open(path, "w") as f:
                csv_writer = csv.DictWriter(f, ["time", "energy", "estimation", "difference"])
                csv_writer.writeheader()
                temp = zip(
                    getattr(self, target)[node]["time"],
                    getattr(self, target)[node]["energy"],
                    getattr(self, target)[node]["estimation"],
                    getattr(self, target)[node]["difference"],
                )
                for time, energy, estimation, difference in temp:
                    csv_writer.writerow({
                        "time": time,
                        "energy": energy,
                        "estimation": estimation,
                        "difference": difference
                    })


def run(sim_folder):
    try:
        e = Estimator(radio_graph=PJ(sim_folder, "radio_tree.json"),
                      rpl_graph=PJ(sim_folder, "rpl_tree.json"),
                      serial_logs=PJ(sim_folder, "messages.csv"),
                      energy_csv=PJ(sim_folder, "powertracker.csv"))

        for node in e.nodes:

            path = PJ(sim_folder, "debug_messages_%d" % node)
            with open(path, "w") as f:
                csv_writer = csv.DictWriter(f, ["time", 'source', 'destination', 'size', 'message_type', 'energy'])
                csv_writer.writeheader()
                for d in e.messages[node]:
                    csv_writer.writerow(d)

            path = PJ(sim_folder, "debug_derivative_%d" % node)
            with open(path, "w") as f:
                csv_writer = csv.DictWriter(f, ["time", "derivative"])
                csv_writer.writeheader()
                grid = zip(e.derivative[node]["time"], e.derivative[node]["derivative"])
                for time, derivative in grid:
                    csv_writer.writerow({"time": time, "derivative": derivative})

            path = PJ(sim_folder, "debug_recalibration_%d" % node)
            with open(path, "w") as f:
                csv_writer = csv.DictWriter(f, ["time", "energy"])
                csv_writer.writeheader()
                grid = zip(e.recalibration[node]["time"], e.recalibration[node]["energy"])
                for time, energy in grid:
                    csv_writer.writerow({"time": time, "energy": energy})

        e.estimate()

        # Saving to file
        e.save(simulation_folder=sim_folder)

    except Exception as e:
        log.warning(e)
        raise e


if __name__ == '__main__':
    run(".")
