"""
Main file.
Handling user input.
Displaying current GameStatus.
"""
import pygame as p
from GameState.gamestate import GameState
from Moves.moves import Move
import AI.chessai as ChessAI
import sys
from multiprocessing import Process, Queue

# Constants for GUI dimensions
BOARD_WIDTH = BOARD_HEIGHT = 512  # Chess board will be 512x512 pixels
MOVE_LOG_PANEL_WIDTH = 250  # Width of the move log panel next to the board
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT  # Same height as the board
DIMENSION = 8  # The chess board is 8x8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION  # Size of each square on the board
MAX_FPS = 15  # Limits the frame rate for animations
IMAGES = {}  # Dictionary to store piece images for fast access during drawing



def loadImages():
    """
    Initialize a global directory of images.
    This will be called exactly once in the main.
    Loads and scales piece images from the 'images/' folder.
    """
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ',  # White pieces
              'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']  # Black pieces
    for piece in pieces:
        # Load and scale each piece image to the square size
        IMAGES[piece] = p.transform.scale(
            p.image.load("Images/" + piece + ".png"),
            (SQUARE_SIZE, SQUARE_SIZE)
        )


def main():
    """
        Main driver for the program.
        This will handle user input and updating the graphics.
    """
    p.init()  # Initialize all pygame modules
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))  # Set up the display surface
    clock = p.time.Clock()  # For controlling the frame rate of the game loop
    screen.fill(p.Color("white"))  # Fill the screen with a white background

    game_state = GameState()  # Create the initial game state object
    valid_moves = game_state.getValidMoves()  # Get the list of valid moves at the start of the game
    move_made = False  # Track if a move has been made (used to trigger updates)
    animate = False  # Track whether the last move should be animated

    loadImages()  # Load all the chess piece images once before entering the game loop

    running = True  # Main game loop flag
    square_selected = ()  # Track the currently selected square (row, col)
    player_clicks = []  # List of player-selected squares to form a move

    game_over = False  # Flag to indicate if the game is over (checkmate or stalemate)
    ai_thinking = False  # Whether the AI is currently evaluating its move
    move_undone = False  # True if a move was undone (used to control AI flow)
    move_finder_process = None  # The process used for asynchronous AI move finding
    move_log_font = p.font.SysFont("Arial", 14, False, False)  # Font used for rendering the move log

    player_one = True  # True if human is playing white
    player_two = False  # True if human is playing black (otherwise AI)

    while running:
        # Determine if it's the human player's turn
        human_turn = (game_state.white_to_move and player_one) or (not game_state.white_to_move and player_two)

        # Handle all pygame events in the queue
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()

            # Handle mouse clicks
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # (x, y) coordinates of the mouse
                    col = location[0] // SQUARE_SIZE  # Determine clicked column
                    row = location[1] // SQUARE_SIZE  # Determine clicked row
                    # Deselect if same square clicked or click was on move log panel
                    if square_selected == (row, col) or col >= 8:
                        square_selected = ()
                        player_clicks = []
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)
                    # After second click, try to make a move
                    if len(player_clicks) == 2 and human_turn:
                        move = Move(player_clicks[0], player_clicks[1], game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.makeMove(valid_moves[i])
                                move_made = True
                                animate = True
                                square_selected = ()
                                player_clicks = []
                        if not move_made:
                            # Keep the last clicked square if the move was invalid
                            player_clicks = [square_selected]

            # Handle keyboard input
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    # Undo last move
                    game_state.undoMove()
                    move_made = True
                    animate = False
                    game_over = False
                    # Stop any AI processing
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True

                elif e.key == p.K_r:
                    # Reset the game
                    game_state = GameState()
                    valid_moves = game_state.getValidMoves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True

        # If it's the AI's turn and the game is ongoing
        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue()  # Queue for inter-process communication
                # Start a separate process for AI move computation
                move_finder_process = Process(
                    target=ChessAI.findBestMove,
                    args=(game_state, valid_moves, return_queue)
                )
                move_finder_process.start()

            # If AI process has finished
            if not move_finder_process.is_alive():
                ai_move = return_queue.get()  # Get the best move from the AI process
                if ai_move is None:
                    # Fallback to random move if AI fails
                    ai_move = ChessAI.findRandomMove(valid_moves)
                game_state.makeMove(ai_move)
                move_made = True
                animate = True
                ai_thinking = False

        # If a move was made (human or AI)
        if move_made:
            if animate:
                # Animate the most recent move
                animateMove(game_state.move_log[-1], screen, game_state.board, clock)
            valid_moves = game_state.getValidMoves()  # Refresh valid move list
            move_made = False
            animate = False
            move_undone = False

        # Redraw the board and pieces
        drawGameState(screen, game_state, valid_moves, square_selected)

        # Draw move log if the game is still running
        if not game_over:
            drawMoveLog(screen, game_state, move_log_font)

        # Check for checkmate and stalemate
        if game_state.checkmate:
            game_over = True
            if game_state.white_to_move:
                drawEndGameText(screen, "Black wins by checkmate")
            else:
                drawEndGameText(screen, "White wins by checkmate")

        elif game_state.stalemate:
            game_over = True
            drawEndGameText(screen, "Stalemate")

        # Cap the frame rate
        clock.tick(MAX_FPS)
        # Update the full display surface to the screen
        p.display.flip()


def drawGameState(screen, game_state, valid_moves, square_selected):
    """
    Responsible for rendering all graphical elements of the current game state.
    This includes the board squares, highlighting, and chess pieces.
    """
    drawBoard(screen)  # Step 1: Draw the base board grid (alternating colors)
    highlightSquares(screen, game_state, valid_moves, square_selected)  # Step 2: Highlight last move and selected piece
    drawPieces(screen, game_state.board)  # Step 3: Draw all the pieces on the board


def drawBoard(screen):
    """
    Draw the 8x8 grid of alternating colored squares.
    The top-left square is always light-colored.
    """
    global colors
    colors = [p.Color("white"), p.Color("gray")]  # Define light and dark square colors
    for row in range(DIMENSION):  # Iterate through all rows
        for column in range(DIMENSION):  # Iterate through all columns
            # Alternate colors based on sum of row and column indices
            color = colors[(row + column) % 2]
            # Draw a rectangle at the appropriate screen position
            p.draw.rect(screen, color, p.Rect(
                column * SQUARE_SIZE,  # x-position
                row * SQUARE_SIZE,     # y-position
                SQUARE_SIZE, SQUARE_SIZE  # width and height
            ))


def highlightSquares(screen, game_state, valid_moves, square_selected):
    """
    Highlight important squares:
    - The destination square of the last move (green)
    - The currently selected piece's square (blue)
    - All valid moves for the selected piece (yellow)
    """
    # Highlight the last move made (if there is one)
    if len(game_state.move_log) > 0:
        last_move = game_state.move_log[-1]
        s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))  # Create a square-sized surface
        s.set_alpha(100)  # Set transparency: 100/255
        s.fill(p.Color('green'))  # Color it green for last move highlight
        screen.blit(s, (
            last_move.end_col * SQUARE_SIZE,
            last_move.end_row * SQUARE_SIZE
        ))  # Blit it onto the destination square

    # Highlight the square selected by the user (if any)
    if square_selected != ():
        row, col = square_selected
        # Ensure the selected square contains a piece of the current player's color
        if game_state.board[row][col][0] == ('w' if game_state.white_to_move else 'b'):
            # Highlight the selected square (blue)
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

            # Highlight valid destination squares for the selected piece (yellow)
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(s, (
                        move.end_col * SQUARE_SIZE,
                        move.end_row * SQUARE_SIZE
                    ))


def drawPieces(screen, board):
    """
    Draw all the chess pieces on the board using the current board state.
    Each piece is represented by a 2-character string (e.g., 'wK', 'bQ').
    '--' indicates an empty square.
    """
    for row in range(DIMENSION):  # Loop through all rows
        for column in range(DIMENSION):  # Loop through all columns
            piece = board[row][column]  # Get the piece at the current square
            if piece != "--":  # Skip empty squares
                # Draw the image of the piece onto the screen at the correct position
                screen.blit(IMAGES[piece], p.Rect(
                    column * SQUARE_SIZE,  # x-coordinate
                    row * SQUARE_SIZE,     # y-coordinate
                    SQUARE_SIZE, SQUARE_SIZE  # width and height of square
                ))

def drawMoveLog(screen, game_state, font):
    """
    Draws the move log panel to the right of the chess board.
    Each entry displays a pair of moves in algebraic notation, e.g., "1. e4 e5".
    """

    # Define a rectangle to represent the move log panel area
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)

    # Fill the move log background with black for contrast
    p.draw.rect(screen, p.Color('black'), move_log_rect)

    move_log = game_state.move_log  # Retrieve the list of all moves made so far

    move_texts = []  # Will hold formatted move strings like "1. e4 e5"

    # Iterate through the move log in pairs (white's move and then black's move)
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + " "  # Add move number and white's move
        if i + 1 < len(move_log):  # Check if black's move exists for this turn
            move_string += str(move_log[i + 1]) + "  "  # Append black's move
        move_texts.append(move_string)  # Add the formatted move string to the list

    # Layout settings for rendering the text
    moves_per_row = 3  # Number of full turn-pairs displayed per row
    padding = 5  # Horizontal padding from the left edge of the move log panel
    line_spacing = 2  # Vertical space between rows of text
    text_y = padding  # Initial vertical position for the first row

    # Render and draw the move log text in grouped rows
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        # Combine up to three move strings into one line of text
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]

        # Create a rendered text surface with the given font and white color
        text_object = font.render(text, True, p.Color('white'))

        # Determine the location to draw the text: offset from the move log panel
        text_location = move_log_rect.move(padding, text_y)

        # Draw the rendered text onto the screen
        screen.blit(text_object, text_location)

        # Move to the next vertical position for the following line of text
        text_y += text_object.get_height() + line_spacing



def drawEndGameText(screen, text):
    """
    Draws a centered end-of-game message (e.g., checkmate or stalemate) on the board.
    Displays a gray shadow with black foreground for readability.
    """
    # Create a font object: Helvetica, size 32, bold=True, italic=False
    font = p.font.SysFont("Helvetica", 32, True, False)

    # Render the text surface in gray (acts as a background shadow)
    text_object = font.render(text, False, p.Color("gray"))

    # Center the text on the board by calculating the offset
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH / 2 - text_object.get_width() / 2,
        BOARD_HEIGHT / 2 - text_object.get_height() / 2
    )

    # Blit (draw) the shadow text slightly offset for a 3D effect
    screen.blit(text_object, text_location)

    # Render the same text in black and blit it slightly offset to overlap the gray shadow
    text_object = font.render(text, False, p.Color('black'))
    screen.blit(text_object, text_location.move(2, 2))  # Offset gives a shadow-like visual



def animateMove(move, screen, board, clock):
    """
    Animates a piece moving from its starting square to its destination square.
    Smoothly interpolates the piece position over several frames for visual effect.
    """
    global colors

    # Calculate total row and column distance for the move
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col

    # How many frames to animate per square moved
    frames_per_square = 10

    # Total number of frames for the animation
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square

    # Animate the piece frame by frame
    for frame in range(frame_count + 1):
        # Interpolate current position between start and end squares
        row = move.start_row + d_row * frame / frame_count
        col = move.start_col + d_col * frame / frame_count

        # Redraw the entire board and pieces to ensure a clean frame
        drawBoard(screen)
        drawPieces(screen, board)

        # Erase the piece from the destination square to avoid duplication
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, end_square)

        # If a piece was captured on the destination square, redraw it (e.g., for en passant)
        if move.piece_captured != '--':
            if move.is_enpassant_move:
                # Adjust the row to show the captured pawn behind the destination square
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_col * SQUARE_SIZE, enpassant_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)

        # Draw the moving piece at its interpolated position
        screen.blit(IMAGES[move.piece_moved], p.Rect(
            col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE
        ))

        # Update the screen to show the current animation frame
        p.display.flip()

        # Delay to maintain 60 frames per second (smooth animation)
        clock.tick(60)



if __name__ == "__main__":
    main()