def get_List_of_ways(osm_map, transformation, sceen_dim):
    WIDTH = sceen_dim[0]
    HEIGHT = sceen_dim[1]

    geo = (0, 0)
    data = osm_map.getWays()
    # data = osm_map.getConnectedWays()
    ways = []
    for x in data:
        currentWay = []
        for y in data[x]:
            xy_of_node = transformation.transform(y[0][0], y[0][1])
            currentWay.append(xy_of_node)
        ways.append(currentWay)
    return (ways)


def rainbow(n):
    colors = [('red', 255, 0, 0), ('orange', 255, 128, 0), ('yellow', 255, 255, 0), ('green', 0, 255, 0),
              ('cyan', 0, 255, 255), ('blue', 0, 0, 255), ('purple', 128, 0, 255), ('magenta', 255, 0, 255)]
    return ((colors[n][1]), (colors[n][2]), (colors[n][3]))
