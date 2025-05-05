class Move:
    # Dictionaries for converting between chess notation (e.g., 'e4') and board indices

    # Maps rank characters ('1'–'8') to row indices (used in 2D board representation)
    ranks_to_rows = {
        "1": 7, "2": 6, "3": 5, "4": 4,
        "5": 3, "6": 2, "7": 1, "8": 0
    }

    # Reverse mapping from row indices back to rank characters
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}

    # Maps file characters ('a'–'h') to column indices
    files_to_cols = {
        "a": 0, "b": 1, "c": 2, "d": 3,
        "e": 4, "f": 5, "g": 6, "h": 7
    }

    # Reverse mapping from column indices back to file characters
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board, is_enpassant_move=False, is_castle_move=False):
        """
        Creates a new Move object representing a single move in the game.

        Args:
            start_square (tuple): (row, col) of the starting square
            end_square (tuple): (row, col) of the ending square
            board (list of lists): current game board state
            is_enpassant_move (bool): whether this move is an en passant capture
            is_castle_move (bool): whether this move is a castling move
        """

        # Extract starting and ending positions
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]

        # Determine which piece is being moved
        self.piece_moved = board[self.start_row][self.start_col]

        # Determine which piece (if any) is being captured
        self.piece_captured = board[self.end_row][self.end_col]

        # Detect pawn promotion: a white pawn reaching row 0 or a black pawn reaching row 7
        self.is_pawn_promotion = (
            self.piece_moved == "wp" and self.end_row == 0
        ) or (
            self.piece_moved == "bp" and self.end_row == 7
        )

        # Handle en passant (special pawn capture)
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            # In en passant, the captured pawn is not located on the destination square
            self.piece_captured = "wp" if self.piece_moved == "bp" else "bp"

        # Handle castling move (king + rook move)
        self.is_castle_move = is_castle_move

        # Convenience flag for whether the move results in a capture
        self.is_capture = self.piece_captured != "--"

        # Generate a unique ID for this move based on its coordinates
        # This is used to compare moves and detect equivalency
        self.moveID = (
            self.start_row * 1000 +
            self.start_col * 100 +
            self.end_row * 10 +
            self.end_col
        )


    def __eq__(self, other):
        """
        Compares two Move objects.
        Two moves are considered equal if their moveIDs match.
        This allows '==' to work correctly between Move instances.
        """
        if isinstance(other, Move):
            return self.moveID == other.moveID  # Compare using unique move identifier
        return False  # Not equal if other object is not a Move


    def getChessNotation(self):
        """
        Returns the move in standard chess notation (e.g., e4, Nf3, Qxe7, 0-0).
        Handles special cases for:
        - pawn promotion
        - en passant captures
        - castling
        - piece captures and quiet moves
        """

        # Handle pawn promotion (assumes promotion to Queen)
        if self.is_pawn_promotion:
            return self.getRankFile(self.end_row, self.end_col) + "Q"

        # Handle castling (kingside and queenside)
        if self.is_castle_move:
            return "0-0-0" if self.end_col == 1 else "0-0"

        # Handle en passant capture
        if self.is_enpassant_move:
            return self.getRankFile(self.start_row, self.start_col)[0] + "x" + \
                self.getRankFile(self.end_row, self.end_col) + " e.p."

        # Handle standard captures
        if self.piece_captured != "--":
            if self.piece_moved[1] == "p":  # Pawn captures (e.g., exd5)
                return self.getRankFile(self.start_row, self.start_col)[0] + "x" + \
                    self.getRankFile(self.end_row, self.end_col)
            else:  # Non-pawn captures (e.g., Nxf3, Qxe7)
                return self.piece_moved[1] + "x" + self.getRankFile(self.end_row, self.end_col)

        # Handle quiet (non-capturing) moves
        if self.piece_moved[1] == "p":  # Pawn move
            return self.getRankFile(self.end_row, self.end_col)
        else:  # Piece move
            return self.piece_moved[1] + self.getRankFile(self.end_row, self.end_col)


    def getRankFile(self, row, col):
        """
        Converts board coordinates (row, col) to standard square notation (e.g., e4).
        Uses mapping dictionaries to convert row to rank and col to file.
        """
        return self.cols_to_files[col] + self.rows_to_ranks[row]


    def __str__(self):
        """
        Returns a human-readable string representation of the move.
        Useful for printing/debugging purposes.
        Examples: 'e4', 'Nf3', 'exd5', '0-0', '0-0-0'
        """

        # Handle castling explicitly
        if self.is_castle_move:
            return "0-0" if self.end_col == 6 else "0-0-0"

        # Get end square in standard notation
        end_square = self.getRankFile(self.end_row, self.end_col)

        # Pawn move handling
        if self.piece_moved[1] == "p":
            if self.is_capture:
                return self.cols_to_files[self.start_col] + "x" + end_square
            else:
                # Add 'Q' for promotion
                return end_square + "Q" if self.is_pawn_promotion else end_square

        # Non-pawn moves
        move_string = self.piece_moved[1]  # e.g., 'N' for knight, 'Q' for queen
        if self.is_capture:
            move_string += "x"
        return move_string + end_square

