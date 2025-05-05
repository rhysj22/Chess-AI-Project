class Castling:
    def __init__(self, wks, bks, wqs, bqs):
        """
        Initializes castling rights for both white and black players.

        Args:
            wks (bool): White kingside castling right (True if allowed)
            bks (bool): Black kingside castling right
            wqs (bool): White queenside castling right
            bqs (bool): Black queenside castling right

        These flags track whether castling is legally available during the game,
        and are updated whenever a king or rook moves (or is captured).
        """
        self.wks = wks  # White King-Side castling (e.g., white king from e1 to g1, rook from h1 to f1)
        self.bks = bks  # Black King-Side castling (e.g., black king from e8 to g8, rook from h8 to f8)
        self.wqs = wqs  # White Queen-Side castling (e.g., white king from e1 to c1, rook from a1 to d1)
        self.bqs = bqs  # Black Queen-Side castling (e.g., black king from e8 to c8, rook from a8 to d8)
