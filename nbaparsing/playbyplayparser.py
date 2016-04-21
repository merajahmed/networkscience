__author__ = 'anirban'
import json
import csv
from collections import OrderedDict

pass_data = json.load(open('playbyplay.json'))
# pass_data = json.load(open('play_by_play_data/2.json'))
headers = pass_data['resultSets'][0]['headers']
header_names = headers[0:5] + headers[6:8] + headers[9:11] + headers[12:-3]

event_dict = {}
team_ids = []

# Automated code to get home and visitor team id


# print gamedata.keys()

# team_ids[0] = gamedata['events'][0]['home']['teamid']
# team_ids[1] = gamedata['events'][0]['visitor']['teamid']

# team_ids = ['1610612752', '1610612741']
team_ids = ['1610612761', '1610612766']

# 1 - shot (i and i+1 comparison)
# 2 - miss and possible blocks ( again check i and i+1 events)
# 3 -
#    10 - possession switch
#    11 - possession kept
#    12 - posssession switched
# 5 - possession lost
# 6 - fouls - other event gets possession
# 7 - violation - other event gets possession
# 8 - substitution

# s.foul -> opponent team had possession, retains possession

def combined_rule_runner(event_id, sub_event_id, home_event, away_event):
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


def rule_runner(event_id, sub_event_id, home_event, away_event):
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
        return combined_rule_runner(event_id, sub_event_id, home_event, away_event)

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


def possession_time(row):
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
        players = [player for player in player_dict.keys() if player_dict[player] == team_ids[int(post_flag)]]
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
        pre_player = [player for player in player_dict.keys() if player_dict[player] == team_ids[int(pre_flag)]]
        post_player = [player for player in player_dict.keys() if player_dict[player] == team_ids[int(post_flag)]]
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


with open('play_by_play.csv', 'wb') as play_file:
    play_writer = csv.writer(play_file)
    play_writer.writerow(['Quarter', 'GameClock', 'EventId', 'Who has the ball', 'Who will now have the ball', 'Home_event', 'Away_event', 'Player1', 'Player1_team_id', 'Player2', 'Player2_team_id', 'Player3', 'Player3_team_id'])
    for i, row in enumerate(pass_data['resultSets'][0]['rowSet']):
        # player_1 id 13, 15 team_id
        # player_2 id 20, 22 team_id
        # player_3 is 27, 29 team_id

        # if row[2] == 4:  # rebounds
        #     continue

        minutes, seconds = row[6].split(':')
        row[6] = float(minutes) * 60 + float(seconds)

        pre_possession_flag, post_possession_flag = rule_runner(row[2], row[3], row[7], row[9])
        if pre_possession_flag == -2 and post_possession_flag == -2:
            continue

        if row[2] == 2:  # misses
            next_row = pass_data['resultSets'][0]['rowSet'][i + 1]
            if next_row[2] == 4:  # rebounds
                pre_flag, post_flag = rule_runner(next_row[2], next_row[3], next_row[7], next_row[9])
                post_possession_flag = post_flag

                # play_writer.writerow([row[6], row[2], pre_possession_flag, post_possession_flag, row[7], row[9], row[13], row[20], row[27]])
                # continue

                # play_writer.writerow([next_row[6], pre_flag, post_flag, next_row[7], next_row[9]])

        play_writer.writerow([row[4], row[6], row[2], pre_possession_flag, post_possession_flag, row[7], row[9], row[13], row[15], row[20], row[22], row[27], row[29]])
#
#
with open('play_by_play.csv', 'rb') as play_file, open('possession.csv', 'wb') as poss_file:
    writer = csv.writer(poss_file)
    writer.writerow(['Quarter', 'Gametime', 'Player_Id'])
    for index, row in enumerate(csv.reader(play_file)):
        if index == 0:
            continue
        my_list = possession_time(row)
        for r in my_list:
            writer.writerow(r)
    writer.writerow([4, 0.0, -1])
    # break

# print json.dumps(event_dict, sort_keys=True, indent=4)


# player name or player id

