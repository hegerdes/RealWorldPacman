import osmium as osm
import copy
import math
import pickle
import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
#from tools.bounds import Bounds

whitlist_tags = (
    'highway=motorway',
    'highway=motorway_link',
    'highway=trunk',
    'highway=trunk_link',
    'highway=primary',
    'highway=primary_link',
    'highway=secondary',
    'highway=secondary_link',
    'highway=tertiary',
    'highway=tertiary_link',
    'highway=unclassified',
    'highway=residential',
    'highway=living_street',
    'highway=service'
)

plot_options = {
    'node_color': 'black',
    'node_size': 1,
    'width': 1,
}

class OSMHandler:
    """ Interface to a OSM-File."""

    def __init__(self, path, bounds_min=(0, 0),
                 bounds_max=(math.inf, math.inf), usecache=True, filterlist=whitlist_tags):
        """ Config the Reader for the OSM-File.

        Parameters
        ----------
        path: path to the osm file
        bounds_min: 2-tuple in following format: (lat_min, lon_min)
        bounds_max: 2-tuple in following format: (lat_max, lon_max)
        usecache: boolean if cache should be used. Default true
        filterlist: list of tags that every entry in osm shoud have
        """
        # Check and fix min and max
        if (bounds_min[0] < bounds_max[0]):
            self.minlat = bounds_min[0]
            self.maxlat = bounds_max[0]
        else:
            self.minlat = bounds_max[0]
            self.maxlat = bounds_min[0]
        if (bounds_min[1] < bounds_max[1]):
            self.minlon = bounds_min[1]
            self.maxlon = bounds_max[1]
        else:
            self.minlon = bounds_max[1]
            self.maxlon = bounds_min[1]

        nodecache = path + '.node.cache'
        waycache = path + '.way.cache'
        graphcache = path + '.graph.cache'
        if (os.path.exists(waycache) and os.path.exists(nodecache) and
                os.path.exists(graphcache) and usecache):
            print('Found OSM cache!')
            self.ways = pickle.load(open(waycache, 'rb'))
            self.nodes = pickle.load(open(nodecache, 'rb'))
            self.graph = nx.read_gpickle(graphcache)
        else:
            print('No OSM cache found!\nGenerating...')
            self.osmfilehadler = OSMFileHandler()
            #self.osmfilehadler.apply_buffer(tarbuffer, 'osm')
            self.osmfilehadler.apply_file(path)
            self.ways = self.osmfilehadler.ways
            self.nodes = self.osmfilehadler.nodes

            # Create graph with no isolated subgraphs
            connectedGraph = list(max(nx.connected_components(self.osmfilehadler.graph), key=len))
            self.graph = self.osmfilehadler.graph.subgraph(connectedGraph)
            self.removeWays()
            nx.write_gpickle(self.graph, graphcache)
            #pickle.dump(self.ways, open(waycache, 'wb'))
            #pickle.dump(self.nodes, open(nodecache, 'wb'))


    def getWays(self):
        return self.ways

    def getGraph(self):
        return self.graph

    def plotGraph(self, plotter_options=plot_options):
        pos = {}
        data = dict(self.graph.nodes(data=True))
        for d in data:
            pos[d] = np.array([data[d]['lon'], data[d]['lat']])
        nx.draw(self.graph, pos, **plotter_options)
        plt.show()

    def findNodeByGeo(self, lon,lat):
        pass

    def removeWays(self):
        to_remove = []
        for way in self.ways:
            for node in self.ways[way]:
                if (not self.graph.has_node(node[1])):
                    to_remove.append(way)
                    break

        for i in to_remove:
            try:
                self.ways.pop(i)
            except KeyError:
                pass





class OSMFileHandler(osm.SimpleHandler):
    """ Custom OMSFileHandler."""

    def __init__(self, bounds=(0, 0, math.inf, math.inf), filter_list=whitlist_tags):
        """ Config the Handler.

        Parameters
        ----------
        bounds: 4-tuple in following format: (lat_min, lon_min, lat_max, lon_max)
        """
        osm.SimpleHandler.__init__(self)
        self.osm_data = []
        self.ways = {}
        self.nodec = 0
        self.nodes = {}
        self.wayc = 0
        self.ways = {}
        self.relc = 0
        self.filter = filter_list
        self.graph = nx.Graph()
        self.min_lat = bounds[0]
        self.min_lon = bounds[1]
        self.max_lat = bounds[2]
        self.max_lon = bounds[3]

    # Function to create a object of every OSM-object
    def tag_inventory(self, elem, elem_type):
        pass

    def filterOSM(self, entrys):
        valid_entry = False
        for tag in entrys.tags:
            if (str(tag) in self.filter): valid_entry = True
        return valid_entry

    # Tag every Node
    def node(self, n):
        if (not n.deleted):
            # self.tag_inventory(n, "node")
            #self.nodes[n.id] = {'lat': n.location.lat, 'lon': n.location.lon}
            self.graph.add_node(n.id, lat=n.location.lat, lon=n.location.lon)
            self.nodec += 1

    # Tag every Relation
    def relation(self, r):
        # self.tag_inventory(r, "relation")
        self.relc += 1

    # Tag every way and create a dict with Key=wayID, Key= list of Node.Locations
    def way(self, w):
        if (self.filterOSM(w)):
            self.wayc += 1
            tmp = []
            tmp_nodes = []
            if (len(w.nodes) > 1):
                for node in w.nodes:
                    try:
                        tmp_node = self.nodes[node.ref]
                        if ((tmp_node['lat'] > self.min_lat and
                             tmp_node['lat'] < self.max_lat and
                             tmp_node['lon'] > self.min_lon and
                             tmp_node['lon']) < self.max_lon):
                            tmp.append([(tmp_node['lat'], tmp_node['lon']), node.ref])
                            tmp_nodes.append(node.ref)
                        else:
                            print('Out of bounds', tmp_node)
                    except KeyError:
                        pass
                        #print('Key not found', node.ref)
            self.ways[w.id] = copy.deepcopy(tmp)
            for i in range(0, len(tmp_nodes)-1):
                self.graph.add_edge(tmp_nodes[i], tmp_nodes[i+1])
                self.graph.add_edge(tmp_nodes[i+1], tmp_nodes[i])


if __name__ == "__main__":
    osm_path = '../../0.Arbeit_BM/OSM-Data/niedersachsen-latest.osm.pbf'
    #oms_bounds = Bounds(osm_path,3,15)
    import sys
    my_handlder = OSMHandler(osm_path,usecache=False)
    print(sys.getsizeof(my_handlder.getGraph))
    my_handlder.plotGraph()
    # print(oms_bounds.get_start_gps_bounds())
    # print(oms_bounds.get_end_gps_bounds())
    # print(nx.to_dict_of_dicts(self.osmfilehadler.graph))
    # print('nodes', self.osmfilehadler.nodes)
    # print('nodec', self.osmfilehadler.nodec)
    # print('wayc', self.osmfilehadler.wayc)
    # print('way_dict', len(self.osmfilehadler.ways))
    # print(self.osmfilehadler.graph.nodes(data=True))
    # print(self.osmfilehadler.graph.edges(data=True))
    # print(self.osmfilehadler.graph[56369074])
    # options = {
    #     'node_color': 'black',
    #     'node_size': 1,
    #     'width': 1,
    #     }
    # #pos = nx.spring_layout()
    # print(nx.circular_layout(my_handlder.graph))
    # nx.draw(my_handlder.graph, **options)
    # plt.show()