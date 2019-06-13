from communicator import Communicator
from game import Game
from ai import AI
import tkinter as tk


class GUI:
    """
    A class responsible for handling the GUI aspects of a for in a row game.
    Also handles the connection of the communicator
    """

    IMAGE_PATHS = ["images/empty_cell.png", "images/player1_disk.png",
                   "images/player2_disk.png", "images/player1_disk_win.png",
                   "images/player2_disk_win.png"]
    FONT = ("times", 24)
    HUMAN = 0
    AI = 1
    MSG_COLOR = "blue"
    EMPTY_CELL_IMG = 0
    PLAYER1_CELL_IMG = 1
    PLAYER2_CELL_IMG = 2
    PLAYER1_WIN_DISK = 3
    PLAYER2_WIN_DISK = 4
    WINDOW_SIZE = 500
    BOARD_HEIGHT = 6
    BOARD_WIDTH = 7
    P1 = "Player 1"
    P2 = "Player 2"
    HOLD_MSG = "Please wait for %s to finnish their turn"
    DRAW = "No more moves. Game ended with a draw"
    WIN = "%s won!"
    DEFAULT_MSG = ""
    TOP = 0
    DROP_RATE = 100

    def __init__(self, root, player, port, ip=None):
        """
        Initialize GUI and connect the communicator
        :param root: The tkinter root
        :param player: An integer representing if the player is human or ai
        :param port: The port to connect to
        :param ip: The ip to connect to
        """
        self.__root = root
        self.__game = Game()
        self.__bottoms = self.__game.get_board().get_bottoms()
        self.__communicator = Communicator(root, port, ip)
        self.__communicator.connect()
        self.__communicator.bind_action_to_message(self.__handle_message)
        self.__top_frame = tk.Frame(self.__root)
        self.__top_frame.pack()
        self.__col_frames = []
        self.__buttons = []
        self.__player = GUI.P1
        self.__opponent = GUI.P2
        if ip is not None:
            self.__player, self.__opponent = self.__opponent, self.__player
        self.__msg_board = tk.Message(root, font=GUI.FONT, fg=GUI.MSG_COLOR)
        self.__msg_board.pack()
        self.__images = []
        self.__load_images()
        self.__place_widgets()
        self.__ai = None
        if player == GUI.AI:
            self.__ai = AI()
        self.__start_game()

    def __start_game(self):
        """
        Allow player one to make a move
        :return: None
        """
        if self.__player == GUI.P1:
            if self.__ai is not None:
                self.__ai_play()
            else:
                self.__change_buttons_state(tk.NORMAL)
        else:
            self.__update_msg(GUI.HOLD_MSG % self.__opponent)

    def __place_widgets(self):
        """
        Place widgets in the gui
        :return: None
        """
        for col in range(GUI.BOARD_WIDTH):
            col_frame = tk.Frame(self.__top_frame)
            col_frame.pack(side=tk.LEFT)
            self.__col_frames.append(col_frame)
            for row in range(GUI.BOARD_HEIGHT):
                cell = tk.Label(col_frame,
                                image=self.__images[GUI.EMPTY_CELL_IMG])
                cell.grid(row=row)
            col_button = tk.Button(col_frame, text=str(col + 1),
                                   command=lambda column=col: self.__play_col(
                                       column), state=tk.DISABLED)
            col_button.grid(row=GUI.BOARD_HEIGHT)
            self.__buttons.append(col_button)

    def __load_images(self):
        """
        Load all images necessary for the gui
        :return: None
        """
        images = []
        for path in GUI.IMAGE_PATHS:
            self.__images.append(tk.PhotoImage(file=path))
        return images

    def __play_col(self, col, report=True):
        """
        Make a move in a column
        :param col: The column's index
        :return: None
        """
        self.__update_msg(GUI.DEFAULT_MSG)
        self.__change_buttons_state(tk.DISABLED)
        player = self.__game.get_current_player()
        frame = self.__col_frames[col]
        if self.__game.get_current_player() == Game.PLAYER_ONE:
            new_img = self.__images[GUI.PLAYER1_CELL_IMG]
        else:
            new_img = self.__images[GUI.PLAYER2_CELL_IMG]
        self.__game.make_move(col)
        bottom = self.__bottoms[col] + 1
        if bottom == GUI.TOP:
            self.__buttons[col] = None
        for cell_index in range(bottom):
            cell = frame.grid_slaves(row=cell_index)[0]
            self.__disk_through_cell(cell, player)
        last_cell = frame.grid_slaves(row=bottom)[0]
        last_cell.configure(image=new_img)
        winner = self.__game.get_winner()
        if report:
            self.__communicator.send_message(col)
            if winner is None:
                self.__update_msg(GUI.HOLD_MSG % self.__opponent)
        if winner is not None:
            self.__handle_win(winner)

    def __update_msg(self, msg):
        """
        Update the message widget with a new message
        :param msg: A string
        :return: None
        """
        self.__msg_board.configure(text=msg)

    def __handle_win(self, winner):
        """
        Change the board to fit the end state of the game
        :param winner: An integer representing the winner of the game
        :return: None
        """
        self.__change_buttons_state(tk.DISABLED)
        self.__buttons = []
        if winner == Game.DRAW:
            self.__update_msg(GUI.DRAW)
            return
        elif winner == Game.PLAYER_ONE:
            msg = GUI.WIN % GUI.P1
            img = self.__images[GUI.PLAYER1_WIN_DISK]
        else:
            msg = GUI.WIN % GUI.P2
            img = self.__images[GUI.PLAYER2_WIN_DISK]
        for cell in self.__game.get_wining_streak():
            row, col = cell
            frame = self.__col_frames[col]
            cell_widget = frame.grid_slaves(row=row)[0]
            cell_widget.configure(image=img)
        self.__update_msg(msg)

    def __handle_message(self, move):
        """
        Specifies the event handler for the message getting event in the
        communicator. Makes a move when invoked
        :param move: A string representing a single move in the game
        :return: None
        """
        move = int(move)
        self.__play_col(move, report=False)
        if self.__ai is not None:
            self.__ai_play()
        else:
            self.__change_buttons_state(tk.NORMAL)

    def __ai_play(self):
        """
        Make a play with the ai
        :return: None
        """
        if self.__game.get_winner() is None:
            self.__ai.find_legal_move(self.__game, self.__play_col)

    def __change_buttons_state(self, state):
        """
        Change all relevant buttons' state
        :param state: Either normal or disabled
        :return: None
        """
        for button in self.__buttons:
            try:
                button.configure(state=state)
            except AttributeError:
                continue

    def __disk_through_cell(self, cell, player=None):
        """
        Animate a disk going through an empty cell
        :param cell: The cell
        :param player: The player whose disk is dropping
        :return: None
        """
        if player is not None:
            if player == Game.PLAYER_ONE:
                cell.configure(image=self.__images[GUI.PLAYER1_CELL_IMG])
            else:
                cell.configure(image=self.__images[GUI.PLAYER2_CELL_IMG])
            cell.update()
            cell.after(GUI.DROP_RATE, self.__disk_through_cell(cell))
        else:
            cell.configure(image=self.__images[GUI.EMPTY_CELL_IMG])
