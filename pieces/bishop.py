from pieces.piece import Piece

"""Bishop Piece"""
class Bishop(Piece):
    
    def __init__(self, team, position):
        self.team = team
        self.position = position
        
    def legal_moves(self, game_tiles):
        legalmoves = []
        
        x = self.position // 8
        y = self.position % 8
        
        opponent = 'White' if self.team == 'Black' else 'Black'
        
        # Possible diagonal moves
        directions = [
            (-1, -1), (-1, 1),
            (1, -1), (1, 1)
        ]
        ## Find possible moves
        for dx, dy in directions:
            a, b = x + dx, y + dy
            while 0 <= a < 8 and 0 <= b < 8:
                target = game_tiles[a][b].pieceonTile
                if target.team is None:
                    legalmoves.append([a, b])
                elif target.team== opponent:
                    legalmoves.append([a, b])
                    break
                else:
                    break
                a += dx
                b += dy

        return legalmoves
    
    def tostring(self):
        return "Bishop"