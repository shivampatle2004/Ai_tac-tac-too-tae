# Architecture Overview

## System Architecture
The application follows a standard client-server architecture.
- **Client (Frontend)**: Runs in the user's browser, handling UI rendering, animations, and user inputs. It communicates statelessly via HTTP JSON with the backend.
- **Server (Backend)**: Flask application serving both the static frontend assets and the game logic REST API.

## Frontend
- Vanilla HTML, CSS, JavaScript.
- CSS Modules used are implicit through targeted class names.
- Leverages Glassmorphism CSS effects and modern transition animations.

## Backend
- Written in Python using Flask.
- Exposes RESTful endpoints (`/api/state`, `/api/move`, `/api/reset`).
- Incorporates `game_engine.py` for state management and rule validation (the Moving Window rule).

## AI Engine
- Isolated in `minimax.py`.
- Stateless function that receives a serialized board representation, simulates game trees, and outputs an optimal index.

## Deployment & GitHub Structure
- Root level contains configuration files: `Procfile`, `requirements.txt`, `.gitignore`.
- Designed to be easily containerized or run on PaaS like Render using `gunicorn`.
