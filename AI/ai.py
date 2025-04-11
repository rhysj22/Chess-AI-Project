
import random
import copy

from gameboard.specialmoves import Move
from pieces.nullpiece import nullpiece

class AI:
    def __init__(self, depth=3):
        self.depth = depth
        self.movex = Move()

    def evaluate_board(self, gametiles):
        piece_values = {
            'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 1000,
            'p': -1, 'n': -3, 'b': -3, 'r': -5, 'q': -9, 'k': -1000
        }
        score = 0
        for row in gametiles:
            for tile in row:
                symbol = tile.pieceonTile.tostring()
                score += piece_values.get(symbol, 0)
        return score

    def generate_all_moves(self, gametiles, color):
        moves = []
        for y in range(8):
            for x in range(8):
                piece = gametiles[y][x].pieceonTile
                if piece.team == color:
                    legal = piece.legal_moves(gametiles)
                    legal = self.movex.filter_pinned_moves(gametiles, legal, y, x, color)
                    for move in legal:
                        moves.append((y, x, move[0], move[1]))
        return moves

    def minimax(self, gametiles, depth, alpha, beta, maximizing):
        if depth == 0:
            return self.evaluate_board(gametiles), None

        color = 'Black' if maximizing else 'White'
        best_move = None
        moves = self.generate_all_moves(gametiles, color)

        if maximizing:
            max_eval = -float('inf')
            for move in moves:
                temp_tiles = copy.deepcopy(gametiles)
                self.make_move(temp_tiles, *move)
                eval, _ = self.minimax(temp_tiles, depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves:
                temp_tiles = copy.deepcopy(gametiles)
                self.make_move(temp_tiles, *move)
                eval, _ = self.minimax(temp_tiles, depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def make_move(self, gametiles, y, x, to_y, to_x):
        piece = gametiles[y][x].pieceonTile
        gametiles[to_y][to_x].pieceonTile = piece
        gametiles[y][x].pieceonTile = nullpiece()
        gametiles[to_y][to_x].pieceonTile.position = self.movex.update_position(to_y, to_x)

    def evaluate(self, gametiles):
        _, move = self.minimax(gametiles, self.depth, -float('inf'), float('inf'), True)
        return move if move else (0, 0, 0, 0)