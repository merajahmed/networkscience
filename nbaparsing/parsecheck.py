from operator import itemgetter

__author__ = 'meraj'
import json
import csv

# gamedata = json.load(open('0021500492.json'))
# print gamedata.keys()
# print(gamedata['gamedate'], gamedata['gameid'])
#
# playermoments = []
# for event in gamedata['events']:
#     for moment in event['moments']:
#         playermoments.append(moment)
# playermoments.sort(key=lambda x:(int(4-x[0]),x[2],x[3]), reverse=True)
# momentsdump = open('momentsdump.csv','w')
# writer = csv.writer(momentsdump)
# # for moment in playermoments:
# #     writer.writerow(moment)
# # momentsdump.close()
# # trial_moments = []
# # trial = []
# # final_moments = []
# for playermoment in playermoments:
#     for i in range(0, 10):
#         trial = [playermoment[0], playermoment[2], playermoment[3]]
#         trial.extend(playermoment[5][i])
#         writer.writerow(trial)
with open('momentsdump.csv','rb') as f:
    shotclock = None
    for i, row in enumerate(csv.reader(f)):
        shotclock = float(row[2])
        break


with open('momentsdump.csv','rb') as f:
    shotclockresetlog = open('shotclock_reset.csv','w')
    writer = csv.writer(shotclockresetlog)
    for i, row in enumerate(csv.reader(f)):
        print(row[2])
        if float(row[2]) >= shotclock:
            writer.writerow(row)

    shotclockresetlog.close()
