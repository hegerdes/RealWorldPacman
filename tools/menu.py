# Import libraries
from IPy import IP
import pygameMenu
import pygame
import os
import pickle

# -----------------------------------------------------------------------------
# Constants and global variables
# -----------------------------------------------------------------------------
class Menu:
    def __init__(self, surface, width, height):
        self.COLOR_BLACK = (0, 0, 0)
        self.COLOR_WHITE = (255, 255, 255)
        self.FPS = 60.0
        self.MENU_BACKGROUND_COLOR = (112, 122, 169)
        self.WINDOW_SIZE = (width, height)
        self.image = pygame.image.load('images/pacman2.png')
        self.background = pygame.image.load('images/menu_background.png')
        # -----------------------------------------------------------------------------
        # Load former client settings if it exists, else set custom port
        # -----------------------------------------------------------------------------
        if os.path.exists('settings/clientsettings.pickle'):
            pickle_off = open('settings/clientsettings.pickle', 'rb')
            data = pickle.load(pickle_off)
            self.IPADRESS = data['IP']
            self.PORT = int(data['PORT'])
            self.USERNAME = data['USERNAME']
        else:
            self.IPADRESS = '127.0.0.1'
            self.PORT = 25565
            self.USERNAME = ''

        self.SURFACE = surface
        self.MAIN_MENU = None
        # self.clock = pygame.time.Clock()
        # self.test = False

    # -----------------------------------------------------------------------------
    # Methods
    # -----------------------------------------------------------------------------

    def main_background(self):
        """
        Background color of the main menu, on this function user can plot
        images, play sounds, etc.

        :return: None
        """

        self.SURFACE.fill((40, 40, 40))
        self.SURFACE.blit(self.image, (0, 0))

    def settings_background(self):
        """
        Background color of the settings menu, on this function user can plot
        images, play sounds, etc.

        :return: None
        """

        self.SURFACE.fill((40, 40, 40))
        self.SURFACE.blit(self.background, (0, 0))

    def setIPAddress(self, value):
        """
        This function sets the IP-Address the server is using.

        :param value: widget value
        :type value: basestring
        :return: None
        """
        if value == 'localhost':
            self.IPADRESS = value
            print('IP Adress set to: {0}'.format(value))
        else:
            try:
                self.IPADRESS = IP(value)
                print('IP Adress set to: {0}'.format(value))
            except:
                self.IPADRESS = value
                print('IP Adress set to: {0}'.format(value))

    def setPort(self, value):
        """
        This function sets the Port.
        :param value: int
        :type value: int
        :return: True if valid, false otherwise
        """
        try:
            port = int(value)
            if 1 <= port <= 65535:
                self.PORT = int(value)
                print('Port is set to: {0}'.format(value))
                return True
            else:
                raise ValueError('Not a valid Port: {0}'.format(value))
        except ValueError as e:
            print(e)
            return False

    def setUserName(self, value):
        """
        This function sets the USERNAME.
        :param value: str
        :type value: str
        :return: None
        """
        self.USERNAME = value
        print('USERNAME was set to {0}'.format(self.USERNAME))

    # def end_main_menu(self):
    # Pacman.game()
    # pygame.display.quit()
    # subprocess.call('python3 PacmanPyGame.py 1', shell=True)
    # exit()
    # self.test = True

    def main(self):
        """
        Main program.
        :return: None
        """

        # Create pygame screen and objects
        # SURFACE = pygame.display.set_mode(WINDOW_SIZE)
        # pygame.display.set_caption('PACMAN - UOS-Praktikum 2019')
        # clock = pygame.time.Clock()

        # Create menus

        # Settings menu
        settings_menu = pygameMenu.Menu(self.SURFACE,
                                        bgfun=self.settings_background,
                                        color_selected=self.COLOR_WHITE,
                                        font=pygameMenu.font.FONT_COMIC_NEUE,
                                        font_color=self.COLOR_BLACK,
                                        font_size=30,
                                        font_size_title=40,
                                        menu_alpha=100,
                                        menu_color=self.MENU_BACKGROUND_COLOR,
                                        menu_height=int(self.WINDOW_SIZE[1]),
                                        menu_width=int(self.WINDOW_SIZE[0]),
                                        onclose=pygameMenu.events.DISABLE_CLOSE,
                                        title='Settings',
                                        menu_color_title=(225, 117, 239),
                                        widget_alignment=pygameMenu.locals.ALIGN_LEFT,
                                        window_height=self.WINDOW_SIZE[1],
                                        window_width=self.WINDOW_SIZE[0]
                                        )
        # Add text inputs with different configurations
        wid0 = settings_menu.add_text_input('Username: ',
                                            default=self.USERNAME,
                                            textinput_id='USERNAME')
        wid1 = settings_menu.add_text_input('IP Address: ',
                                            default=self.IPADRESS,
                                            textinput_id='IP')

        wid2 = settings_menu.add_text_input('Port: ',
                                            default=int(self.PORT),
                                            textinput_id='PORT', input_type=pygameMenu.locals.INPUT_INT)

        def save_data():
            """
            Pickle and print data to console.
            :return: None
            """
            print('Saving data:')
            data = settings_menu.get_input_data()
            for k in data.keys():
                print(u'\t{0}\t=>\t{1}'.format(k, data[k]))
                if k == 'IP':
                    self.setIPAddress(data[k])
                if k == 'PORT':
                    if not self.setPort(data[k]):
                        settings_menu._select(2)
                        settings_menu.get_selected_widget().set_value(self.PORT)
                        return
                if k == 'USERNAME':
                    self.setUserName(data[k])

            pickling = open('settings/clientsettings.pickle', 'wb')
            pickle.dump(data, pickling)
            pickling.close()
            settings_menu.reset(1)

        # settings_menu.add_option('Save data', save_data)  # Call function
        settings_menu.add_option('Return to main menu', save_data,
                                 align=pygameMenu.locals.ALIGN_CENTER)
        settings_menu._menubar._on_return = save_data

        # Main menu
        self.MAIN_MENU = pygameMenu.Menu(self.SURFACE,
                                         bgfun=self.main_background,
                                         color_selected=self.COLOR_WHITE,
                                         draw_region_x=33,
                                         draw_region_y=64,
                                         font=pygameMenu.font.FONT_COMIC_NEUE,
                                         font_color=self.COLOR_BLACK,
                                         font_size=30,
                                         font_size_title=40,
                                         menu_alpha=0,
                                         menu_color=self.MENU_BACKGROUND_COLOR,
                                         menu_height=int(self.WINDOW_SIZE[1]),
                                         menu_width=int(self.WINDOW_SIZE[0]),

                                         # User press ESC button
                                         onclose=pygameMenu.events.CLOSE,
                                         option_shadow=False,
                                         title='Main menu',
                                         window_height=self.WINDOW_SIZE[1],
                                         window_width=self.WINDOW_SIZE[0]
                                         )
        self.MAIN_MENU.set_fps(self.FPS)
        self.MAIN_MENU.add_option('Play', pygameMenu.events.CLOSE)
        self.MAIN_MENU.add_option('Settings', settings_menu)
        self.MAIN_MENU.add_option('Quit', pygameMenu.events.EXIT)

        # Assertions (can be deactivated with '-o' e.g. 'python -o script.py')

        assert self.MAIN_MENU.get_widget('USERNAME', recursive=True) is wid0
        assert self.MAIN_MENU.get_widget('IP', recursive=True) is wid1
        assert self.MAIN_MENU.get_widget('PORT', recursive=True) is wid2

        # -------------------------------------------------------------------------
        # Main loop
        # -------------------------------------------------------------------------
        while self.MAIN_MENU.is_enabled():
            # Tick
            # self.clock.tick(self.FPS)

            # Paint background
            self.main_background()

            # Main menu
            self.MAIN_MENU.mainloop(disable_loop=False)

            # Flip SURFACE
            # pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    Menu(pygame.display.set_mode((768, 768)), 768, 768).main()
