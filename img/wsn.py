#!/usr/bin/env python

"""
Analytical Simulator for WSN.

Right now, we don't have any hidden nodes.
"""

import networkx as nx
import pulp
from networkx import set_node_attributes, get_node_attributes
from networkx import shortest_path, Graph
from scipy.stats import linregress
from random import expovariate
from math import exp
import matplotlib.pyplot as plt
from collections import namedtuple

Event = namedtuple('Event', ['time', 'node'])
Battery_state = namedtuple("Battery_state", ["time", "battery"])


class WSN(Graph):
    """
    Modeling a WSN.
    """

    symbol_time = 16 * 10 ** -6
    T_s = 20 * symbol_time
    turnaround = 12 * symbol_time
    T = 1
    c2_Si = exp(1) - 1
    # COST of one transmission
    COST = 0.001
    L = 1.0

    def __init__(self, **attr):
        super(WSN, self).__init__(**attr)
        self.e0 = 1000.0  # Starting energy for every node (mAh)
        self.events = []
        self.mean_no_knowledge = []
        self.mean_hops_count = []
        self.mean_routing = []
        self.mean_pessimist = []
        self.root = None
        self.global_cost = {}

    @property
    def energy(self):
        """
        Energy of every node
        """
        return self.e0
    @energy.setter
    def energy(self, value):
        for node in self:
            set_node_attributes(self, "energy", {node: value})

    @property
    def term(self):
        """
        How long does a specific node has to remain alive
        """
        return self._term
    @term.setter
    def term(self, value):
        self._term = value
    
    
    @property
    def alpha(self):
        """Compute the alpha of a precise node by regarding the neighbors."""
        beta = self.beta
        eta = self.eta
        c = self.c
        for node in self:
            alpha_num = (1 - eta[node]) * (1 - c[node]) * beta[node] * self.T
            alpha_den = eta[node] + (1 - eta[node]) * c[node] +\
                (1 - eta[node]) * (1 - c[node]) * beta[node] * WSN.T
            alpha = float(alpha_num / alpha_den)
            set_node_attributes(self, "alpha", {node: alpha})
        return get_node_attributes(self, "alpha")

    @property
    def c(self):
        beta = self.beta
        for node in self:
            c = 1 - exp(-12 * WSN.T_s * beta[node])
            set_node_attributes(self, "c", {node: c})
        return get_node_attributes(self, "c")

    @property
    def g(self):
        beta = self.beta
        beta_neighbors = self.beta_neighbors
        for node in self:
            g = 1.0 / (beta[node] + beta_neighbors[node])
            set_node_attributes(self, "g", {node: g})
        return get_node_attributes(self, "g")

    @property
    def eta(self):
        beta = self.beta
        beta_neighbors = self.beta_neighbors
        for node in self:
            eta = beta[node]
            eta /= beta[node] + beta_neighbors[node]
            set_node_attributes(self, "eta", {node: eta})
        return get_node_attributes(self, "eta")

    @property
    def beta_neighbors(self):
        beta = self.beta
        for node in self:
            beta_neighbor = sum(
                [beta[neighbor] for neighbor in self.neighbors(node)])
            set_node_attributes(
                self, "beta_neighbors", {node: float(beta_neighbor)})
        return get_node_attributes(self, "beta_neighbors")

    @property
    def v(self):
        return []

    @property
    def expected_si(self):
        return []

    @property
    def theta(self):
        v = self.v
        delta = self.delta
        for node in self:
            theta = v[node] * (1 - delta[node])
            set_node_attributes(self, "theta", {node: theta})
        return get_node_attributes(self, "theta")

    @property
    def gamma(self):
        p = self.p
        l = self.l
        for node in self:
            gamma = p[node] + (1 - p[node]) * l[node]
            set_node_attributes(self, "gamma", {node: gamma})
        return get_node_attributes(self, "gamma")

    @property
    def l(self):
        for node in self:
            set_node_attributes(self, "l", {node: WSN.L})
        return get_node_attributes(self, "l")

    @property
    def delay(self):
        path = self.path
        sojourn = self.sojourn
        for node in self:
            delay = 0.0
            for step in path(node):
                delay += sojourn[step]
            set_node_attributes(self, "delay", {node: delay})
        return get_node_attributes(self, "delay")

    @property
    def path(self):
        for node in self:
            p = shortest_path(self, node, self.root)
            set_node_attributes(self, "path", {node: p})
        return get_node_attributes(self, "path")

    @property
    def delta(self):
        """ Read the formula from right to left"""
        alpha = self.alpha
        gamma = self.gamma
        for node in self:
            delta = alpha[node] ** 5 + \
                (1.0 - alpha[node] ** 5) * gamma[node]
            delta = alpha[node] ** 5 + \
                (1.0 - alpha[node] ** 5) * gamma[node] * delta
            delta = alpha[node] ** 5 + \
                (1.0 - alpha[node] ** 5) * gamma[node] * delta
            delta = alpha[node] ** 5 + \
                (1.0 - alpha[node] ** 5) * gamma[node] * delta
            set_node_attributes(self, "delta", {node: delta})
        return get_node_attributes(self, "delta")

    @property
    def rho(self):
        return []

    @property
    def c2_si(self):
        return []

    @property
    def c2_ai(self):
        return []

    @property
    def sojourn(self):
        rho = self.rho
        c2_ai = self.c2_ai
        c2_si = self.c2_si
        expected_si = self.expected_si
        for node in self:
            sojourn = rho[node] * expected_si[node] * (c2_si[node] + c2_ai[node])
            sojourn /= 2 * (1 - rho[node])
            sojourn += expected_si
            set_node_attributes(self, "sojourn", {node: sojourn})
        return get_node_attributes(self, "sojourn")

    def node_at_depth(self, level):
        """
        Returns the node that are at at level hops from "root".
        """
        return [node
                for node in self
                if len(shortest_path(self, self.root, node))
                == level]

    def depth(self, node):
        return len(shortest_path(
            self, node, self.root))

    @property
    def beta(self):
        return get_node_attributes(self, "beta")

    @property
    def p(self):
        beta_neighbors = self.beta_neighbors
        c = self.c
        eta = self.eta
        for node in self:
            p = eta[node]
            p *= (1 - exp(-12 * WSN.T_s * beta_neighbors[node]))
            p += (1 - eta[node]) * c[node]
            p /= 1 - (1 - eta[node]) * (1 - c[node])
            set_node_attributes(self, "p", {node: p})
        return get_node_attributes(self, "p")

    @property
    def packet_lose(self):
        delta = self.delta
        for node in self:
            loss_probability = 1.0
            for step in shortest_path(self, node, self.root):
                loss_probability *= 1 - delta[step]
            set_node_attributes(self, "loss_probability",
                                   {node: loss_probability})
        return get_node_attributes(self, "loss_probability")

    def generate_traffic(self, simulation_time=100, mean=1.0):
        """
        Generate the arrival time for a node with a simulation time and a
        Poisson parameter
        """
        events_pool = []
        for node in self:
            time = 0
            while True:
                inter = expovariate(mean)
                time += inter
                if time < simulation_time:
                    events_pool.append(Event(node=node, time=time))
                else:
                    break
        self.events = sorted(events_pool)

    @property
    def cost(self, method="exp", parameter=1.0):
        """
        Cost of transmission for a specific node
        """
        if method == "exp":
            return {node: expovariate(parameter / WSN.COST) for node in self}
        if method == "constant":
            return {node: parameter for node in}

    def apply_traffic(self):
        """
        Give the average energy reserve in a WSN at a precise moment
        """
        transmissions = {node: 0.0 for node in self}
        contributions = {node: 0.0 for node in self}
        forwarding = {node: 0.0 for node in self}
        pessimist = {node: 0.0 for node in self}

        events = self.events
        node_at_depth = self.node_at_depth
        cost = self.cost
        path = self.path
        depth = self.depth
        n = len(self)
        for event in events:
            # First estimator only the transmission cost
            transmissions[event.node] += cost[event.node]
            self.mean_no_knowledge.append(
                self.e0 - sum(transmissions.values()) / n)

            # Second estimator
            for level in range(1, depth(event.node)):
                card_level = len(node_at_depth(level))
                for node in self.node_at_depth(level):
                    contributions[node] += cost[node] / card_level
            self.mean_hops_count.append(self.e0 - sum(transmissions.values() + contributions.values()) / n)

            # Third estimator where all the routes are known
            for forwarder in path[event.node]:
                forwarding[forwarder] += cost[event.node]
            self.mean_routing.append(self.e0 - sum(transmissions.values() + forwarding.values()) / n)

            # Pessimist estimator where all neighbors of all forwarder pays
            for forwarder in path[event.node]:
                for neighbor in self.neighbors(forwarder):
                    pessimist[neighbor] += cost[neighbor]
            self.mean_pessimist.append(self.e0 - sum(transmissions.values() + pessimist.values()) / n)
        self.global_cost = {node: forwarding[node] + transmissions[node] for node in network}


if __name__ == "__main__":

    LAMBDA_RATE = 1.0

    network = WSN()

    network.add_nodes_from(["1a", "1c", "1d", "1e", "e", "a", "1", "12", "13",
                            "14", "16", "17", "18", "19", "5", "6", "7", "8",
                            "9"], beta=LAMBDA_RATE)

    network.add_edges_from([("9", "6"), ("6", "18"), ("18", "5"), ("5", "1"),
                            ("1c", "8"), ("8", "13"), ("13", "16"), ("13",
                                                                     "1d"),
                            ("16", "17"), ("17", "1"), ("1e", "e"), ("e", "1"),
                            ("19", "e"), ("12", "7"), ("7", "1a"), ("1a",
                                                                    "14"),
                            ("14", "1"), ("1d", "a")], energy=1)

    network.root = "1"

    wsn_model = pulp.LpProblem("WSN cache allocation", pulp.LpMaximize)
    wsn_model += plancher

    # constraints
    wsn_model += 

    # Solving our model for this step. We might have to redo this several time
    # for each bottleneck present in the WSN
    wsn_model.solve()

    for l in lambdas:
        print l

    print 1/0


    # Oracle
    x = []
    y = []
    voltage = 3.5
    intensity = 22 * 0.001
    with open("base.log") as f:
        for line in f:
            time_elapsed_on = int(line.split()[2]) / 1000000
            ratio = float(line.split()[4].replace(",", ".")) / 100
            if ratio > 0:
                x.append(time_elapsed_on / ratio)
                y.append(time_elapsed_on)
    y = [network.e0 - intensity * t for t in y]
    plt.plot(x, y, label="oracle")

    network.generate_traffic(simulation_time=500)
    network.apply_traffic()

    node_size = [300 * cost for cost in network.global_cost.values()]

    plt.text(0.5, 0.97, "Node size: Amount of traffic exchanged",
         horizontalalignment='center', transform=plt.gca().transAxes)
    pos = nx.graphviz_layout(network, prog='twopi')
    for node in network:
        nx.draw(network, pos, nodelist=[node],
            node_size=300*network.global_cost[node], alpha=.7, with_labels=True)
    pwet = plt.axis('equal')
    plt.show()


    plt.figure(1)
    ax = plt.subplot(111)

    events = [event.time for event in network.events]

    # First estimation
    mean_no_knowledge_slope, mean_no_knowledge_intercept = linregress(events, network.mean_no_knowledge)[:2]
    plt.plot(events, network.mean_no_knowledge, "g", label="No knowledge")
    plt.plot(x,
         [mean_no_knowledge_slope * t + mean_no_knowledge_intercept for t in x],
         "g--",
         label="No knowledge forecast")


    # Second estimation
    mean_hops_count_slope, mean_hops_count_intercept = linregress(events, network.mean_hops_count)[:2]
    plt.plot(events, network.mean_hops_count, "m", label="Hops known")
    plt.plot(x,
         [mean_hops_count_slope * t + mean_hops_count_intercept for t in x],
         "m--",
         label="Hops known forecast")

    # Third estimation
    mean_routing_slope, mean_routing_intercept = linregress(events, network.mean_routing)[:2]
    plt.plot(events, network.mean_routing, "r", label="Routes known")
    plt.plot(x,
         [mean_routing_slope * t + mean_routing_intercept for t in x],
         "r--",
         label="Routing known forecast")


    # Forth estimation
    mean_pessimist_slope, mean_pessimist_intercept = linregress(events, network.mean_pessimist)[:2]
    plt.plot(events, network.mean_pessimist, "k", label="Pessimist")
    plt.plot(x,
         [mean_pessimist_slope * t + mean_pessimist_intercept for t in x],
         "k--",
         label="Pessimist forecast")


    ax.set_xlabel('time')
    ax.set_ylabel("battery level")

    plt.legend()
    plt.show()