import csv
import networkx as nx
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
                    to_node = 'End'
                elif line[1] == 'missed':
                    from_node = int(line[0])
                    to_node = 'End'
            currentweight = G[from_node][to_node]['weight'] if G.has_edge(from_node, to_node) else 0
            G.add_edge(from_node, to_node, weight=currentweight+1)
    return G

G = creategraph('stripped_OSUvsIowaGraph.txt')
for edge in G.edges():
    print(edge, G.get_edge_data(edge[0], edge[1]))