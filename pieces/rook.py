from pieces.piece import Piece

class Rook(Piece):
    def __init__(self, team, position):
        self.team = team
        self.position = position
        self.moved = False

    def tostring(self):
        return 'Rook'

    def legal_moves(self, gameTiles):
        legalmoves = []
        x = self.position // 8
        y = self.position % 8

        # Only horizontal and vertical directions
        directions = [
            (1, 0), (-1, 0),  # vertical
            (0, 1), (0, -1)   # horizontal
        ]

        for dx, dy in directions:
            a, b = x + dx, y + dy
            while 0 <= a < 8 and 0 <= b < 8:
                target = gameTiles[a][b].pieceonTile
                if target.team is None:
                    legalmoves.append([a, b])
                elif target.team != self.team:
                    legalmoves.append([a, b])
                    break
                else:
                    break
                a += dx
                b += dy

        return legalmoves
