import csv
import networkx
from matplotlib import pyplot as plt

_author__ = 'meraj'

def getteammovements(teamid):
    with open('playerdump.csv', 'r') as playerdump:
        with open(str(teamid)+'movements.csv','w') as teamfile:
            writer = csv.writer(teamfile)
            reader = csv.reader(playerdump)
            for line in reader:
                if line[1] == str(teamid):
                    writer.writerow(line)


def createteamgraph(teamfilename):
    with open(teamfilename,'r') as teamfile:
        reader = csv.reader(teamfile)
        currentplayer = None
        G = networkx.DiGraph()
        for line in reader:
            if currentplayer == line[2]:
                continue
            else:
                if currentplayer is None:
                    currentplayer = line[2]
                    continue
                lastplayer = currentplayer
                currentplayer = line[2]
                currentweight = G[lastplayer][currentplayer]['weight'] if G.has_edge(lastplayer, currentplayer) else 0
                G.add_edge(lastplayer, currentplayer, weight=currentweight+1)
    # for edge in G.edges():
    #     print(edge, G.get_edge_data(edge[0], edge[1]))
    return G

def plotgraph(graph):
    pos = networkx.spring_layout(graph)
    plt.title('All connected components graph')
    plt.axis('off')
    networkx.draw_networkx_nodes(graph, pos, edge_color='r', with_labels=False, node_size=20)
    networkx.draw_networkx_edges(graph, pos, alpha=0.4, width=6.0)
    networkx.draw_networkx_edges(graph, pos, edge_color='r', with_labels=False, alpha=0.3, width=5.0)
    plt.show()

# getteammovements(1610612761)
plotgraph(createteamgraph('1610612761movements.csv'))