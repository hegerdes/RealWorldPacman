import pygame


class Player(pygame.sprite.Sprite):
    '''
    Spawn a player
    '''

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.x = 0
        self.y = 0
        self.image = pygame.image.load('images/alien.png').convert_alpha()
        self.dir = 0

    def control(self, x, y):
        '''
        control player movement
        '''
        self.movex += x
        self.movey += y
