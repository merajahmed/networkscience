__author__ = 'meraj'
import csv


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
    return edgeDictionary, communityDictionary


def calculateModularity(edgeDictionary, communityDictionary):
    return 1


findCommunityEdgesMCL('output/mlrmcl/r=2/wiki-Vote.metis.c1000.i2.0.b0.5','data/wiki-Vote.metis')