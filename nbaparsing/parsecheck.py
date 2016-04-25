__author__ = 'meraj'
import csv
import json


gamedata = json.load(open('0021500492.json'))
print gamedata.keys()
print(gamedata['gamedate'], gamedata['gameid'])


playermoments = []
quarter_time_sets = set()

for event in gamedata['events']:
    for moment in event['moments']:
        if (moment[0], moment[3]) not in quarter_time_sets:
            quarter_time_sets.add((moment[0], moment[3]))
            playermoments.append(moment)

# print quarter_time_sets

playermoments.sort(key=lambda x:(int(4-x[0]),x[2],x[3]), reverse=True)

# for i, moment in enumerate(playermoments):
#     # print moment
#     if i >1000:
#         break
# print len(playermoments[0][5])
#
with open('momentsdump.csv', 'wb') as momentsdump:
    writer = csv.writer(momentsdump)
    for playermoment in playermoments:
        if len(playermoment[5]) < 11:
            continue
        for i in range(0, 11):
            trial = [playermoment[0], playermoment[2], playermoment[3]]
            trial.extend(playermoment[5][i])
            writer.writerow(trial)

# with open('momentsdump.csv', 'rb') as f:
#     shotclock = None
#     for row in csv.reader(f):
#         # print type(row[2])
#         shot_clock = float(row[2])
#         break
#
#
# with open('momentsdump.csv', 'rb') as f, open('shotclock_reset.csv', 'w') as shot_clock_reset_log:
#     writer = csv.writer(shot_clock_reset_log)
#     for row in csv.reader(f):
#         try:
#             # print row[2]
#             if float(row[2]) >= shot_clock:
#                 writer.writerow(row)
#         except ValueError, e:
#             pass