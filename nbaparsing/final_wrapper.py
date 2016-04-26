from collections import OrderedDict
import json
import csv
import math
from math import sqrt, pow
from heapq import nsmallest
import os


from networkx.readwrite import json_graph
import networkx as nx

__author__ = 'anirban, meraj'

class playByPlay:
    def __init__(self, whole_movements_json, play_by_play_json_file, moments_dump_file, play_by_play_csv, possession_csv_file, graph_file):

        # take the files
        self.possession_file_name = possession_csv_file
        self.moments_dump_file_name = moments_dump_file

        # load the play_by_play_data, moments data and get necessary info
        self.pass_data = json.load(open(play_by_play_json_file))
        self.team_ids, self.home_team_name, self.visitor_team_name, self.home_team_abbr, \
                self.visitor_team_abbr, self.visitor_dict, \
                self.home_dict = self.initial_game_data_writer(whole_movements_json)

        # for debugging purposes
        # self.team_ids = ['1610612761', '1610612766']
        # moments playing about and generation
        # self.three_closest_csv = three_closest_file
        # self.closest_player_csv = closest_player_file

        # find out the closest players
        # self.closest_players()  # to calculate the shortest distance for players for merging with play_by_play later

        # merge with play_by_play and write into possession_csv
        self.play_by_play_csv = play_by_play_csv
        self.play_by_play_writer()
        self.merger()
        # TODO: MERGING

        # generate the graph

        self.player_graph = self.create_graph()

        # json the graph
        self.jsonify_graph(self.player_graph, graph_file)

        # TODO: GRAPH MEASURES AND METRICS

    def combined_rule_runner(self, event_id, sub_event_id, home_event, away_event):
        '''
        Runs rules when both events are present
        :param event_id: ids describing broad events
        :param sub_event_id: ids describing sub types of broad events
        :returns: outcomes:- 0 for home event, 1 for away event or -1 to check i and i+1 comparison or -2 for useless events
        '''

        if event_id == 5:
            if 'STEAL' in home_event: # specific to steals and turnovers
                return 1, 0
            elif 'STEAL' in away_event: # specific to steals and turnovers
                return 0, 1
            else:
                return -1, -1
        elif event_id in [1, 2, 4]:  # shots, misses, rebounds
            if 'MISS' or 'shot' or 'REBOUND' in home_event:
                return 0, -1
            elif 'MISS' or 'shot' or 'REBOUND' in away_event:
                return 1, -1

        return -1, -1

    def rule_runner(self, event_id, sub_event_id, home_event, away_event):
        '''
        Runs rules on the basis of event_ids, sub_event ids and team flag
        :param event_id: ids describing broad events
        :param sub_event_id: ids describing sub types of broad events
        :returns: present and future outcome as a tuple
            possible values:- 0 for home event, 1 for away event or -1 to check i and i+1 comparison or -2 for useless events
        '''

        # worry about 8 - substitution and 9 - timeouts later

        if event_id in [8, 9, 12, 13, 18]:
            return -2, -2

        if home_event is None:
            team_flag = 1
        elif away_event is None:
            team_flag = 0
        else:
            return self.combined_rule_runner(event_id, sub_event_id, home_event, away_event)

        if event_id == 1:  # shots
            return team_flag, int(not team_flag)

        if event_id == 2:  # misses
            return team_flag, -1

        if event_id == 4:  # rebound
            return team_flag, team_flag  # we know who gets the ball after rebound, but not who had the ball (determine later)

        if event_id in [6, 7]:  # for fouls, violations
            return -1, int(not team_flag)

        if event_id == 3:  # for free throws
            if sub_event_id != 11:
                return team_flag, int(not team_flag)
            else: # 11 stands for free throw 1 of 2
                return team_flag, team_flag

        if event_id == 5:  # turnovers
            return team_flag, int(not team_flag)

        if event_id == 10:  # jump_ball
            return team_flag, team_flag

    def possession_time(self, row):
        # 1- gametime, 2 - event id,
        # 0 - home_team, 1 - away_team
        # -1 - we don't know
        # -2 - shot, -3 - miss, -4 - steal, -5 - rebound, -6 - turnover
        # rebounds, steals, incoming could be start of plays
        quarter, gametime, event_id, pre_flag, post_flag, home_event, away_event, player_1, player_1_team, player_2, player_2_team, player_3, player_3_team = row

        player_dict = OrderedDict((player, team) for player, team in zip([player_1, player_2, player_3],[player_1_team, player_2_team, player_3_team]))
        if '0' in player_dict:
            del player_dict['0']

        # print player_dict

        if int(event_id) == 10:  # jumpball
            # print 'yolo'
            players = [player for player in player_dict.keys() if player_dict[player] == self.team_ids[int(post_flag)]]
            return [[quarter, gametime, pre_flag]] + [list(element) for element in zip([quarter] * 2, [gametime] * 2, players)]

        if int(event_id) == 1:  # shots
            my_list = []
            if player_2 != '0':
                my_list.append([quarter, gametime, player_2])
            my_list.extend([[quarter, gametime, player_1], [quarter, gametime, -2], [quarter, gametime, post_flag]])
            return my_list

        if int(event_id) == 2:  # misses
            return [[quarter, gametime, player_1], [quarter, gametime, -3]]

        if int(event_id) == 4:  # rebounds
            if player_1 in self.team_ids:  # in case we do not know the rebounds from the logs
                player_1 = self.team_ids.index(player_1)
            return [[quarter, gametime, -5], [quarter, gametime, player_1]]

        if int(event_id) in [6, 7]:  # fouls, violations
            return [[quarter, gametime, -1], [quarter, gametime, post_flag]]

        if int(event_id) == 3:  # free-throws
            my_list = []
            if 'MISS' in home_event or 'MISS' in away_event:  # miss
                my_list = [[quarter, gametime, player_1], [quarter, gametime, -3]]
            else:
                # print row
                my_list = [[quarter, gametime, player_1], [quarter, gametime, -2]]

            if pre_flag != post_flag:
                my_list.append([quarter, gametime, post_flag])

            else:
                my_list.append(([quarter, gametime, pre_flag]))

            return my_list

        if int(event_id) == 5:  # turnovers
            my_list = []
            # print post_flag
            pre_player = [player for player in player_dict.keys() if player_dict[player] == self.team_ids[int(pre_flag)]]
            post_player = [player for player in player_dict.keys() if player_dict[player] == self.team_ids[int(post_flag)]]
            # print post_player
            if not pre_player:
                my_list.append([quarter, gametime, pre_flag])
            else:
                my_list.append([quarter, gametime, pre_player[0]])

            my_list.append([quarter, gametime, -6])
            my_list.append([quarter, gametime, -4])

            if not post_player:
                my_list.append([quarter, gametime, post_flag])
            else:
                my_list.append([quarter, gametime, post_player[0]])

            return my_list

    def play_by_play_writer(self):
        first_team = 0
        with open(self.play_by_play_csv, 'wb') as play_file:
            play_writer = csv.writer(play_file)
            play_writer.writerow(['Quarter', 'GameClock', 'EventId', 'Who has the ball', 'Who will now have the ball', 'Home_event', 'Away_event', 'Player1', 'Player1_team_id', 'Player2', 'Player2_team_id', 'Player3', 'Player3_team_id'])
            for i, row in enumerate(self.pass_data['resultSets'][0]['rowSet']):
                # player_1 id 13, 15 team_id
                # player_2 id 20, 22 team_id
                # player_3 is 27, 29 team_id

                # if row[2] == 4:  # rebounds
                #     continue

                minutes, seconds = row[6].split(':')
                row[6] = float(minutes) * 60 + float(seconds)

                pre_possession_flag, post_possession_flag = self.rule_runner(row[2], row[3], row[7], row[9])
                if pre_possession_flag == -2 and post_possession_flag == -2:
                    continue

                if row[2] == 2:  # misses
                    next_row = self.pass_data['resultSets'][0]['rowSet'][i + 1]
                    if next_row[2] == 4:  # rebounds
                        pre_flag, post_flag = self.rule_runner(next_row[2], next_row[3], next_row[7], next_row[9])
                        post_possession_flag = post_flag

                        # play_writer.writerow([row[6], row[2], pre_possession_flag, post_possession_flag, row[7], row[9], row[13], row[20], row[27]])
                        # continue

                        # play_writer.writerow([next_row[6], pre_flag, post_flag, next_row[7], next_row[9]])

                if i == 0:  # jump_ball part
                    first_team = pre_possession_flag

                play_writer.writerow([row[4], row[6], row[2], pre_possession_flag, post_possession_flag, row[7], row[9], row[13], row[15], row[20], row[22], row[27], row[29]])
        #
        #
        with open(self.play_by_play_csv, 'rb') as play_file, open(self.possession_file_name, 'wb') as poss_file:
            writer = csv.writer(poss_file)
            writer.writerow(['Quarter', 'Gametime', 'Player_Id'])
            current_quarter = 1
            for index, row in enumerate(csv.reader(play_file)):
                if index == 0:
                    continue

                if int(row[0]) != current_quarter:
                    # do the insertion stuff
                    writer.writerow([current_quarter, 0.0, -1])
                    if int(row[0]) == 2 or 3:
                        writer.writerow([row[0], 720.0, int(not(first_team))])
                    else:
                        writer.writerow([row[0], 720.0, int(first_team)])
                    current_quarter = int(row[0])

                my_list = self.possession_time(row)
                for r in my_list:
                    writer.writerow(r)
            writer.writerow([4, 0.0, -1])

    def initial_game_data_writer(self, actual_movements_json):
        gamedata = json.load(open(actual_movements_json))

        # print gamedata.keys()
        # print(gamedata['gamedate'], gamedata['gameid'])

        home_team_id = gamedata['events'][0]['home']['teamid']

        visitor_team_id = gamedata['events'][0]['visitor']['teamid']

        visitor_list = gamedata['events'][0]['visitor']['players']
        home_list = gamedata['events'][0]['home']['players']

        home_team_name = gamedata['events'][0]['home']['name']
        visitor_team_name = gamedata['events'][0]['visitor']['name']

        home_team_abbr = gamedata['events'][0]['home']['abbreviation']
        visitor_team_abbr = gamedata['events'][0]['visitor']['abbreviation']

        visitor_dict = {}
        home_dict = {}

        specific_keys = {'lastname', 'firstname', 'jersey', 'position'}

        for player in visitor_list:
            visitor_dict[player['playerid']] = {}
            for keys in specific_keys:
                visitor_dict[player['playerid']][keys] = player[keys]

        for player in home_list:
            home_dict[player['playerid']] = {}
            for keys in specific_keys:
                home_dict[player['playerid']][keys] = player[keys]

        playermoments = []
        quarter_time_sets = set()

        for event in gamedata['events']:
            for moment in event['moments']:
                if len(moment[5]) < 11:
                    continue

                if (moment[0], moment[3]) not in quarter_time_sets:
                    quarter_time_sets.add((moment[0], moment[3]))
                    playermoments.append(moment)

        playermoments.sort(key=lambda x: (int(4-x[0]), x[2], x[3]), reverse=True)

        with open(self.moments_dump_file_name, 'wb') as momentsdump:
            writer = csv.writer(momentsdump)

            for playermoment in playermoments:
                # if len(playermoment[5]) < 11:
                #     continue

                for i in range(0, 11):
                    trial = [playermoment[0], playermoment[2], playermoment[3]]
                    trial.extend(playermoment[5][i])
                    writer.writerow(trial)

        return [str(home_team_id), str(visitor_team_id)], home_team_name, visitor_team_name, home_team_abbr, \
               visitor_team_abbr, visitor_dict, home_dict

    def closer(self, ball_data, my_list):
        index_x = 5
        index_y = 6

        # print ball_data
        ball_x = float(ball_data[index_x])
        ball_y = float(ball_data[index_y])

        # 3 - team id
        # 4 - player id
        # print ball_x, ball_y, my_list[0][index_x], my_list[0][index_x]
        # print my_list[0]
        player_ball = [sqrt(pow(float(player_detail[index_x]) - ball_x, 2) + pow(float(player_detail[index_y]) - ball_y, 2)) for player_detail in my_list]
        player_index = player_ball.index(min(player_ball))

        # three_players = [player_ball.index(item) for item in nsmallest(3, player_ball)]
        # # print three_players
        # with open('three_player.csv', 'a') as out_file:
        #     writer = csv.writer(out_file)
        #     # print my_list[player_index]
        #     for index in three_players:
        #         writer.writerow([my_list[player_index][1], my_list[index][4], player_ball[index]])

        return [my_list[player_index][1], my_list[player_index][2], my_list[player_index][4], my_list[player_index][index_x], my_list[player_index][index_y], player_ball[player_index]]

    def perform_moments_stuff(self, movement_list, moments):

        home_list = self.home_dict.keys()
        visitor_list = self.visitor_dict.keys()

        first_look = int(float(movement_list[0][2]))
        second_look = int(float(movement_list[1][2]))

        first_time = int(float(movement_list[0][1]))
        last_time = int(float(movement_list[-1][1]))

        my_temp_list = None

        if first_look == 0:
            my_temp_list = home_list
        elif first_look == 1:
            my_temp_list = visitor_list
        elif first_look == -4 or -5:
            if second_look == 0 or second_look in home_list:
                my_temp_list = home_list
            elif second_look == 1 or second_look in visitor_list:
                my_temp_list = visitor_list

        moment_list = []
        trial = []
        ball_data = None
        for i, row in enumerate(moments):
            if (i + 1) % 12 == 0:
                if int(row[4]) in my_temp_list:
                    trial.append(row)

                if float(row[1]) > first_time:  # can change this to first_time + 1 later
                    trial = []
                    continue
                # print ball_data
                # print trial
                final_player = self.closer(ball_data, trial)
                # print final_player[5]
                if final_player[5] <= 1.1:  # for distance threshold
                    # print final_player
                    moment_list.append(final_player)
                trial = []
                if int(float(row[1]) - 0.04) < last_time:
                    break
            else:
                try:
                    if int(row[3]) == -1:
                        ball_data = row
                    else:
                        if int(row[4]) in my_temp_list:
                            trial.append(row)
                except:
                    # print row
                    # print 'yolo'
                    exit(1)

        # print moment_list
        if not moment_list:
            # print 'yolo'
            return None

        current_player = moment_list[0][2]
        new_moments = []
        prev_row = moment_list[0]
        for moment in moment_list[1:]:
            if moment[2] == current_player:
                prev_row = moment
            elif moment[2] != current_player:
                new_moments.append(prev_row)
                new_moments.append(moment)
                current_player = moment[2]

        prev_row = movement_list[0]
        new_data = [movement_list[0]]
        my_index = 0
        j = 0
        i = 1
        for movement in movement_list[1:]:
            for moment in new_moments[my_index:]:
                if moment[0] > movement[1]:  # movement consists of time at index 1 and moment consists of time at index 0
                    new_data.append([prev_row[0], moment[0], moment[2]])
                    j += 1
                    my_index += 1
                else:
                    new_data.append(movement)
                    i += 1
                    break
            if j == len(new_moments):
                new_data.extend(movement_list[i:])
                break
            i += 1

        prev_row = new_data[0]
        indices_list = []
        for i, row in enumerate(new_data[1:]):
            if row[2] == prev_row[2]:
                indices_list.append(i - len(indices_list))
            else:
                prev_row = row

        for indices in indices_list:
            del new_data[indices]

        # print new_data

        return new_data

    def merger(self):
        start_nodes = [0, 1, -4, -5]
        end_nodes = [-2, -3, -1, -6]
        my_list = []
        current_quarter = 1
        entire_correct_play = []
        with open(self.possession_file_name, 'rb') as f, open(self.moments_dump_file_name, 'rb') as moments_file:
            reader = csv.reader(f)
            moments_reader = csv.reader(moments_file)
            reader.next()  # to ignore header
            prev_row = moments_reader.next()
            moments = [[prev_row]]
            j = 0
            for i, moment in enumerate(moments_reader):
                if moment[0] > prev_row[0]:
                    j += 1
                    moments.append([moment])

                moments[j].append(moment)
                prev_row = moment

            for i, row in enumerate(reader):
                my_list.append(row)
                if len(row[2]) <= 2:
                    if int(row[2]) in end_nodes:
                        quarter = int(row[0]) - 1
                        asd = self.perform_moments_stuff(my_list, moments[quarter])
                        if asd is not None:
                            entire_correct_play.extend(asd)
                        my_list = []

        with open(self.possession_file_name, 'wb') as out_file:
            writer = csv.writer(out_file)
            for row in entire_correct_play:
                writer.writerow(row)

    def create_graph(self):
        G = nx.DiGraph()
        start_nodes = [0, 1, -4, -5]
        end_nodes = [-2, -3, -1, -6]

        with open(self.possession_file_name, 'rb') as f:
            file_reader = csv.reader(f)

            for index, row in enumerate(file_reader):
                prev_row = row
                break

            for index, row in enumerate(file_reader):
                # print row
                first_site = int(prev_row[2])
                second_site = int(row[2])

                if second_site in start_nodes:
                    prev_row = row
                    continue

                if G.has_edge(first_site, second_site):
                    # print 'exists'
                    G[first_site][second_site]['weight'] += 1
                else:
                    # print 'trial'
                    G.add_edge(first_site, second_site, weight=1)

                prev_row = row

            # print G.nodes()
            # print G.edges()
            # print(type(G))
            # print(G)
            # print(G is None)
        return G

    def jsonify_graph(self, graphobj, graphfile):
        G = graphobj
        start_nodes = [0, 1, -4, -5]
        end_nodes = [-2, -3, -1, -6]
        j = json_graph.node_link_data(G)
        # print j['nodes']
        i = 0
        k = 0

        for id_pair in j['nodes']:
            if id_pair['id'] in start_nodes:
                i += 1
                id_pair['x'] = 50
                id_pair['y'] = 100 * i
                id_pair['fixed'] = True

            if id_pair['id'] in end_nodes:
                k += 1
                id_pair['x'] = 700
                id_pair['y'] = 100 * k
                id_pair['fixed'] = True

        json.dump(j, open(graphfile, 'w'), indent=2)

    def jsonify_vis(self, graphobj, graphfile):
        G = graphobj
        visgraph = dict()
        start_nodes = [0, 1, -4, -5]
        end_nodes = [-2, -3, -1, -6]
        start_count = 0
        end_count = 0
        visgraph['nodes'] = list()
        visgraph['edges'] = list()
        start_y = [300, 150, -150, -300]
        end_y = [300, 150, -150, -300]
        num_nodes = len(G.nodes()) - 8
        angle_multiplier = 0
        slices = 2*math.pi/num_nodes
        radius = 300
        for node in G.nodes():
            if node in start_nodes:
                visgraph['nodes'].append({'id': node, 'x': -400, 'y': start_y.pop(), 'group': 'start', 'fixed': True})
                print('start')
            elif node in end_nodes:
                visgraph['nodes'].append({'id': node, 'x': 400, 'y': end_y.pop(), 'group': 'end', 'fixed': True})
            else:
                angle = slices * angle_multiplier
                visgraph['nodes'].append({'id': node, 'x': int(radius*math.cos(angle)), 'y': int(radius*math.sin(angle)),
                                          'group': 'players'})
                # visgraph['nodes'].append({'id': node})
                angle_multiplier += 1
        max_weight = max([G.get_edge_data(edge[0], edge[1])['weight'] for edge in G.edges()])
        min_weight = min([G.get_edge_data(edge[0], edge[1])['weight'] for edge in G.edges()])
        for edge in G.edges():
            if edge[0] == edge[1]:
                continue
            weight = G.get_edge_data(edge[0], edge[1])['weight']
            color = {'color': 'red', 'opacity':(weight-min_weight)/float(max_weight-min_weight)}
            visgraph['edges'].append({'from': edge[0], 'to': edge[1], 'value': weight, 'arrows': 'to', 'color': color,
                                      'smooth':False})
        json.dump(visgraph, open(graphfile, 'w'), indent=2)

# game_id = '0021500492'
#
# my_play_by_play = playByPlay('data/positionlog/{}.json'.format(game_id), 'data/playbyplay/{}.json'.format(game_id), # input data
#                              'momentsdump.csv',  # o/p i/p for moments part
#                              'play_by_play.csv', 'possession.csv',  # o/p i/p for play by play part
#                              'possession_graph.json')  # o/p for graph generation part


gamelist = os.listdir('data/playbyplay')
for gamefile in gamelist:
    game_id = gamefile[:-5]

    my_play_by_play = playByPlay('data/positionlog/{}.json'.format(game_id), 'data/playbyplay/{}.json'.format(game_id), # input data
                             'data/momentsdump/{}.csv'.format(game_id),  # o/p i/p for moments part
                             'data/playbyplay_csv/{}.csv'.format(game_id), 'data/possession_csv/{}.csv'.format(game_id),  # o/p i/p for play by play part
                             'data/possession_graph/{}.json'.format(game_id))  # o/p for graph generation part

    nodes = [1]
    nodes.extend(my_play_by_play.visitor_dict.keys())

    for node in nodes:
        try:
            my_play_by_play.player_graph.remove_node(node)
        except:
            pass

    json.dump(my_play_by_play.home_dict, open('jsongraphs_nba/{}.json'.format(game_id), 'w'), indent=2)

    g_json = json_graph.node_link_data(my_play_by_play.player_graph)
    json.dump(g_json, open('jsongraphs_nba/{}.json'.format(game_id), 'w'), indent=2)
    # print my_play_by_play.player_graph