import networkx as nx

#Graph that holds all nodes for game
G = nx.DiGraph()

#Add nodes corresponding to each player on OSU's team
G.add_node(00)
G.add_node(2)
G.add_node(13)
G.add_node(32)
G.add_node(33)
G.add_node(15)
G.add_node(4)
G.add_node(12)
G.add_node(10)
#Nodes that correspond to ends of possessions; made shot (100), missed shot(101)
#,turnover(102), free throws (103)
G.add_node(100)
G.add_node(101)
G.add_node(102)
G.add_node(103)

#Open text file
file = open('OSUvsIowaGraph.txt', 'r')
for line in file:
    leftNode = ''
    action = ''
    rightNode = ''
    passType = ''
    inbound = ''
    splitLine = line.split()
    leftNode = int(splitLine[0])
    action = splitLine[1]
    if len(splitLine) > 2:
        rightNode = splitLine[2]
        if isinstance(rightNode, str) and -1 < rightNode[0] < 9:
            rightNode = int(splitLine[2])
    if len(splitLine) > 3:
        inbound = splitLine[3]
    if action == 'made':
        if not G.out_degree(leftNode):
            G.add_edge(leftNode,100)
            rightNode = 100
        else:
            currentWeight = G.out_degree(leftNode)
            G.add_weighted_edges_from([(leftNode,100,currentWeight+1)])
    if action == 'missed':
       if not G.out_degree(leftNode):
           G.add_edge(leftNode,101)
           rightNode = 101
       else:
           currentWeight = G.out_degree(leftNode)
           G.add_weighted_edges_from([(leftNode,101,currentWeight+1)])      
    if action == 'to':
        if not G.out_degree(leftNode):
            G.add_edge(leftNode,rightNode)
        else:
            currentWeight = G.out_degree(leftNode)
            G.add_weighted_edges_from([(leftNode,rightNode,currentWeight+1)])
    if action == 'turnover':
        if not G.out_degree(leftNode):
            G.add_edge(leftNode,102)
            rightNode = 103
        else:
            currentWeight = G.out_degree(leftNode)
            G.add_weighted_edges_from([(leftNode,102,currentWeight+1)])
    print 'node1: {0} node2: {1} degree:{2}'.format(leftNode, rightNode, G.out_degree(leftNode))
                                            
