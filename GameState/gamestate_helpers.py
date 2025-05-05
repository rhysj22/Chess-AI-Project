from Moves.moves import Move


def checkForPinsAndChecks(game_state):
    """
    Determines if the current player's king is in check and identifies any allied pieces
    that are pinned (i.e., cannot move without exposing the king to check).

    Returns:
        tuple:
            - in_check (bool): True if the king is under attack.
            - pins (list): Information about pinned allied pieces.
            - checks (list): Information about enemy pieces delivering check.

        Each element in `pins` and `checks` is a tuple:
            (row, col, direction_row, direction_col)
    """
    pins = []     # Holds info on pieces that are pinned and their direction
    checks = []   # Holds info on pieces giving check and their direction
    in_check = False  # Flag to indicate if the king is in check

    # Determine player color and locate king position
    if game_state.white_to_move:
        enemy_color = "b"
        ally_color = "w"
        start_row, start_col = game_state.white_king_location
    else:
        enemy_color = "w"
        ally_color = "b"
        start_row, start_col = game_state.black_king_location

    # All 8 directions from the king: vertical, horizontal, and diagonal
    directions = (
        (-1, 0), (0, -1), (1, 0), (0, 1),    # up, left, down, right
        (-1, -1), (-1, 1), (1, -1), (1, 1)   # diagonals: up-left, up-right, down-left, down-right
    )

    for j, direction in enumerate(directions):
        possible_pin = ()  # Track a candidate allied piece that might be pinned
        for i in range(1, 8):
            end_row = start_row + direction[0] * i
            end_col = start_col + direction[1] * i

            # Ensure the target square is on the board
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = game_state.board[end_row][end_col]

                if end_piece[0] == ally_color and end_piece[1] != "K":
                    # First allied piece in this direction — could be pinned
                    if possible_pin == ():
                        possible_pin = (end_row, end_col, direction[0], direction[1])
                    else:
                        # Second allied piece blocks the line — no pin or check possible in this direction
                        break

                elif end_piece[0] == enemy_color:
                    enemy_type = end_piece[1]

                    # Check if the enemy piece type can attack along this direction
                    is_rook_dir = 0 <= j <= 3
                    is_bishop_dir = 4 <= j <= 7
                    is_pawn_attack = (
                        i == 1 and enemy_type == "p" and
                        ((enemy_color == "w" and 6 <= j <= 7) or
                        (enemy_color == "b" and 4 <= j <= 5))
                    )
                    is_adjacent_king = (i == 1 and enemy_type == "K")

                    if (enemy_type == "Q") or \
                    (is_rook_dir and enemy_type == "R") or \
                    (is_bishop_dir and enemy_type == "B") or \
                    is_pawn_attack or is_adjacent_king:

                        if possible_pin == ():
                            # No blocking piece: it's a check
                            in_check = True
                            checks.append((end_row, end_col, direction[0], direction[1]))
                        else:
                            # One blocking allied piece: it's pinned
                            pins.append(possible_pin)
                        break  # No further processing in this direction

                    else:
                        # Enemy piece not relevant for check/pin in this direction
                        break
            else:
                # Out of bounds
                break

    # ---- HANDLE KNIGHT CHECKS SEPARATELY ----
    # Knights can jump over pieces, so direction-based scanning won't catch them
    knight_moves = (
        (-2, -1), (-2, 1), (-1, 2), (1, 2),
        (2, -1), (2, 1), (-1, -2), (1, -2)
    )

    for move in knight_moves:
        end_row = start_row + move[0]
        end_col = start_col + move[1]
        if 0 <= end_row < 8 and 0 <= end_col < 8:
            end_piece = game_state.board[end_row][end_col]
            if end_piece[0] == enemy_color and end_piece[1] == "N":
                # King is in check by a knight
                in_check = True
                checks.append((end_row, end_col, move[0], move[1]))

    return in_check, pins, checks


def getPawnMoves(game_state, row, col, moves):
    """
    Appends all valid pawn moves for a pawn at (row, col) to the `moves` list.
    Considers:
        - standard 1- and 2-square advances
        - diagonal captures
        - en passant
        - movement restrictions due to pins
    """
    # ---- 1. HANDLE PINS ----

    piece_pinned = False
    pin_direction = ()

    # Check if this pawn is pinned and store the direction if so
    for i in range(len(game_state.pins) - 1, -1, -1):
        if game_state.pins[i][0] == row and game_state.pins[i][1] == col:
            piece_pinned = True
            pin_direction = (game_state.pins[i][2], game_state.pins[i][3])
            game_state.pins.remove(game_state.pins[i])  # Remove the pin once processed
            break

    # ---- 2. DETERMINE DIRECTION, STARTING ROW, ENEMY COLOR ----

    if game_state.white_to_move:
        move_amount = -1             # White pawns move "up" the board
        start_row = 6
        enemy_color = "b"
        king_row, king_col = game_state.white_king_location
    else:
        move_amount = 1              # Black pawns move "down"
        start_row = 1
        enemy_color = "w"
        king_row, king_col = game_state.black_king_location

    # ---- 3. ONE-SQUARE FORWARD MOVE ----

    if game_state.board[row + move_amount][col] == "--":
        if not piece_pinned or pin_direction == (move_amount, 0):
            moves.append(Move((row, col), (row + move_amount, col), game_state.board))

            # ---- 4. TWO-SQUARE FORWARD MOVE ----
            if row == start_row and game_state.board[row + 2 * move_amount][col] == "--":
                moves.append(Move((row, col), (row + 2 * move_amount, col), game_state.board))

    # ---- 5. CAPTURE TO THE LEFT ----

    if col - 1 >= 0:
        if not piece_pinned or pin_direction == (move_amount, -1):
            if game_state.board[row + move_amount][col - 1][0] == enemy_color:
                moves.append(Move((row, col), (row + move_amount, col - 1), game_state.board))

            # ---- 6. EN PASSANT TO THE LEFT ----
            if (row + move_amount, col - 1) == game_state.enpassant_possible:
                attacking_piece = blocking_piece = False
                if king_row == row:
                    if king_col < col:
                        inside_range = range(king_col + 1, col - 1)
                        outside_range = range(col + 1, 8)
                    else:
                        inside_range = range(king_col - 1, col, -1)
                        outside_range = range(col - 2, -1, -1)

                    for i in inside_range:
                        if game_state.board[row][i] != "--":
                            blocking_piece = True
                    for i in outside_range:
                        square = game_state.board[row][i]
                        if square[0] == enemy_color and square[1] in ("R", "Q"):
                            attacking_piece = True
                        elif square != "--":
                            blocking_piece = True

                # Only allow en passant if it does not expose the king to attack
                if not attacking_piece or blocking_piece:
                    moves.append(Move((row, col), (row + move_amount, col - 1), game_state.board, is_enpassant_move=True))

    # ---- 7. CAPTURE TO THE RIGHT ----

    if col + 1 <= 7:
        if not piece_pinned or pin_direction == (move_amount, +1):
            if game_state.board[row + move_amount][col + 1][0] == enemy_color:
                moves.append(Move((row, col), (row + move_amount, col + 1), game_state.board))

            # ---- 8. EN PASSANT TO THE RIGHT ----
            if (row + move_amount, col + 1) == game_state.enpassant_possible:
                attacking_piece = blocking_piece = False
                if king_row == row:
                    if king_col < col:
                        inside_range = range(king_col + 1, col)
                        outside_range = range(col + 2, 8)
                    else:
                        inside_range = range(king_col - 1, col + 1, -1)
                        outside_range = range(col - 1, -1, -1)

                    for i in inside_range:
                        if game_state.board[row][i] != "--":
                            blocking_piece = True
                    for i in outside_range:
                        square = game_state.board[row][i]
                        if square[0] == enemy_color and square[1] in ("R", "Q"):
                            attacking_piece = True
                        elif square != "--":
                            blocking_piece = True

                if not attacking_piece or blocking_piece:
                    moves.append(Move((row, col), (row + move_amount, col + 1), game_state.board, is_enpassant_move=True))


def getRookMoves(game_state, row, col, moves):
    """
    Appends all legal rook moves from a given (row, col) to the `moves` list.

    Rooks can move any number of squares in straight lines: vertically or horizontally.
    This method also considers movement restrictions caused by pins.
    """

    # ---- 1. HANDLE PINS ----

    piece_pinned = False
    pin_direction = ()

    for i in range(len(game_state.pins) - 1, -1, -1):
        if game_state.pins[i][0] == row and game_state.pins[i][1] == col:
            piece_pinned = True
            pin_direction = (game_state.pins[i][2], game_state.pins[i][3])

            # If the piece is NOT a queen, we can remove the pin after processing the rook
            # (Queens may also move like bishops, so pin removal must wait in that case)
            if game_state.board[row][col][1] != "Q":
                game_state.pins.remove(game_state.pins[i])
            break

    # ---- 2. DEFINE ROOK MOVEMENT DIRECTIONS ----

    directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
    enemy_color = "b" if game_state.white_to_move else "w"  # Determine opposing color

    # ---- 3. GENERATE MOVES IN EACH DIRECTION ----

    for direction in directions:
        for i in range(1, 8):  # Rooks can move 1 to 7 squares in any direction
            end_row = row + direction[0] * i
            end_col = col + direction[1] * i

            # Stop if the move goes off the board
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:

                # Enforce pin restriction: rook can only move along the pin line
                if not piece_pinned or pin_direction == direction or pin_direction == (-direction[0], -direction[1]):

                    end_piece = game_state.board[end_row][end_col]

                    if end_piece == "--":
                        # Empty square — legal move
                        moves.append(Move((row, col), (end_row, end_col), game_state.board))
                    elif end_piece[0] == enemy_color:
                        # Enemy piece — capture is legal
                        moves.append(Move((row, col), (end_row, end_col), game_state.board))
                        break  # Stop searching this direction after a capture
                    else:
                        # Friendly piece — rook cannot move past or onto it
                        break

            else:
                # Move went out of bounds — stop checking this direction
                break


def getKnightMoves(game_state, row, col, moves):
    """
    Appends all valid knight moves from (row, col) to the `moves` list.
    Knight moves ignore board obstructions but are invalid if the knight is pinned.
    """
    piece_pinned = False

    # ---- 1. Check if this knight is pinned ----
    for i in range(len(game_state.pins) - 1, -1, -1):
        if game_state.pins[i][0] == row and game_state.pins[i][1] == col:
            piece_pinned = True  # Knights can't move if pinned
            game_state.pins.remove(game_state.pins[i])
            break

    # ---- 2. Define knight movement offsets ----
    knight_moves = (
        (-2, -1), (-2, 1), (-1, 2), (1, 2),
        (2, -1), (2, 1), (-1, -2), (1, -2)
    )

    ally_color = "w" if game_state.white_to_move else "b"  # Determine friendly color

    # ---- 3. Generate each potential move ----
    for move in knight_moves:
        end_row = row + move[0]
        end_col = col + move[1]

        # Make sure the target square is on the board
        if 0 <= end_row <= 7 and 0 <= end_col <= 7:
            if not piece_pinned:
                end_piece = game_state.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    # Move is valid if landing on empty or enemy square
                    moves.append(Move((row, col), (end_row, end_col), game_state.board))


def getBishopMoves(game_state, row, col, moves):
    """
    Appends all valid bishop moves from (row, col) to the `moves` list.
    Bishops move diagonally in all four directions, and movement is restricted by pins.
    """
    piece_pinned = False
    pin_direction = ()

    # ---- 1. Check for pin and determine valid movement direction ----
    for i in range(len(game_state.pins) - 1, -1, -1):
        if game_state.pins[i][0] == row and game_state.pins[i][1] == col:
            piece_pinned = True
            pin_direction = (game_state.pins[i][2], game_state.pins[i][3])
            game_state.pins.remove(game_state.pins[i])
            break

    # ---- 2. Define diagonal directions ----
    directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))  # Top-left, top-right, bottom-right, bottom-left
    enemy_color = "b" if game_state.white_to_move else "w"

    # ---- 3. Explore each direction ----
    for direction in directions:
        for i in range(1, 8):  # Bishops can move up to 7 squares in one direction
            end_row = row + direction[0] * i
            end_col = col + direction[1] * i

            # Check board boundaries
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                # Allow movement only along the pin line if pinned
                if not piece_pinned or pin_direction == direction or pin_direction == (-direction[0], -direction[1]):
                    end_piece = game_state.board[end_row][end_col]

                    if end_piece == "--":
                        moves.append(Move((row, col), (end_row, end_col), game_state.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((row, col), (end_row, end_col), game_state.board))
                        break  # Stop direction on capture
                    else:
                        break  # Stop if blocked by friendly piece
            else:
                break  # Direction goes off board


def getQueenMoves(game_state, row, col, moves):
    """
    Get all the queen moves for the queen located at row col and add the moves to the list.
    """
    getBishopMoves(game_state, row, col, moves) # Diagonal moves
    getRookMoves(game_state, row, col, moves) # Horizontal and vertical moves

def getKingMoves(game_state, row, col, moves):
    """
    Appends all valid king moves from (row, col) to the `moves` list.
    The king moves one square in any direction, but cannot move into check.
    """

    # ---- 1. Define the 8 possible king moves (row/col deltas) ----
    row_moves = (-1, -1, -1,  0, 0, 1, 1, 1)
    col_moves = (-1,  0,  1, -1, 1, -1, 0, 1)

    ally_color = "w" if game_state.white_to_move else "b"

    for i in range(8):
        end_row = row + row_moves[i]
        end_col = col + col_moves[i]

        # ---- 2. Skip off-board moves ----
        if 0 <= end_row <= 7 and 0 <= end_col <= 7:
            end_piece = game_state.board[end_row][end_col]

            # ---- 3. Skip moves to squares occupied by allied pieces ----
            if end_piece[0] != ally_color:

                # ---- 4. Temporarily move the king to simulate the position ----
                if ally_color == "w":
                    game_state.white_king_location = (end_row, end_col)
                else:
                    game_state.black_king_location = (end_row, end_col)

                # ---- 5. Check if the new king position is under attack ----
                in_check, pins, checks = checkForPinsAndChecks(game_state)

                if not in_check:
                    # Only allow the move if the king would not be in check
                    moves.append(Move((row, col), (end_row, end_col), game_state.board))

                # ---- 6. Restore king's original position ----
                if ally_color == "w":
                    game_state.white_king_location = (row, col)
                else:
                    game_state.black_king_location = (row, col)


def getCastleMoves(game_state, row, col, moves):
    """
    Appends all valid castling moves for the king at (row, col) to the move list.
    This includes both kingside and queenside castling if allowed by:
        - Castling rights
        - King not currently in check
        - Path not under attack
        - Squares between king and rook are unoccupied
    """
    if game_state.squareUnderAttack(row, col):
        return  # Cannot castle out of, through, or into check

    # ---- Kingside Castling Check ----
    if (game_state.white_to_move and game_state.current_castling_rights.wks) or \
    (not game_state.white_to_move and game_state.current_castling_rights.bks):
        getKingsideCastleMoves(game_state, row, col, moves)

    # ---- Queenside Castling Check ----
    if (game_state.white_to_move and game_state.current_castling_rights.wqs) or \
    (not game_state.white_to_move and game_state.current_castling_rights.bqs):
        getQueensideCastleMoves(game_state, row, col, moves)

def getKingsideCastleMoves(game_state, row, col, moves):
    """
    Appends a kingside castling move to `moves` if it is valid.
    Requires:
        - Squares between king and rook (f1, g1) or (f8, g8) are empty
        - Squares the king passes through are not under attack
    """
    if game_state.board[row][col + 1] == '--' and game_state.board[row][col + 2] == '--':
        if not game_state.squareUnderAttack(row, col + 1) and not game_state.squareUnderAttack(row, col + 2):
            # All conditions met: perform castling move
            moves.append(Move((row, col), (row, col + 2), game_state.board, is_castle_move=True))

            
def getQueensideCastleMoves(game_state, row, col, moves):
    """
    Appends a queenside castling move to `moves` if it is valid.
    Requires:
        - Squares between king and rook (d1, c1, b1) or (d8, c8, b8) are empty
        - Squares the king passes through are not under attack
    """
    if game_state.board[row][col - 1] == '--' and \
    game_state.board[row][col - 2] == '--' and \
    game_state.board[row][col - 3] == '--':
        if not game_state.squareUnderAttack(row, col - 1) and not game_state.squareUnderAttack(row, col - 2):
            # All conditions met: perform castling move
            moves.append(Move((row, col), (row, col - 2), game_state.board, is_castle_move=True))

