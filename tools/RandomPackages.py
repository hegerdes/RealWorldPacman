import xml.etree.ElementTree as emt
import random
import osmread
import sys
import math
import tools.Geo2GameCoords as g2


class RandomPackages:
    """Generate random Points on the streets/nodes of the given OSM file """

    def __init__(self, osm_dict):
        self.all_streets = osm_dict

    def set_bounding_box(self, minlat, maxlat, minlon, maxlon):
        self.minlat = minlat
        self.maxlat = maxlat
        self.minlon = minlon
        self.maxlon = maxlon

    def get_random_from_osm(self, number_points):
        return get_points(self.minlat, self.maxlat, self.minlon, self.maxlon, number_points)

    def get_random_end_point_from_osm(self, number_points):
        return get_end_points(self.minlat, self.maxlat, self.minlon, self.maxlon, number_points)

    def get_random_start_point_from_osm(self, number_points):
        return get_start_points(self.minlat, self.maxlat, self.minlon, self.maxlon, number_points)

    def get_point_on_node(self):
        """Returns a point as a tuple (latitude, longitude) on a node which is in the middle of the box"""

        dist = {}
        random_point = self.get_random_from_osm(1)
        for ways in self.all_streets:
            for lists in self.all_streets[ways]:
                dist[(calculateDistance(lists[0][0], lists[0][1], random_point[0][0], random_point[0][1]))] = (lists[0])

        nearest_node = dist[min(dist)]
        return nearest_node

    def get_end_point_on_node(self):
        """Returns a point as a tuple (latitude, longitude) on a node which is at the edge of the box"""
        dist = {}
        random_point = self.get_random_end_point_from_osm(1)
        for ways in self.all_streets:
            for lists in self.all_streets[ways]:
                dist[(calculateDistance(lists[0][0], lists[0][1], random_point[0][0], random_point[0][1]))] = (lists[0])

        nearest_node = dist[min(dist)]
        return nearest_node

    def get_point_of_interest(self, filename, type):
        nodes = []
        for entity in osmread.parse_file(filename):
            if isinstance(entity, osmread.Node) and 'highway' in entity.tags:
                if entity.tags['highway'] == type:
                    nodes.append((entity.lat, entity.lon))

        print(f'number of {type}: {len(nodes)}')
        if (len(nodes) == 0):
            return []
        return nodes[random.randint(0, len(nodes) - 1)]



    def get_start_point_on_node(self):
        """returns a start point on the left or right side"""
        dist = {}
        random_point = self.get_random_start_point_from_osm(1)
        for ways in self.all_streets:
            for lists in self.all_streets[ways]:
                dist[(calculateDistance(lists[0][0], lists[0][1], random_point[0][0], random_point[0][1]))] = (lists[0])

        nearest_node = dist[min(dist)]
        return nearest_node


def get_start_points(minlat, maxlat, minlon, maxlon, number_points):

    results = []
    for n in range(0, number_points):

        puffer_y_border = (maxlon - minlon) / 4

        y_end = random.uniform(0, puffer_y_border)
        if y_end < (puffer_y_border / 2):
            result_y_end = minlon + y_end
        else:
            result_y_end = maxlon - (puffer_y_border - y_end)

        result_x_end = random.uniform(minlat, maxlat)

        results_end = result_x_end, result_y_end
        results.append(results_end)

    return results


#              bottom, top   ,left   ,right
def get_points(minlat, maxlat, minlon, maxlon, number_points):
    """Random packages are generated in middle of the box."""

    results = []
    for n in range(0, number_points):
        # calculating the points for the packets to spawn
        puffer_x = (maxlat - minlat) / 3
        puffer_y = (maxlon - minlon) / 3

        x = random.uniform(minlat + puffer_x, maxlat - puffer_x)
        y = random.uniform(minlon + puffer_y, maxlon - puffer_y)

        result = x, y
        results.append(result)

    return results


#                   bottom, top   ,left   ,right
def get_end_points(minlat, maxlat, minlon, maxlon, number_points):
    """Random packages are generated in edge of the box"""

    results = []
    for n in range(0, number_points):

        # calculating the end points
        puffer_x_border = (maxlat - minlat) / 4
        puffer_y_border = (maxlon - minlon) / 4

        x_end = random.uniform(0, puffer_x_border)
        if x_end < (puffer_x_border / 2):
            result_x_end = minlat + x_end
        else:
            result_x_end = maxlat - (puffer_x_border - x_end)

        y_end = random.uniform(0, puffer_y_border)
        if y_end < (puffer_y_border / 2):
            result_y_end = minlon + y_end
        else:
            result_y_end = maxlon - (puffer_y_border - y_end)

        results_end = result_x_end, result_y_end
        results.append(results_end)

    return results


def check_if_center(filename, coords):
    """checks if coordinates are inside in center of box"""
    try:
        root = emt.parse(filename).getroot()
    except FileNotFoundError:
        print('File not found')

    for type_tag in root.findall('bounds'):
        minlat = float(type_tag.get('minlat'))  # bottom
        maxlat = float(type_tag.get('maxlat'))  # top

        minlon = float(type_tag.get('minlon'))  # left
        maxlon = float(type_tag.get('maxlon'))  # right

    puffer_x = (maxlat - minlat) / 3
    puffer_y = (maxlon - minlon) / 3

    if ((coords[0] > minlat + puffer_x and coords[0] < maxlat - puffer_x)) and (
            coords[1] > minlon + puffer_y and coords[1] < maxlon - puffer_y):
        return True
    else:
        return False


def calculateDistance(x1, y1, x2, y2):
    dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist


if __name__ == '__main__':
    # example
    filename = '../OSM-Data/streets_new.osm'
    r = RandomPackages(filename)

    center = r.get_point_on_node()
    print(center)
    end = r.get_end_point_on_node()
    print(end)

    start = r.get_start_point_on_node()
    print('start', start)

    print(check_if_center(filename, center))
    print(check_if_center(filename, end))
    print(check_if_center(filename, start))

    bounds = (r.minlon, r.minlat, r.maxlon, r.maxlat)
    print(bounds)

    transformation = g2.Geo2GameCoords(bounds, [1000, 1000])

    print('center', transformation.transform(center[0], center[1]))
    print('end', transformation.transform(end[0], end[1]))
    print('start', transformation.transform(start[0], start[1]))
