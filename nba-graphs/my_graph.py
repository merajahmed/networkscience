__author__ = 'anirban'
from math import sqrt, pow
from heapq import nsmallest
import csv

# keep threshold as less than 1.1 for atleast 5 frames.. if so, then that person has possession

# rule changes in terms of events like shots -> we know who provides the assist and who took the shot,
# so we can discount players in between. Besides that, we are bound to have false positives. Hence, filter out
# that we have people of the same team only retaining possession in one play. So we have to recalculate closest
# distance for players of same team in one play

# retain only between timeperiods of playbyplay

## VERY IMPORTANT
# change visitor_list to vistor_dict.keys and similar for home_list
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

    # three_players = [player_ball.index(item) for item in nsmallest(3, player_ball)]
    # # print three_players
    # with open('three_player.csv', 'a') as out_file:
    #     writer = csv.writer(out_file)
    #     # print my_list[player_index]
    #     for index in three_players:
    #         writer.writerow([my_list[player_index][1], my_list[index][4], player_ball[index]])

    return [my_list[player_index][1], my_list[player_index][2], my_list[player_index][4], my_list[player_index][index_x], my_list[player_index][index_y], player_ball[player_index]]


def perform_moments_stuff(movement_list, moments):
    first_look = int(float(movement_list[0][2]))
    second_look = int(float(movement_list[1][2]))

    first_time = int(float(movement_list[0][1]))
    last_time = int(float(movement_list[-1][1]))

    my_temp_list = None

    if first_look == 0:
        my_temp_list = home_list
    elif first_look == 1:
        my_temp_list = visitor_list
    elif first_look == -4 or -5:
        if second_look == 0 or second_look in home_list:
            my_temp_list = home_list
        elif second_look == 1 or second_look in visitor_list:
            my_temp_list = visitor_list

    moment_list = []
    trial = []
    ball_data = None
    for i, row in enumerate(moments):
        if (i + 1) % 12 == 0:
            if int(row[4]) in my_temp_list:
                trial.append(row)

            if float(row[1]) > first_time:  # can change this to first_time + 1 later
                trial = []
                continue
            # print ball_data
            # print trial
            final_player = closer(ball_data, trial)
            # print final_player[5]
            if final_player[5] <= 1.1:  # for distance threshold
                # print final_player
                moment_list.append(final_player)
            trial = []
            if int(float(row[1]) - 0.04) < last_time:
                break
        else:
            try:
                if int(row[3]) == -1:
                    ball_data = row
                else:
                    if int(row[4]) in my_temp_list:
                        trial.append(row)
            except:
                # print row
                # print 'yolo'
                exit(1)

    # print moment_list
    if not moment_list:
        # print 'yolo'
        return None

    current_player = moment_list[0][2]
    new_moments = []
    prev_row = moment_list[0]
    for moment in moment_list[1:]:
        if moment[2] == current_player:
            prev_row = moment
        elif moment[2] != current_player:
            new_moments.append(prev_row)
            new_moments.append(moment)
            current_player = moment[2]

    prev_row = movement_list[0]
    new_data = [movement_list[0]]
    my_index = 0
    j = 0
    i = 1
    for movement in movement_list[1:]:
        for moment in new_moments[my_index:]:
            if moment[0] > movement[1]:  # movement consists of time at index 1 and moment consists of time at index 0
                new_data.append([prev_row[0], moment[0], moment[2]])
                j += 1
                my_index += 1
            else:
                new_data.append(movement)
                i += 1
                break
        if j == len(new_moments):
            new_data.extend(movement_list[i:])
            break
        i += 1

    prev_row = new_data[0]
    indices_list = []
    for i, row in enumerate(new_data[1:]):
        if row[2] == prev_row[2]:
            indices_list.append(i - len(indices_list))
        else:
            prev_row = row

    for indices in indices_list:
        del new_data[indices]

    # print new_data

    return new_data

visitor_list = [203584, 202689, 1626151, 203148, 203469, 203087, 101107, 203798, 202391, 1626163, 201587, 201946, 201150]
home_list = [200768, 201960, 1626153, 203082, 202685, 2449, 202709, 201942, 203512, 202335, 201949, 203998, 202687]


start_nodes = [0, 1, -4, -5]
end_nodes = [-2, -3, -1, -6]



def merger():
    my_list = []
    current_quarter = 1
    entire_correct_play = []
    with open('possession.csv', 'rb') as f, open('momentsdump.csv', 'rb') as moments_file:
        reader = csv.reader(f)
        moments_reader = csv.reader(moments_file)
        reader.next()  # to ignore header
        prev_row = moments_reader.next()
        moments = [[prev_row]]
        j = 0
        for i, moment in enumerate(moments_reader):
            if moment[0] > prev_row[0]:
                j += 1
                moments.append([moment])

            moments[j].append(moment)
            prev_row = moment

        for i, row in enumerate(reader):
            my_list.append(row)
            if len(row[2]) <= 2:
                if int(row[2]) in end_nodes:
                    quarter = int(row[0]) - 1
                    asd = perform_moments_stuff(my_list, moments[quarter])
                    if asd is not None:
                        entire_correct_play.extend(asd)
                    my_list = []

    with open('possession.csv', 'wb') as out_file:
        writer = csv.writer(out_file)
        for row in entire_correct_play:
            writer.writerow(row)

merger()