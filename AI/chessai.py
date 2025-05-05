"""
This module defines an AI for selecting moves in a chess game using the negamax algorithm
with alpha-beta pruning. It also includes positional evaluation tables to guide the decision-making process.
"""

import random

# --- MATERIAL SCORES ---

# Assigns material value to each piece type (used in static evaluation).
# These values approximate the traditional chess piece valuations.
piece_score = {
    "K": 0,  # King is not scored directly since its loss ends the game.
    "Q": 9,  # Queen is most valuable
    "R": 5,  # Rook
    "B": 3,  # Bishop
    "N": 3,  # Knight
    "p": 1   # Pawn
}

# --- POSITIONAL SCORES (PIECE-SQUARE TABLES) ---

# These tables encourage good piece positioning.
# Higher values represent stronger control or tactical advantage for that square.
# Tables are flipped for black to maintain symmetry from white's perspective.

# Knight is most valuable in the center, less so on the edges.
knight_scores = [
    [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
    [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
    [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
    [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
    [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
    [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
    [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
    [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]
]

# Bishop prefers open diagonals and central influence.
bishop_scores = [
    [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
    [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
    [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
    [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
    [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
    [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
    [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
    [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]
]

# Rooks are best placed on open files and central ranks.
rook_scores = [
    [0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
    [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
    [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
    [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
    [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
    [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
    [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
    [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]
]

# Queen gains value from central control and flexibility.
queen_scores = [
    [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
    [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
    [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
    [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
    [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
    [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
    [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
    [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]
]

# Pawns are evaluated based on progression and structure.
pawn_scores = [
    [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],  # Rank 1 (Black side, white pawns start here)
    [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
    [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
    [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
    [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
    [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
    [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
    [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]   # Rank 8 (White side)
]

# Dictionary linking piece identifiers to their respective square score matrices.
# Black piece tables are vertically flipped versions of white ones.
piece_position_scores = {
    "wN": knight_scores,
    "bN": knight_scores[::-1],
    "wB": bishop_scores,
    "bB": bishop_scores[::-1],
    "wQ": queen_scores,
    "bQ": queen_scores[::-1],
    "wR": rook_scores,
    "bR": rook_scores[::-1],
    "wp": pawn_scores,
    "bp": pawn_scores[::-1]
}

# --- GAME EVALUATION CONSTANTS ---

CHECKMATE = 1000    # Arbitrarily high score to represent a winning state
STALEMATE = 0       # Neutral outcome
DEPTH = 3           # Search depth for the minimax (negamax) algorithm


def findBestMove(game_state, valid_moves, return_queue):
    """
    Initiates the search for the best move using the negamax algorithm with alpha-beta pruning.

    Args:
        game_state (GameState): The current state of the chess game.
        valid_moves (list): List of legal Move objects available to the current player.
        return_queue (Queue): A multiprocessing queue to return the selected best move.
    """
    global next_move
    next_move = None  # Reset best move storage

    # Randomize move order to add variability in equivalent evaluations
    random.shuffle(valid_moves)

    # Launch negamax recursive search
    findMoveNegaMaxAlphaBeta(
        game_state,
        valid_moves,
        DEPTH,
        -CHECKMATE, CHECKMATE,
        1 if game_state.white_to_move else -1
    )

    # Send the selected move back through the queue
    return_queue.put(next_move)


def findMoveNegaMaxAlphaBeta(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    """
    Recursive negamax algorithm with alpha-beta pruning to find the best possible move.
    
    Negamax simplifies minimax by using a single perspective (maximizing) and inverting scores
    for the opponent. Alpha-beta pruning skips branches that cannot influence the final result.

    Args:
        game_state (GameState): Current state of the board.
        valid_moves (list): List of valid moves from this position.
        depth (int): Current depth of search remaining.
        alpha (float): Alpha cutoff (best score guaranteed for maximizer).
        beta (float): Beta cutoff (best score guaranteed for minimizer).
        turn_multiplier (int): +1 for white’s turn, -1 for black’s turn.

    Returns:
        float: The evaluated score of the best position found at this level.
    """
    global next_move

    # --- Base Case: Reached maximum search depth ---
    if depth == 0:
        return turn_multiplier * scoreBoard(game_state)

    max_score = -CHECKMATE  # Initialize to lowest possible score

    # --- Explore each move ---
    for move in valid_moves:
        game_state.makeMove(move)

        # Get the next valid moves after making this move
        next_moves = game_state.getValidMoves()

        # Recursive call: negate score because perspective flips
        score = -findMoveNegaMaxAlphaBeta(
            game_state, next_moves, depth - 1,
            -beta, -alpha, -turn_multiplier
        )

        game_state.undoMove()  # Undo move to restore state

        # --- Update best score found ---
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move  # Only save move at root level

        # --- Alpha-Beta Pruning ---
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break  # Beta cutoff: opponent has a better option already

    return max_score


def scoreBoard(game_state):
    """
    Evaluates the current board state for the AI using multiple strategic heuristics:
    
    - Material value (standard piece worth)
    - Piece-square tables (positional value)
    - Mobility (number of legal moves)
    - King safety (nearby pawns)
    - Passed pawns (potential for promotion)
    - Bishop pair bonus (two bishops work well together)

    Returns:
        float: A total score — positive favors white, negative favors black.
    """

    # Checkmate: if current player is in checkmate, it's a loss
    if game_state.checkmate:
        return -CHECKMATE if game_state.white_to_move else CHECKMATE
    elif game_state.stalemate:
        return STALEMATE  # Neutral

    # --- MOBILITY HEURISTIC ---
    def mobility_score(color):
        """
        Calculates mobility by counting the number of legal moves available for the player.
        Each legal move contributes +0.1 to the score.
        """
        original_turn = game_state.white_to_move
        game_state.white_to_move = (color == 'w')
        moves = game_state.getValidMoves()
        game_state.white_to_move = original_turn  # Restore game state
        return len(moves) * 0.1

    # --- KING SAFETY HEURISTIC ---
    def king_safety_score(color):
        """
        Rewards positions where pawns are protecting the king.
        Each adjacent pawn directly in front of the king adds +0.2 to the score.
        """
        king_pos = game_state.white_king_location if color == 'w' else game_state.black_king_location
        row, col = king_pos
        score = 0
        pawn = 'wp' if color == 'w' else 'bp'
        direction = -1 if color == 'w' else 1  # Pawns protect in front
        for offset in [-1, 0, 1]:  # Left, front, right
            r = row + direction
            c = col + offset
            if 0 <= r < 8 and 0 <= c < 8 and game_state.board[r][c] == pawn:
                score += 0.2
        return score

    # --- PASSED PAWN HEURISTIC ---
    def is_passed_pawn(row, col, color):
        """
        Checks if the pawn has no opposing pawns in its file or adjacent files ahead of it.
        Passed pawns get a bonus due to promotion potential.
        """
        direction = -1 if color == 'w' else 1
        # Scan each square in front of the pawn in its file and adjacent files
        for r in range(row + direction, 8 if color == 'w' else -1, direction):
            for c in range(col - 1, col + 2):  # Same file, left, and right
                if 0 <= c < 8:
                    if game_state.board[r][c] == ('bp' if color == 'w' else 'wp'):
                        return False
        return True

    
    # --- BISHOP PAIR BONUS ---
    def bishop_pair_bonus(color):
        """
        Rewards having both bishops (light- and dark-squared) on the board.
        Having a bishop pair is generally stronger than bishop + knight.
        """
        count = 0
        for row in game_state.board:
            for piece in row:
                if piece == color + 'B':
                    count += 1
        return 0.3 if count >= 2 else 0

    # --- MAIN EVALUATION LOOP ---
    score = 0  # Overall evaluation score

    for row in range(8):
        for col in range(8):
            piece = game_state.board[row][col]
            if piece != "--":
                # --- Material Value ---
                piece_val = piece_score[piece[1]]

                # --- Positional Bonus ---
                position_bonus = 0
                if piece[1] != "K":  # King usually excluded from position tables
                    # Get piece-square bonus (handles flipped boards for black)
                    position_bonus = piece_position_scores.get(piece, [[0]*8]*8)[row][col]

                # --- Passed Pawn Bonus ---
                pawn_bonus = 0
                if piece[1] == 'p' and is_passed_pawn(row, col, piece[0]):
                    pawn_bonus = 0.5

                # --- Combine Heuristics ---
                if piece[0] == 'w':
                    score += piece_val + position_bonus + pawn_bonus
                else:
                    score -= piece_val + position_bonus + pawn_bonus

    # --- Aggregate Additional Heuristics ---
    score += mobility_score('w') - mobility_score('b')
    score += king_safety_score('w') - king_safety_score('b')
    score += bishop_pair_bonus('w') - bishop_pair_bonus('b')

    return score  # Final board score: >0 favors white, <0 favors black


def findRandomMove(valid_moves):
    """
    Selects a move at random from the list of valid moves.

    This function is used as a fallback in case no move is found through evaluation,
    or to introduce variety during development/testing.
    
    Args:
        valid_moves (list): All legal moves available from current position.
    
    Returns:
        Move: Randomly selected move object.
    """
    return random.choice(valid_moves)



# === AI Overview ===
# The AI implemented here uses the Negamax variant of Minimax, enhanced with Alpha-Beta pruning.
# Negamax is a search algorithm that simplifies the minimax process by leveraging symmetry.
# It assumes that the opponent will always play optimally, and it evaluates the game state from the perspective of the current player.

# The algorithm works as follows:
# - It recursively simulates future game states up to a fixed depth.
# - Alpha-beta pruning skips branches that won't influence the final decision, reducing computation.
# - Each board state is evaluated using material values and positional advantage heuristics.
# - Position tables reward center control, open files for rooks, advanced pawns, etc.
# - Depth is limited to 3 plies for performance, but this can be increased for stronger play.
# - The AI does not yet include move ordering or iterative deepening, which could further improve it.
