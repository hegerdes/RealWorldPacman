import requests
import math
import time
import json
import logging
import pygame
from datetime import datetime

logger = logging.getLogger(__name__)

class MovementAI():

    def __init__(self, player, tran, client, surface, cheatmode = False):
        self.SPEED = 1.0
        self.WAIT_COUNT = 60
        self.try_counter = 0
        self.way_len = 0
        self.package_change_count = 0
        self.player = player
        self.transformation = tran
        self.surface = surface
        self.client = client
        self.package_pos = None
        self.dest_way = None
        self.way = None
        self.cheat = cheatmode

        #Test Routing service
        self.getRoute(self.createOSRMquery((0,0),(0,0)))

    def move(self):
        player_pos = self.getPlayerPos()
        destin_pos = self.getDestinationPos()
        package_pos = self.getPackagePos(player_pos)

        if(destin_pos):
            if(self.dest_way == None):
                c_time = time.strftime("%d %m %Y %H-%M-%S", time.gmtime())
                logger.info(c_time + ':GP:Got package:<POS ' + str(self.transform2Geo(player_pos)) + ' TO ' + str(self.transform2Geo(destin_pos)) + 'POS>')
                self.dest_way = self.getRoute(self.createOSRMquery(self.transform2Geo(player_pos), self.transform2Geo(destin_pos)))
            self.package_pos = None
            self.drawWay()
            if(self.cheat):
                self.moveTo(self.dest_way)
            else:
                self.go_to_destination()


        elif(package_pos):
            self.dest_way = None
            if(not self.package_pos):
                c_time = time.strftime("%d %m %Y %H-%M-%S", time.gmtime())
                logger.info(c_time + ':LP:Lost package:<POS ' + str(self.transform2Geo(player_pos)) + ' TO ' + str(self.transform2Geo(package_pos)) + 'POS>')
                self.package_pos = package_pos
                self.way = self.getRoute(self.createOSRMquery(self.transform2Geo(player_pos), self.transform2Geo(self.package_pos)))
            if(self.package_pos != package_pos):
                self.package_change_count += 1
                self.package_pos = package_pos
                self.way = self.getRoute(self.createOSRMquery(self.transform2Geo(player_pos), self.transform2Geo(self.package_pos)))
            else:
                self.package_change_count = 0

            self.drawWay()

            if(self.cheat):
                self.moveTo(self.way)
            else:
                self.go_to_package()


    def createOSRMquery(self, start, end):
        return 'http://localhost:5000/route/v1/driving/{},{};{},{}?generate_hints=false&geometries=geojson&overview=full'.format(start[1], start[0], end[1],end[0])

    def getPlayerPos(self):
        for i in self.client.playerList:
            if (i[4]):
                if 0 <= i[2] <= 7:
                    if i[5] == self.client.playerName:
                        return (i[0], i[1])

    def getPackagePos(self, player_pos):
        if(len(self.client.packageList) > 0):
            dist = 9999.9
            for i, p in enumerate(self.client.packageList):
                p_dist = math.sqrt(abs(pow(player_pos[0]-p[0],2) + pow(player_pos[1]-p[1],2)))
                if(p_dist < dist):
                    dist = p_dist
                    package_pos = p

            return (package_pos[0], package_pos[1])
        else: return None

    def getDestinationPos(self):
        if(self.client.destination):
            return (self.client.destination[0], self.client.destination[1])
        else: return None

    def transform2Geo(self, displaykoord):
        return self.transformation.detransform(displaykoord[0], displaykoord[1])

    def getRoute(self, request_str):
        try:
            r = requests.get(request_str)
        except requests.exceptions.RequestException as err:
            print('Unable to connect to OSRM. Please check connection.\n' + str(err))
            print('Exit')
            exit(1)

        waypoints = json.loads(r.text)['routes'][0]['geometry']['coordinates']
        my_lists = []
        for i in waypoints:
            my_lists.append(self.transformation.transform(i[1], i[0]))

        return my_lists

    def go_to_package(self):
        remove = False
        step_counter = 0
        if(self.way_len != len(self.way)):
            self.way_len = len(self.way)
            self.try_counter = 0
        if(self.try_counter > self.WAIT_COUNT): remove = True
        for i in self.way:
            dist_x = i[0] - self.player.x
            dist_y = i[1] - self.player.y
            if(abs(dist_x) < 1 and abs(dist_y) < 1):
                if(self.package_change_count > 1):
                    continue
                else:
                    remove = True
                    break
            distance = math.sqrt(pow(dist_x, 2) + pow(dist_y, 2))
            dist_x /= distance
            dist_y /= distance
            if(self.package_change_count > 1):
                self.player.x += dist_x * 0.85
                self.player.y += dist_y * 0.85
                step_counter += 1
            else:
                self.player.x += dist_x * self.SPEED
                self.player.y += dist_y * self.SPEED
            self.try_counter += 1
            dist_x = i[0] - self.player.x
            dist_y = i[1] - self.player.y

            if(self.package_change_count < 1):
                if(abs(dist_x) > 1 and abs(dist_y) > 1): break
            elif(step_counter > 5):
                if(abs(dist_x) > 1 and abs(dist_y) > 1): break


        if(len(self.way) > 0 and remove):
            remove = False
            self.way.pop(0)
            self.go_to_package

    def go_to_destination(self):
        remove = False
        if(self.way_len != len(self.dest_way)):
            self.way_len = len(self.dest_way)
            self.try_counter = 0
        if(self.try_counter > self.WAIT_COUNT): remove = True
        for i in self.dest_way:
            dist_x = i[0] - self.player.x
            dist_y = i[1] - self.player.y
            if(abs(dist_x) < 1 and abs(dist_y) < 1):
                remove = True
                break
            distance = math.sqrt(pow(dist_x,2)+ pow(dist_y,2))
            dist_x /= distance
            dist_y /= distance
            self.player.x += dist_x * self.SPEED
            self.player.y += dist_y * self.SPEED
            self.try_counter += 1
            dist_x = i[0] - self.player.x
            dist_y = i[1] - self.player.y
            if(abs(dist_x) > 1 and abs(dist_y) > 1): break


        if(len(self.dest_way) > 0 and remove):
            remove = False
            self.dest_way.pop(0)
            self.go_to_destination()

    def moveTo(self, way):
        for i in way:
            dist_x = i[0] - self.player.x
            dist_y = i[1] - self.player.y
            if(abs(dist_x) < 1 and abs(dist_y) < 1): continue
            distance = math.sqrt(pow(dist_x,2)+ pow(dist_y,2))
            dist_x /= distance
            dist_y /= distance
            self.player.x += dist_x
            self.player.y += dist_y

        if(len(way) > 1):
            way.pop(0)

    def drawWay(self):
        if(self.way and len(self.way) > 1):
            pygame.draw.lines(self.surface, (0,0,255), False, self.way, 4)
        elif(self.dest_way and len(self.dest_way) > 1):
            pygame.draw.lines(self.surface, (0,0,255), False, self.dest_way, 4)
