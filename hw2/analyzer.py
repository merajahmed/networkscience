__author__ = 'meraj'
import csv

#create community dictionary of form - {communityId:[list of vertices]}, and edge dictionary of form - {vertexId:[list of vertexIds connected to]}
def findCommunityEdgesMCL(mcloutfile, metisfile):
    communityDictionary = dict()
    edgeDictionary = dict()
    communityFile = open(mcloutfile,'r')
    lines = communityFile.readlines()
    vertexId = 1
    for line in lines:
        communityId = int(line.rstrip('\n'))
        if communityId not in communityDictionary:
            communityDictionary[communityId] = [vertexId]
        else:
            communityDictionary[communityId].append(vertexId)
        vertexId += 1
    communityFile.close()
    edgeFile = open(metisfile, 'r')
    lines = edgeFile.readlines()
    vertexId = 1
    for line in lines[1:]:
        edgeList = map(lambda x: int(x), line.split())
        edgeDictionary[vertexId] = edgeList
        vertexId += 1
    edgeFile.close()
    return edgeDictionary, communityDictionary


def findCommunityEdgesMetis(metisoutfile, metisfile):
    communityDictionary = dict()
    edgeDictionary = dict()
    edgeList = []
    return edgeDictionary, communityDictionary


def calculateModularity(edgeDictionary, communityDictionary):
    edgesWithinGroups = dict()
    edgeList = list()
    for vertex in edgeDictionary:
        for vertex2 in edgeDictionary[vertex]:
            if (vertex, vertex2) not in edgeList and (vertex2, vertex) not in edgeList:
                       edgeList.append((vertex,vertex2))
    communityList_one = communityDictionary.keys()[0:communityDictionary.keys()/2]
    communityList_two = communityDictionary[communityDictionary.keys()/2+1:]
    modularity = 0.0
    m = 0.0 #number of edges
    for vertex in edgeDictionary:
        m += len(edgeDictionary[vertex])
    m /= 2
    for community_one in communityList_one:
        for community_two in communityList_two:
            for vertex_one in communityList_one[community_one]:
                for vertex_two in communityList_two[community_two]:
                    if (vertex_one, vertex_two) in edgeList or (vertex_two, vertex_one) in edgeList:
                        modularity += 1
                        modularity -= ((len(edgeDictionary[vertex_one])*len(edgeDictionary[vertex_two]))/(2*m))
    modularity = modularity/(2*m)
    return modularity

edgeDictionary, communityDictionary = findCommunityEdgesMCL('output/mlrmcl/r=2/wiki-Vote.metis.c1000.i2.0.b0.5','data/wiki-Vote.metis')
print(calculateModularity(edgeDictionary, communityDictionary))