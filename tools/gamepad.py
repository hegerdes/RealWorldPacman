import pygame


def getButton(joysticks):
    for joy in joysticks:
        for j in range(len(joysticks)):

            # buttons
            for i in range(joysticks[j].get_numbuttons()):
                if joysticks[j].get_button(0):
                    #                    print('X')
                    return ('X')
                if joysticks[j].get_button(1):
                    #                    print('A')
                    return ('A')
                if joysticks[j].get_button(2):
                    #                    print('B')
                    return ('B')
                if joysticks[j].get_button(3):
                    #                    print('Y')
                    return ('Y')
                if joysticks[j].get_button(4):
                    return ('L')
                if joysticks[j].get_button(5):
                    return ('R')

            # arrow keys
            axes = joysticks[j].get_numaxes()
            for i in range(axes):
                xaxis = joysticks[j].get_axis(0)
                if xaxis > 0:
                    #                    print('right')
                    return ('right')
                if xaxis < 0:
                    #                    print('left')
                    return ('left')
                yaxis = joysticks[j].get_axis(1)
                if yaxis > 0:
                    #                    print('down')
                    return ('down')
                if yaxis < 0:
                    #                    print('up')
                    return ('up')
