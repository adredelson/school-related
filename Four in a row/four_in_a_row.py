import tkinter as tk
from gui import GUI
import sys


NUM_ARGUMENTS = 3
PLAYER_ARGUMENT = 1
PORT_ARGUMENT = 2
IP_ARGUMENT = 3
VALID_PLAYERS = ["human", "ai"]
ILLEGAL_ARGS = "Illegal program arguments"
MAX_PORT = 65535
P1 = "Player1"
P2 = "Player2"


def check_args(argv):
    """
    Check validity of received arguments
    :param argv: A list of arguments
    :return: True if the arguments are valid, False otherwise
    """
    if len(argv) < NUM_ARGUMENTS or NUM_ARGUMENTS + 1 < len(argv) or \
            MAX_PORT < int(argv[PORT_ARGUMENT]) or argv[PLAYER_ARGUMENT] not \
            in VALID_PLAYERS:
        print(ILLEGAL_ARGS)
        return False
    return True


if __name__ == '__main__':
    args = sys.argv
    if check_args(args):
        root = tk.Tk()
        args[PLAYER_ARGUMENT] = VALID_PLAYERS.index(args[PLAYER_ARGUMENT])
        args[PORT_ARGUMENT] = int(args[PORT_ARGUMENT])
        act_args = args[1:]
        if len(args) == NUM_ARGUMENTS:
            root.title(P1)
        else:
            root.title(P2)
        game = GUI(root, *act_args)
        root.mainloop()
