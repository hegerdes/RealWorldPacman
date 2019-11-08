import pygame
import matplotlib.pyplot as plotter
import os
import sys
import tarfile
import time
import logging
import pickle
import configparser
import tools.osmparser as OSMP
import tools.gettiles as gettiles
import tools.RandomPackages as RandomPackages
import tools.Geo2GameCoords as Geo2GameCoords
import tools.wayrenderer as tracerender
from tools.movementbylines import MovementLines
from tools.movementbyai import MovementAI
from tools.bounds import Bounds
from distutils.util import strtobool
from tools.RaLaNSData import RaLaNSData
from Client import Client
from tools.player import Player
import tools.Package as Package
from tools.Score import Score
import tools.gamepad as gamepad
import tools.menu as menu

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
MAGENTA = (255, 1, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
YELOW = (255, 255, 0)

ZOOM = 15
TILES_DIM = 3
TILES_SIZE = 256
WIDTH = TILES_DIM * TILES_SIZE
HEIGHT = TILES_DIM * TILES_SIZE
LINE_THICK = 3
PACKAGE_WIDTH = 50
PLAYER_OFFSET = 10
WARNING_OFFSET = 37


tiles_prerendered = False
lines_prerendered = False
rendered_tiles_map = None
rendered_line_map = None

logger = logging.getLogger(__name__)

class Pacman:

    def __init__(self, PORT=25565):
        global WIDTH
        global HEIGHT
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('OMS Pacman')
        self.clock = pygame.time.Clock()
        self.myfont = pygame.font.SysFont('Comic Sans MS', 22)

        self.flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        self.tils_display = pygame.display.set_mode((WIDTH, HEIGHT), self.flags)
        self.main_menu = menu.Menu(self.tils_display, WIDTH, HEIGHT)
        # self.main_menu.main()

        self.GAMETIME = 300
        self.draw_RaLaNS = False
        self.score = None
        self.start_ticks = None

        self.osm_bounds = None
        self.my_osm_data = None
        if os.path.exists('settings/clientsettings.pickle'):
            pickle_off = open('settings/clientsettings.pickle', 'rb')
            data = pickle.load(pickle_off)
            self.client = Client(data['IP'], int(data['PORT']), data['USERNAME'])
        else:
            IPADRESS = 'localhost'
            PORT = 25565
            USERNAME = ''
            self.client = Client(IPADRESS, int(PORT), USERNAME)


        while (self.client.scenario == ""):
            self.client.Pump()
            try:
                self.client.Loop()
            except TypeError:
                print("\nUnable to connect to the server!\nStart a server first!")
                exit()
        print("Scenario path: " + self.client.scenario)

        try:
            tar = tarfile.open(self.client.scenario, "r:gz")
        except FileNotFoundError:
            print('The ' + self.client.scenario + ' is not avaiable\nGame exit')
            exit(1)
        config = configparser.ConfigParser()
        try:
            tarfileobj = tar.extractfile(tar.getmember('map.config'))
            config.read_string(tarfileobj.read().decode("utf-8"))
            ZOOM = int(config['MAP_CONF']['ZOOM'])
            TILES_DIM = int(config['MAP_CONF']['TILES_DIM'])
            TILES_SIZE = int(config['MAP_CONF']['TILES_SIZE'])
            self.GAMETIME = int(config['MAP_CONF']['TIME'])
            self.draw_RaLaNS = strtobool(config['MAP_CONF']['DRAW_RALANS'])
            WIDTH = TILES_DIM * TILES_SIZE
            HEIGHT = TILES_DIM * TILES_SIZE
        except KeyError:
            print('No Mapfile Found! Use Defaults')

        for member in tar.getmembers():
            if ".osm" in member.name:
                tarfileobj = tar.extractfile(member)
                self.osm_bounds = Bounds(tarfileobj, TILES_DIM, ZOOM)
                tarfileobj = tar.extractfile(member)
                self.my_osm_data = OSMP.OSMHandler(self.client.scenario.rsplit("/", 1)[0] + "/" + member.name, tarfileobj.read(), bounds_min=self.osm_bounds.get_start_gps_bounds(), bounds_max=self.osm_bounds.get_end_gps_bounds())

        # calculate random packages
        gps_start = self.osm_bounds.get_start_gps_bounds()
        gps_end = self.osm_bounds.get_end_gps_bounds()
        self.transformation = Geo2GameCoords.Geo2GameCoords((gps_start[1], gps_end[0], gps_end[1], gps_start[0]), [WIDTH, HEIGHT])

        self.r = RandomPackages.RandomPackages(self.my_osm_data.getWays())
        self.r.set_bounding_box(gps_start[0], gps_end[0], gps_start[1], gps_end[1])
        start = self.r.get_start_point_on_node()
        new_start = self.transformation.transform(start[0], start[1])

        self.player = Player()
        self.player.x = int(new_start[0])
        self.player.y = int(new_start[1])

        start_tiles = self.osm_bounds.get_start_tiles_bounds()

        self.tiles = gettiles.get_tile_mosaic(start_tiles[0], start_tiles[1], ZOOM, TILES_DIM)
        self.ways = tracerender.get_List_of_ways(self.my_osm_data, self.transformation, (WIDTH, HEIGHT))

        self.img = self.create_pacman_image('images/alien.png')
        self.pimg = self.create_pacman_image('images/player.png')

        self.ghost_image = pygame.image.load('images/ghost.png').convert_alpha()
        self.warn_img = pygame.image.load('images/warning.png').convert_alpha()

        if(self.draw_RaLaNS):
            zip_name = 'RaLaNS-Data/osna4km2_header_config.zip'
            hdf5_name = 'RaLaNS-Data/\'osna4km2\'.hdf5'
            utm_zone = 32
            self.ralans_data = RaLaNSData(zip_name, hdf5_name, utm_zone)

        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for joy in self.joysticks:
            joy.init()

    def create_pacman_image(self, image_path):
        img = {}
        img[0] = pygame.image.load(image_path).convert_alpha()
        img[1] = pygame.transform.rotate(pygame.image.load(image_path), -45).convert_alpha()
        img[2] = pygame.transform.rotate(pygame.image.load(image_path), -90).convert_alpha()
        img[3] = pygame.transform.flip(pygame.transform.rotate(pygame.image.load(image_path), -225), False, True).convert_alpha()
        img[4] = pygame.transform.flip(pygame.transform.rotate(pygame.image.load(image_path), -180), False, True).convert_alpha()
        img[5] = pygame.transform.flip(pygame.transform.rotate(pygame.image.load(image_path), -135), False, True).convert_alpha()
        img[6] = pygame.transform.rotate(pygame.image.load(image_path), -270).convert_alpha()
        img[7] = pygame.transform.rotate(pygame.image.load(image_path), -315).convert_alpha()
        return img

    def drawTiles(self):
        global tiles_prerendered
        global rendered_tiles_map
        if (tiles_prerendered):
            self.tils_display.blit(rendered_tiles_map, (0, 0))
        else:
            xcount = 0
            for row in self.tiles:
                ycount = 0
                for pic in row:
                    pic = 'images/' + pic
                    picImg = pygame.image.load(pic)
                    self.tils_display.blit(picImg, (xcount * 256, ycount * 256))
                    ycount += 1
                    if (ycount * 256 > WIDTH): break
                xcount += 1
                if (xcount * 256 > WIDTH): break
            print('Generating pre rendered Tiles')
            rendered_tiles_map = self.tils_display.copy()
            tiles_prerendered = True


    def drawLinesRender(self, show_lines=False):
        global lines_prerendered
        global rendered_line_map
        if (lines_prerendered):
            if (show_lines):
                self.tils_display.blit(rendered_line_map, (0, 0))
        else:
            z = 0
            currentColor = tracerender.rainbow(z)
            for way in self.ways:
                pointlist = []
                for i in range(len(way)):
                    wegpunkt = (way[i][0], way[i][1])
                    pointlist.append(wegpunkt)
                    if z < 7:
                        z += 1
                    else:
                        z = 0
                    currentColor = tracerender.rainbow(z)
                if len(pointlist) > 1:
                    pygame.draw.lines(self.tils_display, MAGENTA, False, pointlist, 4)
            print('Generating pre rendered Lines')
            rendered_line_map = self.tils_display.copy()
            lines_prerendered = True


    def drawGhosts(self):
        off = 50 / 2
        for i in self.client.ghostlist:
            self.tils_display.blit(self.ghost_image, (i[0] - off, i[1] - off))
            if i[0] < 0:
                self.tils_display.blit(self.warn_img, (0, i[1] - WARNING_OFFSET))
            if i[0] > WIDTH:
                self.tils_display.blit(self.warn_img, (WIDTH - WARNING_OFFSET * 2, i[1] - WARNING_OFFSET))
            if i[1] < 0:
                self.tils_display.blit(self.warn_img, (i[0] - WARNING_OFFSET, 0))
            if i[1] > HEIGHT:
                self.tils_display.blit(self.warn_img, (i[0] - WARNING_OFFSET, HEIGHT - WARNING_OFFSET * 2))


    def drawPlayer(self):
        for i in self.client.playerList:
            if (i[4]):
                if 0 <= i[2] <= 7:
                    if i[5] == self.client.playerName:
                        self.tils_display.blit(self.pimg[i[2]], (i[0] - PLAYER_OFFSET, i[1] - PLAYER_OFFSET))
                    else:
                        self.tils_display.blit(self.img[i[2]], (i[0] - PLAYER_OFFSET, i[1] - PLAYER_OFFSET))

                textsurface = self.myfont.render(i[5], False, (0, 0, 0))
                self.tils_display.blit(textsurface, (i[0] - textsurface.get_width() / 2, i[1] + textsurface.get_height() / 2))


    def drawPackages(self):
        for i, pos in enumerate(self.client.packageList):
            if not self.draw_RaLaNS:
                pygame.draw.circle(self.tils_display, RED, (int(pos[0]), int(pos[1])), Package.threshold_distance, LINE_THICK)
            else:
                trans = self.ralans_data.get_closest_transmitter_id(self.transformation.detransform(pos[0], pos[1]))
                rec = self.ralans_data.get_receivers(trans)

                # transmitter index to receiver indices
                rec_line = trans // self.ralans_data.header["size_x"]
                rec_row = trans % self.ralans_data.header["size_x"]

                range_meter = 10
                close = list()
                far = list()
                for y in range(rec_line - range_meter, rec_line + range_meter, 2):
                    for x in range(rec_row - range_meter, rec_row + range_meter, 2):

                        if 0 < y < len(rec) and 0 < x < len(rec[y]):
                            if rec[y][x] > Package.threshold_signal:

                                # receiver index to transmitter index
                                t_id = y * self.ralans_data.header["size_x"] + x
                                # get position from transmitter index
                                c = self.ralans_data.get_coords_from_id(t_id)
                                place = self.transformation.transform(c[0], c[1])
                                # draw
                                if rec[y][x] > Package.threshold_signal / 1.5: close.append(place)
                                else: far.append(place)

                for place in close:
                    pygame.draw.circle(self.tils_display, RED, (int(place[0]), int(place[1])), 5, 1)
                for place in far:
                    pygame.draw.circle(self.tils_display, BLUE, (int(place[0]), int(place[1])), 5, 1)

            if self.client.progress_packages and len(self.client.progress_packages) > i:
                for progress in self.client.progress_packages[i]:
                    progress = progress / Package.threshold_carried * Package.threshold_distance
                    if progress > 2:
                        pygame.draw.circle(self.tils_display, CYAN, (int(pos[0]), int(pos[1])), int(progress), 2)
                        pygame.draw.circle(self.tils_display, RED, (int(pos[0]), int(pos[1])), Package.threshold_distance, 2)


        if self.client.destination:
                    pygame.draw.circle(self.tils_display, BLUE, (int(self.client.destination[0]), int(self.client.destination[1])),
                                    Package.threshold_distance, LINE_THICK)
                    if self.client.progress_destination:
                        progress = self.client.progress_destination / Package.threshold_carried * Package.threshold_distance
                        if progress > 1:
                            pygame.draw.circle(self.tils_display, GREEN, (int(self.client.destination[0]), int(self.client.destination[1])),int(progress), 1)

    def drawScore(self):
        if self.client.gamestarted:
            Score.drawPyGame(self.tils_display, self.client.scoreboard, (20, 20), self.myfont)

    def drawEnd(self):
        endFont = pygame.font.SysFont('Comic Sans MS', 85)
        board = endFont.render('GAME END!', True, YELOW)
        self.tils_display.blit(board, (235, HEIGHT/2))
        pygame.display.update()

    def drawTimer(self):
        if(self.start_ticks):
            seconds = (pygame.time.get_ticks() - self.start_ticks)/1000
            try:
                countdown = self.myfont.render('Time: ' + str(self.GAMETIME - seconds)[:6], True, BLACK)
                self.tils_display.blit(countdown, (WIDTH - 110, HEIGHT - 15))
            except IndexError:
                pass


    def draw(self):
        self.drawTiles()
        self.drawLinesRender(True)
        self.drawGhosts()
        self.drawScore()
        self.drawPackages()
        self.drawTimer()
        self.drawPlayer()

    def checkScoreChange(self):
        if(self.client.scoreboard):
            if(not self.score): self.score = self.client.scoreboard
            if(self.score != self.client.scoreboard):
                self.score = self.client.scoreboard
                c_time = time.strftime("%d %m %Y %H-%M-%S", time.gmtime())
                logger.info(c_time + ':SC:' + str(self.client.scoreboard))


    def GameLoop(self, useAI = False):
        #Initial draw
        self.draw()

        #Init movment type
        line_movement = None
        ai_movement = None
        if(useAI):
            ai_movement = MovementAI(self.player,self.transformation,self.client, self.tils_display)
        else:
            line_movement = MovementLines(self.player, rendered_line_map, WIDTH, HEIGHT)

        while True:
            #Start GameTimer
            if(self.client.gamestarted and self.start_ticks == None):
                self.start_ticks = pygame.time.get_ticks()

            keys = pygame.key.get_pressed()
            gamepadButton = gamepad.getButton(self.joysticks)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)

            self.draw()
            self.checkScoreChange()

            #Move and sand to server
            if(useAI):
                ai_movement.move()
            else:
                line_movement.move(keys, gamepadButton)

            #Update Pos to server
            self.client.updatePosition(self.player.x, self.player.y, self.player.dir, self.player.y)

            try:
                self.client.Loop()
            except TypeError:
                print("\nUnable to connect to the server!\nStart a server first!")
                exit()

            pygame.display.update()
            self.clock.tick(60)

            #Game END
            if(self.client.roundEnded):
                self.drawEnd()
                c_time = time.strftime("%d %m %Y %H-%M-%S", time.gmtime())
                logger.info(c_time + ':EG:Spiel Vorbei')
                print('Spiel Vorbei!\n')
                time.sleep(5)
                break


if __name__ == "__main__":
    if(len(os.path.dirname(__file__)) > 0):
        os.chdir(os.path.dirname(__file__))
    logging.basicConfig(filename='eval/mslaw_base.log', level=logging.INFO,)

    pacmanGame = Pacman()
    pacmanGame.GameLoop(True)

