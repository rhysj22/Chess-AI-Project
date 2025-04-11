import pygame
import math
import copy

from gameboard.board import Board
from gameboard.specialmoves import Move
from pieces.nullpiece import nullpiece
from pieces.queen import Queen
from pieces.rook import Rook
from pieces.knight import Knight
from pieces.bishop import Bishop
from AI.ai import AI

# Constants
WIDTH, HEIGHT = 800, 800
TILE_SIZE = WIDTH // 8
FPS = 60

# Pygame Setup
pygame.init()
display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyChess")
clock = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 32)

# Colors
WHITE_TILE = (143, 155, 175)
BLACK_TILE = (66, 134, 244)
GREEN = (0, 255, 0)
BLUE = (0, 0, 128)

# Game Objects
chessBoard = Board()
chessBoard.create_board()
movex = Move()
ai = AI()
allTiles = []
allpieces = []

def render_text(text, pos, color=GREEN, bg=BLUE):
    surf = font.render(text, True, color, bg)
    rect = surf.get_rect(center=pos)
    return surf, rect

def show_start_menu():
    ai_text, ai_rect = render_text("AI", (200, 350))
    pvp_text, pvp_rect = render_text("2 Player", (600, 350))
    title_text, title_rect = render_text("PyChess", (400, 100))
    credit_text, credit_rect = render_text("Made by: Rhys Jones", (400, 700), GREEN)

    while True:
        display.fill((0, 0, 0))
        display.blit(title_text, title_rect)
        display.blit(ai_text, ai_rect)
        display.blit(pvp_text, pvp_rect)
        display.blit(credit_text, credit_rect)

        pygame.draw.rect(display, BLACK_TILE, [100, 300, 200, 100])
        pygame.draw.rect(display, BLACK_TILE, [500, 300, 200, 100])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 100 <= x <= 300 and 300 <= y <= 400:
                    return "ai"
                elif 500 <= x <= 700 and 300 <= y <= 400:
                    return "2 player"

        pygame.display.update()
        clock.tick(FPS)

def draw_tile(x, y, color):
    pygame.draw.rect(display, color, [x, y, TILE_SIZE, TILE_SIZE])
    allTiles.append([color, [x, y, TILE_SIZE, TILE_SIZE]])

def draw_board_and_pieces():
    allpieces.clear()
    ypos = 0
    for row in range(8):
        xpos = 0
        color_toggle = row % 2
        for col in range(8):
            color = WHITE_TILE if color_toggle % 2 == 0 else BLACK_TILE
            draw_tile(xpos, ypos, color)

            piece = chessBoard.gameTiles[row][col].pieceonTile
            if piece.tostring() != "-":
                img = pygame.image.load(f"./images/{piece.team.lower()}_{piece.tostring().lower()}.png")
                img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                allpieces.append([img, [xpos, ypos], piece])

            xpos += TILE_SIZE
            color_toggle += 1
        ypos += TILE_SIZE

    for img_data in allpieces:
        display.blit(img_data[0], img_data[1])

def update_piece_position(x, y):
    return x * 8 + y

def get_tile_color(x, y):
    return WHITE_TILE if (x + y) % 2 == 0 else BLACK_TILE

def run_two_player_mode():
    running = True
    turn = 0
    selected = None
    legal_moves = []
    enpassant = []
    promotion = False
    promote_data = []

    while running:
        display.fill((0, 0, 0))
        draw_board_and_pieces()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                x = mx // TILE_SIZE
                y = my // TILE_SIZE
                piece = chessBoard.gameTiles[y][x].pieceonTile
                color = 'White' if turn % 2 == 0 else 'Black'
                opponent = 'Black' if color == 'White' else 'White'
                king_symbol = 'k' if color == 'White' else 'K'

                if promotion and promote_data:
                    handle_promotion_click(x, y, promote_data)
                    promotion = False
                    promote_data = []
                    continue

                if selected and [y, x] in legal_moves:
                    # Move the piece
                    orig_y, orig_x = selected
                    moving_piece = chessBoard.gameTiles[orig_y][orig_x].pieceonTile

                    # Handle castling
                    if moving_piece.tostring().lower() == 'k' and abs(x - orig_x) == 2:
                        rook_from = 7 if x > orig_x else 0
                        rook_to = orig_x + 1 if x > orig_x else orig_x - 1
                        rook = chessBoard.gameTiles[orig_y][rook_from].pieceonTile
                        chessBoard.gameTiles[orig_y][rook_to].pieceonTile = rook
                        chessBoard.gameTiles[orig_y][rook_from].pieceonTile = nullpiece()
                        rook.position = update_piece_position(orig_y, rook_to)

                    # Handle en passant capture
                    if moving_piece.tostring().lower() == 'p' and chessBoard.gameTiles[y][x].pieceonTile.tostring() == '-':
                        if x != orig_x:
                            cap_y = y + 1 if color == 'Black' else y - 1
                            chessBoard.gameTiles[cap_y][x].pieceonTile = nullpiece()

                    # Handle pawn double-step
                    if moving_piece.tostring() == 'P' and y - orig_y == 2:
                        moving_piece.en_passant = True
                        enpassant = [y, x]
                    elif moving_piece.tostring() == 'p' and orig_y - y == 2:
                        moving_piece.en_passant = True
                        enpassant = [y, x]
                    elif enpassant:
                        chessBoard.gameTiles[enpassant[0]][enpassant[1]].pieceonTile.en_passant = False
                        enpassant = []

                    # Handle promotion
                    if movex.is_promotion(moving_piece, y):
                        promotion = True
                        promote_data = [x, y, moving_piece.team]
                        continue

                    # Perform move
                    chessBoard.gameTiles[y][x].pieceonTile = moving_piece
                    chessBoard.gameTiles[orig_y][orig_x].pieceonTile = nullpiece()
                    moving_piece.position = update_piece_position(y, x)
                    moving_piece.moved = True

                    selected = None
                    legal_moves = []
                    turn += 1
                    continue

                if piece.tostring() != '-' and piece.team == color:
                    moves = piece.legal_moves(chessBoard.gameTiles)

                    # Add castling
                    for option in movex.castling(chessBoard.gameTiles, color):
                        if option == 'ks':
                            moves.append([y, 6])
                        elif option == 'qs':
                            moves.append([y, 2])

                    # Add en passant
                    ep = movex.en_passant(chessBoard.gameTiles, y, x)
                    if ep:
                        dy = 1 if color == 'Black' else -1
                        moves.append([y + dy, x + 1] if ep[1] == 'r' else [y + dy, x - 1])

                    # Filter pinned moves
                    moves = movex.filter_pinned_moves(chessBoard.gameTiles, moves, y, x, color)
                    legal_moves = [m for m in moves]
                    selected = [y, x]

        # Highlight legal moves
        if legal_moves:
            red = pygame.transform.scale(pygame.image.load("./images/Red_Dot.png"), (TILE_SIZE, TILE_SIZE))
            for move in legal_moves:
                display.blit(red, [move[1] * TILE_SIZE, move[0] * TILE_SIZE])

        for img_data in allpieces:
            display.blit(img_data[0], img_data[1])

        pygame.display.update()
        clock.tick(FPS)

def handle_promotion_click(x, y, promote_data):
    px, py, team = promote_data
    pos = update_piece_position(py, px)

    if team == 'White':
        chessBoard.gameTiles[py][px].pieceonTile = Queen('White', pos)
    else:
        chessBoard.gameTiles[py][px].pieceonTile = Queen('Black', pos)

def run_ai_mode():
    running = True
    turn = 0
    selected = None
    legal_moves = []
    enpassant = []
    promotion = False
    promote_data = []

    while running:
        display.fill((0, 0, 0))
        draw_board_and_pieces()

        if turn % 2 == 1 and not promotion:
            sc = copy.deepcopy(chessBoard.gameTiles)
            y, x, fy, fx = ai.evaluate(sc)
            m, n = fx, fy
            moving_piece = chessBoard.gameTiles[y][x].pieceonTile

            # Perform en passant cleanup
            if enpassant:
                chessBoard.gameTiles[enpassant[0]][enpassant[1]].pieceonTile.en_passant = False
                enpassant = []

            # Castling
            if moving_piece.tostring() == 'K' and abs(m - x) == 2:
                rook_from = 7 if m > x else 0
                rook_to = x + 1 if m > x else x - 1
                rook = chessBoard.gameTiles[y][rook_from].pieceonTile
                chessBoard.gameTiles[y][rook_to].pieceonTile = rook
                chessBoard.gameTiles[y][rook_from].pieceonTile = nullpiece()
                rook.position = update_piece_position(y, rook_to)

            # En passant capture
            if moving_piece.tostring() == 'P' and chessBoard.gameTiles[n][m].pieceonTile.tostring() == '-' and m != x:
                chessBoard.gameTiles[y][m].pieceonTile = nullpiece()

            # En passant flag
            if moving_piece.tostring() == 'P' and n - y == 2:
                moving_piece.en_passant = True
                enpassant = [n, m]

            if movex.is_promotion(moving_piece, n):
                chessBoard.gameTiles[y][x].pieceonTile = nullpiece()
                chessBoard.gameTiles[n][m].pieceonTile = Queen('Black', update_piece_position(n, m))
            else:
                chessBoard.gameTiles[n][m].pieceonTile = moving_piece
                chessBoard.gameTiles[y][x].pieceonTile = nullpiece()
                moving_piece.position = update_piece_position(n, m)
                moving_piece.moved = True

            turn += 1
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                x = mx // TILE_SIZE
                y = my // TILE_SIZE
                piece = chessBoard.gameTiles[y][x].pieceonTile

                if promotion and promote_data:
                    handle_promotion_click(x, y, promote_data)
                    promotion = False
                    promote_data = []
                    continue

                if selected and [y, x] in legal_moves:
                    orig_y, orig_x = selected
                    moving_piece = chessBoard.gameTiles[orig_y][orig_x].pieceonTile

                    # Castling
                    if moving_piece.tostring().lower() == 'k' and abs(x - orig_x) == 2:
                        rook_from = 7 if x > orig_x else 0
                        rook_to = orig_x + 1 if x > orig_x else orig_x - 1
                        rook = chessBoard.gameTiles[orig_y][rook_from].pieceonTile
                        chessBoard.gameTiles[orig_y][rook_to].pieceonTile = rook
                        chessBoard.gameTiles[orig_y][rook_from].pieceonTile = nullpiece()
                        rook.position = update_piece_position(orig_y, rook_to)

                    # En passant
                    if moving_piece.tostring().lower() == 'p' and chessBoard.gameTiles[y][x].pieceonTile.tostring() == '-':
                        if x != orig_x:
                            cap_y = y + 1 if moving_piece.team == 'Black' else y - 1
                            chessBoard.gameTiles[cap_y][x].pieceonTile = nullpiece()

                    # Set en passant
                    if moving_piece.tostring() == 'p' and orig_y - y == 2:
                        moving_piece.en_passant = True
                        enpassant = [y, x]
                    elif enpassant:
                        chessBoard.gameTiles[enpassant[0]][enpassant[1]].pieceonTile.en_passant = False
                        enpassant = []

                    # Promotion
                    if movex.is_promotion(moving_piece, y):
                        promotion = True
                        promote_data = [x, y, moving_piece.team]
                        continue

                    chessBoard.gameTiles[y][x].pieceonTile = moving_piece
                    chessBoard.gameTiles[orig_y][orig_x].pieceonTile = nullpiece()
                    moving_piece.position = update_piece_position(y, x)
                    moving_piece.moved = True
                    selected = None
                    legal_moves = []
                    turn += 1
                    continue

                if piece.tostring() != '-' and piece.team == 'White':
                    moves = piece.legal_moves(chessBoard.gameTiles)

                    # Add castling
                    for option in movex.castling(chessBoard.gameTiles, 'White'):
                        if option == 'ks':
                            moves.append([7, 6])
                        elif option == 'qs':
                            moves.append([7, 2])

                    # Add en passant
                    ep = movex.en_passant(chessBoard.gameTiles, y, x)
                    if ep:
                        dy = -1
                        moves.append([y + dy, x + 1] if ep[1] == 'r' else [y + dy, x - 1])

                    # Filter pinned
                    moves = movex.filter_pinned_moves(chessBoard.gameTiles, moves, y, x, 'White')
                    legal_moves = [m for m in moves]
                    selected = [y, x]

        # Highlight legal moves
        if legal_moves:
            red = pygame.transform.scale(pygame.image.load("./images/red_dot.png"), (TILE_SIZE, TILE_SIZE))
            for move in legal_moves:
                display.blit(red, [move[1] * TILE_SIZE, move[0] * TILE_SIZE])

        for img_data in allpieces:
            display.blit(img_data[0], img_data[1])

        pygame.display.update()
        clock.tick(FPS)

def show_endgame(message):
    text, rect = render_text(message, (400, 400))
    while True:
        display.fill((0, 0, 0))
        display.blit(text, rect)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

def main():
    mode = show_start_menu()
    if mode == "2 player":
        run_two_player_mode()
    else:
        run_ai_mode()

if __name__ == "__main__":
    main()
