import os
import sys
import time
from sys import stdin, exit
from _thread import *
from time import sleep
import logging
from PodSixNet.Connection import connection, ConnectionListener

logger = logging.getLogger(__name__)

class Client(ConnectionListener):

    def __init__(self, host, port, name="Player"):
        self.Connect((host, port))
        print("Client gestartet")
        self.playerList = []
        self.packageList = []
        self.progress_packages = None
        self.progress_destination = 0
        self.ghostlist = []
        self.playernum = 0
        self.startx = 0
        self.starty = 0
        self.destination = None
        self.connected = False
        self.gamestarted = False
        self.gamestopped = False
        self.roundEnded = False
        self.scenario = ''
        self.scoreboard = None
        self.playerName = name
        connection.Send({"action": "name", "name": name})

    def InputLoop(self):
        connection.Send({"action": "name", "name": stdin.readline().rstrip("\n")})

    def Loop(self):
        connection.Pump()
        self.Pump()

    def updatePosition(self, xpos, ypos, anglex, angley):
        """
        Versendet die aktualisierten Koordinaten an den Server

        :param xpos: Neue X-Koordinate

        :param ypos: Neue Y-Koordinate

        :param anglex: X-Koordinate auf die der Spieler guckt

        :param angley: Y-Koordinate auf die der Spieler guckt

        """
        connection.Send({"action": "location", "xpos": xpos, "ypos": ypos,
                         "anglex": anglex, "angley": angley})

    def getPlayerLocations(self):
        """
        2D Liste der Spieler.

        Erster Index ist die Spielernummer.

        Zweite Indices sind:

        [0]: X Koordinate

        [1]: Y Koordinate

        [2]: X Richtung, in welcher der Spieler schaut

        [3]: Y Richtung, in welcher der Spieler schaut

        [4]: Nimmt Teil boolean

        [5]: Player Name

        :return: Liste der Spieler
        """
        return self.playerList

    def getPackageLocations(self):
        """
        :return: Liste der Pakete, welche vom Server geschickt wurden
        """
        return self.packageList

    def makeObserver(self):
        """
        makes the client to a passive observer. It will not be shown to other clients.
        """
        connection.Send({"action": "makeObserver"})

    def Network_connected(self, data):
        print("Verbindung hergestellt")

    def Network_error(self, data):
        print('Fehler:', data['error'][1])
        self.gamestopped = True

    def Network_disconnected(self, data):
        print('Verbindung getrennt')
        self.gamestopped = True

    def Network_serverRestart(self):
        print("Restart")

    def Network_number(self, data):
        self.playernum = data['number']

    def Network_players(self, data):
        playernumber = data['playernum']
        playernumber.sort()
        for i in playernumber:
            if i > len(self.playerList) - 1:
                self.playerList.append([])
                self.playerList[i].append(data['xpos'][i])
                self.playerList[i].append(data['ypos'][i])
                self.playerList[i].append(data['anglex'][i])
                self.playerList[i].append(data['angley'][i])
                self.playerList[i].append((data['nimmtTeil'][i]))
                self.playerList[i].append((data['players'][i]))
            else:
                self.playerList[i][0] = data['xpos'][i]
                self.playerList[i][1] = data['ypos'][i]
                self.playerList[i][2] = data['anglex'][i]
                self.playerList[i][3] = data['angley'][i]
                self.playerList[i][4] = data['nimmtTeil'][i]
                self.playerList[i][5] = data['players'][i]

    def Network_startgame(self, data):
        print("Spiel gestartet")
        c_time = time.strftime("%d %m %Y %H-%M-%S", time.gmtime())
        logger.info(c_time + ':SG:Spiel gestartet')
        self.gamestarted = True

    def Network_startposition(self, data):
        self.startx = data['posx']
        self.starty = data['posy']

    def Network_updatePlayerLocations(self, data):
        who = data['who']
        if (data['nimmtTeil']):
            self.playerList[who][0] = data['xpos']
            self.playerList[who][1] = data['ypos']
            self.playerList[who][2] = data['anglex']
            self.playerList[who][3] = data['angley']
            self.playerList[who][4] = data['nimmtTeil']
            self.playerList[who][5] = data['players']

    def Network_kickplayer(self, data):
        print("Spiel bereits gestartet. Du darfst nicht mehr beitreten!")
        os._exit(0)

    def Network_updatePackageLocations(self, data):
        self.packageList = data['locations']

    def Network_drawPackageDestination(self, data):
        #print('drawPackageDestination')
        self.destination = data['location']

    def Network_erasePackageDestination(self, data):
        #print('ErasePackageDestination')
        self.destination = None

    def Network_updateGhosts(self, data):
        ghostnumber = data['id']
        for i in ghostnumber:
            if i > len(self.ghostlist) - 1:
                self.ghostlist.append([])
                self.ghostlist[i].append(data['xpos'][i])
                self.ghostlist[i].append(data['ypos'][i])
            else:
                self.ghostlist[i][0] = data['xpos'][i]
                self.ghostlist[i][1] = data['ypos'][i]

    def Network_scenario(self, data):
        self.scenario = data['scenario']

    def Network_drawScoreboard(self, data):
        self.scoreboard = data['scoreboard']

    def Network_roundEnded(self, data):
        self.roundEnded = data['ended']

    def Network_updateProgress(self, data):
        self.progress_packages = data['progress']

    def Network_updateDestination(self, data):
        self.progress_destination = data['progress_dest']

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Host und Port vergessen. host:port")
    else:
        host, port = sys.argv[1].split(":")
        c = Client(host, int(port))
        while 1:
            c.Loop()
            sleep(0.001)
