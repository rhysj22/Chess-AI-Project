# Chess AI Project for Intro to AI Miniproject

## Project Description
 This project is designed to implement a standard chess game.
 When launched, the user will have the option to play with another person or with 
 an artifical intelligence bot. 

### AI Engine Details
This AI uses a minimiax algorithm with alpha beta pruning.
This is intended to maximize its own outcome and minimize the
user's outcome based on a given board layout. 

## Launch Instructions
1. ensure pygame is installed. If not:
    - pip install pygame

2. Run main.py



## Current Issues/Tasks
1. Game is not terminated.
    When a player puts their opponent in checkmate,
    no indication of checkmate is made. Also, the player can
    take their opponents' king and continue.

2. AI does not work properly. 
    After the Ai makes its first move. It will continually
    move one of its rooks back and forth.


3. Improvement to the UI.
    I think the UI is a bit elementary.
    I would ideally like an improvement to the UI
    That makes it look a little more professional.
    - Animates piece moves
    - Tracks previous move