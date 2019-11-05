import h5py
import pyproj
import numpy as np
import math

class RaLaNSData:

    def __init__(self, zip_name, hdf5_name, utm_zone=32):
        self.zip_name = zip_name
        self.hdf5_name = hdf5_name
        self.header, self.config = parser.read_header_config(zip_name)

        file = h5py.File(self.hdf5_name, 'r')
        self.data = file['coverage']

        # get utm corners
        center = string_to_float_list(self.config["center"][1:])
        borders = string_to_float_list(self.config["borders"][1:])
        self.utm_bottom_left = center[0] + borders[0], center[1] + borders[1]
        self.utm_top_right = center[0] + borders[2], center[1] + borders[2]

        # utm to geo, order: lat, lon
        p = pyproj.Proj(proj="utm", zone=utm_zone)
        self.geo_bottom_left = p(self.utm_bottom_left[0], self.utm_bottom_left[1], inverse=True)
        self.geo_bottom_left = (self.geo_bottom_left[1], self.geo_bottom_left[0])
        self.geo_top_right = p(self.utm_top_right[0], self.utm_top_right[1], inverse=True)
        self.geo_top_right = (self.geo_top_right[1], self.geo_top_right[0])

        #print('geo_top_right', self.geo_top_right)
        self.all_transmitters = self.get_all_transmitters()

    def get_closest_four_transmitters(self, coords):
        """ computes a preselection for get_closest_transmitter_id
        :param coords: geo coordinates in (lat, lon)
        :return: list of the ids of the fourclosest transmitter
        """
        # given params
        x , y   = coords
        x1, y1  = self.geo_bottom_left
        row_len = self.header['size_x']
        col_len = self.header['size_y']

        # compute distance between two neighboring transmitters
        xstep = self.all_transmitters[1][0] - x1
        ystep = self.all_transmitters[self.header['size_x']][1] - y1
        xmin, ymin = self.all_transmitters[0]
        xmax, ymax = self.all_transmitters[-1]

#        # DEBUG
#        print(f'x: {x}, y: {y}')
#        print(f'x1: {x1}, y1: {y1}')
#        print(f'xstep: {xstep}, ystep: {ystep}')

        # compute indizes of next transmitters
        xlow , ylow  = ( int((x - x1) / xstep) , int((y - y1) / ystep) )
        xhigh, yhigh = ( xlow + 1 , ylow + 1 )

        # check for out of bounds cases
        if x < xmin:
            xlow = xhigh = 0
        elif x >= xmax:
            xlow = xhigh = row_len - 1

        if y < ymin:
            ylow = yhigh = 0
        elif y >= ymax:
            ylow = yhigh = col_len - 1
        
        # helper func for getting the index in a flat array
        def get_flat_index(x, y):
            return x + row_len * y

        result = [ (xlow, ylow), (xlow, yhigh), (xhigh, ylow), (xhigh, yhigh) ]
        result = [ get_flat_index(x, y) for x, y in result]

        return result


    def get_closest_transmitter_id(self, coords):
        """
        Calculate the closest transmitter to coords
        :param coords: geo coordinates in (lat, lon)
        :return: id of closest transmitter
        """

        # calculate distances to the closest four transmitters 
        dist = []
        for index in self.get_closest_four_transmitters(coords):
            transmitter = self.all_transmitters[index]
            dist.append({
                "index": index, 
                "dist": calculateDistance(
                    coords[0], coords[1], transmitter[0], transmitter[1])
            })

        # find closest transmitter
        nearest = 0
        for index in range(len(dist)):
            if dist[index]["dist"] < dist[nearest]["dist"]:
                nearest = index

        return dist[nearest]["index"]
 
    def get_all_transmitters(self):
        """

        :return: list of all transmitters with (lat, lon) for each index
        """
        res_x = np.linspace(self.geo_bottom_left[0], self.geo_top_right[0], self.header["size_x"])
        res_y = np.linspace(self.geo_bottom_left[1], self.geo_top_right[1], self.header["size_y"])

        # all combinations, from bottom left to top right line by line
        res = [(x, y) for y in res_y for x in res_x]

        return res

    def get_receivers(self, transmitter_id):
        receiver = self.data[transmitter_id]
        return receiver

    def get_coords_from_id(self, transmitter_id):
        return self.all_transmitters[transmitter_id]


def string_to_float_list(in_string):
    res = in_string.strip('][').split(', ')
    res = [float(x) for x in res]
    return res


def calculateDistance(x1, y1, x2, y2):
    dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist


if __name__ == '__main__':
    import RaLaNSParser as parser

    zip_name = '../RaLaNS-Data/osna4km2_area_to_area_10.zip'
    hdf5_name = '../RaLaNS-Data/\'osna4km2\'.hdf5'
    utm_zone = 32

    d = RaLaNSData(zip_name, hdf5_name, utm_zone)
    t = d.get_closest_transmitter_id((52.25767544842923, 8.051297809088988))
    r = d.get_receivers(t)

    flat = [val for row in r for val in row]
    min_value = min(flat)
    max_value = max(flat)

    # check if no signal strength is in this line
    empty = False
    for index, lines in enumerate(r):
        for value in lines:
            if value != min_value:
                empty = True
        if not empty:
            print('line is empty: ', index)
        else:
            print('max is: ', max(lines))
        empty = False


else:
    import tools.RaLaNSParser as parser
