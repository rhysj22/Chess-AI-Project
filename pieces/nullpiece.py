from pieces.piece import Piece


class nullpiece(Piece):
    
    def __init__(self):
        self.team = None

    def tostring(self):
        return "-"
