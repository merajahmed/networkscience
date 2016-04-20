__author__ = 'anirban'
import csv

import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()

start_nodes = [0, 1, -4, -5]
end_nodes = [-2, -3, -1, -6]

with open('possession.csv', 'rb') as f:
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

        if first_site in end_nodes:
            continue

        if second_site in start_nodes:
            continue

        if G.has_edge(first_site, second_site):
            G[first_site][second_site]['weight'] += 1
        else:
            G.add_edge(first_site, second_site, weight=1)

        prev_row = row

print G.edge
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos, node_size=1000)
nx.draw_networkx_edges(G, pos, width=1)
nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')
plt.axis('off')
plt.savefig('weighted_graph.png')
plt.show()