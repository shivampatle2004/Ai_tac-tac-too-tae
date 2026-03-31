# Deployment Guide

## GitHub Deployment
1. Initialize repository (`git init`).
2. Add files (`git add .`), committing with descriptive messages.
3. Push to `main` branch.

## Render Deployment (Free Tier)
1. Go to Render.com -> New Web Service.
2. Connect your GitHub repository.
3. **Name**: `ai-tic-tac-toe`
4. **Environment**: `Python 3`
5. **Build Command**: `pip install -r requirements.txt`
6. **Start Command**: `gunicorn backend.app:app`
7. Click `Create Web Service`.

Note: Render uses `Procfile` internally if detected, but setting Start Command natively in the dashboard provides highest stability.
