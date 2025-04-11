from pieces.piece import Piece

class Queen(Piece):
    def __init__(self, team, position):
        self.team = team
        self.position = position

    def tostring(self):
        return 'Queen'

    def legal_moves(self, gametiles):
        legalmoves = []
        x = self.position // 8
        y = self.position % 8

        # All 8 directions (bishop + rook)
        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),   # Rook directions
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # Bishop directions
        ]

        for dx, dy in directions:
            a, b = x + dx, y + dy
            while 0 <= a < 8 and 0 <= b < 8:
                target_piece = gametiles[a][b].pieceonTile
                if target_piece.team is None:
                    legalmoves.append([a, b])
                elif target_piece.team != self.team:
                    legalmoves.append([a, b])
                    break
                else:
                    break
                a += dx
                b += dy

        return legalmoves
