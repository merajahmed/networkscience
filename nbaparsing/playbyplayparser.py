__author__ = 'anirban'
import json

pass_data = json.load(open('playbyplay.json'))

headers = pass_data['resultSets'][0]['headers']
header_names = headers[0:5] + headers[6:8] + headers[9:11] + headers[12:-3]

event_dict = {}

for i, row in enumerate(pass_data['resultSets'][0]['rowSet']):
    if row[2] not in event_dict:
        event_dict[row[2]] = {}

    if row[3] not in event_dict[row[2]]:
        event_dict[row[2]][row[3]] = [row[6], row[7], row[9]]

# print event_dict
print json.dumps(event_dict, sort_keys=True, indent=4)

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