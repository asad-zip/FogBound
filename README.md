# Fogbound 🌫️

ML-powered fog prediction system with multi-hour and multi-day forecasting.

## About

Fogbound predicts fog conditions hours and days in advance, perfect for fog photography and exploration enthusiasts.

## Project Status

📍 **Phase 1: Data Collection Pipeline** - In progress

## Setup

### Prerequisites
- Python 3.9+
- PostgreSQL
- Git

### Installation

1. Clone the repository
2. Create virtual environment:
```bash
   python3 -m venv venv
   source venv/bin/activate
```
3. Install dependencies:
```bash
   pip install -r requirements.txt
```
4. Copy `.env.example` to `.env` and configure your settings

## Project Structure
```
fogbound/
├── src/
│   ├── data/       # Data collection and processing
│   ├── models/     # ML models
│   ├── api/        # Web API
│   └── utils/      # Helper functions
├── tests/          # Test files
├── notebooks/      # Jupyter notebooks for exploration
└── docs/           # Documentation
```

## Roadmap

- [x] Phase 0: Foundation & Setup
- [ ] Phase 1: Data Collection Pipeline
- [ ] Phase 2: Fog Detection & Labeling
- [ ] Phase 3: ML Model Development
- [ ] Phase 4: Backend API
- [ ] Phase 5: Frontend Dashboard
- [ ] Phase 6: Alerts System
- [ ] Phase 7: AWS Deployment
- [ ] Phase 8: Polish & Portfolio
