from pieces.piece import Piece
import math

""" Pawn Piece"""
class Pawn(Piece):
    
    ## Establish the team and position of the piece
    def __init__(self, team, position):
        self.team = team
        self.position = position
        self.en_passant = False
    
    def legal_moves(self, game_tiles):
        legalmoves = []
        x = self.position // 8
        y = self.position % 8
        
        ## Get the piece on the tile
        piece = game_tiles[x][y].pieceonTile
        direction = 1 if piece.team == 'Black' else -1
        opponent = 'White' if piece.team == 'Black' else 'Black'
        ## Check if the piece is on the tile
        def is_empty(x, y):
            return game_tiles[x][y].pieceonTile.tostring() == '-'
        ## Check if the piece is an opponent
        def is_opponent_piece(x, y):
            return game_tiles[x][y].pieceonTile.team == opponent

        # Single forward move
        if 0 <= x + direction < 8 and is_empty(x + direction, y):
            legalmoves.append([x + direction, y])

            # Double move from initial position
            start_row = 1 if piece.team == 'Black' else 6
            if x == start_row and is_empty(x + 2 * direction, y):
                legalmoves.append([x + 2 * direction, y])

        # Capture diagonally
        for dy in [-1, 1]:
            new_x, new_y = x + direction, y + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                if is_opponent_piece(new_x, new_y):
                    legalmoves.append([new_x, new_y])

        return legalmoves

    def tostring(self):
        return "Pawn"
        

