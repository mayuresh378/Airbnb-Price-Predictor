# Airbnb Price Predictor

A full-stack machine learning web app that predicts Airbnb listing prices for Indian cities using CatBoost. Features Google OAuth, interactive price calculator with Leaflet map, analytics dashboard, currency converter, and batch CSV prediction.

## Features

- **Price Prediction** — Predict optimal listing price based on 10+ property features (room type, property type, amenities, location, etc.)
- **Interactive Map** — Drag-and-drop marker on Leaflet map for location-based pricing
- **Currency Converter** — Real-time USD/INR exchange rates
- **ROI Calculator** — Estimate annual revenue and occupancy
- **Market Insights** — Compare your price against similar listings in the city
- **Analytics Dashboard** — Chart.js visualizations (bar, doughnut, line charts) of prediction history
- **Prediction History** — Filterable, paginated table with CSV export
- **Google OAuth** — Sign in with Google for personalized experience
- **Batch CSV Prediction** — REST API endpoint for bulk predictions
- **Responsive Design** — Glassmorphism UI with dark mode, mobile navigation

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask, SQLAlchemy, Authlib |
| ML Model | CatBoost (trained on 70k+ listings) |
| Frontend | Vanilla JS, Chart.js, Leaflet.js |
| Styling | Custom CSS (glassmorphism, dark mode) |
| Database | SQLite (dev) / PostgreSQL (production) |
| Deployment | Docker / Render |

## Project Structure

```
├── app.py                      # Flask application with all routes
├── models.py                   # SQLAlchemy models (User, Prediction)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image
├── docker-compose.yml          # Docker Compose config
├── Procfile                    # Render deployment config
├── render.yaml                 # Render blueprint (web + PostgreSQL)
├── .gitignore                  # Git ignore rules
├── Artifacts/
│   ├── Model.pkl               # Trained CatBoost model
│   └── Preprocessor.pkl        # Data preprocessor
├── src/Airbnb/pipelines/
│   └── Prediction_Pipeline.py  # Model loading and prediction
├── static/
│   ├── style.css               # Complete design system
│   └── script.js               # Frontend logic
├── templates/
│   ├── base.html               # Layout with navbar, footer, toast
│   ├── index.html              # Landing page with hero, stats, CTA
│   ├── predict.html            # Price prediction form
│   ├── dashboard.html          # Analytics dashboard
│   ├── history.html            # Prediction history
│   ├── login.html              # Login with Google OAuth
│   ├── register.html           # Registration
│   ├── about.html              # About the project
│   └── report.html             # Detailed prediction report
└── Notebook_Experiments/       # Jupyter notebooks (EDA, training)
```

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Local Setup

```bash
# Clone the repository
git clone https://github.com/mayuresh378/airbnb-price-predictor.git
cd airbnb-price-predictor

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional for local dev)
# set GOOGLE_CLIENT_ID=your-client-id
# set GOOGLE_CLIENT_SECRET=your-client-secret
# set SECRET_KEY=your-secret-key

# Run the app
python app.py
```

Open http://localhost:8080 in your browser.

### Docker

```bash
docker-compose up --build
```

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → **APIs & Services** → **Credentials**
3. Create **OAuth 2.0 Client ID** (Web application)
4. Add authorized redirect URI: `http://localhost:8080/auth/google/callback`
5. Set environment variables:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`

## Deployment on Render

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` — provisions web service + PostgreSQL
5. Set environment variables in Render dashboard:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `SECRET_KEY` (auto-generated)
6. Add callback URL in Google Cloud Console:
   - `https://your-app.onrender.com/auth/google/callback`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/predict` | POST | Single prediction (JSON) |
| `/api/batch-predict` | POST | Batch CSV prediction |
| `/api/stats` | GET | Prediction statistics |
| `/predict` | GET/POST | Web form for prediction |
| `/dashboard` | GET | Analytics dashboard |
| `/history` | GET | Prediction history |
| `/auth/google` | GET | Google OAuth login |
| `/auth/google/callback` | GET | OAuth callback |
| `/login` | GET | Login page |
| `/register` | GET/POST | Registration |

## License

MIT
