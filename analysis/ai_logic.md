# AI Logic & Minimax

## Algorithm
The AI uses the **Minimax Algorithm**, which simulates potential future game states to maximize its own winning chances while minimizing the human player's chances.

## Alpha-Beta Pruning
Injected into the Minimax recursive tree to cut off branches that are mathematically proven to be sub-optimal, greatly reducing computational overhead.

## The Moving Window Complexity
Because moves are removed, the game tree is technically infinite (cyclic). A standard Minimax would crash via recursion limit or out-of-memory.
Solution: **Depth Limited Search**. The algorithm stops calculating at depth = 6.

## Evaluation Function
Since the tree is cut at depth 6, most branches won't reach a natural terminal state. We use a heuristic evaluation function:
- Scours the board for "2 in a row" alignments.
- Awards `+10` for AI 2-in-a-row strings.
- Penalizes `-10` for Player 2-in-a-row strings.
- Values the center slot slightly higher (`+3`).
