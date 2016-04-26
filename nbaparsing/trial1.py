# from os import path
import json
import csv


gamedata = json.load(open('0021500492.json'))
print gamedata.keys()

print gamedata['events'][0]['visitor']['teamid']
print gamedata['events'][0]['home']['teamid']

visitor_list = gamedata['events'][0]['visitor']['players']
home_list = gamedata['events'][0]['home']['players']

print gamedata['events'][0]['home']['name']

# visitor_dict = {}
# home_dict = {}
#
# specific_keys = {'lastname', 'firstname', 'jersey', 'position'}
#
# for player in visitor_list:
#     visitor_dict[player['playerid']] = {}
#     for keys in specific_keys:
#         visitor_dict[player['playerid']][keys] = player[keys]
#
# for player in home_list:
#     home_dict[player['playerid']] = {}
#     for keys in specific_keys:
#         home_dict[player['playerid']][keys] = player[keys]
#
# print visitor_dict.keys()
#
# print home_dict.keys()

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


# for file_index in range(1,7):
#     pass_data = json.load(open(path.join('play_by_play_data', '{}.json'.format(file_index))))
#     for i, row in enumerate(pass_data['resultSets'][0]['rowSet']):
#         if row[27] == 0 and row[13] == 0 and row[20] != 0:  # only 2nd
#             print 'only 2'
#             print row
#         elif row[13] == 0 and row[27] != 0 and row[20] != 0:  # 2nd and 3rd
#             print '2 and 3'
#             print row
#         elif row[20] == 0 and row[27] != 0 and row[13] != 0:  # 1st and 3rd
#             print '1 and 3'
#             print row
#         elif row[27] != 0 and row[13] == 0 and row[20] == 0:  # only 3rd
#             print '3'
#             print row
#         elif row[13] != 0 and row[20] != 0 and row[27] != 0:  # all three
#             print 'all 3'
#             print row
#
# with open('shotclock_reset.csv', 'rb') as f:
#     reader = csv.reader(f)
#     for i, row in enumerate(reader):
#         print row
#         if i >20:
#             break