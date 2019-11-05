import gzip
from math import sqrt
import numpy as np


class Ghost:
    """all ghosts"""
    ghosts = []

    def __init__(self, transformation, tracefile, nodenumber, **kwargs):
        """
        Initialize Ghost. Processes the bonnmotion trace.

        :param transformation: Transformation object to transform Geo to screen coords
        :param tracefile: bonnmotion tracefile
        :param nodenumber: number of node which should be taken in bonnmotion trace
        :param kwargs:
        """

        """counter"""
        self.__i = 0
        """time x y coordinates for turning points in bonnmotion trace"""
        self.__data = []
        """speed value for each turn"""
        self.__speed = 1

        self.x = 0
        self.y = 0
        self.id = len(self.ghosts)

        # read the waypoints
        with gzip.open(tracefile, 'rt') as file:
            j = 0
            for line in file:
                # convert line into standard bonnmotion format
                rargs = [(',\n', ''), (']', ''), (' [', ' '), (', ', ' '), (',', ' ')]
                for args in rargs:
                    line = line.replace(*args)
                self.__data = np.reshape(list(map(np.double, line.split(' '))), (-1, 3))
                if nodenumber == j:
                    break
                j += 1
            file.close()

        # transform Geo coords to display coords
        for a in range(len(self.__data)):
            self.__data[a, 1:] = transformation.transform(self.__data[a, 2], self.__data[a, 1])

        # update position of ghost to the first position
        (self.x, self.y) = self.__data[self.__i, 1:]

    def update(self):
        """
        updates position of ghost. The ghost is moving to the next turning point of the bonnmotion trace
        with the speed in the trace.

        :return:
        """
        # calculate distance to next waypoint
        distancex = self.__data[self.__i, 1] - self.x
        distancey = self.__data[self.__i, 2] - self.y
        length = sqrt(pow(distancex, 2.0) + pow(distancey, 2.0))

        # if not animation[0].running:
        # animation[0] = animate(ghost, tween='linear', duration=1, pos=(xy[counter[0], :]))

        if length <= 0.5 * self.__speed:
            # reached next waypoint
            # self.center = self.__data[self.__i, 1:]
            (self.x, self.y) = self.__data[self.__i, 1:]
            self.__i += 1

            if self.__i != len(self.__data):
                # calculate duration, distance and speed towards next waypoint
                duration = self.__data[self.__i, 0] - self.__data[self.__i - 1, 0]
                distancex = self.__data[self.__i, 1] - self.x
                distancey = self.__data[self.__i, 2] - self.y
                length = sqrt(pow(distancex, 2.0) + pow(distancey, 2.0))
                if duration == 0:
                    duration = 1
                self.__speed = length / duration
            else:
                # end of waypoint route
                (self.x, self.y) = self.__data[0, 1:]
                self.__i = 0
                self.__speed = 1
                return

        if length != 0:
            # update position in the direction of next waypoint
            distancex /= length
            distancey /= length
            self.x += distancex * self.__speed
            self.y += distancey * self.__speed
