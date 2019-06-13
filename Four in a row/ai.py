from game import Game
from copy import deepcopy
from datetime import datetime


class AI:
    """
    A class responsible of evaluating the best possible move in a given turn
    in a game of four in a row. AI objects have attributes "best move", which
    is the column which the ai calculated to be the optimal move in the current
    turn, and "explored", which is a dictionary with game states as keys and
    the rating associated with them as values
    """

    # arrange possible moves so that we start checking from the middle
    # columns first, since we can make the most connections in the middle
    # of the board
    VALID_MOVES = [3, 2, 4, 1, 5, 0, 6]
    PLAYER_DISKS = Game.LAST_TURN // 2
    DEFAULT_TURNS_AHEAD = 7
    MIN_TURNS_AHEAD = 2
    NO_MOVE_ERROR = "No possible AI moves"
    DRAW_RATING = 0
    RATING = 1
    LOWEST_RATING = -float("inf")

    def __init__(self):
        """
        Constructor for AI object
        """
        self.__best_move = None
        self.__explored = {}

    def find_legal_move(self, g, func, timeout=None):
        """
        Find a legal move for the ai
        :param g: Game object
        :param func: A function that will receive a legal move as a parameter
        :param timeout: A float representing a time limit in seconds
        :return: None
        """
        start = datetime.now()
        if g.get_winner() is not None:
            raise LookupError(AI.NO_MOVE_ERROR)
        cur_turn = g.get_turn()
        best = AI.PLAYER_DISKS - (cur_turn // 2) # win this turn
        worst = ((cur_turn + 1) // 2) -AI.PLAYER_DISKS # lose next turn
        if timeout is None:
            # remove all null rating game states from the dictionary so we
            # may search more turns ahead
            self.__explored = dict(
                filter(lambda state: state[AI.RATING] != AI.DRAW_RATING,
                       self.__explored.items()))
            self.__rate_moves(AI.DEFAULT_TURNS_AHEAD, g, worst, best)
            func(self.__best_move)
        else:
            turns_ahead = AI.MIN_TURNS_AHEAD
            while (datetime.now() - start).seconds < timeout:
                self.__explored = dict(
                    filter(lambda state: state[AI.RATING] != AI.DRAW_RATING,
                           self.__explored.items()))
                rating = self.__rate_moves(turns_ahead, g, worst, best)
                turns_ahead += 1
                func(self.__best_move)
                if rating == best:
                    break

    def __rate_moves(self, turns_ahead, game_copy, low_bound, up_bound):
        """
        Rate moves by checking some turns ahead
        :param turns_ahead: An integer representing the number of turns ahead
        :param game_copy: A game object
        :param low_bound: lowest rating calculated
        :param up_bound: highest rating calculated
        :return: A tuple with the best rating and either None for the lowest
        recursion level or an integer representing a move for higher levels
        """
        winner = game_copy.get_winner()
        if turns_ahead == 0 or winner is not None:
            # we rate a move ending with the opponent's win as the opponent's
            # winning disk index - opponent's total disks. If the game ended,
            # than either the opponent won (because opponent was the last to
            # make a move) or the game ended with a draw
            rating = (game_copy.get_turn() // 2) - AI.PLAYER_DISKS
            if winner is None or winner == Game.DRAW:
                rating = AI.DRAW_RATING
            return rating
        best_rating = AI.LOWEST_RATING
        for move in AI.VALID_MOVES:
            temp_game = deepcopy(game_copy)
            try:
                temp_game.make_move(move)
            except RuntimeError:
                continue
            # a single state of the game can be reached in multiple ways,
            # so we cache the rating of each state, so that we don't need
            # to compute it more than once
            state = str(temp_game.get_board())
            if state in self.__explored:
                rating = self.__explored[state]
            else:
                # we calculate the rating of the move alternating between the
                # player and the opponent. We assume that the opponent will
                # always choose the best move that he can, which is the worst
                # move as far as the player is concerned.
                rating = -self.__rate_moves(turns_ahead - 1, temp_game,
                                            -up_bound, -low_bound)
                self.__explored[state] = rating
            if rating > best_rating:
                best_rating, best_move = rating, move
            # we want the moves with the highest rating, so if the rating is
            # lower than the lowest we computed, it's irrelevant and if it's
            # higher than or equal to the highest we computed, there's no need
            # to explore the rest of the moves possible from the current state,
            # because we get the opponent's chosen rating and we know the
            # opponent will choose the lowest rating possible
            low_bound = max(low_bound, rating)
            if low_bound >= up_bound:
                break
        self.__best_move = best_move
        return best_rating
