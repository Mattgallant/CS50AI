import unittest
import tictactoe as ttt


class TestTictactoe(unittest.TestCase):

    # Tests when the board is empty, should return 0
    def test_player1(self):
        board = ttt.initial_state()
        self.assertEqual("X", ttt.player(board))

    def test_player2(self):
        board = ttt.initial_state()
        board[0][0] = "X"
        self.assertEqual("O", ttt.player(board))
