

class Board:
    """
    A class representing a board in a game of four in a row. A board has
    attributes "cells", which is a list of lists representing the cells of
    the board, and "bottoms", which is a list representing the lowest free
    cell of each column in the board
    """

    EMPTY = None
    TOP = 0
    FULL_STACK_ERROR = "Illegal move"
    VERTICAL = 2
    HORIZONTAL = 6
    DIAGONAL1 = 9
    DIAGONAL2 = 3
    DIRECTIONS = (2, 6, 9, 3)
    WIN_LENGTH = 4
    DIRECTION_ERROR = "Invalid direction"

    def __init__(self, height, width):
        """
        Constructor for board object
        :param height: the height of the board
        :param width: the width of the board
        """
        self.__cells = [[Board.EMPTY] * width for _ in range(height)]
        self.__bottoms = [height - 1 for _ in range(width)]

    def get_player_at(self, location):
        """
        Get the content of the board in a given location
        :param location: A tuple representing the required (row, col) location
        :return: Either an integer or none
        """
        row, col = location
        return self.__cells[row][col]

    def add_to_col(self, player, col):
        """
        Place a player disk at the lowest free cell of the stack
        :param player: An integer representing the player
        :param col: Index of the column to add disk to
        :return: None
        """
        if self.__bottoms[col] < Board.TOP:
            raise RuntimeError(Board.FULL_STACK_ERROR)
        self.__cells[self.__bottoms[col]][col] = player
        self.__bottoms[col] -= 1

    def search_streak(self, col, direction, player):
        """
        Search for a winning streak of player disks
        :param col: The column to which the last disk was added
        :param direction: The direction in which to search
        :param player: An integer representing the player
        :return: A list of (row, col) tuples if such a streak exists, None
        otherwise
        """
        if direction == Board.VERTICAL:
            return self.__search_vertical(col, player)
        elif direction == Board.HORIZONTAL:
            return self.__search_horizontal(self.__bottoms[col] + 1, player)
        elif direction == Board.DIAGONAL1:
            return self.__search_streak_diagonal1(self.__bottoms[col] + 1, col,
                                                  player, self.__cells)
        elif direction == Board.DIAGONAL2:
            return self.__search_streak_diagonal2(self.__bottoms[col] + 1, col,
                                                  player)
        else:
            raise TypeError(Board.DIRECTION_ERROR)

    def __search_vertical(self, col, player):
        """
        Search for a streak with a given length of player disks vertically
        :param col: The column to which the last disk was added
        :param player: An integer representing the player
        :return: A list of (row, col) tuples if such a streak exists, None
        otherwise
        """
        streak = []
        if self.__bottoms[col] + Board.WIN_LENGTH > len(self.__cells):
            return None
        for row in range(self.__bottoms[col]+1, len(self.__cells)):
            if self.__cells[row][col] == player:
                streak.append((row, col))
            else:
                streak = []
            if len(streak) == Board.WIN_LENGTH:
                break
        else:
            return None
        return streak

    def __search_horizontal(self, row, player):
        """
        Search for a streak with a given length of player disks horizontally
        :param row: The row to which the last disk was added
        :param player: An integer representing the player
        :return: A list of (row, col) tuples if such a streak exists, None
        otherwise
        """
        streak = []
        for col in range(len(self.__cells[0])):
            if self.__cells[row][col] == player:
                streak.append((row, col))
            else:
                streak = []
            if len(streak) == Board.WIN_LENGTH:
                break
        else:
            return None
        return streak

    def __search_streak_diagonal1(self, row, col, player, matrix):
        """
        Search for a streak with a given length of player disks horizontally
        :param row: The row to which the last disk was added
        :param col: The column to which the last disk was added
        :param player: An integer representing the player
        :param matrix: A list of lists representing the board
        :return: A list of (row, col) tuples if such a streak exists, None
        otherwise
        """
        # the length of a bottom-left to top-right diagonal containing a given
        # cell is calculated as follows: if the height of the matrix is smaller
        # than or equal to the width - the length is the sum of row and column
        # indices + 1 if sum <= height and maximal diagonal length - |maximal
        # diagonal length - sum of indices| if sum > height
        height = len(matrix)
        width = len(matrix[0])
        max_diagonal = min(width, height)
        indices_sum = row + col
        if indices_sum < height:
            diag_len = indices_sum + 1
            row_range = range(indices_sum, -1, -1)
            col_range = range(diag_len)
        else:
            diag_len = max_diagonal - abs(max_diagonal - indices_sum)
            row_range = range(height - 1, height - diag_len - 1, -1)
            col_range = range(width - diag_len, width)
        if diag_len < Board.WIN_LENGTH:
            return None
        streak = []
        for row_idx, col_idx in zip(row_range, col_range):
            if matrix[row_idx][col_idx] == player:
                streak.append((row_idx, col_idx))
            else:
                streak = []
            if len(streak) == Board.WIN_LENGTH:
                break
        else:
            return None
        return streak

    def __search_streak_diagonal2(self, row, col, player):
        """
        Search for a streak with a given length of player disks horizontally
        :param row: The row to which the last disk was added
        :param col: The column to which the last disk was added
        :param player: An integer representing the player
        :return: A list of (row, col) tuples if such a streak exists, None
        otherwise
        """
        width = len(self.__cells[0])
        reversed_board = []
        for prev_row in self.__cells:
            reversed_board.append(prev_row[::-1])
        new_col = width - col - 1
        streak = self.__search_streak_diagonal1(row, new_col, player,
                                                reversed_board)
        if streak is not None:
            for index, loc in enumerate(streak):
                row_idx, col_idx = loc
                streak[index] = row_idx, width - col_idx - 1
        return streak

    def get_bottoms(self):
        """
        :return: A list representing the bottom row of each column
        """
        return self.__bottoms

    def get_cells(self):
        """
        :return: The matrix representing the current game state
        """
        return self.__cells

    def __str__(self):
        """
        :return: A string representation of the board
        """
        string = ""
        for row in self.__cells:
            for cell in row:
                string += str(cell).center(4)
            string += "\n"
        return string
