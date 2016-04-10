__author__ = 'anirban'
import json
import csv

pass_data = json.load(open('playbyplay.json'))

headers = pass_data['resultSets'][0]['headers']
header_names = headers[0:5] + headers[6:8] + headers[9:11] + headers[12:-3]

event_dict = {}

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


def combined_rule_runner(event_id, sub_event_id, home_event, away_event):
    '''
    Runs rules when both events are present
    :param event_id: ids describing broad events
    :param sub_event_id: ids describing sub types of broad events
    :returns: outcomes:- 0 for home event, 1 for away event or -1 to check i and i+1 comparison or -2 for useless events
    '''

    if event_id == 5:
        if 'STEAL' in home_event: # specific to steals and turnovers
            return 0
        elif 'STEAL' in away_event: # specific to steals and turnovers
            return 1
        else:
            return -1

    return -1


def rule_runner(event_id, sub_event_id, home_event, away_event):
    '''
    Runs rules on the basis of event_ids, sub_event ids and team flag
    :param event_id: ids describing broad events
    :param sub_event_id: ids describing sub types of broad events
    :returns: outcomes:- 0 for home event, 1 for away event or -1 to check i and i+1 comparison or -2 for useless events
    '''

    # worry about 8 - substitution and 9 - timeouts later

    if event_id in [8, 9, 12, 13, 18]:
        return -2

    if event_id in [1, 2, 4]: # shots, misses, rebounds
        return -1

    if home_event is None:
        team_flag = 1
    elif away_event is None:
        team_flag = 0
    else:
        return combined_rule_runner(event_id, sub_event_id, home_event, away_event)

    if event_id == 3: # for free throws
        if sub_event_id != 11:
            return int(not team_flag)
        else: # 11 stands for free throw 1 of 2
            return team_flag
    elif event_id in [5, 6, 7]: # turnovers, fouls, violations
        return int(not team_flag)
    elif event_id == 10:
        return team_flag

# for i, row in enumerate(pass_data['resultSets'][0]['rowSet']):
#     if row[2] not in event_dict:
#         event_dict[row[2]] = {}
#
#     if row[3] not in event_dict[row[2]]:
#         event_dict[row[2]][row[3]] = [row[6], row[7], row[9]]

# print event_dict
# print json.dumps(event_dict, sort_keys=True, indent=4)

# for event_id in event_dict.keys():
#     for sub_event_id in event_dict[event_id].keys():
#         home_event = event_dict[event_id][sub_event_id][1]
#         away_event = event_dict[event_id][sub_event_id][2]
#         event_dict[event_id][sub_event_id].append(rule_runner(event_id, sub_event_id, home_event, away_event))

with open('play_by_play.csv', 'wb') as play_file:
    play_writer = csv.writer(play_file)
    play_writer.writerow(['GameClock', 'Possession_ID', 'Home_event', 'Away_event'])
    for i, row in enumerate(pass_data['resultSets'][0]['rowSet']):
        possession_flag = rule_runner(row[2], row[3], row[7], row[9])
        play_writer.writerow([row[6], possession_flag, row[7], row[9]])

# print json.dumps(event_dict, sort_keys=True, indent=4)


# player name or player id

# with open('play_by_play_home.csv', 'wb') as home_file, open('play_by_play_away.csv', 'wb') as away_file, open('play_by_play_possession.csv', 'wb') as possession_file:
#     home_writer = csv.writer(home_file)
#     home_writer.writerow([name for name in header_names if name != 'VISITORDESCRIPTION'])
#     away_writer = csv.writer(away_file)
#     away_writer.writerow([name for name in header_names if name != 'HOMEDESCRIPTION'])
#     possesion_writer = csv.writer(possession_file)
#     possesion_writer.writerow(header_names)
#     for row in pass_data['resultSets'][0]['rowSet']:
#         # consider row[7], row[8], row[9] -> descriptions for home, neutral, away
#         my_list = row[0:5]
#         my_list.extend(row[6:8])
#         my_list.extend(row[9:11])
#         my_list.extend(row[12:-3])
#
#         if row[7] is not None and row[9] is not None:
#             possesion_writer.writerow(my_list)
#         elif row[7] is not None:
#             del my_list[9]
#             home_writer.writerow(my_list)
#         elif row[9] is not None:
#             del my_list[7]
#             away_writer.writerow(my_list)

32