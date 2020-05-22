"""
Tic Tac Toe Player
"""
import copy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    playCount = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] != EMPTY:
                playCount += 1
    if (playCount % 2) == 1:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    i corresponds to the row of the move (0, 1, or 2)
    j corresponds to which cell in the row corresponds to the move (also 0, 1, or 2)
    """
    actionsSet = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                actionsSet.add((i, j))
    return actionsSet


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    board_copy = copy.deepcopy(board)
    move = player(board_copy)

    if board_copy[i][j] is not EMPTY:
        raise Exception("Invalid Move")
    else:
        board_copy[i][j] = move
    return board_copy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    if utility(board) == 1:
        return X
    elif utility(board) == -1:
        return O
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if utility(board) != 0:
        # This means the game has been won by one of the two players
        return True
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # Check horizontal wins
    for i in range(3):
        if board[i][0] == EMPTY:
            continue
        previous = board[i][0]
        for j in range(3):
            if previous != board[i][j]:
                break  # Go to next row
            if j == 2:
                if previous == X:
                    return 1
                else:
                    return -1

    # Check vertical wins
    for i in range(3):
        if board[0][i] == EMPTY:
            continue
        previous = board[0][i]
        for j in range(3):
            if previous != board[j][i]:
                break  # Go to next row
            if j == 2:
                if previous == X:
                    return 1
                else:
                    return -1

    if board[1][1] == EMPTY:
        return 0

    # Check positive diagonal wins
    if board[2][0] == board[1][1] == board[0][2]:
        if board[1][1] == X:
            return 1
        else:
            return -1

    # Check negative diagonal wins
    if board[0][0] == board[1][1] == board[2][2]:
        if board[1][1] == X:
            return 1
        else:
            return -1

    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    currentactions = actions(board)
    if player(board) == X:
        vT = -math.inf
        move = set()
        for action in currentactions:
            v = minvalue(result(board, action))
            if v > vT:
                vT = v
                move = action
    else:
        vT = math.inf
        move = set()
        for action in currentactions:
            v = maxvalue(result(board, action))
            if v < vT:
                vT = v
                move = action
    return move


def maxvalue(board):
    """
    Calculates the max value of a given board recursively together with minvalue
    """

    if terminal(board):
        return utility(board)

    v = -math.inf
    posactions = actions(board)

    for action in posactions:
        vret = minvalue(result(board, action))
        v = max(v, vret)

    return v


def minvalue(board):
    """
    Calculates the min value of a given board recursively together with maxvalue
    """

    if terminal(board): return utility(board)

    v = math.inf
    posactions = actions(board)

    for action in posactions:
        vret = maxvalue(result(board, action))
        v = min(v, vret)

    return v

'''def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    The move returned should be the optimal action (i, j) that is one of the allowable actions on the board. If multiple moves are equally optimal, any of those moves is acceptable.
    If the board is a terminal board, the minimax function should return None.
    """
    if terminal(board):
        return None

    moves_list = list()

    if player(board) == X:
        for action in actions(board):
            action_score = (max_value2(board, action), action)  # V value, action
            moves_list.append(action_score)
            v_list = [i[0] for i in moves_list]
            max_index = v_list.index(max(v_list))
            return moves_list[max_index][1]
    else:
        for action in actions(board):
            action_score = (min_value2(board, action), action)
            moves_list.append(action_score)
            v_list = [i[0] for i in moves_list]
            min_index = v_list.index(min(v_list))
            return moves_list[min_index][1]
    # Max picks action a in actions(s) that produces highest value of MIN_VALUE(Result(S,A))
    # Min picks action a in actions(s) that produces smallest value of MAX_VALUE(result(s,a))


def max_value2(board, action):
    if terminal(board):
        return utility(board)
    new_board = result(board, action)
    return minimax(board)


def min_value2(board, action):
    if terminal(board):
        return utility(board)
    new_board = result(board, action)
    return minimax(board)

def max_value(board):
    if terminal(board):
        return utility(board)
    v = -2  # Should suffice for "infinity" in this game
    for action in actions(board):
        new_v = max(v, min_value(result(board, action))[0])
        print("new_v: " + str(new_v) + " v: " + str(v))
        if new_v > v:
            v = new_v
            best_action = action
    return (v, best_action)


def min_value(board):
    if terminal(board):
        return utility(board)
    v = 2
    for action in actions(board):
        result_board = result(board, action)
        new_v = min(v, max_value(result_board)[0])
        print("new_v: " + str(new_v) + " v: " + str(v) + "Type of new_v: " + str(type(new_v)))
        if new_v <= v:
            v = new_v
            best_action = action
    return (v, best_action)'''


