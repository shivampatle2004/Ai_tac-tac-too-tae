# Application Flow

## The Game Loop
1. **Initialize Game**: Client fetches `/api/state` on load.
2. **Move Submission**: Player clicks a cell. Client optimistically updates UI, blocking further input, and POSTs to `/api/move`.
3. **Backend Validation**: Flask receives move. `game_engine` verifies turn and cell validity.
4. **Moving Window Execution (Player)**: 
   - Move is placed.
   - Win condition verified.
   - If player queue > 3, oldest is removed.
5. **AI Turn Trigger**: If no win, control transfers to AI.
6. **AI Decision**: Minimax calculates optimal position.
7. **Moving Window Execution (AI)**:
   - AI move placed.
   - Win condition verified.
   - If AI queue > 3, oldest is removed.
8. **State Return**: Updated board state securely sent back to client.

## Removal Logic
Tracked using two simple FIFO Queues (lists in Python), one for `X` and one for `O`.
