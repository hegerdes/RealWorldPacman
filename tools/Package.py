#import pgzrun
import math
import time
""" 
Defines Package class which capsulates the transmitting mechanics for packages.
"""

threshold_carried = 180
threshold_distance = 50


def calculateDistance(x1, y1, x2, y2):
    dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist

class Package:
    def __init__(self, packageManager, rand_pack, trans, num_players, num_ghosts):
        """
        initializes package.

        :param rand_pack: RandomPackage object
        :param trans: Geo2GameCoords object
        """

        # initialize start and end point
        self.position    = rand_pack.get_point_on_node()
        self.destination = rand_pack.get_end_point_on_node()
        self.position    = trans.transform(self.position[0], self.position[1])
        self.destination = trans.transform(self.destination[0], self.destination[1])

        # initialize rest
        self.progress = [0 for id in range(num_players)]
        self.carried = False
        self.delivered = False
        self.carrier = -1
        self.packageManager = packageManager
        self.num_players = num_players
        self.num_ghosts = num_ghosts
        self.dest_progress = 0
        self.carried_by_ghost = False
        self.last_stolen_by_ghost = time.time()

    def update(self, playerList, ghostList, delta):
        """
        updates the progress list depending on players distance to the
        package.

        :param playerList: list of the coordinate of all players
        :param delta: time in seconds since last update
        :return: True if anything has changed. Otherwise False
        """
        changed = False

        if not self.carried and not self.delivered:
            # STATE is STATIONARY
            for player_id, player_pos in enumerate(playerList):
                if self.can_grab_package(player_id, player_pos, delta):
                    # set carrier
                    self.carrier = player_id
                    self.carried_by_ghost = False
                    self.packageManager.carrier_changed(player_id)
                    changed = True
                    # goes into STATE CARRIED
                    print(f'Package {self.position}: state changed to CARRIED')
                    self.carried    = True
                    self.delivered = False

            # ghost takes package that is stationary
            for ghost_id, ghost_pos in enumerate(ghostList):
                if not self.packageManager.is_carrying(ghost_id, False) and \
                        calculateDistance(ghost_pos[0], ghost_pos[1], self.position[0],
                                          self.position[1]) < threshold_distance:
                    self.carrier = ghost_id
                    self.carried_by_ghost = True
                    changed = True
                    print(f'Package {self.position}: state changed to CARRIED (by Ghost:{ghost_id})')
                    self.carried = True
                    self.delivered = False

        elif self.carried and not self.delivered:
            # STATE is CARRIED
            # move package to player position
#            print('i update position')
            if self.carried_by_ghost:
                self.position = ghostList[self.carrier]
            else:
                self.position = playerList[self.carrier]
            changed = True

            # was the package stolen by player?
            for player_id, player_pos in enumerate(playerList):
                if self.can_grab_package(player_id, player_pos, delta):
                    # carrier changed!
                    if not self.carried_by_ghost:
                        self.packageManager.remove_destination(self.carrier)

                    self.packageManager.progress_changed = True
                    self.carrier = player_id
                    self.carried_by_ghost = False
                    self.packageManager.carrier_changed(player_id)
                    changed = True
                    # goes into STATE CARRIED
                    print(f'Package {self.position}: state stayed to CARRIED (aka. package stolen by {player_id})')
                    self.carried   = True
                    self.delivered = False
                    self.last_stolen_by_ghost = time.time()

            # was the package stolen by ghost?
            current_time = time.time()
            for ghost_id, ghost_pos in enumerate(ghostList):
                if current_time - self.last_stolen_by_ghost > 5 and \
                        not self.packageManager.is_carrying(ghost_id, False) and \
                        calculateDistance(ghost_pos[0], ghost_pos[1], self.position[0],
                                          self.position[1]) < threshold_distance:
                    if not self.carried_by_ghost:
                        self.packageManager.remove_destination(self.carrier)
                    self.carrier = ghost_id
                    self.carried_by_ghost = True
                    changed = True
                    # goes into STATE CARRIED
                    print(f'Package {self.position}: state stayed to CARRIED (aka. package stolen by ghost:{ghost_id})')
                    self.carried = True
                    self.delivered = False
                    self.last_stolen_by_ghost = time.time()

            # was the package delivered?
            if not self.carried_by_ghost and self.can_deliver_package(delta):
                # remove destination from client view
                self.packageManager.remove_destination(self.carrier)
                changed = True
                # goes into STATE DELIVERED
                print(f'Package at {self.position}: state changed to DELIVERED')
                self.carried   = False
                self.carried_by_ghost = False
                self.delivered = True
                self.packageManager.package_delivered()

        elif self.delivered:
            # STATE is DELIVERED
            pass
        else:
            # INVALID STATE !!!!
            print('[FAIL] Package at position {self.position}: INVALID STATE!!!!!')

        return changed


    def can_grab_package(self, player_id, player_position, delta):
        """
        Checks if player with player_id has enough progress to grab a package
        Changes progress
        :param player_id:
        :param player_position: tuple of coordinates
        :param delta: time since last update
        :return: True if able to grab. Otherwise False
        """
        if not player_position[2]:
            return False
        if self.packageManager.is_carrying(player_id):
            if self.progress[player_id] != 0:
                self.progress[player_id] = 0
                self.packageManager.progress_changed = True
            return False

        dist_weight = 1.8
        dist = calculateDistance(player_position[0], player_position[1], self.position[0], self.position[1])

        # player is in reach of package
        if dist < threshold_distance:
            dist_value = threshold_distance - dist
            self.progress[player_id] += dist_value * dist_weight * delta

            if self.progress[player_id] >= threshold_carried:
                # all progress for all players is reset when taking a package
                self.packageManager.progress_changed = True
                self.progress = [0 for _ in self.progress]
                return True

            else:
                self.packageManager.progress_changed = True
                return False

        else:
            if self.progress[player_id] != 0:
                self.packageManager.progress_changed = True
            self.progress[player_id] = 0
            return False


    def can_deliver_package(self, delta):
        """
            Checks if carrier has enough progress to deliver a package
            Changes destination progress
            :param delta: time since last update
            :return: True if able to deliver. Otherwise False
        """
        dest_dist_weight = 2.7
        dest_dist = calculateDistance(self.destination[0], self.destination[1], self.position[0], self.position[1])

        # check distance to destination
        if dest_dist < threshold_distance:
            dest_dist_value = threshold_distance - dest_dist
            self.dest_progress += dest_dist_value * dest_dist_weight * delta
            self.packageManager.progress_changed = True

            if self.dest_progress >= threshold_carried:
                self.dest_progress = 0
                return True
            else:
                return False

        else:
            if self.dest_progress != 0:
                self.packageManager.progress_changed = True
            self.dest_progress = 0
            return False

class PackageManager:
    """ organzes all packages and renders them according to their internal
    state.
    """

    def __init__(self, numPackages, rand_pack, transformation, num_player, num_ghost, score):
        """
        creates inital packages.

        :param numPackages: number of packages that is supposed to be active at any
            given point in time.
        :param rand_pack: RandomPackage object
        :param transformation: Geo2GameCoords object
        :param num_player number of player
        :param score: Score object
        """
        self.rand_pack  = rand_pack
        self.trans      = transformation
        self.num_player = num_player
        self.num_ghost = num_ghost
        self.active = [Package(self, rand_pack, transformation, num_player, num_ghost) for i in range(numPackages)]

        self.changed_carriers = set()
        self.former_carriers = set()
        self.score = score
        self.last_timestamp = time.time()
        self.last_progress = []
        self.progress_changed = False


    def package_delivered(self):
        """
        gets called by a package instance when it was delievered.
        """
        for i, package in enumerate(self.active):
            if package.delivered:
                self.score.increase_score(package.carrier)
                self.active[i] = Package(self, self.rand_pack,
                                         self.trans,
                                         self.num_player, self.num_ghost)

    def carrier_changed(self, carrier):
        """
        gets called when a package got a new carrier.

        :param carrier: player id of player who now carries a new package.
        """
        self.changed_carriers.add(carrier)

    def remove_destination(self, player_id):
        """
        gets called when a client should remove the formerly displayed
        destination from the screen.

        :param player_id: id of player whose client should be updated.
        """
        self.former_carriers.add(player_id)

    def update(self, playerList, ghostList, delta):
        """ calls the update for every active package.

        :param playerList: list of the coordinates of all players (x, y)
        :param ghostList: List of the coordinates of all ghosts (x,y)
        :param delta: time in seconds since last call.
        :return: True if anything has changed. Otherwise False
        """

        changed = False
        self.progress_changed = False

        for package in self.active:
            if not changed:
                changed = package.update(playerList, ghostList, delta)
            else:
                package.update(playerList, ghostList, delta)

        return changed

    def get_positions(self):
        """
        returns a list of the positions of every active package.
        :return: list of the positions of every active package.
        """
        return [package.position for package in self.active]

    def get_destinations(self):
        destinations = []
        for package in self.active:
            if not package.carried_by_ghost and package.carrier in self.changed_carriers:
                self.changed_carriers.remove(package.carrier)
                destinations.append( (package.carrier, package.destination) )

        return destinations

    def get_former_carriers(self):
        former_carriers = self.former_carriers.copy()
        self.former_carriers = set()
        return former_carriers

    def is_carrying(self, id, check_player=True):
        # is there a package carried by player?
        for package in self.active:
            if (not check_player) == package.carried_by_ghost:
                if package.carrier == id:
                    return True
        # no package found for player
        return False

    def check_progress(self):
        progress_list = []
        for p in self.active:
            progress_list.append(p.progress)

        if self.last_progress == progress_list:
            return False
        else:
            self.last_progress = progress_list
            return True

    def get_progress(self):
        return [p.progress for p in self.active]

    def get_carried_dest_progress(self):
        result = []
        for package in self.active:
            if package.carried and not package.carried_by_ghost:
                result.append((package.dest_progress, package.carrier))
        return result
