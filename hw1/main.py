import networkx as nx
import csv
__author__ = 'meraj'

class data_network:
    def __init__(self, filename, data_type):  # where data_type is facebook, wiki_vote, gnutella etc
        self.G = nx.read_edgelist(filename, create_using=nx.DiGraph(), nodetype=int)
        self.data_type = data_type

    def centrality(self):
        centrality_terms = {'in_degree': nx.in_degree_centrality,
                            'out_degree': nx.out_degree_centrality,
                            'degree': nx.degree_centrality,
                            'closeness': nx.closeness_centrality,
                            'betweeness': nx.betweenness_centrality,
                            'eigen': nx.eigenvector_centrality,
                            'page_rank': nx.pagerank}

        for term in centrality_terms:
            with open('{}_centrality_{}.csv'.format(term, self.data_type), 'wb') as csv_file:
                writer = csv.writer(csv_file)
                centrality_measure = centrality_terms[term](self.G)
                for node in centrality_measure:
                    writer.writerow([node, centrality_measure[node]])

def main():
    wiki_vote = data_network('dataset/Wiki-Vote.txt', 'wiki')
    wiki_vote.centrality()

if __name__ == '__main__':
    main()