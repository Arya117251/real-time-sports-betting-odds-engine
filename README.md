# Real-Time Sports Betting Odds Engine

Live NBA game data streaming pipeline with ML-powered win prediction.

## Architecture

ESPN API → Python Producer → GCP Pub/Sub → Consumer → ML Model → Predictions

## Tech Stack

- Streaming: GCP Pub/Sub
- ML: Scikit-learn (Random Forest, 61% accuracy)
- Data Processing: Pandas, Python
- API: ESPN Sports API

## Project Structure

scripts/          - Data pipeline scripts
data/            - Game datasets (218 games)
models/          - Trained ML models

## What I Built

1. Real-time data ingestion from ESPN API
2. Streaming pipeline using GCP Pub/Sub (producer-consumer pattern)
3. Historical data collection (30 days of NBA games)
4. ML model training (Random Forest predicting game outcomes)

## Setup

pip install pandas scikit-learn google-cloud-pubsub requests
python scripts/train_model.py

