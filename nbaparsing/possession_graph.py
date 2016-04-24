__author__ = 'anirban'
import csv
import json
import math
import networkx as nx
from networkx.readwrite import json_graph


def creategraph(possessionfilename):
    G = nx.DiGraph()
    start_nodes = [0, 1, -4, -5]
    end_nodes = [-2, -3, -1, -6]

    with open(possessionfilename, 'rb') as f:
        file_reader = csv.reader(f)

        for index, row in enumerate(file_reader):
            if index == 0:
                continue
            else:
                prev_row = row
                break

        for index, row in enumerate(file_reader):
            first_site = int(prev_row[2])
            second_site = int(row[2])

            if second_site in start_nodes:
                prev_row = row
                continue

            if first_site in end_nodes:
                print prev_row, row
                print first_site, second_site
                print 'yolo'

            if G.has_edge(first_site, second_site):
                G[first_site][second_site]['weight'] += 1
            else:
                G.add_edge(first_site, second_site, weight=1)

            prev_row = row
    return G


def jsonify_graph(graphobj, graphfile):
    G = graphobj
    start_nodes = [0, 1, -4, -5]
    end_nodes = [-2, -3, -1, -6]
    j = json_graph.node_link_data(G)
    print j['nodes']
    i = 0
    k = 0

    for id_pair in j['nodes']:
        if id_pair['id'] in start_nodes:
            i += 1
            id_pair['x'] = 50
            id_pair['y'] = 100 * i
            id_pair['fixed'] = True

        if id_pair['id'] in end_nodes:
            k += 1
            id_pair['x'] = 700
            id_pair['y'] = 100 * k
            id_pair['fixed'] = True

    json.dump(j, open(graphfile, 'w'), indent=2)

def jsonify_vis(graphobj, graphfile):
    G = graphobj
    visgraph = dict()
    start_nodes = [0, 1, -4, -5]
    end_nodes = [-2, -3, -1, -6]
    start_count = 0
    end_count = 0
    visgraph['nodes'] = list()
    visgraph['edges'] = list()
    start_y = [300, 150, -150, -300]
    end_y = [300, 150, -150, -300]
    num_nodes = len(G.nodes()) - 8
    angle_multiplier = 0
    slices = 2*math.pi/num_nodes
    radius = 300
    for node in G.nodes():
        if node in start_nodes:
            visgraph['nodes'].append({'id': node, 'x': -400, 'y': start_y.pop(), 'group': 'start', 'fixed': True})
            print('start')
        elif node in end_nodes:
            visgraph['nodes'].append({'id': node, 'x': 400, 'y': end_y.pop(), 'group': 'end', 'fixed': True})
        else:
            angle = slices * angle_multiplier
            visgraph['nodes'].append({'id': node, 'x': int(radius*math.cos(angle)), 'y': int(radius*math.sin(angle)), 'group': 'players'})
            # visgraph['nodes'].append({'id': node})
            angle_multiplier += 1
    max_weight = max([G.get_edge_data(edge[0], edge[1])['weight'] for edge in G.edges()])
    min_weight = min([G.get_edge_data(edge[0], edge[1])['weight'] for edge in G.edges()])
    for edge in G.edges():
        if edge[0] == edge[1]:
            continue
        weight = G.get_edge_data(edge[0], edge[1])['weight']
        color = {'color':'red', 'opacity':(weight-min_weight)/float(max_weight-min_weight)}
        visgraph['edges'].append({'from': edge[0], 'to': edge[1], 'value': weight, 'arrows': 'to','color':color,'smooth':False})
    json.dump(visgraph, open(graphfile, 'w'), indent=2)

jsonify_graph(creategraph('possession.csv'), 'possession_graph.json')
# print G.edge
# pos = nx.spring_layout(G)
# nx.draw_networkx_nodes(G, pos, node_size=1000)
# nx.draw_networkx_edges(G, pos, width=1)
# nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')
# plt.axis('off')
# plt.savefig('weighted_graph.png')
# plt.show()
