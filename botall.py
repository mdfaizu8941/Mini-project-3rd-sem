import chess
import chess.engine
import pygame
import random

# Load piece images
piece_images = {}
piece_symbols = {'P': 'wp', 'N': 'wn', 'B': 'wb', 'R': 'wr', 'Q': 'wq', 'K': 'wk',
                 'p': 'bp', 'n': 'bn', 'b': 'bb', 'r': 'br', 'q': 'bq', 'k': 'bk'}

def load_images():
    """Load chess piece images."""
    for symbol, name in piece_symbols.items():
        piece_images[symbol] = pygame.transform.scale(
            pygame.image.load(f'images/{name}.png'), (75, 75))

# Piece values for evaluation
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 2000
}

# Piece-square tables to improve positional play
PIECE_SQUARE_TABLES = {
    chess.PAWN: [
         0,   5,  10,  50,  50,  10,   5,   0,
         5,  10,  20,  35,  35,  20,  10,   5,
         0,   5,  10,  25,  25,  10,   5,   0,
         0,   0,   5,  20,  20,   5,   0,   0,
         0,   0,   0,  15,  15,   0,   0,   0,
         0,  -5,   0,   5,   5,   0,  -5,   0,
         0, -10,  -5,   0,   0,  -5, -10,   0,
         0,   0,   0,   0,   0,   0,   0,   0
    ],
    chess.KNIGHT: [-50, -40, -30, -30, -30, -30, -40, -50,
                   -40, -20, 0, 5, 5, 0, -20, -40,
                   -30, 5, 10, 15, 15, 10, 5, -30,
                   -30, 0, 15, 20, 20, 15, 0, -30,
                   -30, 5, 15, 20, 20, 15, 5, -30,
                   -30, 0, 10, 15, 15, 10, 0, -30,
                   -40, -20, 0, 0, 0, 0, -20, -40,
                   -50, -40, -30, -30, -30, -30, -40, -50],
    chess.BISHOP: [-20, -10, -10, -10, -10, -10, -10, -20,
                   -10, 5, 0, 0, 0, 0, 5, -10,
                   -10, 10, 10, 10, 10, 10, 10, -10,
                   -10, 0, 10, 10, 10, 10, 0, -10,
                   -10, 5, 5, 10, 10, 5, 5, -10,
                   -10, 0, 5, 10, 10, 5, 0, -10,
                   -10, 0, 0, 0, 0, 0, 0, -10,
                   -20, -10, -10, -10, -10, -10, -10, -20],
    chess.ROOK: [0, 0, 5, 10, 10, 5, 0, 0,
                 -5, 0, 0, 0, 0, 0, 0, -5,
                 -5, 0, 0, 0, 0, 0, 0, -5,
                 -5, 0, 0, 0, 0, 0, 0, -5,
                 -5, 0, 0, 0, 0, 0, 0, -5,
                 -5, 0, 0, 0, 0, 0, 0, -5,
                 5, 10, 10, 10, 10, 10, 10, 5,
                 0, 0, 5, 10, 10, 5, 0, 0],
    chess.QUEEN: [-20, -10, -10, -5, -5, -10, -10, -20,
                  -10, 0, 5, 0, 0, 0, 0, -10,
                  -10, 5, 5, 5, 5, 5, 0, -10,
                  0, 0, 5, 5, 5, 5, 0, -5,
                  -5, 0, 5, 5, 5, 5, 0, -5,
                  -10, 0, 5, 5, 5, 5, 0, -10,
                  -10, 0, 0, 0, 0, 0, 0, -10,
                  -20, -10, -10, -5, -5, -10, -10, -20],
    chess.KING: [20, 30, 10, 0, 0, 10, 30, 20,
                 20, 20, 0, 0, 0, 0, 20, 20,
                 -10, -20, -20, -20, -20, -20, -20, -10,
                 -20, -30, -30, -40, -40, -30, -30, -20,
                 -30, -40, -40, -50, -50, -40, -40, -30,
                 -30, -40, -40, -50, -50, -40, -40, -30,
                 -30, -40, -40, -50, -50, -40, -40, -30,
                 -30, -40, -40, -50, -50, -40, -40, -30]
}


def evaluate_board(board):
    """Evaluate board position considering piece values, mobility, and threats."""
    if board.is_checkmate():
        return float('-inf') if board.turn == chess.WHITE else float('inf')
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    
    evaluation = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES.get(piece.piece_type, 0)
            position_value = PIECE_SQUARE_TABLES[piece.piece_type][square] if piece.piece_type in PIECE_SQUARE_TABLES else 0
            if board.is_attacked_by(not piece.color, square):
                value -= value // 2  # Penalize attacked pieces
            evaluation += (value + position_value) if piece.color == chess.WHITE else -(value + position_value)
    
    return evaluation

def order_moves(board):
    """Order moves to improve pruning efficiency, prioritizing captures and checks."""
    def move_value(move):
        if board.is_capture(move):
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            if victim:
                # Ensure king's value does not affect move ordering incorrectly
                if victim.piece_type == chess.KING:
                    return float('inf')  # Prioritize checkmates but avoid assigning an explicit value
                if attacker:
                    return PIECE_VALUES[victim.piece_type] - PIECE_VALUES.get(attacker.piece_type, 0)
        return 0

    
    moves = list(board.legal_moves)
    return sorted(moves, key=lambda move: (board.gives_check(move), move_value(move)), reverse=True)

def principal_variation_search(board, depth, alpha, beta, maximizing_player):
    """Refined Minimax with Alpha-Beta Pruning using Principal Variation Search."""
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    
    first_move = True
    for move in order_moves(board):
        board.push(move)
        if first_move:
            eval = -principal_variation_search(board, depth - 1, -beta, -alpha, not maximizing_player)
            first_move = False
        else:
            eval = -principal_variation_search(board, depth - 1, -alpha - 1, -alpha, not maximizing_player)
            if alpha < eval < beta:
                eval = -principal_variation_search(board, depth - 1, -beta, -alpha, not maximizing_player)
        board.pop()
        
        alpha = max(alpha, eval)
        if alpha >= beta:
            break  # Prune
    
    return alpha

def find_best_move(board, depth):
    """Finds the best move for the bot using Principal Variation Search."""
    best_move = None
    max_eval = float('-inf')
    
    for move in order_moves(board):
        board.push(move)
        eval = -principal_variation_search(board, depth - 1, float('-inf'), float('inf'), False)
        board.pop()
        if eval > max_eval:
            max_eval = eval
            best_move = move
    
    return best_move

def initialize_ui():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Chess Bot")
    load_images()
    return screen

def draw_board(screen, board):
    """Draws the chessboard and pieces."""
    colors = [pygame.Color("khaki"), pygame.Color("brown")]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col * 75, row * 75, 75, 75))
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row, col = divmod(square, 8)
            screen.blit(piece_images[piece.symbol()], (col * 75, (7 - row) * 75))

def get_square_from_mouse(pos):
    x, y = pos
    col = x // 75
    row = 7 - (y // 75)
    return chess.square(col, row)

def main():
    screen = initialize_ui()
    board = chess.Board()
    selected_square = None
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                square = get_square_from_mouse(event.pos)
                if selected_square is None:
                    if board.piece_at(square) and board.color_at(square) == chess.WHITE:
                        selected_square = square
                else:
                    move = chess.Move(selected_square, square)
                    if move in board.legal_moves:
                        board.push(move)
                        bot_move = find_best_move(board, 3)
                        if bot_move:
                            board.push(bot_move)
                    selected_square = None
        draw_board(screen, board)
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
