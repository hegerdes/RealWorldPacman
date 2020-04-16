import csv
import pygame
import math


class MovementGeo:

    def __init__(self, player, WIDTH, HEIGHT):

        self.alles = []
        with open("OSM-Data/os_small_geo.txt") as csvfile:
            baum = csv.reader(csvfile, delimiter=",")
            for lau in baum:
                self.alles.append(float(lau[0]))
        self.player = player
        self.n = 202249
        self.kreuzung = False
        self.warten = False
        self.sackgasse = False
        self.vorzuruck = True
        self.welcherverweis = 0
        self.los = False
        self.stop = False
        self.key = False
        self.einmal = False
        self.sicht = 0
        self.pfeilwinkel = 0
        self.zeit = 0
        self.vorzuruckverweis = True
        self.tkreuzung = False
        self.tkreuzungsicht = False
        self.wirklichtkreuzung = False
        self.punkt = True
        self.aktiv = False
        self.nochaktiv = False
        self.aktivl = False
        self.abstandx = 1
        self.abstandy = 1
        self.tschwer = False
        self.schwer = 1
        self.tleicht = False
        self.leicht = 1
        self.kreuzungverweis = False
        self.sackgasseverweis = False
        self.Randomausgesucht = False
        self.Random = False
        self.aktivspace = False
        self.winkelabstandalt = 10000
        self.wechselverweis = False
        self.sonderfall1 = False
        self.sonderfall3 = False
        self.ticker = False
        self.testo = 0
        self.player.x = self.alles[self.n]
        self.player.y = self.alles[self.n + 1]
        self.winkelpfeil = 0
        self.winkelplayer = 0
        self.pfeil = [self.player.x, self.player.y]
        self.destination = [1.0, 2.0]
        ##print(self.alles)

    # def angle_to(self, target):
    #     """Return the angle from this actors position to target, in degrees."""
    #     if isinstance(target, Actor):
    #         tx, ty = target.pos
    #     else:
    #         tx, ty = target
    #     myx, myy = self.pos
    #     dx = tx - myx
    #     dy = myy - ty   # y axis is inverted from mathematical y in Pygame
    #     return degrees(atan2(dy, dx))
    # def angle(self, angle):
    #     self._angle = angle
    #     w, h = self._orig_surf.get_size()
    #
    #     ra = radians(angle)
    #     sin_a = sin(ra)
    #     cos_a = cos(ra)
    #     self.height = abs(w * sin_a) + abs(h * cos_a)
    #     self.width = abs(w * cos_a) + abs(h * sin_a)
    #     ax, ay = self._untransformed_anchor
    #     p = self.pos
    #     self._anchor = transform_anchor(ax, ay, w, h, angle)
    #     self.pos = p
    #     self._update_transform(_set_angle)
    #
    # def transform_anchor(ax, ay, w, h, angle):
    #     """Transform anchor based upon a rotation of a surface of size w x h."""
    #     theta = -radians(angle)
    #
    #     sintheta = sin(theta)
    #     costheta = cos(theta)
    #
    #     # Dims of the transformed rect
    #     tw = abs(w * costheta) + abs(h * sintheta)
    #     th = abs(w * sintheta) + abs(h * costheta)
    #
    #     # Offset of the anchor from the center
    #     cax = ax - w * 0.5
    #     cay = ay - h * 0.5
    #
    #     # Rotated offset of the anchor from the center
    #     rax = cax * costheta - cay * sintheta
    #     ray = cax * sintheta + cay * costheta
    #
    #     return (
    #         tw * 0.5 + rax,
    #         th * 0.5 + ray
    #     )
    #
    # def _update_transform(self, function):
    #     if function in self.function_order:
    #         i = self.function_order.index(function)
    #         del self._surface_cache[i:]

    def zudrehen(self, player, wohindrehen):
        ###winkelberechnung
        C = [1, 1]
        B = [1, 0]
        C[0] = wohindrehen[0] - player.x
        C[1] = wohindrehen[1] - player.y
        B[0] = 1
        B[1] = 0
        betrag = math.sqrt((C[0] * C[0]) + (C[1] * C[1]))
        # betrag=wurzel((c[0]^2)+(c[1]^2))
        mussnochinwinkel = (1 * C[0]) / (betrag)
        alienwinkelbogen = math.acos(mussnochinwinkel)
        # alienwinkel=arccos(mussnochinwinkel)
        # image = open("images/alien.png")
        # alienwinkel=90
        alienwinkel = math.degrees(alienwinkelbogen)
        print(C, B)
        alien = pygame.image.load('images/alien.png')
        pygame.transform.rotate(player.image, alienwinkel)
        return alienwinkel

    def pfeildrehen(self, aktuellenwinkel, richtungdreh):
        pfeilbild = pygame.image.load('images/pfeilbild1.png')
        if richtungdreh == True:
            self.pfeilwinkel += 1
            pygame.transform.rotate(pfeilbild, self.pfeilwinkel)
        if richtungdreh == False:
            self.pfeilwinkel -= 1
            pygame.transform.rotate(pfeilbild, self.pfeilwinkel)
        return self.pfeilwinkel

    def move_by_geo(self, keys, gamepadButton):
        if self.punkt == True:

            k = int(self.alles[self.n + 2])
            if keys[pygame.K_UP] and self.kreuzung == False:
                # print("a-p",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten)
                if k > 1:
                    self.kreuzung = True
                    # print("a",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten)
                if k == 0:
                    # print("b",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten)
                    self.vorzuruck, self.sackgasse, self.kreuzung = self.prufen(self.n, self.vorzuruck)
                    # print("c",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten)
                    if self.sackgasse == False:
                        # print("d",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten)
                        if self.vorzuruck == True:
                            self.n = self.n + 4 + k
                            # print("e",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten)
                        if self.vorzuruck == False:
                            self.n = self.n - 4 - int(self.alles[self.n - 1])
                            # print("f",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten)
                    self.kreuzung = False
                if k == 1:
                    # print("g###########",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten)
                    self.vorzuruck, self.sackgasse, self.kreuzung = self.prufen(self.n, self.vorzuruck)
                    # print("h###########",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten)
                    if self.kreuzung == True:
                        self.tkreuzung = True
                    # print("h",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten)
                    if self.sackgasse == False and self.kreuzung == False:
                        # print("i",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten)
                        self.vorzuruckverweis, self.sackgasseverweis, self.kreuzungverweis = self.prufen(
                            int(self.alles[self.n + 3]), self.vorzuruck)
                        # print("j",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis)
                        if self.kreuzungverweis == False:
                            if self.sackgasseverweis == True:
                                # print("k",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis)
                                if self.vorzuruck == True:
                                    self.n = self.n + 4 + k
                                    # print("l",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis)
                                if self.vorzuruck == False:
                                    self.n = self.n - 4 - int(self.alles[self.n - 1])
                                    # print("m",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis)
                            if self.sackgasseverweis == False:
                                # print("self.n",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis)
                                if self.vorzuruckverweis == True:
                                    self.n = int(self.alles[self.n + 3]) + 4 + int(
                                        self.alles[int(self.alles[self.n + 3]) + 2])
                                    self.vorzuruck = True
                                    # print("o",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis)
                                if self.vorzuruckverweis == False:
                                    self.n = int(self.alles[self.n + 3]) - 4 - int(
                                        self.alles[int(self.alles[self.n + 3]) - 1])
                                    self.vorzuruck = False
                                    # print("p",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis)
                        if self.kreuzungverweis == True:
                            self.kreuzung = True
            if keys[pygame.K_RIGHT] == False:
                self.nochaktiv = False
            if keys[pygame.K_LEFT] == False:
                self.aktivl = False
            if self.kreuzung == True and self.einmal == False:
                # print("q-u",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten)
                self.vorzuruckverweis, self.sackgasseverweis, self.kreuzungverweis = self.prufen(
                    int(self.alles[self.n + 3 + self.welcherverweis]), self.vorzuruck)
                # print("q",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis)
                sondervorzuruck, sondersackgasse, sonderkreuzung = self.prufen(self.n, self.vorzuruck)
                if k > 1 and self.kreuzungverweis == True and sonderkreuzung == False:
                    # print("self.sonderfall1")
                    self.sonderfall1 = True
                if k == 1 and self.kreuzungverweis == True and sonderkreuzung == True:
                    self.tkreuzung = True
                    # print("sonderfall2")
                if k > 1 and self.kreuzungverweis == False and sonderkreuzung == True:
                    self.sonderfall3 = True
                    # self.ticker=True
                    # print("self.sonderfall3")
                if self.sonderfall3 == True:
                    if self.ticker == True:
                        self.sicht = self.n
                        if self.vorzuruck == True:
                            # print("t14",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis,self.welcherverweis,self.sicht)
                            self.destination[0] = self.alles[self.n + 4 + k]
                            self.destination[1] = self.alles[self.n + 5 + k]
                            winkelplayer = self.zudrehen(self.player, self.destination)
                            # self.player.angle = self.player.angle_to(self.destination)
                        if self.vorzuruck == False:
                            # print("u14",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis,self.welcherverweis,self.sicht)
                            self.destination[0] = self.alles[self.n - 4 - int(self.alles[self.n - 1])]
                            self.destination[1] = self.alles[self.n - 3 - int(self.alles[self.n - 1])]
                            winkelplayer = self.zudrehen(self.player, self.destination)
                            # self.player.angle = self.player.angle_to(self.destination)
                        self.ticker = False
                        self.welcherverweis -= 1
                    else:
                        self.sicht = int(self.alles[self.n + 3 + self.welcherverweis])
                        if self.vorzuruckverweis == True:
                            # print("t4",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis,self.welcherverweis,self.sicht)
                            self.destination[0] = self.alles[self.sicht + int(self.alles[self.sicht + 2]) + 4]
                            self.destination[1] = self.alles[self.sicht + int(self.alles[self.sicht + 2]) + 5]
                            winkelplayer = self.zudrehen(self.player, self.destination)
                            # self.player.angle = self.player.angle_to(self.destination)
                        if self.vorzuruckverweis == False:
                            # print("u4",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis,self.welcherverweis,self.sicht)
                            self.destination[0] = self.alles[self.sicht - int(self.alles[self.sicht - 1]) - 4]
                            self.destination[1] = self.alles[self.sicht - int(self.alles[self.sicht - 1]) - 3]
                            winkelplayer = self.zudrehen(self.player, self.destination)
                            # self.player.angle = self.player.angle_to(self.destination)
                if self.sonderfall1 == True:
                    self.sicht = int(self.alles[self.welcherverweis + self.n + 3])  ####+3oder+2
                    if self.wechselverweis == False:
                        self.destination[0] = self.alles[self.sicht + int(self.alles[self.sicht + 2]) + 4]
                        self.destination[1] = self.alles[self.sicht + int(self.alles[self.sicht + 2]) + 5]
                        winkelplayer = self.zudrehen(self.player, self.destination)
                        # self.player.angle = self.player.angle_to(self.destination)
                        self.wechselverweis = True
                        self.welcherverweis -= 1
                        self.vorzuruckverweis = True
                    else:
                        self.destination[0] = self.alles[self.sicht + int(self.alles[self.sicht - 1]) - 4]
                        self.destination[1] = self.alles[self.sicht + int(self.alles[self.sicht - 1]) - 3]
                        winkelplayer = self.zudrehen(self.player, self.destination)
                        # self.player.angle = self.player.angle_to(self.destination)
                        self.wechselverweis = False
                        self.sonderfall1 = False
                        self.vorzuruckverweis = False

                if self.tkreuzung == False and self.kreuzungverweis == False and self.sonderfall3 == False:
                    if self.sackgasseverweis == True:
                        self.welcherverweis = self.welcherverweis + 1
                        # print("zwei",self.welcherverweis)
                        # print("r",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis,self.welcherverweis,self.sicht)
                    if self.sackgasseverweis == False:
                        self.sicht = int(self.alles[self.n + 3 + self.welcherverweis])
                        self.einmal = True
                        # print("s",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis,self.welcherverweis,self.sicht)
                        if self.vorzuruckverweis == True:
                            # print("t",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis,self.welcherverweis,self.sicht)
                            self.destination[0] = self.alles[self.sicht + int(self.alles[self.sicht + 2]) + 4]
                            self.destination[1] = self.alles[self.sicht + int(self.alles[self.sicht + 2]) + 5]
                            winkelplayer = self.zudrehen(self.player, self.destination)
                            # self.player.angle = self.player.angle_to(self.destination)
                        if self.vorzuruckverweis == False:
                            # print("u",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis,self.welcherverweis,self.sicht)
                            self.destination[0] = self.alles[self.sicht - int(self.alles[self.sicht - 1]) - 4]
                            self.destination[1] = self.alles[self.sicht - int(self.alles[self.sicht - 1]) - 3]
                            winkelplayer = self.zudrehen(self.player, self.destination)
                            # self.player.angle = self.player.angle_to(self.destination)
                if self.tkreuzung == True and self.kreuzungverweis == False:
                    if self.vorzuruck == True:
                        # print("t1",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis,self.welcherverweis,self.sicht)
                        self.destination[0] = self.alles[self.n + 4 + k]
                        self.destination[1] = self.alles[self.n + 5 + k]
                        winkelplayer = self.zudrehen(self.player, self.destination)
                        # self.player.angle = self.player.angle_to(self.destination)
                    if self.vorzuruck == False:
                        # print("u1",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis,self.welcherverweis,self.sicht)
                        self.destination[0] = self.alles[self.n - 4 - int(self.alles[self.n - 1])]
                        self.destination[1] = self.alles[self.n - 3 - int(self.alles[self.n - 1])]
                        winkelplayer = self.zudrehen(self.player, self.destination)
                        # self.player.angle = self.player.angle_to(self.destination)
                    self.tkreuzung = False
                    self.tkreuzungsicht = True
                    self.wirklichtkreuzung = True
                if self.tkreuzung == True and self.kreuzungverweis == True:
                    self.sicht = int(self.alles[int(
                        self.alles[self.n + 2]) + self.n + 2])  ####self.sicht für die einzelnen self.schwer anpassen
                    if self.schwer == 1:
                        self.sicht = self.n
                        if self.vorzuruck == True:
                            # print("t11",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis,self.welcherverweis,self.sicht)
                            self.destination[0] = self.alles[self.n + 4 + k]
                            self.destination[1] = self.alles[self.n + 5 + k]
                            winkelplayer = self.zudrehen(self.player, self.destination)
                            # self.player.angle = self.player.angle_to(self.destination)
                        if self.vorzuruck == False:
                            # print("u11",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis,self.welcherverweis,self.sicht)
                            self.destination[0] = self.alles[self.n - 4 - int(self.alles[self.n - 1])]
                            self.destination[1] = self.alles[self.n - 3 - int(self.alles[self.n - 1])]
                            winkelplayer = self.zudrehen(self.player, self.destination)
                            # self.player.angle = self.player.angle_to(self.destination)
                    if self.schwer == 2:
                        # print("h11",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis,self.welcherverweis,self.sicht)
                        self.destination[0] = self.alles[
                            int(self.alles[self.n + 2 + int(self.alles[self.n + 2])]) + int(
                                self.alles[int(self.alles[self.n + 2 + int(self.alles[self.n + 2])]) + 2]) + 4]
                        self.destination[1] = self.alles[
                            int(self.alles[self.n + 2 + int(self.alles[self.n + 2])]) + int(
                                self.alles[int(self.alles[self.n + 2 + int(self.alles[self.n + 2])]) + 2]) + 5]
                        winkelplayer = self.zudrehen(self.player, self.destination)
                        # self.player.angle = self.player.angle_to(self.destination)
                        self.vorzuruckverweis = True

                    if self.schwer == 3:
                        # print("j11",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis,self.welcherverweis,self.sicht)
                        self.destination[0] = self.alles[
                            int(self.alles[self.n + 2 + int(self.alles[self.n + 2])]) - int(
                                self.alles[int(self.alles[self.n + 2 + int(self.alles[self.n + 2])]) - 1]) - 4]
                        self.destination[1] = self.alles[
                            int(self.alles[self.n + 2 + int(self.alles[self.n + 2])]) - int(
                                self.alles[int(self.alles[self.n + 2 + int(self.alles[self.n + 2])]) - 1]) - 3]
                        winkelplayer = self.zudrehen(self.player, self.destination)
                        # self.player.angle = self.player.angle_to(self.destination)
                        self.vorzuruckverweis = False
                    self.tschwer = True
                if self.tkreuzung == False and self.kreuzungverweis == True:
                    self.sicht = int(self.alles[int(self.alles[
                                                        self.n + 2]) + self.n + 2])  # ausgetauscht int(self.alles[self.n+2]) mit self.welcherverweis und +2 zu+3
                    if self.leicht == 1:
                        # print("h111",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis,self.welcherverweis,self.sicht)
                        self.destination[0] = self.alles[
                            int(self.alles[self.n + 2 + int(self.alles[self.n + 2])]) + int(
                                self.alles[int(self.alles[self.n + 2 + int(self.alles[self.n + 2])]) + 2]) + 4]
                        self.destination[1] = self.alles[
                            int(self.alles[self.n + 2 + int(self.alles[self.n + 2])]) + int(
                                self.alles[int(self.alles[self.n + 2 + int(self.alles[self.n + 2])]) + 2]) + 5]
                        winkelplayer = self.zudrehen(self.player, self.destination)
                        # self.player.angle = self.player.angle_to(self.destination)
                        self.vorzuruckverweis = True
                    if self.leicht == 2:
                        # print("j111",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis,self.sackgasseverweis,self.welcherverweis,self.sicht)
                        self.destination[0] = self.alles[
                            int(self.alles[self.n + 2 + int(self.alles[self.n + 2])]) - int(
                                self.alles[int(self.alles[self.n + 2 + int(self.alles[self.n + 2])]) - 1]) - 4]
                        self.destination[1] = self.alles[
                            int(self.alles[self.n + 2 + int(self.alles[self.n + 2])]) - int(
                                self.alles[int(self.alles[self.n + 2 + int(self.alles[self.n + 2])]) - 1]) - 3]
                        winkelplayer = self.zudrehen(self.player, self.destination)
                        # self.player.angle = self.player.angle_to(self.destination)
                        self.vorzuruckverweis = False
                    self.tleicht = True
                self.einmal = True
            if keys[pygame.K_RIGHT] == False:
                self.aktiv = False
            if keys[pygame.K_LEFT] == False:
                self.aktivl = False
            if self.aktiv == False and self.kreuzung == True and self.aktivl == False:
                if keys[pygame.K_RIGHT] or self.Random == True:
                    if self.tkreuzungsicht == False:
                        if self.welcherverweis < k:
                            self.welcherverweis = self.welcherverweis + 1
                            # print("einen",self.welcherverweis,self.einmal,self.kreuzung)
                        if self.welcherverweis >= k:
                            self.welcherverweis = 0
                            # print("test2",self.welcherverweis,self.einmal,self.kreuzung)
                            if self.wirklichtkreuzung == True:
                                self.tkreuzung = True
                                # print("test3",self.welcherverweis,self.einmal,self.kreuzung)
                            if self.sonderfall3 == True:
                                self.ticker = True
                    if self.tkreuzungsicht == True and self.kreuzungverweis == False:
                        self.tkreuzungsicht = False
                        # print("test1",self.welcherverweis,self.einmal,self.kreuzung)
                    if self.tschwer == True:
                        if self.schwer >= 3:
                            self.schwer = 0
                        if self.schwer < 3:
                            self.schwer = self.schwer + 1

                        # print("self.schwer",self.schwer)
                    if self.tleicht == True:
                        if self.leicht >= 2:
                            self.leicht = 0
                        if self.leicht < 2:
                            self.leicht = self.leicht + 1

                        # print("self.leicht",self.leicht)
                    self.warten = True
                    self.einmal = False
                    self.stop = True
                    # print("1t",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.welcherverweis,self.sicht)
                    self.aktiv = True
                if keys[pygame.K_LEFT]:
                    # print("2t",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten)
                    if self.tkreuzungsicht == False:
                        if self.welcherverweis >= 0:
                            self.welcherverweis = self.welcherverweis - 1
                            # print("einen1",self.welcherverweis,self.einmal,self.kreuzung)
                        if self.welcherverweis < 0:
                            self.welcherverweis = k - 1
                            # print("test21",self.welcherverweis,self.einmal,self.kreuzung)
                            if self.wirklichtkreuzung == True:
                                self.tkreuzung = True
                                # print("test31",self.welcherverweis,self.einmal,self.kreuzung)
                    if self.tkreuzungsicht == True:
                        self.tkreuzungsicht = False
                        # print("test11",self.welcherverweis,self.einmal,self.kreuzung)
                    self.warten = True
                    self.einmal = False
                    self.stop = True
                    # print("1l",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.welcherverweis,self.sicht)
                    self.aktivl = True
            if self.Random == True and self.kreuzung == True:
                # self.winkelpfeil=self.abrufendeswinkels(self.pfeil)
                # self.winkelplayer=self.abrufendeswinkels(self.player)
                self.winkelabstand = abs(self.winkelpfeil - self.winkelplayer)
                self.rundungfehlerwinkel = abs(self.winkelabstandalt - self.winkelabstand)  # neu winkel
                if self.rundungfehlerwinkel < 0.000001 and self.testo >= 10:  # self.winkelabstandalt==self.winkelabstand:#self.testo vielleicht
                    self.Randomausgesucht = True
                    # print("richtig",pfeil.angle,self.player.angle,self.winkelabstand,self.winkelabstandalt)
                else:
                    # print("Fehler",pfeil.angle,self.player.angle,self.winkelabstand,self.winkelabstandalt)
                    self.testo += 1  # self.testo vielleicht
                if self.winkelabstand < self.winkelabstandalt:
                    self.winkelabstandalt = self.winkelabstand

            if self.warten == True and self.kreuzung == True:
                if (keys[pygame.K_UP] and self.Random == False) or self.Randomausgesucht == True:
                    if self.tkreuzungsicht == True or (self.schwer == 1 and self.kreuzungverweis == True):
                        if self.vorzuruck == True:
                            self.n = self.n + 4 + k
                            self.vorzuruck = True
                            # print("wr",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis)
                        if self.vorzuruck == False:
                            self.n = self.n - 4 - int(self.alles[self.n - 1])
                            self.vorzuruck = False
                            # print("xr",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis)
                    if self.tkreuzungsicht == False or (
                            self.schwer > 1 and self.kreuzungverweis == True) or self.sonderfall1 == True:
                        if self.vorzuruckverweis == True:
                            self.n = self.sicht + int(self.alles[self.sicht + 2]) + 4
                            self.vorzuruck = True
                            # print("w",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis)
                        if self.vorzuruckverweis == False:
                            self.n = self.sicht - int(self.alles[self.sicht - 1]) - 4
                            self.vorzuruck = False
                            # print("x",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis)
                    self.kreuzung = False
                    self.welcherverweis = 0
                    self.stop = False
                    self.warten = False
                    self.tkreuzung = False
                    self.tkreuzungsicht = False
                    self.wirklichtkreuzung = False
                    self.wechselverweis = False
                    self.ticker = False
                    self.sonderfall3 = False
                    ####vielleicht
                    self.leicht = 1
                    self.schwer = 1
                    self.sonderfall1 = False
                    self.tleicht = False
                    self.tschwer = False
                    self.testo = 0
                    #####
                    # if self.Randomausgesucht==True:
                    # print("kreuzungausgesucht")
                    self.Randomausgesucht = False
                    self.winkelabstandalt = 10000
            if keys[pygame.K_DOWN]:
                # print("y",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis)
                if self.vorzuruck == True:
                    self.vorzuruck = False
                if self.vorzuruck == False:
                    self.vorzuruck = True
            if self.sackgasse == True:
                # print("z",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.warten,self.vorzuruckverweis)
                if self.vorzuruck == True:
                    self.vorzuruck = False
                if self.vorzuruck == False:
                    self.vorzuruck = True
                self.sackgasse = False
            self.ablaufenvorx = self.alles[int(self.n)]
            self.ablaufenvory = self.alles[int(self.n + 1)]
            self.ablaufenx = self.player.x - self.ablaufenvorx
            self.ablaufeny = self.player.y - self.ablaufenvory
            self.ablaufenxfurrundung = abs(self.ablaufenx)
            self.ablaufenyfurrundung = abs(self.ablaufeny)
            if self.ablaufenxfurrundung > 0.0000001 or self.ablaufenyfurrundung > 0.0000001:  # self.ablaufenx!=0 or self.ablaufeny!=0:#schägat aus wegen rundungsabweichungen
                # print("p1",self.n,k,self.vorzuruck,self.kreuzung,self.sackgasse,self.player.x,self.ablaufenvorx)
                self.destination[0] = self.ablaufenvorx
                self.destination[1] = self.ablaufenvory
                winkelplayer = self.zudrehen(self.player, self.destination)
                # self.player.angle = self.player.angle_to(self.destination)
            if self.player.x != self.ablaufenvorx:
                self.abstandx = abs(self.player.x - self.ablaufenvorx)
            if self.player.y != self.ablaufenvory:
                self.abstandy = abs(self.player.y - self.ablaufenvory)
            if self.abstandx >= self.abstandy:
                self.verhaltnis = self.abstandy / self.abstandx
                self.furx = 1
                self.fury = self.verhaltnis
            if self.abstandy >= self.abstandx:
                self.verhaltnis = self.abstandx / self.abstandy
                self.furx = self.verhaltnis
                self.fury = 1
        if self.player.x == self.ablaufenvorx and self.player.y == self.ablaufenvory:
            self.punkt == True
        if self.player.x != self.ablaufenvorx:
            self.abstandx = abs(self.player.x - self.ablaufenvorx)
        if self.player.y != self.ablaufenvory:
            self.abstandy = abs(self.player.y - self.ablaufenvory)

        if self.abstandx > 1.0:
            if self.ablaufenx >= 0.0:
                self.player.x = self.player.x - self.furx
            if self.ablaufenx < 0.0:
                self.player.x = self.player.x + self.furx
        else:
            self.player.x = self.ablaufenvorx

        if self.abstandy > 1.0:
            if self.ablaufeny >= 0.0:
                self.player.y = self.player.y - self.fury
            if self.ablaufeny < 0.0:
                self.player.y = self.player.y + self.fury

        else:
            self.player.y = self.ablaufenvory
        self.pfeil[0] = self.player.x
        self.pfeil[1] = self.player.y
        self.zeit = self.zeit + 1
        if keys[pygame.K_SPACE] == False:
            self.aktivspace = False
        if keys[pygame.K_SPACE] and self.aktivspace == False:
            if self.Random == False and self.aktivspace == False:
                self.Random = True
                self.aktivspace = True
                # print("Randomaktiv")
            if keys[pygame.K_SPACE] == False:
                self.aktivspace = False
            if self.Random == True and self.aktivspace == False:
                self.Random = False
                self.aktivspace = True
                # print("Randomnichtaktiv")
        if self.Random == True and keys[pygame.K_UP] == False:  # keyboard[keys.UP]==False
            if keys[pygame.K_RIGHT]:
                winkelpfeil = self.drehen(self, winkelpfeil, True)
                # pfeil.angle-=1
                self.winkelabstandalt = 10000  # neu
            if keys[pygame.K_LEFT]:
                winkelpfeil = self.pfeildrehen(self, winkelpfeil, False)
                # pfeil.angle+=1
                self.winkelabstandalt = 10000  # neu

    def prufen(self, pos, richtung):
        self.vorposabstand = int(self.alles[pos + 2])
        self.zuposabstand = int(self.alles[pos - 1])
        self.vorabstand = abs(self.alles[pos + self.vorposabstand + 4] - self.alles[pos]) + abs(
            self.alles[pos + self.vorposabstand + 5] - self.alles[pos + 1])
        self.zuabstand = abs(self.alles[pos - self.zuposabstand - 4] - self.alles[pos]) + abs(
            self.alles[pos - self.zuposabstand - 3] - self.alles[pos + 1])
        if self.vorabstand <= 6.0 and self.zuabstand > 6.0:
            return True, False, False
        if self.vorabstand > 6.0 and self.zuabstand <= 6.0:
            return False, False, False
        if self.vorabstand < 6.0 and self.zuabstand < 6.0:
            if self.vorabstand == 0.0:
                return False, False, False
            if self.zuabstand == 0.0:
                return True, False, False
            if self.vorabstand != 0.0 and self.zuabstand != 0.0:
                return richtung, False, True
        if self.vorabstand > 6.0 and self.zuabstand > 6.0:
            return richtung, True, False
