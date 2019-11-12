import copy
import time
import datetime


class Metric():
    def __init__(self):
        self.score = 0
        self.lost_c = 0
        self.avg_get = datetime.timedelta()
        self.avg_del = datetime.timedelta()

    def print(self):
        pass


def parse(p_file):
    current_game = None
    games = []
    skip = False
    last_time = None
    for line in p_file:
        if('PARAMS' in line): break
        if(skip):
            skip = False
            continue
        args = line.split(':')
        if 'Spiel gestartet\n' in args:
            current_game = Metric()
            last_time = datetime.datetime.fromtimestamp(time.mktime(time.strptime(args[2], "%d %m %Y %H-%M-%S")))
            skip = True
        if 'Spiel Vorbei\n' in args:
            if(current_game.score > 0):
                current_game.avg_del /= current_game.score
            else:
                current_game.avg_del = datetime.timedelta(minutes=5)
            if(current_game.score + current_game.lost_c > 0):
                current_game.avg_get /= (current_game.score + current_game.lost_c)
            else:
                current_game.avg_get = datetime.timedelta(minutes=5)
            games.append(copy.deepcopy(current_game))
            current_game = None
        if 'SC' in args:
            cur_time = datetime.datetime.fromtimestamp(time.mktime(time.strptime(args[2], "%d %m %Y %H-%M-%S")))
            current_game.avg_del += cur_time -last_time
            last_time = cur_time
            current_game.score += 1
            skip = True
        if 'GP' in args:
            cur_time = datetime.datetime.fromtimestamp(time.mktime(time.strptime(args[2], "%d %m %Y %H-%M-%S")))
            current_game.avg_get += cur_time -last_time
            last_time = cur_time
        if 'LP' in args:
            if(current_game):
                current_game.lost_c += 1
                last_time = datetime.datetime.fromtimestamp(time.mktime(time.strptime(args[2], "%d %m %Y %H-%M-%S")))

    return games

def calcAVG(games):
    score = 0
    lost_count = 0
    avg_get = datetime.timedelta()
    avg_del = datetime.timedelta()

    for game in games:
        score += game.score
        lost_count += game.lost_c
        avg_get += game.avg_get
        avg_del += game.avg_del

    score /= len(games)
    lost_count /= len(games)
    avg_del /= len(games)
    avg_get /= len(games)
    return [score, lost_count, avg_get, avg_del]

def printLog(date):
    for game in data:
        print('Score:',game.score, '\nLost_count:', game.lost_c, '\nAVG_get:', game.avg_get, '\nAVG_del:', game.avg_del)


if __name__ == "__main__":

    logs_rand_num = ['eval/rand/ghost_num/base-rand.log','eval/rand/ghost_num/ghost+2-rand.log', 'eval/rand/ghost_num/ghost+4-rand.log', 'eval/rand/ghost_num/ghost+6-rand.log', 'eval/rand/ghost_num/ghost+8-rand.log']

    logs_rand_pasue = ['eval/rand/ghost_pause/pause_base.log','eval/rand/ghost_pause/pause_2000.log', 'eval/rand/ghost_pause/pause_4000.log']

    logs_rand_speed = ['eval/rand/ghost_speed/speed_0_8.log', 'eval/rand/ghost_speed/speed_base.log', 'eval/rand/ghost_speed/speed_4_12.log', 'eval/rand/ghost_speed/speed_6_14.log']

    logs_mslaw_num = ['eval/mslaw/ghost_num/mslaw_base.log', 'eval/mslaw/ghost_num/ghost+2-mslaw.log', 'eval/mslaw/ghost_num/ghost+4-mslaw.log', 'eval/mslaw/ghost_num/ghost+6-mslaw.log']

    logs_mslaw_speed = ['eval/mslaw/ghost_num/mslaw_base.log', 'eval/mslaw/ghost_speed/speed_0_8-mslaw.log', 'eval/mslaw/ghost_speed/speed_4_12-mslaw.log']

    logs_mslaw_cluster_ratio = ['eval/mslaw/cluster_ratio/mslaw_base.log','eval/mslaw/cluster_ratio/cluster_ratio_10.log', 'eval/mslaw/cluster_ratio/cluster_ratio_15.log', 'eval/mslaw/cluster_ratio/cluster_ratio_2.log']

    logs_mslaw_cluster_range = ['eval/mslaw/cluster_range/mslaw_base.log','eval/mslaw/cluster_range/cluster_range_20.log', 'eval/mslaw/cluster_range/cluster_range_30.log', 'eval/mslaw/cluster_range/cluster_range_40.log', 'eval/mslaw/cluster_range/cluster_range_50.log']

    logs_mslaw_waypoint_num = ['eval/mslaw/numWaypoints/mslaw_base.log', 'eval/mslaw/numWaypoints/waypoints_200.log']

    logs = logs_mslaw_waypoint_num
    for log in logs:
        print(log)
        f = open(log)
        data = parse(f)

        for i in calcAVG(data):
            print(i)