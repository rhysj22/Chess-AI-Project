from pieces.piece import Piece

class Knight(Piece):
    
    def __init__(self, team, position):
        self.team = team
        self.position = position

    def tostring(self):
        return "Knight"

    def legal_moves(self, gametiles):
        legalmoves = []
        x = self.position // 8
        y = self.position % 8

        # All possible knight moves (L-shape)
        move_offsets = [
            (-2, -1), (-2, +1),
            (-1, -2), (-1, +2),
            (+1, -2), (+1, +2),
            (+2, -1), (+2, +1),
        ]

        for dx, dy in move_offsets:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                target_piece = gametiles[new_x][new_y].pieceonTile
                if target_piece.team != self.team:
                    legalmoves.append([new_x, new_y])

        return legalmoves
