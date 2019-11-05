import pygame

MAGENTA_FULL = (255, 1, 255, 255)

class MovementLines:

    def __init__(self, player, surface, WIDTH, HEIGHT):
        self.player = player
        self.rendered_line_map = surface
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.Movementtype = 1
        self.player_lock = 1
        self.player_speed = 1
        self.player_off = 10
        self.player_direction = 0
        self.Speedlock = 0
        self.Directionlock = 0
        self.Movementlock = 1
        self.Jumplock = False

    def handelBounds(self):
        Mins = 99999999

        if self.player.x < (2 * self.player_speed + 2):  # Determines on which end of the border we look.   /// 0 or 1 or 2
            for k in range((2 * self.player_speed + 2),
                           self.HEIGHT - (
                                   2 * self.player_speed + 2)):  # Look for suitable place to "land on"        /// (0, 1, 2,) 3, 4, 5... 697 (698, 699, 700)
                if self.rendered_line_map.get_at((int(self.WIDTH - (2 * self.player_speed + 2)), int(
                        k))) == MAGENTA_FULL:  # by looking which pixels are the right color. Color is trivial  // 697, k
                    if abs(int(
                            self.player.y) - k) < Mins:  # Safe the closest to the current (Mirrored) position in next and the distance in Mins
                        next = k  # /// position where the detector is supposed to be
                        Mins = abs(int(self.player.y) - k)
            if Mins < 999999:  # Comparison to trivial large value to make sure a match is found.
                self.player.x = self.WIDTH - (2 * self.player_speed + 2)  # If Match was found, move to that position, reset Mins
                self.player.y = next
                Mins = 99999999
            else:  # If not then you can't exit the map this way - a dead end
                self.player.x = self.player.x + 1

        if self.player.x > self.WIDTH - (2 * self.player_speed + 2):  # repeat for all four cardinal directions   /// 698, 699, 700
            for k in range((2 * self.player_speed + 2), self.HEIGHT - (2 * self.player_speed + 2)):  # /// 3,...,397
                if self.rendered_line_map.get_at((int((2 * self.player_speed + 2)), int(k))) == MAGENTA_FULL:  # /// 3, k
                    if abs(int(self.player.y) - k) < Mins:
                        next = k  # /// pos of detector
                        Mins = abs(int(self.player.y) - k)
            if Mins < 999999:
                self.player.x = (2 * self.player_speed + 2)  # ///
                self.player.y = next
                Mins = 99999999
            else:
                self.player.x = self.player.x - 1

        if self.player.y < (2 * self.player_speed + 2):
            for k in range((2 * self.player_speed + 2), self.WIDTH - (2 * self.player_speed + 2)):
                if self.rendered_line_map.get_at((int(k), int(self.HEIGHT - (2 * self.player_speed + 2)))) == MAGENTA_FULL:
                    if abs(int(self.player.x) - k) < Mins:
                        next = k
                        Mins = abs(int(self.player.x) - k)
            if Mins < 999999:

                self.player.x = next
                self.player.y = self.HEIGHT - (2 * self.player_speed + 2)
                Mins = 99999999
            else:
                self.player.y = self.player.y + 1

        if self.player.y > self.HEIGHT - (2 * self.player_speed + 2):
            for k in range((2 * self.player_speed + 2), self.WIDTH - (2 * self.player_speed + 2)):
                if self.rendered_line_map.get_at((int(k), int(2 * self.player_speed + 2))) == MAGENTA_FULL:
                    if abs(int(self.player.x) - k) < Mins:
                        next = k
                        Mins = abs(int(self.player.x) - k)
            if Mins < 999999:

                self.player.x = next
                self.player.y = (2 * self.player_speed + 2)
                Mins = 99999999
            else:
                self.player.y = self.player.y - 1




    def accel(self, up):
        self.player_speed
        if up == 0:
            self.player_speed = min([self.player_speed + 1, 6])
        if up == 1:
            self.player_speed = max([0, self.player_speed - 1])
        print('Momentane Geschwindigkeit:', self.player_speed)


    # def dnp(self, ):
    #     global pacman
    #     if self.player_direction == 0:
    #         pacman = pacman0
    #     if self.player_direction == 1:
    #         pacman = pacman1
    #     if self.player_direction == 2:
    #         pacman = pacman2
    #     if self.player_direction == 3:
    #         pacman = pacman3
    #     if self.player_direction == 4:
    #         pacman = pacman4
    #     if self.player_direction == 5:
    #         pacman = pacman5
    #     if self.player_direction == 6:
    #         pacman = pacman6
    #     if self.player_direction == 7:
    #         pacman = pacman7


    def Autofahren(self, direct):
        self.player.dir = direct
        self.Movementlock = max(0, self.Movementlock - 1)
        if 1 < self.player.x < self.WIDTH - 1 and 1 < self.player.y < self.HEIGHT - 1 and self.Movementlock == 0:
            if direct == 0:
                if (self.rendered_line_map.get_at((int(self.player.x) + 1, int(self.player.y))) == MAGENTA_FULL):
                    self.player.x = self.player.x + 1
                    self.player.y = self.player.y
                    self.Movementlock += 1
                    self.Jumplock = False
                elif (self.rendered_line_map.get_at((int(self.player.x) + 1, int(self.player.y + 1))) == MAGENTA_FULL):
                    self.player.x = self.player.x + 1
                    self.player.y = self.player.y + 1
                    self.Movementlock += 2
                    self.Jumplock = False
                elif (self.rendered_line_map.get_at((int(self.player.x), int(self.player.y + 1))) == MAGENTA_FULL) and self.Jumplock == False:
                    self.player.x = self.player.x
                    self.player.y = self.player.y + 1
                    self.Movementlock += 1
                else:
                    self.Jumplock = True
            if direct == 1:
                if (self.rendered_line_map.get_at((int(self.player.x) + 1, int(self.player.y + 1))) == MAGENTA_FULL):
                    self.player.x = self.player.x + 1
                    self.player.y = self.player.y + 1
                    self.Movementlock += 2
                    self.Jumplock = False
                elif (self.rendered_line_map.get_at((int(self.player.x), int(self.player.y + 1))) == MAGENTA_FULL):
                    self.player.x = self.player.x
                    self.player.y = self.player.y + 1
                    self.Movementlock += 1
                    self.Jumplock = False
                elif (self.rendered_line_map.get_at((int(self.player.x) - 1, int(self.player.y + 1))) == MAGENTA_FULL) and self.Jumplock == False:
                    self.player.x = self.player.x - 1
                    self.player.y = self.player.y + 1
                    self.Movementlock += 2
                else:
                    self.Jumplock = True
            if direct == 2:
                if (self.rendered_line_map.get_at((int(self.player.x), int(self.player.y + 1))) == MAGENTA_FULL):
                    self.player.x = self.player.x
                    self.player.y = self.player.y + 1
                    self.Movementlock += 1
                    self.Jumplock = False
                elif (self.rendered_line_map.get_at((int(self.player.x) - 1, int(self.player.y + 1))) == MAGENTA_FULL):
                    self.player.x = self.player.x - 1
                    self.player.y = self.player.y + 1
                    self.Movementlock += 2
                    self.Jumplock = False
                elif (self.rendered_line_map.get_at((int(self.player.x - 1), int(self.player.y))) == MAGENTA_FULL) and self.Jumplock == False:
                    self.player.x = self.player.x - 1
                    self.player.y = self.player.y
                    self.Movementlock += 1
                else:
                    self.Jumplock = True
            if direct == 3:
                if (self.rendered_line_map.get_at((int(self.player.x) - 1, int(self.player.y + 1))) == MAGENTA_FULL):
                    self.player.x = self.player.x - 1
                    self.player.y = self.player.y + 1
                    self.Movementlock += 2
                    self.Jumplock = False
                elif (self.rendered_line_map.get_at((int(self.player.x) - 1, int(self.player.y))) == MAGENTA_FULL):
                    self.player.x = self.player.x - 1
                    self.player.y = self.player.y
                    self.Movementlock += 1
                    self.Jumplock = False
                elif (self.rendered_line_map.get_at((int(self.player.x - 1), int(self.player.y - 1))) == MAGENTA_FULL) and self.Jumplock == False:
                    self.player.x = self.player.x - 1
                    self.player.y = self.player.y - 1
                    self.Movementlock += 2
                else:
                    self.Jumplock = True
            if direct == 4:
                if (self.rendered_line_map.get_at((int(self.player.x) - 1, int(self.player.y))) == MAGENTA_FULL):
                    self.player.x = self.player.x - 1
                    self.player.y = self.player.y
                    self.Movementlock += 1
                    self.Jumplock = False
                elif (self.rendered_line_map.get_at((int(self.player.x) - 1, int(self.player.y - 1))) == MAGENTA_FULL):
                    self.player.x = self.player.x - 1
                    self.player.y = self.player.y - 1
                    self.Movementlock += 2
                    self.Jumplock = False
                elif (self.rendered_line_map.get_at((int(self.player.x), int(self.player.y - 1))) == MAGENTA_FULL) and self.Jumplock == False:
                    self.player.x = self.player.x
                    self.player.y = self.player.y - 1
                    self.Movementlock += 1
                else:
                    self.Jumplock = True
            if direct == 5:
                if (self.rendered_line_map.get_at((int(self.player.x) - 1, int(self.player.y - 1))) == MAGENTA_FULL):
                    self.player.x = self.player.x - 1
                    self.player.y = self.player.y - 1
                    self.Movementlock += 2
                    self.Jumplock = False
                elif (self.rendered_line_map.get_at((int(self.player.x), int(self.player.y - 1))) == MAGENTA_FULL):
                    self.player.x = self.player.x
                    self.player.y = self.player.y - 1
                    self.Movementlock += 1
                    self.Jumplock = False
                elif (self.rendered_line_map.get_at((int(self.player.x + 1), int(self.player.y - 1))) == MAGENTA_FULL) and self.Jumplock == False:
                    self.player.x = self.player.x + 1
                    self.player.y = self.player.y - 1
                    self.Movementlock += 2
                else:
                    self.Jumplock = True
            if direct == 6:
                if (self.rendered_line_map.get_at((int(self.player.x), int(self.player.y - 1))) == MAGENTA_FULL):
                    self.player.x = self.player.x
                    self.player.y = self.player.y - 1
                    self.Movementlock += 1
                    self.Jumplock = False
                elif (self.rendered_line_map.get_at((int(self.player.x) + 1, int(self.player.y - 1))) == MAGENTA_FULL):
                    self.player.x = self.player.x + 1
                    self.player.y = self.player.y - 1
                    self.Movementlock += 2
                    self.Jumplock = False
                elif (self.rendered_line_map.get_at((int(self.player.x + 1), int(self.player.y))) == MAGENTA_FULL) and self.Jumplock == False:
                    self.player.x = self.player.x + 1
                    self.player.y = self.player.y
                    self.Movementlock += 1
                else:
                    self.Jumplock = True
            if direct == 7:
                if (self.rendered_line_map.get_at((int(self.player.x) + 1, int(self.player.y - 1))) == MAGENTA_FULL):
                    self.player.x = self.player.x + 1
                    self.player.y = self.player.y - 1
                    self.Movementlock += 2
                    self.Jumplock = False
                elif (self.rendered_line_map.get_at((int(self.player.x) + 1, int(self.player.y))) == MAGENTA_FULL):
                    self.player.x = self.player.x + 1
                    self.player.y = self.player.y
                    self.Movementlock += 1
                    self.Jumplock = False
                elif (self.rendered_line_map.get_at((int(self.player.x + 1), int(self.player.y + 1))) == MAGENTA_FULL) and self.Jumplock == False:
                    self.player.x = self.player.x + 1
                    self.player.y = self.player.y + 1
                    self.Movementlock += 2
                else:
                    self.Jumplock = True
            if self.Jumplock == True and self.Movementlock == 0:
                if direct == 0:
                    if (self.rendered_line_map.get_at((int(self.player.x+1), int(self.player.y-1))) == MAGENTA_FULL ):
                        self.player.x = self.player.x +1
                        self.player.y = self.player.y -1
                        self.Movementlock += 2
                        self.Jumplock = False
                    elif (self.rendered_line_map.get_at((int(self.player.x ), int(self.player.y - 1))) == MAGENTA_FULL):
                        self.player.x = self.player.x
                        self.player.y = self.player.y -1
                        self.Movementlock += 1
                elif direct == 1:
                    if (self.rendered_line_map.get_at((int(self.player.x+1), int(self.player.y))) == MAGENTA_FULL ):
                        self.player.x = self.player.x+1
                        self.player.y = self.player.y
                        self.Movementlock += 1
                        self.Jumplock = False
                    elif (self.rendered_line_map.get_at((int(self.player.x + 1), int(self.player.y - 1))) == MAGENTA_FULL):
                        self.player.x = self.player.x+1
                        self.player.y = self.player.y-1
                        self.Movementlock += 2
                elif direct == 2:
                    if (self.rendered_line_map.get_at((int(self.player.x+1), int(self.player.y+1))) == MAGENTA_FULL ):
                        self.player.x = self.player.x+1
                        self.player.y = self.player.y+1
                        self.Movementlock += 2
                        self.Jumplock = False
                    elif (self.rendered_line_map.get_at((int(self.player.x + 1), int(self.player.y))) == MAGENTA_FULL):
                        self.player.x = self.player.x+1
                        self.player.y = self.player.y
                        self.Movementlock += 1
                elif direct == 3:
                    if (self.rendered_line_map.get_at((int(self.player.x), int(self.player.y+1))) == MAGENTA_FULL ):
                        self.player.x = self.player.x
                        self.player.y = self.player.y +1
                        self.Movementlock += 1
                        self.Jumplock = False
                    elif (self.rendered_line_map.get_at((int(self.player.x + 1), int(self.player.y + 1))) == MAGENTA_FULL):
                        self.player.x = self.player.x+1
                        self.player.y = self.player.y+1
                        self.Movementlock += 2
                elif direct == 4:
                    if (self.rendered_line_map.get_at((int(self.player.x-1), int(self.player.y+1))) == MAGENTA_FULL ):
                        self.player.x = self.player.x -1
                        self.player.y = self.player.y +1
                        self.Movementlock += 2
                        self.Jumplock = False
                    elif (self.rendered_line_map.get_at((int(self.player.x), int(self.player.y + 1))) == MAGENTA_FULL):
                        self.player.x = self.player.x
                        self.player.y = self.player.y +1
                        self.Movementlock += 1
                elif direct == 5:
                    if (self.rendered_line_map.get_at((int(self.player.x-1), int(self.player.y))) == MAGENTA_FULL ):
                        self.player.x = self.player.x-1
                        self.player.y = self.player.y
                        self.Movementlock += 1
                        self.Jumplock = False
                    elif (self.rendered_line_map.get_at((int(self.player.x - 1), int(self.player.y + 1))) == MAGENTA_FULL):
                        self.player.x = self.player.x-1
                        self.player.y = self.player.y +1
                        self.Movementlock += 2
                elif direct == 6:
                    if (self.rendered_line_map.get_at((int(self.player.x-1), int(self.player.y-1))) == MAGENTA_FULL ):
                        self.player.x = self.player.x-1
                        self.player.y = self.player.y-1
                        self.Movementlock += 2
                        self.Jumplock = False
                    elif (self.rendered_line_map.get_at((int(self.player.x - 1), int(self.player.y ))) == MAGENTA_FULL):
                        self.player.x = self.player.x -1
                        self.player.y = self.player.y
                        self.Movementlock += 1
                elif direct == 7:
                    if (self.rendered_line_map.get_at((int(self.player.x), int(self.player.y-1))) == MAGENTA_FULL ):
                        self.player.x = self.player.x
                        self.player.y = self.player.y -1
                        self.Movementlock += 1
                        self.Jumplock = False
                    elif (self.rendered_line_map.get_at((int(self.player.x - 1), int(self.player.y - 1))) == MAGENTA_FULL):
                        self.player.x = self.player.x -1
                        self.player.y = self.player.y -1
                        self.Movementlock += 2

    def move(self, keys, gamepadButton):
        if (keys[pygame.K_l] or gamepadButton == 'L'):
            self.Movementtype = 1
        if (keys[pygame.K_r] or gamepadButton == 'R'):
            self.Movementtype = 0
        if (keys[pygame.K_s] or gamepadButton == 'A') and self.Speedlock == 0:
                self.accel(1)
                self.Speedlock = 10
        elif (keys[pygame.K_w] or gamepadButton == 'B') and self.Speedlock == 0:
            self.accel(0)
            self.Speedlock = 10
        if self.Speedlock > 0:
            self.Speedlock -= 1
        if self.Movementtype == 0:
            if ((2 * self.player_speed + 1 < self.player.x < self.WIDTH - (2 * self.player_speed + 1) and (
                    2 * self.player_speed + 1) < self.player.y < self.HEIGHT - (2 * self.player_speed + 1)) or True):
                if (keys[pygame.K_DOWN] or gamepadButton == 'down') and self.Directionlock == 0:
                    self.Directionlock = 7
                    if self.player_direction > 3:
                        self.player_direction = self.player_direction - 4
                        # dnp()
                    else:
                        self.player_direction = self.player_direction + 4
                        # dnp()
                if (keys[pygame.K_RIGHT] or gamepadButton == 'right') and self.Directionlock == 0:
                    self.Directionlock = 7
                    if self.player_direction < 7:
                        self.player_direction += 1
                        # dnp()
                    else:
                        self.player_direction = 0
                        # dnp()
                if (keys[pygame.K_LEFT] or gamepadButton == 'left') and self.Directionlock == 0:
                    self.Directionlock = 7
                    if self.player_direction > 0:
                        self.player_direction -= 1
                        # dnp()
                    else:
                        self.player_direction = 7
                        # dnp()
            if keys[pygame.K_q] or gamepadButton == 'X':
                self.player_lock = 1
            if keys[pygame.K_e] or gamepadButton == 'Y':
                self.player_lock = 0
            for k in range(0, self.player_speed):
                if keys[pygame.K_UP] or self.player_lock == 1 or gamepadButton == 'up':
                    self.Autofahren(self.player_direction)
                    self.handelBounds()

            if self.Directionlock > 0:
                self.Directionlock -= 1
                self.handelBounds()

        elif self.Movementtype == 1:
            for kmh in range(0, self.player_speed):
                if 1 < self.player.x < self.WIDTH - 1 and 1 < self.player.y < self.HEIGHT - 1:
                    if keys[pygame.K_DOWN] or gamepadButton == 'down':
                        if self.rendered_line_map.get_at((int(self.player.x),
                                                     int(self.player.y) + 1)) == MAGENTA_FULL:
                            self.player.y += 1
                        elif self.rendered_line_map.get_at((int(self.player.x + 1),
                                                       int(self.player.y) + 1)) == MAGENTA_FULL:
                            self.player.y += 1
                            self.player.x += 1
                        elif self.rendered_line_map.get_at((int(self.player.x - 1),
                                                       int(self.player.y) + 1)) == MAGENTA_FULL:
                            self.player.y += 1
                            self.player.x -= 1
                    if keys[pygame.K_UP] or gamepadButton == 'up':
                        if self.rendered_line_map.get_at((int(self.player.x),
                                                     int(self.player.y) - 1)) == MAGENTA_FULL:
                            self.player.y -= 1
                        elif self.rendered_line_map.get_at((int(self.player.x + 1),
                                                       int(self.player.y) - 1)) == MAGENTA_FULL:
                            self.player.y -= 1
                            self.player.x += 1
                        elif self.rendered_line_map.get_at((int(self.player.x - 1),
                                                       int(self.player.y) - 1)) == MAGENTA_FULL:
                            self.player.y -= 1
                            self.player.x -= 1
                    if keys[pygame.K_RIGHT] or gamepadButton == 'right':
                        if self.rendered_line_map.get_at((int(self.player.x) + 1,
                                                     int(self.player.y))) == MAGENTA_FULL:
                            self.player.x += 1
                        elif self.rendered_line_map.get_at((int(self.player.x + 1),
                                                       int(self.player.y) - 1)) == MAGENTA_FULL:
                            self.player.y -= 1
                            self.player.x += 1
                        elif self.rendered_line_map.get_at((int(self.player.x + 1),
                                                       int(self.player.y) + 1)) == MAGENTA_FULL:
                            self.player.y += 1
                            self.player.x += 1
                    if keys[pygame.K_LEFT] or gamepadButton == 'left':
                        if self.rendered_line_map.get_at((int(self.player.x) - 1,
                                                     int(self.player.y) + 1)) == MAGENTA_FULL:
                            self.player.x -= 1
                        elif self.rendered_line_map.get_at((int(self.player.x - 1),
                                                       int(self.player.y) - 1)) == MAGENTA_FULL:
                            self.player.y -= 1
                            self.player.x -= 1
                        elif self.rendered_line_map.get_at((int(self.player.x - 1),
                                                       int(self.player.y) + 1)) == MAGENTA_FULL:
                            self.player.y += 1
                            self.player.x -= 1
                self.handelBounds()