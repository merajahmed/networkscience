__author__ = 'anirban'
import csv
import json

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
            first_site = prev_row[2]
            second_site = row[2]

            if second_site in start_nodes:
                prev_row = row
                continue

            if G.has_edge(first_site, second_site):
                G[first_site][second_site]['weight'] += 1
            else:
                G.add_edge(first_site, second_site, weight=1)

            prev_row = row
    return G


def jsonify_graph(graphobj, graphfile):
    G = graphobj
    json.dump(json_graph.node_link_data(G), open(graphfile,'w'),indent=2)


jsonify_graph(creategraph('possession.csv'), 'possession_graph.json')
# print G.edge
# pos = nx.spring_layout(G)
# nx.draw_networkx_nodes(G, pos, node_size=1000)
# nx.draw_networkx_edges(G, pos, width=1)
# nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')
# plt.axis('off')
# plt.savefig('weighted_graph.png')
# plt.show()