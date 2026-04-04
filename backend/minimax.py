import math

def check_win(board, mark):
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]] == mark:
            return True
    return False

def evaluate(board):
    """
    Heuristic evaluation function.
    Positive score is good for AI ('O'), negative is good for human ('X').
    """
    score = 0
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for condition in win_conditions:
        line = [board[i] for i in condition]
        o_count = line.count('O')
        x_count = line.count('X')
        empty_count = line.count('')
        
        if o_count == 2 and empty_count == 1:
            score += 10
        elif x_count == 2 and empty_count == 1:
            score -= 10
        elif o_count == 1 and empty_count == 2:
            score += 1
        elif x_count == 1 and empty_count == 2:
            score -= 1
            
    if board[4] == 'O':
        score += 3
    elif board[4] == 'X':
        score -= 3
        
    return score

def get_possible_moves(board):
    return [i for i, spot in enumerate(board) if spot == '']

def simulate_move(board, moves_queue, pending_removal, index, mark):
    new_board = list(board)
    new_queue = list(moves_queue)
    
    # 1. Remove pending first (start of turn)
    if pending_removal is not None:
        new_board[pending_removal] = ''
    
    # 2. Place new
    new_board[index] = mark
    new_queue.append(index)
    
    # 3. Check win (with potentially 4 on board)
    if check_win(new_board, mark):
        return new_board, new_queue, None, True
        
    # 4. If no win, flag oldest for NEXT turn
    new_pending = None
    if len(new_queue) > 3:
        new_pending = new_queue.pop(0)
        
    return new_board, new_queue, new_pending, False

def minimax(board, ai_moves, player_moves, pending_ai, pending_player, depth, alpha, beta, is_maximizing):
    if depth == 0:
        return evaluate(board)
        
    possible_moves = get_possible_moves(board)
    if not possible_moves:
        return 0
        
    if is_maximizing:
        best_score = -math.inf
        for move in possible_moves:
            # AI turn starts: remove pending_ai
            new_board, new_ai_moves, new_pending_ai, is_win = simulate_move(board, ai_moves, pending_ai, move, 'O')
            if is_win:
                return 100 + depth
            
            score = minimax(new_board, new_ai_moves, player_moves, new_pending_ai, pending_player, depth - 1, alpha, beta, False)
            best_score = max(score, best_score)
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        return best_score
    else:
        best_score = math.inf
        for move in possible_moves:
            # Player turn starts: remove pending_player
            new_board, new_player_moves, new_pending_player, is_win = simulate_move(board, player_moves, pending_player, move, 'X')
            if is_win:
                return -100 - depth
            
            score = minimax(new_board, ai_moves, new_player_moves, pending_ai, new_pending_player, depth - 1, alpha, beta, True)
            best_score = min(score, best_score)
            beta = min(beta, score)
            if beta <= alpha:
                break
        return best_score

def get_best_move(board, ai_moves, player_moves, pending_ai=None, pending_player=None, max_depth=6):
    best_score = -math.inf
    best_move = None
    alpha = -math.inf
    beta = math.inf
    
    possible_moves = get_possible_moves(board)
    
    if len(possible_moves) == 9: 
        return 4
    
    for move in possible_moves:
        new_board, new_ai_moves, new_pending_ai, is_win = simulate_move(board, ai_moves, pending_ai, move, 'O')
        if is_win:
            return move
        
        score = minimax(new_board, new_ai_moves, player_moves, new_pending_ai, pending_player, max_depth - 1, alpha, beta, False)
        
        if score > best_score:
            best_score = score
            best_move = move
            
        alpha = max(alpha, score)
        
    return best_move if best_move is not None else possible_moves[0]
