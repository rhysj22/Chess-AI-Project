from Moves.moves import Move
from Moves.castling import Castling
from GameState.gamestate_helpers import (
    checkForPinsAndChecks,
    getPawnMoves,
    getRookMoves,
    getKnightMoves,
    getBishopMoves,
    getQueenMoves,
    getKingMoves,
    getCastleMoves
)

class GameState:
    
    
    def __init__(self):
        """
        Initializes the complete state of a chess game, including the board layout,
        player turn tracking, move history, special move conditions (e.g., en passant, castling),
        and status flags like checkmate or stalemate.
        """

        # 8x8 board represented as a 2D list of strings.
        # Each string uses two characters:
        # - First character: 'w' (white) or 'b' (black)
        # - Second character: piece type: Rook, Knight, Bishop, Queen, King, or pawn
        # "--" represents an empty square.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],  # Black's back rank
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],  # Black pawns
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # Empty ranks
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],  # White pawns
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]   # White's back rank
        ]

        # Maps each piece type to its corresponding move-generating function.
        # This is used during move generation for efficient dispatch.
        self.moveFunctions = {
            "p": getPawnMoves,
            "R": getRookMoves,
            "N": getKnightMoves,
            "B": getBishopMoves,
            "Q": getQueenMoves,
            "K": getKingMoves
        }

        # Indicates whose turn it is to move.
        # True means it's White's turn; False means it's Black's.
        self.white_to_move = True

        # A list of all moves made so far, stored as Move objects.
        # Supports move history display, undoing moves, and game analysis.
        self.move_log = []

        # Track the current position of each king for fast access during checks.
        self.white_king_location = (7, 4)  # e1
        self.black_king_location = (0, 4)  # e8

        # Game-ending condition flags
        self.checkmate = False   # True if a player is in checkmate
        self.stalemate = False   # True if a player is in stalemate
        self.in_check = False    # True if the current player is in check

        # List of pin data (for pieces restricting king movement)
        # Each pin is represented as a dictionary with relevant info
        self.pins = []

        # List of check data (for pieces threatening the king)
        # Each check is represented as a dictionary
        self.checks = []

        # Tracks the square where an en passant capture is currently possible
        # Format: (row, col) or () if none
        self.enpassant_possible = ()

        # Keeps a log of all past en passant states to support undo
        self.enpassant_possible_log = [self.enpassant_possible]

        # Castling rights for both players (king-side and queen-side)
        self.current_castling_rights = Castling(
            wks=True,  # White king-side (e1 to g1)
            bks=True,  # Black king-side (e8 to g8)
            wqs=True,  # White queen-side (e1 to c1)
            bqs=True   # Black queen-side (e8 to c8)
        )

        # Keeps a log of castling rights after each move to support undo
        self.castle_rights_log = [
            Castling(
                self.current_castling_rights.wks,
                self.current_castling_rights.bks,
                self.current_castling_rights.wqs,
                self.current_castling_rights.bqs
            )
        ]

      
    def makeMove(self, move):
        """
        Executes a move on the board, updating the game state accordingly.
        
        Args:
            move (Move): A Move object containing the start and end coordinates, 
                        piece moved, captured piece, and special move flags.
        """

        # ---- 1. UPDATE BOARD POSITION ----

        # Remove the piece from its start square
        self.board[move.start_row][move.start_col] = "--"

        # Place the piece on the destination square
        self.board[move.end_row][move.end_col] = move.piece_moved

        # Record the move in the move history log
        self.move_log.append(move)

        # ---- 2. SWITCH PLAYER TURN ----

        # If it was white's move, switch to black and vice versa
        self.white_to_move = not self.white_to_move

        # ---- 3. UPDATE KING POSITION ----

        # If a king is moved, update its location for check detection
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)

        # ---- 4. HANDLE PAWN PROMOTION ----

        # Promote pawn to queen by default if it reaches the back rank
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"  # 'wQ' or 'bQ'

        # ---- 5. HANDLE EN PASSANT ----

        if move.is_enpassant_move:
            # Remove the captured pawn from the square behind the destination
            self.board[move.start_row][move.end_col] = "--"

        # ---- 6. UPDATE EN PASSANT POSSIBILITY ----

        # If a pawn moved two squares forward, enable en passant for the next turn
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            # Otherwise, clear the en passant possibility
            self.enpassant_possible = ()

        # Record current en passant state so it can be restored on undo
        self.enpassant_possible_log.append(self.enpassant_possible)

        # ---- 7. HANDLE CASTLING ----

        if move.is_castle_move:
            if move.end_col - move.start_col == 2:
                # King-side castling: move rook from h-file to f-file
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = "--"
            else:
                # Queen-side castling: move rook from a-file to d-file
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = "--"

        # ---- 8. UPDATE CASTLING RIGHTS ----

        # Update castling rights based on the move (e.g., if king or rook moved)
        self.updateCastling(move)

        # Record the new castling rights so they can be restored during undo
        self.castle_rights_log.append(
            Castling(
                self.current_castling_rights.wks,
                self.current_castling_rights.bks,
                self.current_castling_rights.wqs,
                self.current_castling_rights.bqs
            )
        )


    def undoMove(self):
        """
        Undoes the last move made, reverting the board and game state
        to the previous configuration.
        """
        if len(self.move_log) != 0:
            # ---- 1. REVERSE LAST MOVE ----

            # Remove the last move from the move log
            move = self.move_log.pop()

            # Move the piece back to its original square
            self.board[move.start_row][move.start_col] = move.piece_moved

            # Restore the captured piece, if any, to its square
            self.board[move.end_row][move.end_col] = move.piece_captured

            # ---- 2. SWITCH TURN BACK ----

            # Revert the player turn
            self.white_to_move = not self.white_to_move

            # ---- 3. RESTORE KING LOCATION ----

            # If a king was moved, update its stored location
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)

            # ---- 4. UNDO EN PASSANT MOVE ----

            if move.is_enpassant_move:
                # Remove the pawn placed on the destination square
                self.board[move.end_row][move.end_col] = "--"

                # Restore the captured pawn behind the destination square
                self.board[move.start_row][move.end_col] = move.piece_captured

            # ---- 5. UNDO PROMOTION ----

            if move.is_pawn_promotion:
                # Replace promoted queen with a pawn
                self.board[move.end_row][move.end_col] = move.piece_moved[0] + "p"

            # ---- 6. RESTORE CASTLING MOVE ----

            if move.is_castle_move:
                if move.end_col - move.start_col == 2:
                    # Undo king-side castling: move rook back from f-file to h-file
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = "--"
                else:
                    # Undo queen-side castling: move rook back from d-file to a-file
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = "--"

            # ---- 7. RESTORE EN PASSANT STATE ----

            # Remove the last recorded en passant square
            self.enpassant_possible_log.pop()

            # Restore the previous en passant state
            self.enpassant_possible = self.enpassant_possible_log[-1]

            # ---- 8. RESTORE CASTLING RIGHTS ----

            # Remove the last recorded castling rights
            self.castle_rights_log.pop()

            # Restore previous castling rights
            last_rights = self.castle_rights_log[-1]
            self.current_castling_rights = Castling(
                last_rights.wks,
                last_rights.bks,
                last_rights.wqs,
                last_rights.bqs
            )

            # ---- 9. CLEAR CHECK/STATUS FLAGS ----

            # Reset checkmate, stalemate, and check status
            self.checkmate = False
            self.stalemate = False
            self.in_check = False


    def updateCastling(self, move):
        """
        Updates the castling rights based on the piece moved or captured.

        Castling rights are permanently lost if:
        - A king is moved (removes both king-side and queen-side rights for that player).
        - A rook is moved from its original square.
        - A rook is captured on its original square.
        """

        # ---- 1. HANDLE ROOK CAPTURES ----

        # If a white rook was captured, check if it was one of the original rooks
        if move.piece_captured == "wR":
            if move.end_col == 0:  # Captured on a1: white queen-side rook
                self.current_castling_rights.wqs = False
            elif move.end_col == 7:  # Captured on h1: white king-side rook
                self.current_castling_rights.wks = False

        # If a black rook was captured, check if it was one of the original rooks
        elif move.piece_captured == "bR":
            if move.end_col == 0:  # Captured on a8: black queen-side rook
                self.current_castling_rights.bqs = False
            elif move.end_col == 7:  # Captured on h8: black king-side rook
                self.current_castling_rights.bks = False

        # ---- 2. HANDLE KING MOVES ----

        # If the white king is moved, both castling rights are lost
        if move.piece_moved == 'wK':
            self.current_castling_rights.wqs = False
            self.current_castling_rights.wks = False

        # If the black king is moved, both castling rights are lost
        elif move.piece_moved == 'bK':
            self.current_castling_rights.bqs = False
            self.current_castling_rights.bks = False

        # ---- 3. HANDLE ROOK MOVES ----

        # If a white rook moves from its original square, remove the relevant right
        elif move.piece_moved == 'wR':
            if move.start_row == 7:  # White back rank
                if move.start_col == 0:  # a1 rook (queen-side)
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:  # h1 rook (king-side)
                    self.current_castling_rights.wks = False

        # If a black rook moves from its original square, remove the relevant right
        elif move.piece_moved == 'bR':
            if move.start_row == 0:  # Black back rank
                if move.start_col == 0:  # a8 rook (queen-side)
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:  # h8 rook (king-side)
                    self.current_castling_rights.bks = False


    def getValidMoves(self):
        """
        Generates all valid (legal) moves for the current player, taking into account:
        - Checks (single or double)
        - Pins (pieces that cannot legally move without exposing the king)
        - Castling availability

        Returns:
            list: A list of Move objects that are legal to play.
        """

        # ---- 1. SAVE CURRENT CASTLING RIGHTS ----
        # Temporarily store current castling rights so we can restore them later
        temp_castle_rights = Castling(
            self.current_castling_rights.wks,
            self.current_castling_rights.bks,
            self.current_castling_rights.wqs,
            self.current_castling_rights.bqs
        )

        moves = []  # Will store valid moves to return

        # ---- 2. DETERMINE CHECK AND PIN STATUS ----
        # Analyze the board to update whether the king is in check, and identify any pins/checks
        self.in_check, self.pins, self.checks = checkForPinsAndChecks(self)

        # Get the current player's king location
        king_row, king_col = (
            self.white_king_location if self.white_to_move else self.black_king_location
        )

        # ---- 3. HANDLE CASE: KING IS IN CHECK ----
        if self.in_check:
            if len(self.checks) == 1:
                # SINGLE CHECK: Can escape by moving king, blocking the attack, or capturing the attacker
                moves = self.getAllPossibleMoves()

                # Extract attacker information
                check = self.checks[0]
                check_row, check_col = check[0], check[1]
                piece_checking = self.board[check_row][check_col]

                valid_squares = []  # Squares that can block or capture the checking piece

                if piece_checking[1] == "N":
                    # Knights cannot be blocked — only capturing the knight or moving king is allowed
                    valid_squares = [(check_row, check_col)]
                else:
                    # For sliding pieces (R, B, Q), add the squares between the attacker and the king
                    for i in range(1, 8):
                        valid_square = (
                            king_row + check[2] * i,
                            king_col + check[3] * i
                        )
                        valid_squares.append(valid_square)
                        if valid_square == (check_row, check_col):  # Stop at the attacker
                            break

                # Filter out any moves that don't move the king or block/capture the attacker
                for i in range(len(moves) - 1, -1, -1):  # Reverse iteration for safe removal
                    if moves[i].piece_moved[1] != "K":
                        if (moves[i].end_row, moves[i].end_col) not in valid_squares:
                            moves.remove(moves[i])

            else:
                # DOUBLE CHECK: Only valid move is to move the king
                moves = []
                getKingMoves(self, king_row, king_col, moves)

        else:
            # ---- 4. HANDLE CASE: NOT IN CHECK ----

            # Generate all pseudo-legal moves and then filter them through pin logic
            moves = self.getAllPossibleMoves()

            # Check if castling is available and legal, and add it to the move list
            if self.white_to_move:
                getCastleMoves(self, self.white_king_location[0], self.white_king_location[1], moves)
            else:
                getCastleMoves(self, self.black_king_location[0], self.black_king_location[1], moves)

        # ---- 5. CHECK FOR CHECKMATE OR STALEMATE ----

        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
                self.stalemate = False
            else:
                self.stalemate = True
                self.checkmate = False
        else:
            self.checkmate = False
            self.stalemate = False

        # ---- 6. RESTORE CASTLING RIGHTS ----
        # This is important because some pseudo-moves simulate actual play and may affect castling rights.
        self.current_castling_rights = temp_castle_rights

        return moves  # Return the final filtered list of legal moves


    def inCheck(self):
        """
        Determines if the current player's king is in check (i.e., under direct attack).

        Returns:
            bool: True if the king is under attack, False otherwise.
        """
        if self.white_to_move:
            # Check if the white king's square is attacked
            return self.squareUnderAttack(self.white_king_location[0], self.white_king_location[1])
        else:
            # Check if the black king's square is attacked
            return self.squareUnderAttack(self.black_king_location[0], self.black_king_location[1])


    def squareUnderAttack(self, row, col):
        """
        Determines if a given square is under attack by the opponent's pieces.

        Args:
            row (int): Row index of the square to evaluate.
            col (int): Column index of the square to evaluate.

        Returns:
            bool: True if any opposing move targets this square, False otherwise.
        """

        # Temporarily switch turns to simulate the opponent's perspective.
        self.white_to_move = not self.white_to_move

        # Generate all possible moves for the opponent.
        # These moves include pseudo-legal moves that don’t consider self-check.
        opponents_moves = self.getAllPossibleMoves()

        # Revert turn to the current player.
        self.white_to_move = not self.white_to_move

        # Check if any move by the opponent targets the specified (row, col).
        for move in opponents_moves:
            if move.end_row == row and move.end_col == col:
                return True  # The square is under attack

        return False  # No moves attack the square


    def getAllPossibleMoves(self):
        """
        Generates all *pseudo-legal* moves for the current player.
        These moves do NOT consider whether the king is left in check as a result.
        (Filtering for legality happens in getValidMoves.)

        Returns:
            list: A list of Move objects that represent all possible actions
                for the current player, ignoring checks.
        """
        moves = []  # List to accumulate generated moves

        # Loop over every square on the 8x8 board
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.board[row][col]  # Get the piece at the current square

                if piece != "--":  # Ignore empty squares
                    color = piece[0]  # 'w' for white, 'b' for black

                    # Only generate moves for the current player's pieces
                    if (color == "w" and self.white_to_move) or (color == "b" and not self.white_to_move):
                        piece_type = piece[1]  # e.g., 'p', 'R', 'N', 'B', 'Q', 'K'

                        # Use the moveFunctions dictionary to dispatch to the correct generator
                        self.moveFunctions[piece_type](self, row, col, moves)

        return moves  # Return the complete list of pseudo-legal moves