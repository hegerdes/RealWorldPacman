import os
import sys
import json
import pickle
import argparse
import time
import gzip
import tarfile
import requests
from Client import Client
from tools.Geo2GameCoords import Geo2GameCoords
from tools.bounds import Bounds

parser = argparse.ArgumentParser(
    description='Starts a dedicated client for plotting. Tries and connects to the lobby of a Server.')
parser.add_argument('-c', '--config', help='pickle file with configuration',
                    default='clientsettings.pickle')
parser.add_argument('-o', '--output', help='output file, where bonnmotion' \
                                           + 'traces are saved to.', default='log.tar.gz')
parser.add_argument('-f', '--frequency', help='sample rate in samples per' \
                                              + 'second', default=5, type=int)
parser.add_argument('-m', '--osm-map', help='osm file', default='map.osm')
parser.add_argument('-d', '--tiles-dim', help='dimensions of tiles', default=3,
                    type=int)
parser.add_argument('-z', '--zoom-level', help='zoom level of tiles', default=15,
                    type=int)
parser.add_argument('-wi', '--width', help='Screen width', default=768, type=int)
parser.add_argument('-he', '--height', help='Screen height', default=768, type=int)
parser.add_argument('-u', '--url', help='URL of OSRM (e.g. "http://localhost:5000")',
                    default=None)

args = parser.parse_args()

if os.path.exists(args.config):
    with open(args.config, 'rb') as f:
        config = pickle.load(f)
else:
    config = {
        'IP': 'localhost',
        'PORT': '25565',
        'USERNAME': 'plotter',
    }
config['USERNAME'] = 'plotter'

print(f'config:')
for key, val in config.items():
    print(f'\t{key}: {val}')

client = Client(config['IP'], int(config['PORT']), config['USERNAME'])
client.makeObserver()

bounds = Bounds(args.osm_map, args.tiles_dim, args.zoom_level)
start = bounds.get_start_gps_bounds()
end = bounds.get_end_gps_bounds()
trans = Geo2GameCoords((start[1], end[0], end[1], start[0]),
                       (args.width, args.height))

running = True
start = None
data = None
players = None
ghosts = None

while running:
    client.Loop()
    if client.gamestarted:

        if not start:
            start = time.time()
            now = 0
            print(f'match started at {start}.')
        else:
            now = time.time() - start

        # first get initial data from server. 
        # (especially the number of players and ghosts!)
        if not ghosts or not players:
            print('waiting for server data...')
        while not ghosts or not players:
            print('pumping')
            client.Loop()
            players = client.playerList
            ghosts = client.ghostlist
            time.sleep(.002)
        if not ghosts or not players:
            print('done!')

        # players = client.playerList
        # ghosts = client.ghostlist

        if not data:
            # save meta information
            participating = [p for p in players if p[4]]
            # create a blank line for each node
            data = [[] for _ in participating + ghosts]
            # get usernames
            print(players)
            meta = {'num_players': len(participating),
                    'num_ghosts': len(ghosts),
                    'total': len(participating) + len(ghosts), 
                    'usernames': [p[5] for p in participating],}
            print(f'There are {meta["num_players"]} players and ' \
                  + f'{meta["num_ghosts"]} Ghosts in this match. (Total ' \
                  + f'participating: {meta["total"]})')

        # get timestamp and location for every participating player
        ignored = 0
        for i, player in enumerate(participating):
            if player[4]:
                data[i].append({
                    'time': now,
                    'geo': trans.detransform(player[0], player[1]),
                })
            else:
                ignored += 1
        for j, ghost in enumerate(ghosts):
            data[meta['num_players'] + j].append({
                'time': now,
                'geo': trans.detransform(ghost[0], ghost[1]),
            })

        print(f'time: {now}, logged {len(participating) - ignored} player and {len(ghosts)} ghost locations')

    time.sleep(1 / args.frequency)
    running = not client.gamestopped

print('-----------------------------\nResults:')
if data and len(data) > 0:
    total = sum([len(row) for row in data])
    print(f'logged {total} in total!\n')

    print(f'starting to write to "{args.output}"...')

    # finding nonexistent filenames
    plot_filename = 'plot.movements.geo.gz'
    meta_filename = 'meta.txt'

    # check if files are already existing
    question = f'There exists one or both file ({plot_filename} or ' \
               + f'{meta_filename}) that have to be temporarily written. Do you ' \
               + 'want to overwrite existing files? (y/n)'
    if os.path.exists(plot_filename) or os.path.exists(meta_filename):
        answer = input(question)
        while answer != 'y' and answer != 'n':
            print('Please type in \'y\' or \'n\'!')
            answer = input(question)
        if answer == 'n':
            print('Canceling. No output written.')
            sys.exit()

    # correct data accoring to street map
    if args.url:
        sum_deviants = 0
        num_corrected = 0
        num_failed = 0
        print('Try and correct geo data to street map by using osrm@{args.url}.')
        player_id = 0
        for node in data:
            node_pos = 0
            for datum in node:
                request = f'{args.url}/nearest/v1/driving/{datum["geo"][1]},{datum["geo"][0]}'
                print(f'performing request: {request}')
                resp = requests.get(request)
                result = json.loads(resp.text)
                if result["code"] == "Ok":
                    dist = result["waypoints"][0]["distance"]
                    corr = result["waypoints"][0]["location"]
                    datum[1], datum[0] = corr
                    sum_deviants += dist
                    num_corrected += 1
                else:
                    print('[WARN] could not correct waypoint of player ' \
                          + f'{player_id} at position {node_pos}!')
                    num_failed += 1

                node_pos += 1

            player_id += 1

        if num_failed != 0:
            print(f'[WARN] There were problems with {num_failed} waypoints.')

        print(f'summed deviant distance is: {sum_deviants}, average: ' \
              + f'{sum_deviants / num_corrected}')
    else:
        print('If OSRM correction is desired please give url via -u (--url)!')

    # write the bonnmotion plots
    with gzip.open(plot_filename, 'wt+') as f:
        for node in data:
            for datum in node:
                # write datum to current line
                f.write(f'{datum["time"]} [{datum["geo"][0]} {datum["geo"][1]}], ')
            # begin new node by starting a new line if line is not still empty
            if len(node) > 0:
                f.write('\n')

    # write meta information
    with open(meta_filename, 'wt') as f:
        f.write(json.dumps(meta))

    print(f'start packing the tar archive ("{args.output}")...')
    with tarfile.open(args.output, 'w:gz') as archive:
        archive.add(plot_filename)
        archive.add(meta_filename)

    # remove temp files
    os.remove(plot_filename)
    os.remove(meta_filename)

    print('done!')

else:
    print('no data has been logged')
