from operator import itemgetter

__author__ = 'meraj'
import json
import csv

gamedata = json.load(open('0021500492.json'))
print gamedata.keys()

playermoments = []
for event in gamedata['events']:
    for moment in event['moments']:
        playermoments.append(moment)
playermoments.sort(key=lambda x:(4-x[0],x[2]), reverse=True)
momentsdump = open('momentsdump.csv','w')
writer = csv.writer(momentsdump)
# for moment in playermoments:
#     writer.writerow(moment)
# momentsdump.close()
trial_moments = []
trial = []
final_moments = []
for playermoment in playermoments:
    for i in range(0, 10):
        trial = [playermoment[0], playermoment[2]]
        trial.extend(playermoment[5][i])
        writer.writerow(trial)
