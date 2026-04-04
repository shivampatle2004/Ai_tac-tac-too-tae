import time

class GameEngine:
    def __init__(self, match_id, player_x, player_o):
        self.match_id = match_id
        self.player_x = player_x  # username of X
        self.player_o = player_o  # username of O, or 'AI'
        self.reset()

    def reset(self):
        self.board = [''] * 9
        self.player_moves_x = []
        self.player_moves_o = []
        self.pending_removal_x = None
        self.pending_removal_o = None
        self.current_turn = 'X'
        self.winner = None
        self.game_over = False
        self.last_move_time = time.time()

    def check_win(self, mark, board=None):
        if board is None:
            board = self.board
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for condition in win_conditions:
            if board[condition[0]] == board[condition[1]] == board[condition[2]] == mark:
                return True
        return False

    def make_move(self, index, requested_by_username):
        if self.game_over:
            return False, "Game is over", None
            
        if self.check_timeout():
            return False, "Timeout", None

        # Verify turn
        if self.current_turn == 'X' and requested_by_username != self.player_x:
            return False, "Not your turn", None
        if self.current_turn == 'O' and requested_by_username != self.player_o:
            return False, "Not your turn", None
            
        if index < 0 or index > 8 or self.board[index] != '':
            return False, "Invalid location", None

        mark = self.current_turn
        moves_queue = self.player_moves_x if mark == 'X' else self.player_moves_o
        
        # --- NEW DEFERRED REMOVAL LOGIC ---
        # 1. Remove the pending piece at the START of the turn
        removed_index = None
        if mark == 'X' and self.pending_removal_x is not None:
            removed_index = self.pending_removal_x
            self.board[removed_index] = ''
            self.pending_removal_x = None
        elif mark == 'O' and self.pending_removal_o is not None:
            removed_index = self.pending_removal_o
            self.board[removed_index] = ''
            self.pending_removal_o = None

        # 2. Place the new mark
        self.board[index] = mark
        moves_queue.append(index)
        
        # 3. Check for win (with potentially 4 marks on board during this turn)
        if self.check_win(mark):
            self.winner = mark
            self.game_over = True
            return True, "Win", removed_index
            
        # 4. If no win, check if we need to flag the oldest for next turn removal
        if len(moves_queue) > 3:
            oldest = moves_queue.pop(0)
            if mark == 'X':
                self.pending_removal_x = oldest
            else:
                self.pending_removal_o = oldest
            
        self.current_turn = 'O' if mark == 'X' else 'X'
        self.last_move_time = time.time()
        
        return True, "Success", removed_index

    def check_timeout(self):
        # 10s turn constraint + 2s buffer network latency 
        if not self.game_over and (time.time() - self.last_move_time) > 12:
            self.game_over = True
            self.winner = 'O' if self.current_turn == 'X' else 'X'
            self.winner += " (by timeout)"
            return True
        return False

    def get_state(self):
        return {
            'match_id': self.match_id,
            'player_x': self.player_x,
            'player_o': self.player_o,
            'board': self.board,
            'current_turn': self.current_turn,
            'winner': self.winner,
            'game_over': self.game_over,
            'move_count': len(self.player_moves_x) + len(self.player_moves_o),
            'time_left': max(0, int(11 - (time.time() - self.last_move_time))),
            'moves_x': self.player_moves_x,
            'moves_o': self.player_moves_o,
            'pending_removal_x': self.pending_removal_x,
            'pending_removal_o': self.pending_removal_o,
            'next_to_remove': {
                'X': self.pending_removal_x,
                'O': self.pending_removal_o
            }
        }
