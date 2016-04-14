import csv

import networkx as nx
from collections import OrderedDict
import operator
import numpy as np

__author__ = 'meraj'


def creategraph(graphfilename):
    G = nx.DiGraph()
    with open(graphfilename, 'r') as graphfile:
        reader = csv.reader(graphfile, delimiter=' ')
        for line in reader:
            from_node = None
            to_node = None
            if len(line) == 2:
                continue
            if len(line) == 4:
                from_node = 'Start'
                to_node = int(line[2])
            elif len(line) == 3:
                #separate cases so as to decide edge weights later based on action, and other conditions
                if line[1] == 'to':
                    from_node = int(line[0])
                    to_node = int(line[2])
                elif line[1] == 'made':
                    from_node = int(line[0])
                    to_node = 'MADE'
                elif line[1] == 'missed':
                    from_node = int(line[0])
                    to_node = 'MISSED'
            currentweight = G[from_node][to_node]['weight'] if G.has_edge(from_node, to_node) else 0
            G.add_edge(from_node, to_node, weight=currentweight+1)
    return G

def calculate_degree_centrality(G):
    node_degrees = dict()
    for edge in G.edges():
        node_1 = edge[0]
        node_2 = edge[1]
        weight = G.get_edge_data(node_1, node_2)
        node_degrees[node_1] = node_degrees.get(node_1, 0)+weight['weight']
        node_degrees[node_2] = node_degrees.get(node_2, 0)+weight['weight']
    ordered_degrees = OrderedDict(sorted(node_degrees.items(),key=operator.itemgetter(1),reverse=True))
    sum_degrees = sum(ordered_degrees.values())
    for key in ordered_degrees:
        ordered_degrees[key] = ordered_degrees[key]/float(sum_degrees)
    ordered_degrees.pop('MADE')
    ordered_degrees.pop('MISSED')
    ordered_degrees.pop('Start')
    graph_centrality = 0
    max_degree = ordered_degrees.itervalues().next()
    for node in ordered_degrees:
        graph_centrality += (max_degree-ordered_degrees[node])
    graph_centrality /= len(G.nodes())
    return ordered_degrees, graph_centrality


def calculate_entropy(G):
    nodes = G.nodes()
    nodes.remove('Start')
    size = len(nodes)
    total_weight = 0
    probability_array = np.ndarray(shape=(size,size), dtype=float)
    for i in range(size):
        for j in range(size):
            if G.has_edge(nodes[i], nodes[j]):
                probability_array[i][j] = G.get_edge_data(nodes[i], nodes[j])['weight']
            else:
                probability_array[i][j] = 0
            total_weight += probability_array[i][j]
    probability_array /= total_weight
    entropy = 0
    for i in range(size):
        for j in range(size):
            p = probability_array[i][j]
            if p != 0:
                entropy -= p*np.log2(p)
    return entropy



G = creategraph('OSUvsIowaGraph.txt')
print(calculate_entropy(G))
print(calculate_degree_centrality(G))