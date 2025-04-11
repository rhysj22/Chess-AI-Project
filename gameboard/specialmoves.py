from pieces.nullpiece import nullpiece

class Move:
    def __init__(self):
        pass

    def find_king(self, gametiles, symbol):
        for x in range(8):
            for y in range(8):
                if gametiles[x][y].pieceonTile.tostring() == symbol:
                    return x, y
        return -1, -1

    def is_checked(self, gametiles, king_symbol, opponent_color):
        king_x, king_y = self.find_king(gametiles, king_symbol)
        for x in range(8):
            for y in range(8):
                piece = gametiles[x][y].pieceonTile
                if piece.team == opponent_color:
                    moves = piece.legal_moves(gametiles)
                    for move in moves:
                        if move == [king_x, king_y]:
                            return ["checked", [x, y]]
        return ["notchecked"]

    def update_position(self, x, y):
        return x * 8 + y

    def legal_moves_under_check(self, gametiles, color):
        moves = []
        king_symbol = 'K' if color == 'Black' else 'k'
        opponent = 'White' if color == 'Black' else 'Black'

        for x in range(8):
            for y in range(8):
                piece = gametiles[x][y].pieceonTile
                if piece.team == color:
                    for move in piece.legal_moves(gametiles):
                        to_x, to_y = move
                        captured = gametiles[to_x][to_y].pieceonTile

                        gametiles[to_x][to_y].pieceonTile = piece
                        gametiles[x][y].pieceonTile = nullpiece()
                        gametiles[to_x][to_y].pieceonTile.position = self.update_position(to_x, to_y)

                        if self.is_checked(gametiles, king_symbol, opponent)[0] == "notchecked":
                            moves.append([x, y, to_x, to_y])

                        gametiles[x][y].pieceonTile = piece
                        gametiles[to_x][to_y].pieceonTile = captured
                        gametiles[x][y].pieceonTile.position = self.update_position(x, y)

        return moves

    def castling(self, gametiles, color):
        king_symbol = 'K' if color == 'Black' else 'k'
        rook_symbol = 'R' if color == 'Black' else 'r'
        row = 0 if color == 'Black' else 7
        result = []

        for col in range(8):
            if gametiles[row][col].pieceonTile.tostring() == king_symbol:
                king = gametiles[row][col].pieceonTile
                if not king.moved:
                    # Kingside
                    if (
                        gametiles[row][col + 3].pieceonTile.tostring() == rook_symbol and
                        not gametiles[row][col + 3].pieceonTile.moved and
                        all(gametiles[row][col + i].pieceonTile.tostring() == '-' for i in [1, 2])
                    ):
                        result.append('ks')

                    # Queenside
                    if (
                        gametiles[row][0].pieceonTile.tostring() == rook_symbol and
                        not gametiles[row][0].pieceonTile.moved and
                        all(gametiles[row][i].pieceonTile.tostring() == '-' for i in [1, 2, 3])
                    ):
                        result.append('qs')
                break
        return result

    def en_passant(self, gametiles, y, x):
        piece = gametiles[y][x].pieceonTile
        if piece.tostring().lower() != 'p':
            return []

        if piece.tostring() == 'P' and y == 4:
            if x + 1 < 8 and gametiles[y][x + 1].pieceonTile.tostring() == 'p' and gametiles[y][x + 1].pieceonTile.enpassant:
                return [[y, x], 'r']
            if x - 1 >= 0 and gametiles[y][x - 1].pieceonTile.tostring() == 'p' and gametiles[y][x - 1].pieceonTile.enpassant:
                return [[y, x], 'l']

        if piece.tostring() == 'p' and y == 3:
            if x + 1 < 8 and gametiles[y][x + 1].pieceonTile.tostring() == 'P' and gametiles[y][x + 1].pieceonTile.enpassant:
                return [[y, x], 'r']
            if x - 1 >= 0 and gametiles[y][x - 1].pieceonTile.tostring() == 'P' and gametiles[y][x - 1].pieceonTile.enpassant:
                return [[y, x], 'l']

        return []

    def filter_pinned_moves(self, gametiles, moves, y, x, color):
        legal_moves = []
        king_symbol = 'K' if color == 'Black' else 'k'
        opponent = 'White' if color == 'Black' else 'Black'
        moving_piece = gametiles[y][x].pieceonTile

        for move in moves:
            m, k = move
            captured = gametiles[m][k].pieceonTile

            gametiles[m][k].pieceonTile = moving_piece
            gametiles[y][x].pieceonTile = nullpiece()

            if self.is_checked(gametiles, king_symbol, opponent)[0] == "notchecked":
                legal_moves.append(move)

            gametiles[y][x].pieceonTile = moving_piece
            gametiles[m][k].pieceonTile = captured

        return legal_moves

    def is_promotion(self, piece, to_y):
        return (piece.tostring() == 'P' and to_y == 7) or (piece.tostring() == 'p' and to_y == 0)

    def is_stalemate(self, gametiles, color):
        opponent = 'White' if color == 'Black' else 'Black'
        king_symbol = 'K' if color == 'Black' else 'k'

        if self.is_checked(gametiles, king_symbol, opponent)[0] == "checked":
            return False

        for x in range(8):
            for y in range(8):
                piece = gametiles[x][y].pieceonTile
                if piece.team == color:
                    moves = piece.legal_moves(gametiles)
                    filtered = self.filter_pinned_moves(gametiles, moves, x, y, color)
                    if filtered:
                        return False
        return True

    def is_move_legal(self, gametiles, from_x, from_y, to_x, to_y, color):
        piece = gametiles[from_x][from_y].pieceonTile
        if piece.team != color:
            return False
        moves = piece.legal_moves(gametiles)
        legal = self.filter_pinned_moves(gametiles, moves, from_x, from_y, color)
        return [to_x, to_y] in legal
