from math import sqrt, pow
from heapq import nsmallest
from collections import OrderedDict
import json
import csv
import math

from networkx.readwrite import json_graph
import networkx as nx

__author__ = 'anirban, meraj'

class playByPlay:
    def __init__(self, whole_movements_json, play_by_play_json_file, moments_dump_file, three_closest_file,
                 closest_player_file, play_by_play_csv, possession_csv_file, graph_file):

        # take the files
        self.possession_file_name = possession_csv_file
        self.moments_dump_file_name = moments_dump_file

        # load the play_by_play_data, moments data and get necessary info
        self.pass_data = json.load(open(play_by_play_json_file))
        # self.team_ids, self.visitor_dict, self.home_dict = self.initial_game_data_writer(whole_movements_json)

        # for debugging purposes
        self.team_ids = ['1610612761', '1610612766']

        # moments playing about and generation
        # self.three_closest_csv = three_closest_file
        # self.closest_player_csv = closest_player_file

        # find out the closest players
        # self.closest_players()  # to calculate the shortest distance for players for merging with play_by_play later

        # merge with play_by_play and write into possession_csv
        self.play_by_play_csv = play_by_play_csv
        self.play_by_play_writer()
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

                play_writer.writerow([row[4], row[6], row[2], pre_possession_flag, post_possession_flag, row[7], row[9], row[13], row[15], row[20], row[22], row[27], row[29]])
        #
        #
        with open(self.play_by_play_csv, 'rb') as play_file, open(self.possession_file_name, 'wb') as poss_file:
            writer = csv.writer(poss_file)
            writer.writerow(['Quarter', 'Gametime', 'Player_Id'])
            for index, row in enumerate(csv.reader(play_file)):
                if index == 0:
                    continue
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
        for event in gamedata['events']:
            for moment in event['moments']:
                playermoments.append(moment)
        playermoments.sort(key=lambda x: (int(4-x[0]), x[2], x[3]), reverse=True)

        with open(self.moments_dump_file_name, 'wb') as momentsdump:
            writer = csv.writer(momentsdump)
            for playermoment in playermoments:
                for i in range(0, 10):
                    trial = [playermoment[0], playermoment[2], playermoment[3]]
                    trial.extend(playermoment[5][i])
                    writer.writerow(trial)

        # with open('momentsdump.csv', 'rb') as f:
        #     shotclock = None
        #     for row in csv.reader(f):
        #         # print type(row[2])
        #         shot_clock = float(row[2])
        #         break

        # with open('momentsdump.csv', 'rb') as f, open('shotclock_reset.csv', 'wb') as shot_clock_reset_log:
        #     writer = csv.writer(shot_clock_reset_log)
        #     for row in csv.reader(f):
        #         try:
        #             # print row[2]
        #             if float(row[2]) >= shot_clock:
        #                 writer.writerow(row)
        #         except ValueError, e:
        #             pass

        return [str(home_team_id), str(visitor_team_id)], visitor_dict, home_dict


    def closer(self, ball_data, player_moment_row):
        index_x = 5
        index_y = 6

        # print ball_data
        ball_x = float(ball_data[index_x])
        ball_y = float(ball_data[index_y])

        # 3 - team id
        # 4 - player id
        # print ball_x, ball_y, player_moment_row[0][index_x], player_moment_row[0][index_x]
        # print player_moment_row[0]
        player_ball = [sqrt(pow(float(player_detail[index_x]) - ball_x, 2) + pow(float(player_detail[index_y]) - ball_y, 2)) for player_detail in player_moment_row]
        player_index = player_ball.index(min(player_ball))

        three_players = [player_ball.index(item) for item in nsmallest(3, player_ball)]
        # print three_players
        with open(self.three_closest_csv, 'a') as out_file:
            writer = csv.writer(out_file)
            row = [player_moment_row[player_index][1]]
            # print player_moment_row[player_index]
            row.extend([(player_moment_row[index][4], player_ball[index]) for index in three_players])
            writer.writerow(row)

        return player_moment_row[player_index][1], player_moment_row[player_index][2], \
               player_moment_row[player_index][4], player_moment_row[player_index][index_x], \
               player_moment_row[player_index][index_y], player_ball[player_index],


    def closest_players(self):
        with open(self.moments_dump_file_name, 'r') as f:
            trial = []
            ball_data = []
            open(self.three_closest_csv, 'w').close()
            with open(self.closest_player_csv, 'wb') as out_file:
                writer = csv.writer(out_file)
                for i, line in enumerate(csv.reader(f)):
                    if (i + 1) % 11 == 0:
                        # print ball_data
                        final_player = self.closer(ball_data, trial)
                        writer.writerow(final_player)
                        trial = []
                        # break
                    else:
                        # print line
                        if int(line[3]) == -1:
                            ball_data = line
                        else:
                            trial.append(line)
                    if i > 10000:
                        break
                    # print trial


    def create_graph(self):
        G = nx.DiGraph()
        start_nodes = [0, 1, -4, -5]
        end_nodes = [-2, -3, -1, -6]

        with open(self.possession_file_name, 'rb') as f:
            file_reader = csv.reader(f)

            for index, row in enumerate(file_reader):
                if index == 0:
                    continue
                else:
                    prev_row = row
                    break

            for index, row in enumerate(file_reader):
                first_site = int(prev_row[2])
                second_site = int(row[2])

                if second_site in start_nodes:
                    prev_row = row
                    continue

                if G.has_edge(first_site, second_site):
                    G[first_site][second_site]['weight'] += 1
                else:
                    G.add_edge(first_site, second_site, weight=1)

                prev_row = row
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

my_play_by_play = playByPlay('0021500492.json', 'playbyplay.json',  # input data
                             'momentsdump.csv', 'three_player.csv', 'playerdump.csv',  # o/p i/p for moments part
                             'play_by_play.csv', 'possession.csv',  # o/p i/p for play by play part
                             'possession_graph.json')  # o/p for graph generation part

