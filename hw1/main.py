import networkx as nx
import csv
from collections import OrderedDict

__author__ = 'anirban & meraj'


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


def main():
    wiki_vote = DataNetwork('dataset/Wiki-Vote.txt', 'wiki', 'directed')
    wiki_vote.centrality()
    wiki_vote.clustering_coefficient()

if __name__ == '__main__':
    main()