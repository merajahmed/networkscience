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



                    ## Two possible algorithms
                    ## 1) Take frame
                    ## 2) find closest player
                    ## 3) dist >0 and < 1.01
                    ## 4) Compare consecutive time frames upto 4 for ball and see if closest distance changes
                    ## 5) If predicted ball position (or remembered player's position changes), then player lost possession the moment it crossed the distance threshold
                    ## 6) Keep evaluating the frames till distance returns back to 0.something and stays like that