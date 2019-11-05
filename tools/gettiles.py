import requests
import shutil
import copy
import tools.geo2tiles
import math
import os.path


def get_url(tile_x, tile_y, zoom):
    return 'https://a.tile.openstreetmap.de/' + str(zoom) + '/' + str(tile_x) + '/' + str(tile_y) + '.png'


# Download the tile and save it to images
def getTilePath(tile_x, tile_y, zoom):
    path = 'images/map_' + str(zoom) + '_' + str(tile_x) + '_' + str(tile_y) + '.png'
    # Ceck if file alradex exists
    if (not os.path.exists(path)):
        url = get_url(tile_x, tile_y, zoom)
        print('Downloading: ' + url)
        pic = requests.get(url, stream=True)
        path = 'images/map_' + str(zoom) + '_' + str(tile_x) + '_' + str(tile_y) + '.png'
        with open(path, 'wb') as out_file:
            shutil.copyfileobj(pic.raw, out_file)
    return path[7:]


# Generates a list of tiles
def get_all_tile_numbers(lat_min, lon_min, lat_max, lon_max, zoom):
    tiele_list = list()
    tiles_min = gps2tiles.deg2num(lat_min, lon_min, zoom)
    tiles_max = deg2num(lat_max, lon_max, zoom)
    for tile_x in range(tiles_min[0], tiles_max[0]):
        tmp = list()
        for tile_y in range(tiles_max[1], tiles_min[1]):
            tmp.append(getTilePath(tile_x, tile_y, zoom))
        tiele_list.append(copy.deepcopy(tmp))
    return tiele_list


def get_tile_mosaic(start_x, start_y, zoom, DIM=3):
    tiele_list = list()
    for tile_x in range(start_x, start_x + DIM):
        tmp = list()
        for tile_y in range(start_y, start_y + DIM):
            tmp.append(getTilePath(tile_x, tile_y, zoom))
        tiele_list.append(copy.deepcopy(tmp))
    return tiele_list


if __name__ == "__main__":
    print('Call this as a import')
