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
            current_game.avg_del /= current_game.score
            current_game.avg_get /= (current_game.score + current_game.lost_c)
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
    f = open('eval/base-rand.log')
    data = parse(f)

    for i in calcAVG(data):
        print(i)