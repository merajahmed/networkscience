import networkx as nx
import csv
from collections import OrderedDict
import matplotlib.pyplot as plt

__author__ = 'Anirban and Meraj'


class DataNetwork:
    GRAPH_TYPE_DICT = {'directed': nx.DiGraph,
                       'undirected': nx.Graph,
                       'multidirected': nx.MultiDiGraph,
                       'multiundirected': nx.MultiGraph}

    CENTRALITY_DICT = {'in_degree': nx.in_degree_centrality,
                       'out_degree': nx.out_degree_centrality,
                       'degree': nx.degree_centrality,
                       'closeness': nx.closeness_centrality,
                       'betweeness': nx.betweenness_centrality,
                       'eigen': nx.eigenvector_centrality,
                       'page_rank': nx.pagerank}

    def __init__(self, filename, data_type, graph_type):  # where data_type is facebook, wiki_vote, gnutella etc
        self.graph_type = graph_type
        self.G = nx.read_edgelist(filename, create_using=self.GRAPH_TYPE_DICT[self.graph_type](), nodetype=int)
        self.data_type = data_type

    def other_graph_info(self):
        with open('{}_graph_information.txt'.format(self.data_type), 'w') as my_file:
            # my_file.write('Average degree connectivity {}'.format(nx.average_degree_connectivity(self.G)))
            my_file.write('Average clustering coefficient {}\n'.format(nx.average_clustering(self.G.to_undirected())))
            my_file.write('Degree pearson correlation coefficient {}\n'.format(
                nx.degree_pearson_correlation_coefficient(self.G)))

            # Do this for the largest component (could give us insight)
            # my_file.write('Center of graph {}\n'.format(nx.center(self.G)))
            # my_file.write('Diameter of graph {}\n'.format(nx.diameter(self.G)))
            # my_file.write('Average node connectivity '.format(nx.average_node_connectivity(self.G)))
            # my_file.write('Average degree connectivity '.format(nx.average_degree_connectivity(self.G)))

    def centrality(self):
        if self.graph_type == 'undirected':
            self.CENTRALITY_DICT.pop('in_degree', None)
            # None has been done to take care of exception in case key doesn't exist
            self.CENTRALITY_DICT.pop('out_degree', None)  # like wise

        with open('{}_centrality.csv'.format(self.data_type), 'wb') as csv_file:
            writer = csv.writer(csv_file)
            centrality_measures = []
            node_order = None
            for centrality, function_name in self.CENTRALITY_DICT.items():
                centrality_measure = function_name(self.G)
                ordered_centrality_measure = OrderedDict(sorted(centrality_measure.items(), key=lambda x: x[0]))
                centrality_measures.append(list(ordered_centrality_measure.values()))
                if node_order is None:
                    node_order = list(ordered_centrality_measure.keys())
            csvheader = ['NodeID']
            csvheader += list(self.CENTRALITY_DICT.keys())
            writer.writerow(csvheader)
            for i in range(len(node_order)):
                centrality_values = [node_order[i]]
                for j in range(len(centrality_measures)):
                    centrality_values.append(centrality_measures[j][i])
                writer.writerow(centrality_values)

    def clustering_coefficient(self):
        undirected_G = self.G.to_undirected()
        with open('clustering_coefficients_{}.csv'.format(self.data_type), 'wb') as csv_file:
            writer = csv.writer(csv_file)
            clustering_dict = nx.clustering(undirected_G)
            for node in clustering_dict:
                writer.writerow([node, clustering_dict[node]])

    def network_graphs(self):
        # degree histogram
        degree_sequence = sorted(nx.degree(self.G).values(), reverse=True)  # degree sequence
        # print degree_sequence
        dmax = max(degree_sequence)

        plt.loglog(degree_sequence, 'b-', marker='o')
        plt.title("Degree rank plot")
        plt.ylabel("degree")
        plt.xlabel("rank")
        plt.savefig(self.data_type + "_degree_histogram.png")
        plt.close()

        # connected components subgraphs
        Gcc = sorted(nx.connected_component_subgraphs(self.G.to_undirected()), key=len, reverse=True)[0]
        pos = nx.spring_layout(Gcc)
        plt.axis('off')
        nx.draw_networkx_nodes(Gcc, pos, node_size=20)
        nx.draw_networkx_edges(Gcc, pos, alpha=0.4)

        plt.savefig(self.data_type + "_connected_subgraphs.png")
        plt.close()

def main():
    wiki_vote = DataNetwork('dataset/Wiki-Vote.txt', 'wiki', 'directed')
    wiki_vote.centrality()
    wiki_vote.clustering_coefficient()
    wiki_vote.other_graph_info()

    facebook = DataNetwork('dataset/facebook_combined.txt', 'facebook', 'undirected')
    facebook.centrality()
    facebook.clustering_coefficient()
    facebook.other_graph_info()

    gnutella = DataNetwork('dataset/p2p-Gnutella08.txt', 'gnutella', 'directed')
    gnutella.centrality()
    gnutella.clustering_coefficient()
    gnutella.other_graph_info()

    grqc = DataNetwork('dataset/CA-GrQc.txt', 'gr-qc', 'directed')
    grqc.centrality()
    grqc.clustering_coefficient()
    grqc.other_graph_info()

    wiki_vote.network_graphs()
    facebook.network_graphs()
    grqc.network_graphs()
    gnutella.network_graphs()

if __name__ == '__main__':
    main()