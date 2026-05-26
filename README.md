# 🏠 Airbnb Price Predictor

A full-stack machine learning web app that predicts Airbnb listing prices for Indian cities using **CatBoost**. Features Google OAuth, interactive price calculator with Leaflet map, analytics dashboard, currency converter, and batch CSV prediction.

---

## 📸 Screenshots

| Page | Preview |
|------|---------|
| 🏠 Home | Hero with animated stats, feature cards, steps, CTA |
| 🔮 Predict | Interactive form with map, sliders, amenities, ROI |
| 📊 Dashboard | Charts, counters, market insights |
| 📜 History | Filterable table with pagination & CSV export |
| 🔐 Login | Google OAuth + email/password auth |

---

## ✨ Features

- 🔮 **Price Prediction** — Predict optimal listing price based on 10+ property features (room type, property type, amenities, location, etc.)
- 🗺️ **Interactive Map** — Drag-and-drop marker on Leaflet map for location-based pricing
- 💱 **Currency Converter** — Real-time USD/INR exchange rates via exchangerate-api.com
- 📊 **ROI Calculator** — Estimate annual revenue and occupancy rate
- 📈 **Market Insights** — Compare your predicted price against similar listings in the city
- 📉 **Analytics Dashboard** — Chart.js visualizations (bar, doughnut, line charts) of prediction history
- 📜 **Prediction History** — Filterable, paginated table with CSV export
- 🔐 **Google OAuth** — Sign in with Google for personalized experience
- 📦 **Batch CSV Prediction** — REST API endpoint for bulk predictions
- 🌙 **Dark Mode** — Toggle between light and dark themes
- 📱 **Responsive Design** — Glassmorphism UI with mobile navigation
- 🎨 **Animated UI** — Particle canvas, scroll animations, morph blobs, 3D hover cards

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| 🖥️ Backend | Flask, SQLAlchemy, Authlib |
| 🤖 ML Model | CatBoost (trained on 70k+ listings) |
| 🎨 Frontend | Vanilla JS, Chart.js, Leaflet.js |
| 💄 Styling | Custom CSS (glassmorphism, dark mode, animations) |
| 🗄️ Database | SQLite (dev) / PostgreSQL (production) |
| 🚀 Deployment | Docker / Render |
| 🔑 Auth | Google OAuth 2.0 |

---

## 📁 Project Structure

```
├── app.py                      # Flask application with all routes
├── models.py                   # SQLAlchemy models (User, Prediction)
├── requirements.txt            # Python dependencies (Flask, authlib, catboost, etc.)
├── Dockerfile                  # Docker image for containerized deployment
├── docker-compose.yml          # Docker Compose with volume for SQLite
├── Procfile                    # Render deployment config (gunicorn)
├── render.yaml                 # Render blueprint (web service + PostgreSQL)
├── .gitignore                  # Git ignore rules
├── Artifacts/
│   ├── Model.pkl               # Trained CatBoost model (1 MB)
│   └── Preprocessor.pkl        # Data preprocessor pipeline
├── src/Airbnb/
│   ├── pipelines/
│   │   └── Prediction_Pipeline.py  # Model loading & prediction logic
│   ├── components/
│   │   ├── Data_ingestion.py       # Data loading utilities
│   │   ├── Data_transformation.py  # Feature engineering
│   │   └── Model_trainer.py        # Model training script
│   └── utils/
│       └── utils.py                # Helper functions
├── static/
│   ├── style.css               # Complete design system (2500+ lines)
│   └── script.js               # Frontend logic (particles, map, charts, forms)
├── templates/
│   ├── base.html               # Layout with navbar, footer, scroll bar, toast
│   ├── index.html              # Landing page with hero, stats, CTA
│   ├── predict.html            # Price prediction form with map
│   ├── dashboard.html          # Analytics dashboard with charts
│   ├── history.html            # Prediction history table
│   ├── login.html              # Login with Google OAuth
│   ├── register.html           # Registration form
│   ├── about.html              # About the project
│   └── report.html             # Detailed prediction report
└── Notebook_Experiments/       # Jupyter notebooks (EDA, model training)
```

---

## 📊 Dataset & Model Performance

- **Dataset**: 70,000+ Airbnb listings from Indian cities (Mumbai, Delhi, Bangalore, Goa, Chennai, Hyderabad, Kolkata, Jaipur, Pune, Kochi)
- **Features**: Property type, room type, accommodates, bedrooms, bathrooms, beds, amenities count, location (lat/lng), city
- **Algorithm**: CatBoost Regressor
- **Metrics**:
  - R² Score: ~0.72
  - MAE: ~₹2,500
  - RMSE: ~₹4,200
- **Artifacts**: `Model.pkl` (trained model) + `Preprocessor.pkl` (encoding pipeline)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip
- (Optional) Docker for containerized setup

### Local Setup

```bash
# Clone the repository
git clone https://github.com/mayuresh378/Airbnb-Price-Predictor.git
cd Airbnb-Price-Predictor

# (Recommended) Create virtual environment
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
# Windows PowerShell:
#   $env:SECRET_KEY = "your-random-secret-key"
#   $env:GOOGLE_CLIENT_ID = "your-google-client-id"
#   $env:GOOGLE_CLIENT_SECRET = "your-google-client-secret"
#
# Linux/Mac:
#   export SECRET_KEY="your-random-secret-key"
#   export GOOGLE_CLIENT_ID="your-google-client-id"
#   export GOOGLE_CLIENT_SECRET="your-google-client-secret"

# Run the app
python app.py
```

Open **http://localhost:8080** in your browser. 🎉

### Docker 🐳

```bash
docker-compose up --build
```

---

## 🔑 Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Navigate to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth 2.0 Client ID**
5. Application type: **Web application**
6. Authorized JavaScript origins: `http://localhost:8080`
7. Authorized redirect URIs: `http://localhost:8080/auth/google/callback`
8. Click **Create** — copy the Client ID and Client Secret
9. Set as environment variables:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`

---

## ☁️ Deployment on Render

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repository
4. Render auto-detects `render.yaml` — provisions web service + free PostgreSQL
5. Set these environment variables in Render dashboard:
   - `GOOGLE_CLIENT_ID` — from Google Cloud Console
   - `GOOGLE_CLIENT_SECRET` — from Google Cloud Console
   - `SECRET_KEY` — auto-generated, but you can set a custom one
6. Add production callback URL in Google Cloud Console:
   - `https://your-app-name.onrender.com/auth/google/callback`
7. Deploy! Render builds and runs automatically

---

## 🌐 API Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/predict` | POST | Single prediction (JSON input) | Optional |
| `/api/batch-predict` | POST | Batch CSV file prediction | Required |
| `/api/stats` | GET | Overall prediction statistics | Required |
| `/predict` | GET/POST | Web form for price prediction | Optional |
| `/dashboard` | GET | Analytics dashboard with charts | Required |
| `/history` | GET | Prediction history with filters | Required |
| `/report/<id>` | GET | Detailed prediction report | Required |
| `/auth/google` | GET | Initiate Google OAuth login | - |
| `/auth/google/callback` | GET | OAuth callback handler | - |
| `/login` | GET/POST | Login page (email/password) | - |
| `/register` | GET/POST | Registration page | - |
| `/logout` | GET | Logout current session | - |

### Batch CSV Prediction

Upload a CSV with columns: `property_type, room_type, accommodates, bedrooms, bathrooms, beds, city, latitude, longitude, amenities`

```bash
curl -X POST -F "file=@listings.csv" \
  -H "Authorization: Bearer <session_id>" \
  https://your-app.com/api/batch-predict
```

---

## 🖥️ Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | ✅ Yes | - | Flask secret key for sessions |
| `GOOGLE_CLIENT_ID` | ❌ No* | - | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | ❌ No* | - | Google OAuth client secret |
| `DATABASE_URL` | ❌ No | `sqlite:///airbnb.db` | PostgreSQL connection string (production) |
| `FLASK_DEBUG` | ❌ No | `0` | Enable debug mode (`1` for development) |

*\*Google OAuth login requires both `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.*

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `Model.pkl not found` | Ensure you're in the project root directory |
| Google OAuth `invalid_client` | Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set correctly |
| Google OAuth `invalid_claim: iss` | Check that redirect URI matches exactly in Google Cloud Console |
| Port 8080 in use | Change port in `app.py` or set `$env:PORT=8081` |
| SQLite "database is locked" | Delete `instance/airbnb.db` and restart |
| `git push` rejected | Run `git pull --rebase origin main` first |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m "Add amazing feature"`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 🛣️ Roadmap

- [ ] Add more Indian cities (Pune, Ahmedabad, Chandigarh)
- [ ] Support for additional room/property types
- [ ] Multi-language support (Hindi, Marathi, etc.)
- [ ] Price history trends and seasonal prediction
- [ ] Host dashboard with earning projections
- [ ] Mobile app (React Native)

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📬 Contact

**Mayuresh Naik** — [GitHub](https://github.com/mayuresh378)

Project Link: [https://github.com/mayuresh378/Airbnb-Price-Predictor](https://github.com/mayuresh378/Airbnb-Price-Predictor)

---

⭐ **Star this repo if you found it useful!**
