# Chess AI Project for Intro to AI Miniproject

## Project Description
 This project is designed to implement a standard chess game.
 The chess engine includes an integrated AI opponent that makes decisions using the **Negamax algorithm** with **alpha-beta pruning**, allowing it to efficiently explore the game tree and evaluate potential outcomes.


## Launch Instructions
1. ensure pygame is installed. If not:
    - pip install -r requirements.txt
   

2. Run main.py



## AI Overview

### How It Works

- **Negamax Algorithm**: A streamlined variant of Minimax that assumes both players play optimally. It simplifies the evaluation logic by flipping the sign of scores depending on which player's turn it is.
- **Alpha-Beta Pruning**: Optimizes the search by pruning branches that cannot affect the final decision, drastically reducing the number of positions evaluated.
- **Search Depth**: The engine searches 3 moves deep (i.e., 3 plies) to evaluate the best possible move. This can be adjusted for stronger or faster AI performance.

---

### Evaluation Heuristics

The AI evaluates each board state using a combination of tactical and positional strategies:

- **Material Value**: Each piece is assigned a standard point value (e.g., Queen = 9, Rook = 5).
- **Piece-Square Tables**: Each piece has a predefined table assigning bonus points for favorable positions (e.g., knights in the center, rooks on open files).
- **Mobility**: Positions with more legal moves are favored to encourage piece activity.
- **King Safety**: The AI rewards positions where pawns protect the king from direct attack.
- **Passed Pawns**: Pawns that have no opposing pawns ahead of them receive bonus points for their promotion potential.
- **Bishop Pair Bonus**: A player owning both bishops receives a small bonus, reflecting their long-term advantage.

---

### AI Modes

- **Best Move**: The AI runs a 3-ply deep search to determine the most promising move using the above heuristics.
- **Random Move**: As a fallback or for testing purposes, the AI can also select a move at random from the valid move list.

---

### Performance & Design Notes

- The AI runs in a **separate process** using Python’s `multiprocessing` module to ensure the main GUI remains responsive.
- While effective for casual play, the AI can be further improved with:
  - Iterative deepening
  - Move ordering heuristics
  - Quiescence search
  - Transposition tables

