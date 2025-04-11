from pieces.piece import Piece
    
    
""" King Piece"""
class King(Piece):
    
    def __init__(self, team, position):
        self.team = team
        self.position = position
        self.isMoved = False
    
    def legal_moves(self, game_tiles):
        legalmoves = []
        
        x = self.position // 8
        y = self.position % 8
        
        # Possible moves
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),         (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        
        for dx, dy in directions:
            new_x = x + dx
            new_y = y + dy
            
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                target_piece = game_tiles[new_x][new_y].pieceonTile
                
                # Check if the target tile is empty or occupied by an opponent's piece
                if target_piece.team != self.team:
                    legalmoves.append([new_x, new_y])
                    
        return legalmoves
        
        
    def tostring(self):
        return "King"
