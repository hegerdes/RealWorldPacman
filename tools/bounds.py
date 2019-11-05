import xml.etree.ElementTree as ET
import tools.geo2tiles as converter


# import Geo2Tiles as converter

class Bounds():

    def __init__(self, filename, tieles_dim, zoom):
        self.file = filename
        self.dim = tieles_dim
        self.zoom = zoom
        root = ET.parse(self.file).getroot()
        for type_tag in root.findall('bounds'):
            self.minlat = float(type_tag.get('minlat'))
            self.minlon = float(type_tag.get('minlon'))
            self.maxlat = float(type_tag.get('maxlat'))
            self.maxlon = float(type_tag.get('maxlon'))

    # Retruns the gps bounds of the filname.osm
    def get_OSM_bounds(self):
        return (self.minlat, self.minlon, self.maxlat, self.maxlon)

    # Retruns the gps bounds of the filname.osm
    def get_start_tiles_bounds(self):
        start_tiles = converter.deg2num(self.maxlat, self.minlon, self.zoom)
        return (start_tiles[0] + 1, start_tiles[1] + 1)

    # Retruns the gps bounds of the filname.osm
    def get_end_tiles_bounds(self):
        start_tiles = converter.deg2num(self.maxlat, self.minlon, self.zoom)
        return (start_tiles[0] + self.dim, start_tiles[1] + self.dim)

    # Retruns the gps bounds of the filname.osm
    def get_start_gps_bounds(self):
        tmp = self.get_start_tiles_bounds()
        return converter.num2deg(tmp[0], tmp[1], self.zoom)

    # Retruns the gps bounds of the filname.osm
    def get_end_gps_bounds(self):
        tmp = self.get_end_tiles_bounds()
        return converter.num2deg(tmp[0] + 1, tmp[1] + 1, self.zoom)


if __name__ == "__main__":
    bo = Bounds('OSM-Data/westerberg.osm', 3, 15)
    print(bo.get_OSM_bounds())
    print(bo.get_start_tiles_bounds())
    print(bo.get_start_gps_bounds())
    print(bo.get_end_tiles_bounds())
    print(bo.get_end_gps_bounds())
    print(converter.deg2num(52.29504228453733, 7.987060546875, 15))
