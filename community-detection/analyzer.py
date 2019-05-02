from __future__ import division
__author__ = 'meraj'
import networkx as nx
import community
import math
from collections import Counter
from itertools import chain
import os


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


def create_text_for_cnm(cnm_text_file):
    temp_community_dict = {}

    with open(cnm_text_file, 'r') as f:
        for line in f.readlines()[6:]:
            vertex_id, community_id = int(line.rstrip('\n').split()[0]), line.rstrip('\n').split()[1]
            temp_community_dict[vertex_id] = community_id

    text_list = [value for (key, value) in sorted(temp_community_dict.iteritems())]
    return '\n'.join(text_list)


def findCommunityEdgesMetis(metisoutfile, metisfile):
    communityDictionary = dict()
    edgeDictionary = dict()
    edgeList = []
    return edgeDictionary, communityDictionary


def convert_to_networkx(metisfilepath):
    G = nx.Graph()
    with open(metisfilepath, 'r') as metisfile:
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
    #print(degree(S))
    return sum(1 for v in degree(S))


def conductance(G, S, T=None):
    if T is None:
        T = set(G) - set(S)
    num_cut_edges = cut_size(G, S, T)
    volume_S = volume(G, S)
    volume_T = volume(G, T)
    if volume_T == 0:
        return 0
    return num_cut_edges / min(volume_S, volume_T)


def normalized_cut_size(G, S, T=None):
    if T is None:
        T = set(G) - set(S)
    num_cut_edges = cut_size(G, S, T=T)
    volume_S = volume(G, S)
    volume_T = volume(G, T)
    return num_cut_edges * ((1 / volume_S) + (1 / volume_T))

#returns number_of_components, min conductance across all components, list of conductance values for components with more than one community
def calculate_conductance(metisOutFilePath, metisFilePath): # work in progress
    # We are calculating conductance by comparing the average value of conductance in a method
    community_dict = {}
    vertex_dict = {}
    with open(metisOutFilePath, 'r') as metisOutFile:
        for line_id, line in enumerate(metisOutFile.readlines()):
            vertex_id = line_id + 1
            community_id = int(line.rstrip('\n'))
            if community_id not in community_dict:
                community_dict[community_id] = set([vertex_id])
            else:
                community_dict[community_id].add(vertex_id)
            vertex_dict[vertex_id] = community_id
    nxGraph = convert_to_networkx(metisFilePath)
    connected_components = nx.connected_component_subgraphs(nxGraph)
    component_conductance_values = list()
    count = 0
    for component in connected_components:
        count += 1
        component_nodes = nx.nodes(component)
        component_community_list = set()
        for node in component_nodes:
            component_community_list.add(vertex_dict[node])
        conductance_values = [conductance(component, community_dict[community_id]) for community_id in component_community_list]
        component_conductance_values.append(min(conductance_values))
    # # calculate average conductance
    # conductance_values = [conductance(nxGraph, community_dict[community_id]) for community_id in community_dict]
    # average_conductance_value = sum(conductance_values)/len(conductance_values)
    number_of_componets = count
    valid_conductance_values = filter(lambda x: x != 0, component_conductance_values)
    min_conductance_value = min(valid_conductance_values)
    return number_of_componets, min_conductance_value, valid_conductance_values


def calculate_ncut_value(metisOutFilePath, metisFilePath):
    community_dict = {}
    vertex_dict = {}
    with open(metisOutFilePath, 'r') as metisOutFile:
        for line_id, line in enumerate(metisOutFile.readlines()):
            vertex_id = line_id + 1
            community_id = int(line.rstrip('\n'))
            if community_id not in community_dict:
                community_dict[community_id] = set([vertex_id])
            else:
                community_dict[community_id].add(vertex_id)
            vertex_dict[vertex_id] = community_id
    nxGraph = convert_to_networkx(metisFilePath)

    ncut_values = [nx.normalized_cut_size(nxGraph, community_dict[community_id]) for community_id in community_dict]
    average_ncut_value = sum(ncut_values) / len(ncut_values)
    return average_ncut_value

def entropy(labels):
    p, lns = Counter(labels), float(len(labels))
    return -sum(count/lns * math.log(count/lns, 2) for count in p.values())

def calculate_entropy(metis_gt_file, metis_out_file):
    ground_community_dict = {}
    groundtruthnodes = set()
    with open(metis_gt_file, 'r') as metis_gt:
        lines =  metis_gt.readlines()
        community_id = 0
        for line in lines:
            nodelist = map(lambda x: int(x), line.split())
            for node in nodelist:
                groundtruthnodes.add(node)
                if node not in ground_community_dict:
                    ground_community_dict[node] = [community_id]
                else:
                    ground_community_dict[node].append(community_id)
            community_id += 1
    test_community_dict = dict()
    with open(metis_out_file, 'r') as metis_file:
        lines = metis_file.readlines()
        vertexid = 0
        for line in lines:
            vertexid += 1
            if vertexid not in groundtruthnodes:
                continue
            else:
                community_id = int(line[0])
                if community_id not in test_community_dict:
                    test_community_dict[community_id] = [vertexid]
                else:
                    test_community_dict[community_id].append(vertexid)
    entropy = 0
    for community_id in test_community_dict:
        total = float(len(test_community_dict[community_id]))
        truecommunityset = set()
        for node in test_community_dict[community_id]:
            for truecommunity in ground_community_dict[node]:
                truecommunityset.add(truecommunity)
        entropydict = dict()
        truecommunitylist = list(truecommunityset)
        for community in truecommunitylist:
            for node in test_community_dict[community_id]:
                if ground_community_dict[node] == community:
                    contribution = 1.0/len(ground_community_dict[node])
                    entropydict[community] = entropydict.get(community, 0.0) + contribution
        plogp = 0.0
        for community in entropydict:
            plogp += ((entropydict[community]/total)*math.log(entropydict[community]/total))
        plogp *= -1
        entropy += ((len(test_community_dict[community_id])/float(len(groundtruthnodes)))*plogp)
    return entropy

filenames_list = ['ca-GrQc', 'facebook_combined', 'p2p-Gnutella08', 'wiki-Vote']#, 'com-youtube.ungraph']

directory_list = ['r=1', 'r=2', 'r=3', 'cnm']

for dir_name in directory_list:
    for fname in os.listdir('/home/0/guptanir/my_folder/output/metis/{}/.'.format(dir_name)):
        file_path = '/home/0/guptanir/my_folder/output/metis/{}/{}'.format(dir_name, fname)
        if '_output' in fname or 'youtube' in fname:
            continue
        for f in filenames_list:
            if f in fname:
                other_file_path = '/home/0/guptanir/my_folder/data/{}.metis'.format(f)
                break
        try:
            print('{} Conductance: {}'.format(fname, calculate_conductance(file_path, other_file_path)))
            print('{} Modularity: {}'.format(fname, calculateModularityMetis(file_path, other_file_path)))
            print('{} Average Ncut value: {}'.format(fname, calculate_ncut_value(file_path, other_file_path)))
        except:
            pass

print '\n\nMLRMCL\n\n'
#
# # for mlrmcl
for i in [1, 2, 3]:
    for file_name in filenames_list:
        file_path = '/home/0/guptanir/my_folder/output/mlrmcl/r={}/{}.metis.c1000.i{}.0.b0.5'.format(i, file_name, i)
        other_file_path = '/home/0/guptanir/my_folder/data/{}.metis'.format(file_name)
        print('{} Modularity: {}'.format(file_name, calculateModularityMetis(file_path, other_file_path)))
        print('{} Average Ncut value: {}'.format(file_name, calculate_ncut_value(file_path, other_file_path)))
        print('{} Conductance: {}'.format(file_name, calculate_conductance(file_path, other_file_path)))

print '\n\nCNM\n\n'

for filename, other_filename in zip(['grqc_cnm.txt', 'facebook_cnm.txt', 'Gnutella_cnm.txt', 'wiki_cnm.txt'],
                                    filenames_list):
    data = create_text_for_cnm('/home/0/guptanir/my_folder/output/CNM/{}'.format(filename))
    other_file_path = '/home/0/guptanir/my_folder/data/{}.metis'.format(other_filename)
    with open('/home/0/guptanir/my_folder/output/CNM/temp_' + filename, 'w') as f:
        f.write(data)
    print('{} Conductance: {}'.format(filename,
                                      calculate_conductance('/home/0/guptanir/my_folder/output/CNM/temp_' + filename,
                                                            other_file_path)))
    print(
        '{} Average Ncut value: {}'.format(filename,
                                           calculate_ncut_value(
                                               '/home/0/guptanir/my_folder/output/CNM/temp_' + filename,
                                               other_file_path)))

print 'For METIS\n'
print 'For r=1\n'
print calculate_entropy('/home/0/guptanir/my_folder/data/com-youtube.ungraph.metis.GT',
                        '/home/0/guptanir/my_folder/output/metis/r=1/com-youtube.ungraph.metis.part.1275')
print '\nFor r=2\n'
print calculate_entropy('/home/0/guptanir/my_folder/data/com-youtube.ungraph.metis.GT',
                        '/home/0/guptanir/my_folder/output/metis/r=2/com-youtube.ungraph.metis.part.27084')
print '\nFor r=3\n'
print calculate_entropy('/home/0/guptanir/my_folder/data/com-youtube.ungraph.metis.GT',
                        '/home/0/guptanir/my_folder/output/metis/r=3/com-youtube.ungraph.metis.part.154505')

print 'For MLRMCL\n'
print 'For r=1\n'
print calculate_entropy('/home/0/guptanir/my_folder/data/com-youtube.ungraph.metis.GT',
                        '/home/0/guptanir/my_folder/output/mlrmcl/r=1/com-youtube.ungraph.metis.c1000.i1.0.b0.5')
print '\nFor r=2\n'
print calculate_entropy('/home/0/guptanir/my_folder/data/com-youtube.ungraph.metis.GT',
                        '/home/0/guptanir/my_folder/output/mlrmcl/r=2/com-youtube.ungraph.metis.c1000.i2.0.b0.5')
print '\nFor r=3\n'
print calculate_entropy('/home/0/guptanir/my_folder/data/com-youtube.ungraph.metis.GT',
                        '/home/0/guptanir/my_folder/output/mlrmcl/r=3/com-youtube.ungraph.metis.c1000.i3.0.b0.5')
