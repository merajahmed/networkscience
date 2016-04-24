__author__ = 'meraj'
import csv
import json


gamedata = json.load(open('0021500492.json'))
print gamedata.keys()
print(gamedata['gamedate'], gamedata['gameid'])

playermoments = []
for event in gamedata['events']:
    for moment in event['moments']:
        playermoments.append(moment)
playermoments.sort(key=lambda x:(int(4-x[0]),x[2],x[3]), reverse=True)
with open('momentsdump.csv', 'wb') as momentsdump:
    writer = csv.writer(momentsdump)
    # for moment in playermoments:
    #     writer.writerow(moment)
    # momentsdump.close()
    # trial_moments = []
    # trial = []
    # final_moments = []
    for playermoment in playermoments:
        for i in range(0, 10):
            trial = [playermoment[0], playermoment[2], playermoment[3]]
            trial.extend(playermoment[5][i])
            writer.writerow(trial)

with open('momentsdump.csv', 'rb') as f:
    shotclock = None
    for row in csv.reader(f):
        # print type(row[2])
        shot_clock = float(row[2])
        break


with open('momentsdump.csv', 'rb') as f, open('shotclock_reset.csv', 'w') as shot_clock_reset_log:
    writer = csv.writer(shot_clock_reset_log)
    for row in csv.reader(f):
        try:
            # print row[2]
            if float(row[2]) >= shot_clock:
                writer.writerow(row)
        except ValueError, e:
            pass