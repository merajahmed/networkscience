import csv
import math
import networkx as nx
from collections import OrderedDict
import operator
import numpy as np
import copy
from operator import itemgetter
import os
__author__ = 'meraj'


def creategraph(graphfilename):
    G = nx.DiGraph()
    with open(graphfilename, 'r') as graphfile:
        reader = csv.reader(graphfile, delimiter=' ')
        for line in reader:
            from_node = None
            to_node = None
            if len(line) == 4 and line[3] == '':
                line.pop()
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


def calculate_degree_centrality(OG, start_nodes, end_nodes):
    G = copy.deepcopy(OG)
    node_degrees = dict()
    for edge in G.edges():
        node_1 = edge[0]
        node_2 = edge[1]
        weight = G.get_edge_data(node_1, node_2)
        node_degrees[node_1] = node_degrees.get(node_1, 0)+weight['weight']
        node_degrees[node_2] = node_degrees.get(node_2, 0)+weight['weight']
    ordered_degrees = OrderedDict(sorted(node_degrees.items(), key=operator.itemgetter(1), reverse=True))
    sum_degrees = sum(ordered_degrees.values())
    for key in ordered_degrees:
        ordered_degrees[key] = ordered_degrees[key]/float(sum_degrees)
    for node in start_nodes+end_nodes:
        ordered_degrees.pop(node)
    graph_centrality = 0
    max_degree = ordered_degrees.itervalues().next()
    for node in ordered_degrees:
        graph_centrality += (max_degree-ordered_degrees[node])
    graph_centrality /= len(G.nodes())
    return ordered_degrees, graph_centrality


def calculate_entropy(OG, start_nodes):
    G = copy.deepcopy(OG)
    nodes = G.nodes()
    for node in start_nodes:
        nodes.remove(node)
    size = len(nodes)
    total_weight = 0
    probability_array = np.ndarray(shape=(size, size), dtype=float)
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


def get_pass_probability(player1, player2, OG, start_nodes, end_nodes):
    G = copy.deepcopy(OG)
    pass_weight = 0
    if G.has_edge(player1, player2):
        pass_weight = G.get_edge_data(player1, player2)['weight']
    else:
        return 0
    nodes = G.nodes()
    total_weight = 0.0
    for node in start_nodes+end_nodes:
        nodes.remove(node)
    for node in nodes:
        if G.has_edge(player1, node):
            total_weight += G.get_edge_data(player1, node)['weight']
    return pass_weight/float(total_weight)


def get_shot_rate(player, OG, made_nodes, miss_nodes):
    G = copy.deepcopy(OG)
    hit_count = 0.0
    miss_count = 0.0
    shot_rate = 0.0
    for node in made_nodes:
        if G.has_edge(player, node):
            hit_count = G.get_edge_data(player, node)['weight']
        else:
            return 0
    for node in miss_nodes:
        if G.has_edge(player, node):
            miss_count = G.get_edge_data(player, node)['weight']
    return hit_count/float(hit_count+miss_count)


def get_flux(OG, start_nodes, end_nodes, made_nodes, miss_nodes):
    G = copy.deepcopy(OG)
    nodes = G.nodes()
    for node in start_nodes+end_nodes:
        nodes.remove(node)
    flux = 0.0
    for node1 in nodes:
        for node2 in nodes:
            flux += (get_pass_probability(node1, node2, G, start_nodes, end_nodes)*(get_shot_rate(node1, G, made_nodes, miss_nodes)-get_shot_rate(node2, G, made_nodes, miss_nodes)))
    return flux


def clustering_coefficient(G, cutoff, start_nodes, end_nodes):
    TG = threshold_graph_ranked(G, cutoff, start_nodes, end_nodes)
    nodes = TG.nodes()
    for edge in TG.edges():
        if TG.has_edge(edge[1], edge[0]):
            TG.add_edge(edge[1], edge[0], weight=TG.get_edge_data(edge[0], edge[1])['weight']+TG.get_edge_data(edge[1], edge[0])['weight'])
            TG.add_edge(edge[0], edge[1], weight=TG.get_edge_data(edge[0], edge[1])['weight']+TG.get_edge_data(edge[1], edge[0])['weight'])
    TG = TG.to_undirected()
    return nx.clustering(TG)


def threshold_graph(G, cutoff, start_nodes, end_nodes):
    TG = copy.deepcopy(G)
    for node in start_nodes+end_nodes:
        TG.remove_node(node)
    for node in G.nodes():
        all_edges = TG.edges(node)
        total_weight = 0.0
        for edge in all_edges:
            total_weight += TG.get_edge_data(*edge)['weight']
        cutoff_weight = math.floor(cutoff*total_weight)
        for edge in all_edges:
            if TG.get_edge_data(*edge)['weight'] < cutoff_weight:
                TG.remove_edge(*edge)
    return TG


def threshold_graph_ranked(G, cutoff, start_nodes, end_nodes):
    TG = copy.deepcopy(G)
    for node in start_nodes+end_nodes:
        TG.remove_node(node)
    for node in G.nodes():
        all_edges = TG.edges(node)
        weighted_edges = list()
        for edge in all_edges:
            weighted_edges.append((edge, TG.get_edge_data(*edge)['weight']))
        ordered_edges = sorted(weighted_edges, key=itemgetter(1), reverse=True)
        thresholded_edges = ordered_edges[:int(math.ceil(cutoff*len(ordered_edges)))]
        pruned_edges = filter(lambda x: x not in thresholded_edges, ordered_edges)
        for edge in pruned_edges:
            TG.remove_edge(*edge[0])
    return TG


def calculate_measures():
    graph_files = os.listdir('college_games')
    for graph_file in graph_files:
        nxgraph = creategraph('college_games/'+graph_file)
        print('file name:' , graph_file)
        print('clustering coefficient:' , clustering_coefficient(nxgraph, 0.8, ['Start'], ['MADE', 'MISSED']))
        print('entropy:' , calculate_entropy(nxgraph, ['Start']))
        print('flux:' , get_flux(nxgraph, ['Start'], ['MADE', 'MISSED'], ['MADE'], ['MISSED']))
        print('degree centrality:' , calculate_degree_centrality(nxgraph, ['Start'], ['MADE', 'MISSED']))
calculate_measures()