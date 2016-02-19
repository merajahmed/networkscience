from __future__ import division
__author__ = 'meraj'
import csv
import networkx as nx
import community
from itertools import chain


# create community dictionary of form - {communityId:[list of vertices]}, and edge dictionary of form - {vertexId:[list of vertexIds connected to]}
def findCommunityEdgesMCL(mcloutfile, metisfile):
    communityDictionary = dict()
    edgeDictionary = dict()

    with open(mcloutfile, 'r') as communityFile:
        for line_id, line in enumerate(communityFile.readlines()):
            vertexId = line_id + 1
            communityId = int(line.rstrip('\n'))
            if communityId not in communityDictionary:
                communityDictionary[communityId] = [vertexId]
            else:
                communityDictionary[communityId].append(vertexId)

    with open(metisfile, 'r') as edgeFile:
        for line_id, line in enumerate(edgeFile.readlines()[1:]):
            vertexId = line_id + 1
            edgeList = map(lambda x: int(x), line.split())
            edgeDictionary[vertexId] = edgeList

    return edgeDictionary, communityDictionary


def findCommunityEdgesMetis(metisoutfile, metisfile):
    communityDictionary = dict()
    edgeDictionary = dict()
    edgeList = []
    return edgeDictionary, communityDictionary


def convert_to_networkx(metisfilepath):
    G = nx.Graph()
    with open(metisfilepath,'r') as metisfile:
        lines = metisfile.readlines()
        vertexId = 1
        for line in lines[1:]:
            edgeList = map(lambda x: (vertexId, int(x)), line.split())
            G.add_edges_from(edgeList)
            vertexId += 1
    return G


def calculateModularityMetis(metisOutFilePath, metisFilePath):
    with open(metisOutFilePath, 'r') as metisOutFile:
        nxGraph = convert_to_networkx(metisFilePath)
        partition = dict()

        for line_id, line in enumerate(metisOutFile.readlines()):
            vertexId = line_id + 1
            partition[vertexId] = int(line.split()[0])
        modularity = community.modularity(partition, nxGraph)
    return modularity

    # edgesWithinGroups = dict()
    # edgeList = list()
    # for vertex in edgeDictionary:
    #     for vertex2 in edgeDictionary[vertex]:
    #         if (vertex, vertex2) not in edgeList and (vertex2, vertex) not in edgeList:
    #                    edgeList.append((vertex,vertex2))
    # communityList_one = communityDictionary.keys()[0:communityDictionary.keys()/2]
    # communityList_two = communityDictionary[communityDictionary.keys()/2+1:]
    # modularity = 0.0
    # m = 0.0 #number of edges
    # for vertex in edgeDictionary:
    #     m += len(edgeDictionary[vertex])
    # m /= 2
    # for community_one in communityList_one:
    #     for community_two in communityList_two:
    #         for vertex_one in communityList_one[community_one]:
    #             for vertex_two in communityList_two[community_two]:
    #                 if (vertex_one, vertex_two) in edgeList or (vertex_two, vertex_one) in edgeList:
    #                     modularity += 1
    #                     modularity -= ((len(edgeDictionary[vertex_one])*len(edgeDictionary[vertex_two]))/(2*m))
    # modularity = modularity/(2*m)
    # return modularity


### Taken from networkx's latest code ###
### HOWEVER MODIFIED, DUE TO OUR GRAPHS BEING NOT WEIGHTED ###
### Assumes each edge to be of weight = 1 ###

def cut_size(G, S, T=None):
    edges = nx.edge_boundary(G, S, T)
    if G.is_directed():
        edges = chain(edges, nx.edge_boundary(G, T, S))
    return sum(1 for u, v in edges)


def volume(G, S):
    degree = G.out_degree if G.is_directed() else G.degree
    return sum(1 for v in degree(S))


def conductance(G, S, T=None):
    if T is None:
        T = set(G) - set(S)
    num_cut_edges = cut_size(G, S, T)
    volume_S = volume(G, S)
    volume_T = volume(G, T)
    return num_cut_edges / min(volume_S, volume_T)


def calculate_conductance(metisOutFilePath, metisFilePath): # work in progress

    # We are calculating conductance by comparing the average value of conductance in a method
    community_dict = {}
    with open(metisOutFilePath, 'r') as metisOutFile:
        for line_id, line in enumerate(metisOutFile.readlines()):
            vertex_id = line_id + 1
            community_id = int(line.rstrip('\n'))
            if community_id not in community_dict:
                community_dict[community_id] = set([vertex_id])
            else:
                community_dict[community_id].add(vertex_id)

    nxGraph = convert_to_networkx(metisFilePath)

    # calculate average conductance

    conductance_values = [conductance(nxGraph, community_dict[community_id]) for community_id in community_dict]
    average_conductance_value = sum(conductance_values)/len(conductance_values)
    return average_conductance_value

def entropy()

# print('Wiki Vote Modularity:', calculateModularityMetis('output/mlrmcl/r=3/wiki-Vote.metis.c1000.i3.0.b0.5','data/wiki-Vote.metis'))
# print('Gnutella Modularity:', calculateModularityMetis('output/mlrmcl/r=3/p2p-Gnutella08.metis.c1000.i3.0.b0.5','data/p2p-Gnutella08.metis'))
# print('Facebook Modularity:', calculateModularityMetis('output/mlrmcl/r=3/facebook_combined.metis.c1000.i3.0.b0.5','data/facebook_combined.metis'))
# print('Ca-GrQc:', calculateModularityMetis('output/mlrmcl/r=3/ca-GrQc.metis.c1000.i3.0.b0.5','data/ca-GrQc.metis'))
# print('Youtube Modularity:', calculateModularityMetis('output/mlrmcl/r=3/com-youtube.ungraph.metis.c1000.i3.0.b0.5','data/com-youtube.ungraph.metis'))

print calculate_conductance('output/metis/ncut_r=1/facebook_combined.metis.part.100', 'data/wiki-Vote.metis')
