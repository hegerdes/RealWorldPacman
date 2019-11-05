class Score:
    def __init__(self, usernames, callback):
        """
        :param usernames: dictionary with custom usernames and score of players
        :param overlay_position: position of the score overlay. (x,y)
            describing the rough center of the text field.
        """
        self.userNamesWithScores = usernames
        self.callback = callback

    def increase_score(self, carrierid):
        """
        increases the score for the player with id player_id by one.
        :param carrierid: id of carrier 
        """
        self.userNamesWithScores.get(carrierid)['score'] += 1
        self.callback()

    def draw(screen, scoreboard, overlay_position=(786, 20)):
        """ calls the draw method for every active package and prints the
        score overlay.
        """

        y = overlay_position[1]
        stepy = 20
        screen.draw.text("Scoreboard:", centerx=overlay_position[0], top=y, color="black")
        y += stepy
        screen.draw.text("Player", right=overlay_position[0], top=y, color="black")
        screen.draw.text("Score", left=overlay_position[0] + 5, top=y, color="black")

        for score in scoreboard:
            y += stepy
            screen.draw.text(score['username'], right=overlay_position[0], top=y, color="black")
            screen.draw.text(str(score['score']), left=overlay_position[0] + 5, top=y, color="black")

    def drawPyGame(display, scoreboard, overlay_position, font):
        y = overlay_position[1]
        stepy = 20
        
        text = "Scoreboard: "
        for score in scoreboard:
            text += score["username"] + " (" + str(score["score"]) + ") "
        board = font.render(text, False, (0, 0, 0))
        display.blit(board, overlay_position)

    def getScoreboard(self):
        return [
            {'username': self.userNamesWithScores.get(i)['username'], 'score': self.userNamesWithScores.get(i)['score']}
            for i in self.userNamesWithScores]
