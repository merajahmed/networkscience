from math import sqrt, pow
from heapq import nsmallest
import csv

def closer(ball_data, my_list):
    index_x = 5
    index_y = 6

    # print ball_data
    ball_x = float(ball_data[index_x])
    ball_y = float(ball_data[index_y])

    # 3 - team id
    # 4 - player id
    # print ball_x, ball_y, my_list[0][index_x], my_list[0][index_x]
    # print my_list[0]
    player_ball = [sqrt(pow(float(player_detail[index_x]) - ball_x, 2) + pow(float(player_detail[index_y]) - ball_y, 2)) for player_detail in my_list]
    player_index = player_ball.index(min(player_ball))

    three_players = [player_ball.index(item) for item in nsmallest(3, player_ball)]
    # print three_players
    with open('three_player.csv', 'a') as out_file:
        writer = csv.writer(out_file)
        row = [my_list[player_index][1]]
        # print my_list[player_index]
        row.extend([(my_list[index][4], player_ball[index]) for index in three_players])
        writer.writerow(row)

    return my_list[player_index][1], my_list[player_index][2], my_list[player_index][4], my_list[player_index][index_x], my_list[player_index][index_y], player_ball[player_index],


with open('momentsdump.csv', 'r') as f:
    trial = []
    final_player_data = []
    ball_data = []
    open('three_player.csv', 'w').close()
    with open('playerdump.csv', 'wb') as out_file:
        writer = csv.writer(out_file)
        for i, line in enumerate(csv.reader(f)):
            if (i + 1) % 11 == 0:
                # print ball_data
                final_player = closer(ball_data, trial)
                writer.writerow(final_player)
                trial = []
                # break
            else:
                # print line
                if int(line[3]) == -1:
                    ball_data = line
                else:
                    trial.append(line)
            if i > 10000:
                break
                # print trial



## Two possible algorithms
## 1) Take frame
## 2) find closest player
## 3) dist >0 and < 1.01
## 4) Compare consecutive time frames upto 4 for ball and see if closest distance changes
## 5) If predicted ball position (or remembered player's position changes), then player lost possession the moment it crossed the distance threshold
## 6) Keep evaluating the frames till distance returns back to 0.something and stays like that