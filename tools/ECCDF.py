import math
import sys
import Package
import time
from Client import Client
import numpy as np
import matplotlib.pyplot as plt
from PodSixNet.Connection import connection, ConnectionListener
from time import sleep


class ECCDF():
    """ This class creates an ECCDF-Plot with the y-Axis being
    the distrubution percentage and x-Axis the time of contact
    between Players and Ghosts in PACMAN-UOS 
    """

    def __init__(self, host, port):
        self.c = Client(host, port)
        self.listOfEncounters = []
        self.playerInVicinity = {}

    # -----------------------------------------------------------------------------
    # Methods
    # -----------------------------------------------------------------------------
    def euclideanDistance(self, ghost_pos_x, ghost_pos_y, player_pos_x, player_pos_y):
        """ Calculate the euclidean distance between the Ghosts & Players 
        :param ghostPosition x,y:
        :param playerPosition x,y:
        """
        return math.sqrt((player_pos_x - ghost_pos_x) ** 2 + (player_pos_y - ghost_pos_y) ** 2)

    def log_encounters(self):
        """ Logs all encounters in the range of 50 pixels between Ghosts and Players and their duration
        :param ghostPosition: a list of current playerPositions
        :param playerPosition: an array of current playerPositions
        """
        for ghost_id, ghost_pos in enumerate(self.c.ghostlist):
            for player_id, player_pos in enumerate(self.c.playerList):

                euclidean = self.euclideanDistance(
                    ghost_pos[0], ghost_pos[1], player_pos[0], player_pos[1])

                # When the player enters the vicinity of a ghost, he is added as key to a dict with entry time as value and the ghost in whose vicinity he is.

                if (euclidean < Package.threshold_distance) and (player_id not in self.playerInVicinity):
                    self.playerInVicinity[player_id] = {
                        'time': time.time(), 'ghost_id': ghost_id}

                if (euclidean > Package.threshold_distance) and (player_id in self.playerInVicinity) and (
                        ghost_id == self.playerInVicinity[player_id]['ghost_id']):
                    total = time.time() - self.playerInVicinity.pop(player_id).get('time')
                    self.listOfEncounters.append(total)

    def plot(self):
        """ We are are plotting the ECCDF at the end of the game """
        n = len(self.listOfEncounters)
        x = np.sort(self.listOfEncounters)
        y = 1 - (np.arange(1, n + 1) / n)
        plt.plot(x, y, marker='.', linestyle='none')
        plt.xlabel('Duration of encounters in sec')
        plt.ylabel('ECCDF')
        plt.show()

# -----------------------------------------------------------------------------
# Main Method
# -----------------------------------------------------------------------------


if __name__ == '__main__':
    if not len(sys.argv) == 2:
        print("Host und Port vergessen. host:port")
        exit()
    startClient = True
    host, port = sys.argv[1].split(":")
    ECCDF = ECCDF(host, int(port))
    ECCDF.c.makeObserver()
    print('Waiting for game start: ')
    while startClient:
        ECCDF.c.Loop()
        while ECCDF.c.gamestarted and not ECCDF.c.roundEnded:
            ECCDF.c.Loop()
            ECCDF.log_encounters()
            sleep(0.001)
        if ECCDF.c.roundEnded:
            print('Game ended')
            startClient = False
    ECCDF.plot()
