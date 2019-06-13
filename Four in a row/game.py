from board import Board


class Game:
    """
     A class representing A game of four in a row. A game has attributes
     "board", which is a Board object for keeping track of the game's
     advancement; "turn", an integer representing the current turn; "winner",
     which states who won the game, and "winning streak", which indicates
     the board coordinates of the game winning disk streak
    """

    PLAYER_ONE = 0
    PLAYER_TWO = 1
    DRAW = 2
    HEIGHT = 6
    WIDTH = 7
    LAST_TURN = HEIGHT * WIDTH + 1
    GAME_END_ERROR = "Illegal move"

    def __init__(self):
        """
        Constructor for game object
        """
        self.__turn = 1
        self.__board = Board(Game.HEIGHT, Game.WIDTH)
        self.__winner = None
        self.__winning_streak = None

    def make_move(self, column):
        """
        Add a disk to a column and check if the move ended the game
        :param column: The column's index
        :return: None
        """
        if self.__winner is not None:
            raise RuntimeError(Game.GAME_END_ERROR)
        if self.__turn % 2 == 0:
            player = Game.PLAYER_TWO
        else:
            player = Game.PLAYER_ONE
        self.__board.add_to_col(player, column)
        self.__turn += 1
        for direction in Board.DIRECTIONS:
            streak = self.__board.search_streak(column, direction, player)
            if streak is not None:
                self.__winner = player
                self.__winning_streak = streak
                break
        else:
            if self.__turn == Game.LAST_TURN:
                self.__winner = Game.DRAW

    def get_winner(self):
        """
        :return: An integer representing the winner, None if the game is
        still on
        """
        return self.__winner

    def get_player_at(self, row, col):
        """
        Get the player whose disk is in a given location
        :param row: Row index
        :param col: Column index
        :return: An integer representing the player, None if there's no disk
        in the location
        """
        return self.__board.get_player_at((row, col))

    def get_current_player(self):
        """
        :return: An integer representing which player's turn it is
        """
        if self.__turn % 2 == 0:
            return Game.PLAYER_TWO
        else:
            return Game.PLAYER_ONE

    def get_wining_streak(self):
        """
        :return: A list of (row, col) tuples containing the wining disks
        """
        return self.__winning_streak

    def get_board(self):
        """
        :return: The game's board object
        """
        return self.__board

    def get_turn(self):
        """
        :return: An integer representing current turn
        """
        return self.__turn
