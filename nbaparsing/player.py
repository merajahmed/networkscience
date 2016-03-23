__author__ = 'anirban'

import csv
from math import sqrt, pow

def closer(ball_data, my_list):
    # print ball_data
    ball_x = float(ball_data[4])
    ball_y = float(ball_data[5])

    player_ball = [sqrt(pow(float(player_detail[4]) - ball_x, 2) + pow(float(player_detail[5]) - ball_y, 2)) for player_detail in my_list]
    player_index = player_ball.index(min(player_ball))

    return my_list[player_index][1], my_list[player_index][2], my_list[player_index][3], my_list[player_index][4], my_list[player_index][5], player_ball[player_index],


with open('momentsdump.csv', 'r') as f:
    trial = []
    final_player_data = []
    ball_data = []
    with open('playerdump.csv', 'wb') as out_file:
        writer = csv.writer(out_file)
        for i, line in enumerate(csv.reader(f)):
            if (i + 1) % 11 == 0:
                # print ball_data
                final_player = closer(ball_data, trial)
                writer.writerow(final_player)
                trial = []
            else:
                # print line
                if int(line[3]) == -1:
                    ball_data = line
                else:
                    trial.append(line)
                # print trial