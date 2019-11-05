from pyproj import Transformer


class Geo2GameCoords:
    """ converts geographic coordinates to game coordinates. """

    def __init__(self, bounding_box, screen_dim):
        """ Configures the transformation.

        Parameters
        ----------
        bounding_box: 4-tuple in following format: (left, bottom, right, top)
        screen_dim: 2-tuple in following format: (width, height)
        """

        # print('bounding_box: ', bounding_box)

        self.trans = Transformer.from_crs(4326, 3857)
        self.detrans = Transformer.from_crs(3857, 4326)

        # [ transform(lat, lon) ]
        self.left, self.bottom = self.trans.transform(
            bounding_box[1], bounding_box[0])
        self.right, self.top = self.trans.transform(
            bounding_box[3], bounding_box[2])

        # print('converted:    ', (self.left, self.top, self.right, self.bottom))

        self.width = screen_dim[0]
        self.height = screen_dim[1]

        # compute ratios 
        width_source = self.right - self.left
        height_source = self.top - self.bottom
        ratio_source = width_source / height_source
        ratio_target = self.width / self.height

        # print('ratio_source, ratio_target', ratio_source, ratio_target)
        # print('width, height', width_source, height_source)

        # compute transformation matrix from EPSG:3857 to screen coords
        # i.e.     | scale 0     0   |    | scale 0   h_off |
        #          |   0 scale v_off |    |   0 scale   0   |
        #          |   0   0     0   |    |   0   0     0   |

        if ratio_source < ratio_target:
            self.scale = self.height / height_source
            self.offset = {'x': (self.width - width_source * self.scale) / 2
                , 'y': 0}
        else:
            self.scale = self.width / width_source
            self.offset = {'x': 0
                , 'y': (self.height - height_source * self.scale) / 2}

    def transform(self, lat, lon):
        # print('lon, lat (4326): ', lon, lat)
        x, y = self.trans.transform(lat, lon)
        # print('lon, lat (3857): ', x, y)
        x = x - self.left
        y = y - self.bottom

        # scale to screen size
        x = self.scale * x + self.offset['x']
        y = self.scale * y + self.offset['y']

        # bring origin from left-bottom to left-top
        y = self.height - y

        return (x, y)

    def detransform(self, x, y):
        """ does the inverse transformation to Geo2GameCoords.transform
        """
        # bring origin from left-top to left-bottom 
        y = self.height - y

        # scale to map size
        x = (x - self.offset['x']) / self.scale
        y = (y - self.offset['y']) / self.scale

        # relocate origin
        x = x + self.left
        y = y + self.bottom

        lat, lon = self.detrans.transform(x, y)

        return (lat, lon)
