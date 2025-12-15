# Duck-Escape
# Strategy Game

A turn-based strategy puzzle game built with **Python** and **Pygame**, where the player’s goal is to **trap a duck inside a grid** before it escapes through the edges.

The duck uses **A\* pathfinding** to intelligently search for the shortest escape route, while the player strategically places blocks to stop it.

---
## Game Overview

- The game is played on a **grid-based board**
- The **duck starts near the center**
- The **edges of the board are escape goals**
- The player and the duck take turns
- The duck automatically moves toward the nearest open edge

### Win Conditions
- **Player Wins:** If all paths to the board edges are blocked  
- **Duck Wins:** If the duck reaches any open edge cell

---

## Gameplay Mechanics

### Player Turn
- Click on an empty cell to place a **player block**
- Player blocks prevent the duck from moving through that cell

### Duck Turn
- The duck calculates the **shortest path to the nearest open edge**
- Uses **A\* algorithm** to decide the optimal move
- Moves automatically after each player action

---

##  Levels System

The game includes multiple difficulty levels with increasing board size and obstacle density.

---

##  Artificial Intelligence

- The duck is controlled by an **AI agent**
- Uses **A\* pathfinding algorithm**
- Evaluates all open edge cells
- Chooses the shortest valid escape path dynamically after each move

---
##  Technical Details

### Built With
- **Python**
- **Pygame**
- **A\* Search Algorithm**
- **Breadth-First Search (BFS)** for path validation
- Object-Oriented Design (OOP)

### Core Components
- `Board`: Grid management and obstacle placement
- `DuckAgent`: AI movement and pathfinding
- `GameManager`: Turn handling and win conditions
- `Button`: UI interaction system
- `Config`: Game configuration and constants

---

##  How to Run the Game

1. Install dependencies:
```bash
pip install pygame
2. run python main.py
3. make sure you down load assets
