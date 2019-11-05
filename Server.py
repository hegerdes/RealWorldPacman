import os
import sys
import time
import configparser
from weakref import WeakKeyDictionary
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from _thread import *
import tools.RandomPackages as RandomPackages
import tools.Geo2GameCoords as Geo2GameCoords
from tools.bounds import Bounds
import tools.osmparser as OSMP
from tools.Package import PackageManager
from tools.Score import Score
from tools.Ghost import Ghost
import numpy
import tarfile
import gzip


class ClientChannel(Channel):
    def __init__(self, *args, **kwargs):
        self.name = ""
        self.xpos = 0
        self.ypos = 0
        self.locationx = 20
        self.locationy = 20
        self.playernum = 0
        self.nimmtTeil = True
        self.traegtPaket = False

        Channel.__init__(self, *args, **kwargs)

    def Close(self):
        self._server.DelPlayer(self)

    def Network_message(self, data):
        self._server.SendToAll({"action": "message", "message": data['message'], "who": self.name})

    def Network_name(self, data):
        self.name = data['name']
        # print("name angenommen")
        self._server.SendPlayers()

    def Network_location(self, data):
        self.xpos = data['xpos']
        self.ypos = data['ypos']
        self.locationx = data['anglex']
        self.locationy = data['angley']
        self._server.SendToAll({"action": "updatePlayerLocations",
                                "players": self.name,
                                "xpos": data['xpos'],
                                "ypos": data['ypos'],
                                "anglex": self.locationx,
                                "angley": self.locationy,
                                "nimmtTeil": self.nimmtTeil,
                                "who": self.playernum})

    def Network_makeObserver(self, data):
        # set client to passive observer
        self.nimmtTeil = False
        # update all connected clients
        self._server.SendPlayers()
        # debug
        print(f'client (name: {self.name}) is now observer.')


class MyServer(Server):
    channelClass = ClientChannel

    def __init__(self, scenarioName, traceName, *args, **kwargs):
        """

        initialisiert alle Instanzvaribalen des Servers

        """
        Server.__init__(self, *args, **kwargs)
        self.players = WeakKeyDictionary()
        self.gamestarted = False
        self.actualPlayerID = 0
        self.last_timestamp = time.time()
        self.starttime = time.time()
        self.numberOfPlayers = 0
        self.numberOfGhosts = 8
        self.usernames = {}
        self.scoreboard = None
        self.osm_bounds = None
        self.my_osm_data = None
        self.game_ended = False
        self.TIME = 300  # Spielzeit in Sekunden. Hier 5 Minuten!
        ZOOM = 15
        TILES_DIM = 3
        TILES_SIZE = 256
        WIDTH = TILES_DIM * TILES_SIZE
        HEIGHT = TILES_DIM * TILES_SIZE
        # pygamesurface = pygame.display.set_mode((HEIGHT, WIDTH))

        self.scenarioName = scenarioName
        try:
            tar = tarfile.open(scenarioName, "r:gz")
        except FileNotFoundError:
            print('The ' + self.scenarioName + ' is not avaiable\nGame exit')
            exit(1)
        config = configparser.ConfigParser()
        try:
            tarfileobj = tar.extractfile(tar.getmember('map.config'))
            config.read_string(tarfileobj.read().decode("utf-8"))
            ZOOM = int(config['MAP_CONF']['ZOOM'])
            TILES_DIM = int(config['MAP_CONF']['TILES_DIM'])
            TILES_SIZE = int(config['MAP_CONF']['TILES_SIZE'])
            self.TIME = int(config['MAP_CONF']['TIME'])
            WIDTH = TILES_DIM * TILES_SIZE
            HEIGHT = TILES_DIM * TILES_SIZE
        except KeyError:
            print('No Mapfile Found! Use Defaults')
        for member in tar.getmembers():
            if ".osm" in member.name:
                tarfileobj = tar.extractfile(member)
                self.osm_bounds = Bounds(tarfileobj, TILES_DIM, ZOOM)
                tarfileobj = tar.extractfile(member)
                self.my_osm_data = OSMP.OSMHandler(scenarioName.rsplit("/", 1)[0] + "/" + member.name,
                                                   tarfileobj.read(),
                                                   bounds_min=self.osm_bounds.get_start_gps_bounds(),
                                                   bounds_max=self.osm_bounds.get_end_gps_bounds())

        print('Server gestartet')
        self.playerList = []
        gps_start = self.osm_bounds.get_start_gps_bounds()
        gps_end = self.osm_bounds.get_end_gps_bounds()
        self.r = RandomPackages.RandomPackages(self.my_osm_data.getWays())
        self.r.set_bounding_box(gps_start[0], gps_end[0], gps_start[1], gps_end[1])
        t = start_new_thread(self.InputLoop, ())

        # Create tranformation object for ghosts:

        self.trans = Geo2GameCoords.Geo2GameCoords(
            (gps_start[1], gps_end[0], gps_end[1], gps_start[0]), [WIDTH, HEIGHT])

        # Create Ghosts here:
        #print(self.numberOfGhosts)
        for member in tar.getmembers():
            if traceName in member.name:
                for i in range(self.numberOfGhosts):
                    tarfileobj = tar.extractfile(member)
                    Ghost.ghosts.append(Ghost(self.trans, tarfileobj, i))

    def InputLoop(self):
        """
            Liest dauerhaft ein und verarbeitet eingegebene Kommandos

            *Start startet das Spiel und hindert neue daran noch beizutreten

            *Stop stoppt den Server und alle Spieler werden runtergeworfen

            *Restart ruft erneut die __init__ vom Server auf, macht aber
            aktuell noch Probleme
        """
        while 1:
            command = input("Kommando bitte (start / stop):\n")
            if command.rstrip("\n").lower() == "start":
                if self.gamestarted is True:
                    print("Spiel ist bereits gestartet")
                else:
                    self.startGame()
            elif command.rstrip("\n").lower() == "stop":
                self.SendToAll({"action": "roundEnded",
                                "ended": True})
                self.Pump()
                os._exit(0)
            elif command.rstrip("\n").lower() == "restart":
                self.SendToAll({"action": "serverRestart"})
                self.__init__(self.scenarioName)
                self.placePackage()
            time.sleep(0.001)

    def startGame(self):
        self.setUsernames()
        self.setScoreboard()
        self.starttime = time.time()
        self.placePackage()
        self.packageData()
        self.gamestarted = True
        self.last_timestamp = time.time()
        self.SendToAll({"action": "startgame"})
        print("Spiel wurde gestartet")
        self.SendToAll({"action": "roundEnded", "ended": False})

    def Connected(self, channel, addr):
        """ wird automatisch aufgerufen, wenn ein Spieler beitritt"""
        if self.gamestarted is True:
            channel.Send({"action": "kickplayer"})
            print("Spieler wurde gekickt, da Spiel bereits gestartet")
        else:
            self.AddPlayer(channel)

    def AddPlayer(self, player):
        """ Fügt Spieler hinzu und gibt allen die Information"""
        print("Neuer Spieler" + str(player.addr))

        self.players[player] = True
        start = self.r.get_start_point_on_node()
        start = self.trans.transform(start[0], start[1])

        #self.SendPlayers()
        player.Send({"action": "scenario", "scenario": self.scenarioName})
        player.Send({"action": "number", "number": self.actualPlayerID})
        player.playernum = self.actualPlayerID
        self.actualPlayerID += 1
        player.xpos = start[0]
        player.ypos = start[1]
        # player.Send({"action": "startposition", "posx": start[0],
        # "posy": start[1]})
        # print("players", [p for p in self.players])
        self.SendPlayers()
        self.numberOfPlayers += 1
        print("Anzahl Spieler: " + str(self.getConnectedPlayers()))

    def DelPlayer(self, player):
        """Loescht Spieler, falls dieser den Server verlässt"""
        print("Spieler geloescht" + str(player.addr))
        player.nimmtTeil = False
        self.SendPlayers()
        #self.numberOfPlayers -= 1
        self.SendToAll({"action": "deletePlayer", "deletePlayer": player.playernum})

    def SendPlayers(self):
        """Verschickt an alle Spieler die Position der anderen Spieler"""
        self.SendToAll({"action": "players",
                        "players": [p.name for p in self.players],
                        "playernum": [p.playernum for p in self.players],
                        "xpos": [p.xpos for p in self.players],
                        "ypos": [p.ypos for p in self.players],
                        "anglex": [p.locationx for p in self.players],
                        "angley": [p.locationy for p in self.players],
                        "nimmtTeil": [p.nimmtTeil for p in self.players]})

    def SendToAll(self, data):
        [p.Send(data) for p in self.players]

    def Launch(self):

        while True:
            self.Pump()
            if(self.game_ended): break
            now = time.time()
            delta = now - self.last_timestamp
            if (self.gamestarted and time.time() - self.starttime > self.TIME):
                self.gamestarted = False
                self.game_ended = True
                self.SendToAll({"action": "roundEnded",
                                "ended": True})
                print("Spiel beendet")
            if delta >= 1 / 40 and self.gamestarted:
                self.last_timestamp = now
                for ghost in Ghost.ghosts:
                    ghost.update()
                self.SendToAll({"action": "updateGhosts",
                                "xpos": [float(g.x) for g in Ghost.ghosts],
                                "ypos": [float(g.y) for g in Ghost.ghosts],
                                "id": [g.id for g in Ghost.ghosts]})

                player_pos = [(p.xpos, p.ypos, p.nimmtTeil) for p in self.players]
                ghost_pos = [(float(ghost.x), float(ghost.y)) for ghost in Ghost.ghosts]
                changed = self.package_manager.update(player_pos, ghost_pos, delta)

                if self.package_manager.progress_changed:
                    self.progressData()

                if changed:
                    self.packageData()
            time.sleep(0.0001)

    def placePackage(self):
        """Platziert Pakete anhand der Anzahl an verbundenen Spielern"""
        anzahlSpieler = self.getConnectedPlayers()
        #               0  1  2  3  4  5  6  7  8  9 10 11 12 13  14  15
        player_table = [0, 1, 1, 1, 3, 3, 3, 4, 4, 6, 6, 7, 8, 9, 10, 10]
        ghost_table = [0, 0, 1, 2, 2, 3, 3, 5, 5, 5, 5, 6, 6, 7, 9, 10]
        for i in range(anzahlSpieler + 1 - len(player_table)):
            player_table.append(int((i + len(player_table)) * 1 / 2))
        for i in range(len(Ghost.ghosts) + 1 - len(ghost_table)):
            ghost_table.append(int((i + len(ghost_table)) * 1 / 2))

        num_packages = player_table[anzahlSpieler] + ghost_table[len(Ghost.ghosts)]
        self.package_manager = PackageManager(num_packages, self.r, self.trans, anzahlSpieler, len(Ghost.ghosts),
                                              self.scoreboard)

    def getConnectedPlayers(self):
        """Gibt Anzahl der verbundenen Spieler zurück"""
        return self.numberOfPlayers

    def packageData(self):
        """Sendet die aktualisierten Packagepositions an alle Spieler"""
        self.SendToAll({"action": "updatePackageLocations",
                     "locations": self.package_manager.get_positions()})

        for carrier, destination in self.package_manager.get_destinations():
            for i, player in enumerate(self.players):
                if i == carrier:
                    print(f'player {carrier} has to draw destination at {destination}')
                    player.Send({"action": "drawPackageDestination",
                               "location": destination})

        for carrier in self.package_manager.get_former_carriers():
            for i, player in enumerate(self.players):
                if i == carrier:
                    print(f"player {carrier} has to erase destination")
                    player.Send({"action": "erasePackageDestination"})

    def setUsernames(self):
        """ Sets the usernames
        params: actualScore
        """
        for p in self.players:
            if p.nimmtTeil:
                self.usernames[p.playernum] = {'username': p.name, 'score': 0}

    def setScoreboard(self):
        self.scoreboard = Score(self.usernames, self.updateScoreboard)
        self.SendToAll({'action': 'drawScoreboard', 'scoreboard': self.scoreboard.getScoreboard()})

    def progressData(self):
        self.SendToAll({"action": "updateProgress",
                        "progress": self.package_manager.get_progress()})
        for package in self.package_manager.get_carried_dest_progress():
            for i, player in enumerate(self.players):
                if i == package[1]:
                    player.Send({"action": "updateDestination",
                                 "progress_dest": package[0]})


    def updateScoreboard(self):
        self.SendToAll({'action': 'drawScoreboard', 'scoreboard': self.scoreboard.getScoreboard()})


def start_server(host, port, scenarioPath, filenamesPrefix, scenarioNamePrefix=None, traceNamePrefix=None):
    """ Loop for user, till he chooses the scenario to be played """
    if not scenarioNamePrefix:
        print('Available scenarios:', filenamesPrefix)
        scenarioNamePrefix = input('Please choose one of the above listed scenarios: ')
    if scenarioNamePrefix not in filenamesPrefix:
        print('\nSomething went wrong! Please enter the filename exactly as given!')
        start_server(host, port, scenarioPath, filenamesPrefix)

    traceFilenamesPrefix = []
    tar = tarfile.open(scenariosPath + scenarioNamePrefix + ".tar.gz", "r:gz")
    for member in tar.getmembers():
        if ".movements.geo.gz" in member.name:
            traceFilenamesPrefix.append(member.name.replace(".movements.geo.gz", ""))
    if not traceNamePrefix:
        print('Available traces:', traceFilenamesPrefix)
        traceNamePrefix = input('Please choose one of the above listed traces: ')
    if traceNamePrefix in traceFilenamesPrefix:
        s = MyServer(scenarioPath + scenarioNamePrefix + ".tar.gz", traceNamePrefix + ".movements.geo.gz",
                     localaddr=(host, int(port)))
        s.Launch()
    else:
        print('\nSomething went wrong! Please enter the tracename exactly as given!')
        start_server(host, port, scenarioPath, filenamesPrefix, scenarioNamePrefix)


if __name__ == '__main__':
    if(len(os.path.dirname(__file__)) > 0):
        os.chdir(os.path.dirname(__file__))

    scenariosPath = 'scenarios/'
    (_, _, filenames) = next(os.walk(scenariosPath))
    filenames = [filename.replace(".tar.gz", "") for filename in filenames if ".cache" not in filename]

    if len(sys.argv) != 2 and len(sys.argv) != 3 and len(sys.argv) != 4:
        print("Usage:", sys.argv[0], "host:port", "[scenarioFilePrefix]", "[traceNamePrefix]")
        print("Use", sys.argv[0], "localhost:25565", "osna-small", "randstreet")
    elif len(sys.argv) == 2:
        host, port = sys.argv[1].split(":")
        start_server(host, port, scenariosPath, filenames)
    elif len(sys.argv) == 3:
        host, port = sys.argv[1].split(":")
        start_server(host, port, scenariosPath, filenames, sys.argv[2])
    elif len(sys.argv) == 4:
        host, port = sys.argv[1].split(":")
        start_server(host, port, scenariosPath, filenames, sys.argv[2], sys.argv[3])


