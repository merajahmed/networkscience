import networkx as nx
import csv
__author__ = 'meraj'

G = nx.read_edgelist("dataset/Wiki-Vote.txt", create_using=nx.DiGraph(), nodetype=int)
idc_wiki = nx.in_degree_centrality(G)
writer = csv.writer(open('indegree_centrality_wiki-vote', 'wb'))
for node in idc_wiki:
    writer.writerow([node, idc_wiki[node]])
odc_wiki = nx.out_degree_centrality(G)
writer = csv.writer(open('outdegree_centrality_wiki-vote', 'wb'))
for node in odc_wiki:
    writer.writerow([node, odc_wiki[node]])
dc_wiki = nx.degree_centrality(G)
writer = csv.writer(open('degree_centrality_wiki-vote', 'wb'))
for node in dc_wiki:
    writer.writerow([node, dc_wiki[node]])
cc_wiki = nx.closeness_centrality(G)
writer = csv.writer(open('closeness_centrality_wiki-vote', 'wb'))
for node in cc_wiki:
    writer.writerow([node, cc_wiki[node]])
bc_wiki = nx.betweenness_centrality(G)
writer = csv.writer(open('betweennness_centrality_wiki-vote', 'wb'))
for node in bc_wiki:
    writer.writerow([node, bc_wiki[node]])
eigen_wiki = nx.eigenvector_centrality(G)
writer = csv.writer(open('eigen_centrality_wiki-vote', 'wb'))
for node in eigen_wiki:
    writer.writerow([node, eigen_wiki[node]])
pagerank = nx.pagerank(G)
writer = csv.writer(open('pagerank_wiki-vote', 'wb'))
for node in pagerank:
    writer.writerow([node, pagerank[node]])
