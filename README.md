# AI Tic Tac Toe (Moving Window Variant)

## Overview
A modern, production-ready Tic-Tac-Toe application where the game never ends in a tie. Players are limited to 3 active marks on the board. When they place a 4th, their oldest mark vanishes!

## Features
- **Moving Window Mechanics**: Replaces oldest pieces to prevent ties.
- **Unbeatable AI**: Powered by Minimax & Alpha-Beta pruning algorithms.
- **Glassmorphism UI**: Beautiful, dark-mode default modern interface.
- **Visual Cues**: Oldest pieces pulsate to warn players they will disappear next.

## Requirements
- Python 3.10+
- Flask & Gunicorn

## Run Locally
```bash
pip install -r requirements.txt
python backend/app.py
```
Visit `http://localhost:5000`.

## Documentation
Check the `analysis/` folder for detailed system architecture, flow diagrams, and AI logic mechanics.

## Screenshots
> [Placeholder for Screenshots: Drop your images here after deploying]
