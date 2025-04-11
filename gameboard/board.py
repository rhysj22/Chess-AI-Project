from gameboard.tile import Tile
from pieces.nullpiece import nullpiece
from pieces.queen import Queen
from pieces.pawn import Pawn
from pieces.rook import Rook
from pieces.bishop import Bishop
from pieces.king import King
from pieces.knight import Knight

class Board:
    def __init__(self):
        self.gameTiles = [[Tile(row * 8 + col, nullpiece()) for col in range(8)] for row in range(8)]

    # Setup the board with pieces in standard starting positions
    def create_board(self):
        # Helper function to place major pieces
        def place_back_row(row, team):
            piece_classes = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
            for col, piece_class in enumerate(piece_classes):
                position = row * 8 + col
                self.gameTiles[row][col] = Tile(position, piece_class(team, position))

        # Helper function to place pawns
        def place_pawns(row, team):
            for col in range(8):
                position = row * 8 + col
                self.gameTiles[row][col] = Tile(position, Pawn(team, position))

        # Place black pieces
        place_back_row(0, "Black")
        place_pawns(1, "Black")

        # Place white pieces
        place_pawns(6, "White")
        place_back_row(7, "White")

    # Print the board in a readable format (one row per line)
    def print_board(self):
        for row in self.gameTiles:
            for tile in row:
                print('|', end=tile.pieceonTile.tostring())
            print("|")
