import os
import csv
import io
import uuid
import json
import requests
import time
from io import StringIO
from datetime import datetime, timedelta

from flask import (
    Flask, request, render_template, redirect, url_for,
    flash, session, jsonify, make_response
)
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth

from models import db, User, Prediction
from src.Airbnb.pipelines.Prediction_Pipeline import CustomData, PredictPipeline

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'airbnb-predictor-secret-key-change-in-production')
db_url = os.environ.get('DATABASE_URL', 'sqlite:///airbnb.db')
if db_url and db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.jinja_env.auto_reload = True

db.init_app(app)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

with app.app_context():
    db.create_all()

predict_pipeline = PredictPipeline()

INDIAN_CITY_MAP = {
    "Mumbai": "NYC", "Delhi": "DC", "Bangalore": "SF",
    "Chennai": "Chicago", "Hyderabad": "SF", "Pune": "Boston",
    "Goa": "LA", "Kolkata": "Chicago", "Jaipur": "Boston",
    "Ahmedabad": "NYC", "Surat": "NYC", "Vadodara": "NYC",
    "Jaipur": "Boston", "Udaipur": "Boston", "Jodhpur": "Boston", "Jaisalmer": "NYC",
    "Kochi": "LA", "Trivandrum": "LA", "Alleppey": "LA", "Kozhikode": "LA",
    "Amritsar": "Chicago", "Chandigarh": "DC", "Ludhiana": "Chicago",
    "Indore": "NYC", "Bhopal": "Chicago",
    "Lucknow": "DC", "Varanasi": "DC", "Agra": "DC",
    "Dehradun": "SF", "Rishikesh": "LA", "Nainital": "SF",
    "Shimla": "SF", "Manali": "Boston", "Dharamshala": "Boston",
    "Nashik": "Boston", "Nagpur": "Chicago",
    "Mysore": "SF", "Mangalore": "LA", "Coimbatore": "Chicago",
    "Panaji": "LA", "Calangute": "LA",
    "Noida": "DC", "Gurgaon": "DC", "Faridabad": "DC",
    "Digha": "Chicago", "Darjeeling": "Boston",
    "Madurai": "Chicago", "Warangal": "SF"
}

INDIAN_STATES = {
    "Maharashtra": ["Mumbai", "Pune", "Nashik", "Nagpur"],
    "Delhi NCR": ["Delhi", "Noida", "Gurgaon", "Faridabad"],
    "Karnataka": ["Bangalore", "Mysore", "Mangalore"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
    "Telangana": ["Hyderabad", "Warangal"],
    "Goa": ["Goa", "Panaji", "Calangute"],
    "West Bengal": ["Kolkata", "Digha", "Darjeeling"],
    "Rajasthan": ["Jaipur", "Udaipur", "Jodhpur", "Jaisalmer"],
    "Kerala": ["Kochi", "Trivandrum", "Alleppey", "Kozhikode"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara"],
    "Uttarakhand": ["Dehradun", "Rishikesh", "Nainital"],
    "Himachal Pradesh": ["Shimla", "Manali", "Dharamshala"],
    "Punjab": ["Amritsar", "Chandigarh", "Ludhiana"],
    "Madhya Pradesh": ["Indore", "Bhopal"],
    "Uttar Pradesh": ["Lucknow", "Varanasi", "Agra"]
}

US_TO_INDIAN = {}
for in_city, us_c in INDIAN_CITY_MAP.items():
    US_TO_INDIAN.setdefault(us_c, []).append(in_city)

MARKET_AVERAGES = {}
_csv_path = os.path.join(os.path.dirname(__file__), "Artifacts", "train_data.csv")
if os.path.exists(_csv_path):
    try:
        import pandas as pd
        import numpy as np
        _df = pd.read_csv(_csv_path)
        if 'log_price' in _df.columns:
            _df['_price'] = np.exp(_df['log_price'])
        elif 'price' in _df.columns:
            _df['_price'] = _df['price']
        _stats = _df.groupby('city')['_price'].agg(['mean', 'min', 'max', 'count']).to_dict('index')
        for _us_c, _data in _stats.items():
            if _us_c in US_TO_INDIAN:
                for _in_c in US_TO_INDIAN[_us_c]:
                    MARKET_AVERAGES[_in_c] = {
                        "avg": round(_data['mean'], 2),
                        "min": round(_data['min'], 2),
                        "max": round(_data['max'], 2),
                        "count": int(_data['count'])
                    }
    except Exception:
        pass

INDIAN_COORDS = {
    "Mumbai": (19.0760, 72.8777), "Delhi": (28.7041, 77.1025),
    "Bangalore": (12.9716, 77.5946), "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867), "Pune": (18.5204, 73.8567),
    "Goa": (15.4909, 73.8278), "Kolkata": (22.5726, 88.3639),
    "Jaipur": (26.9124, 75.7873),
    "Ahmedabad": (23.0225, 72.5714), "Surat": (21.1702, 72.8311), "Vadodara": (22.3072, 73.1812),
    "Udaipur": (24.5854, 73.7125), "Jodhpur": (26.2389, 73.0243), "Jaisalmer": (26.9157, 70.9083),
    "Kochi": (9.9312, 76.2673), "Trivandrum": (8.5241, 76.9366), "Alleppey": (9.4981, 76.3388), "Kozhikode": (11.2588, 75.7804),
    "Amritsar": (31.6340, 74.8723), "Chandigarh": (30.7333, 76.7794), "Ludhiana": (30.9010, 75.8573),
    "Indore": (22.7196, 75.8577), "Bhopal": (23.2599, 77.4126),
    "Lucknow": (26.8467, 80.9462), "Varanasi": (25.3176, 82.9739), "Agra": (27.1767, 78.0081),
    "Dehradun": (30.3165, 78.0322), "Rishikesh": (30.0869, 78.2676), "Nainital": (29.3803, 79.4626),
    "Shimla": (31.1048, 77.1734), "Manali": (32.2432, 77.1892), "Dharamshala": (32.2190, 76.3234),
    "Nashik": (19.9975, 73.7898), "Nagpur": (21.1458, 79.0882),
    "Mysore": (12.2958, 76.6394), "Mangalore": (12.9141, 74.8560), "Coimbatore": (11.0168, 76.9558),
    "Panaji": (15.4909, 73.8278), "Calangute": (15.5439, 73.7553),
    "Noida": (28.5355, 77.3910), "Gurgaon": (28.4595, 77.0266), "Faridabad": (28.4089, 77.3178),
    "Digha": (21.6737, 87.5465), "Darjeeling": (27.0410, 88.2663),
    "Madurai": (9.9252, 78.1198), "Warangal": (17.9784, 79.5941)
}

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")
LIVE_PRICE_CACHE = {}
LIVE_PRICE_CACHE_TIME = {}

def fetch_live_prices(city_name):
    now = time.time()
    key = city_name.lower()
    if key in LIVE_PRICE_CACHE and (now - LIVE_PRICE_CACHE_TIME.get(key, 0)) < 1800:
        return LIVE_PRICE_CACHE[key]
    result = None
    if RAPIDAPI_KEY:
        try:
            h = {"X-RapidAPI-Key": RAPIDAPI_KEY, "X-RapidAPI-Host": "airbnb13.p.rapidapi.com"}
            p = {
                "location": city_name + ", India",
                "checkin": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "checkout": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
                "adults": "1", "currency": "USD"
            }
            r = requests.get("https://airbnb13.p.rapidapi.com/search-location", params=p, headers=h, timeout=10)
            if r.status_code == 200:
                d = r.json()
                results = d.get("results", [])
                if results:
                    prices = []
                    for item in results:
                        pp = item.get("price")
                        if isinstance(pp, dict):
                            pv = pp.get("rate", pp.get("total", 0))
                        else:
                            pv = pp
                        if pv and float(pv) > 0:
                            prices.append(float(pv))
                    if prices:
                        result = {"avg": round(sum(prices)/len(prices), 2), "min": round(min(prices), 2), "max": round(max(prices), 2), "count": len(prices), "source": "live"}
        except Exception:
            pass
    if not result:
        result = MARKET_AVERAGES.get(city_name)
        if result:
            result = {**result, "source": "model"}
    if result:
        LIVE_PRICE_CACHE[key] = result
        LIVE_PRICE_CACHE_TIME[key] = now
    return result

def run_prediction(property_type, room_type, amenities, accommodates, bathrooms,
                   bed_type, cancellation_policy, cleaning_fee, city,
                   host_has_profile_pic, host_identity_verified, host_response_rate,
                   instant_bookable, latitude, longitude, number_of_reviews,
                   review_scores_rating, bedrooms, beds):
    data = CustomData(
        property_type=property_type, room_type=room_type, amenities=amenities,
        accommodates=accommodates, bathrooms=bathrooms, bed_type=bed_type,
        cancellation_policy=cancellation_policy, cleaning_fee=cleaning_fee,
        city=city, host_has_profile_pic=host_has_profile_pic,
        host_identity_verified=host_identity_verified,
        host_response_rate=host_response_rate, instant_bookable=instant_bookable,
        latitude=latitude, longitude=longitude,
        number_of_reviews=number_of_reviews,
        review_scores_rating=review_scores_rating,
        bedrooms=bedrooms, beds=beds
    )
    pred = predict_pipeline.predict(data.get_data_as_dataframe())
    return round(pred[0], 2)

def get_insights(form, us_city, lat, lng, amenities_count):
    insights = {}
    room_types = ["Entire home/apt", "Private room", "Shared room"]
    base = dict(
        property_type=form.get("property_type"), amenities=amenities_count,
        accommodates=form.get("accommodates"), bathrooms=form.get("bathrooms"),
        bed_type=form.get("bed_type"), cancellation_policy=form.get("cancellation_policy"),
        cleaning_fee=form.get("cleaning_fee"),
        host_has_profile_pic=form.get("host_has_profile_pic"),
        host_identity_verified=form.get("host_identity_verified"),
        host_response_rate=form.get("host_response_rate"),
        instant_bookable=form.get("instant_bookable"),
        latitude=lat, longitude=lng,
        number_of_reviews=form.get("number_of_reviews"),
        review_scores_rating=form.get("review_scores_rating"),
        bedrooms=form.get("bedrooms"), beds=form.get("beds")
    )
    for rt in room_types:
        try:
            insights[rt] = run_prediction(**{**base, "room_type": rt, "city": us_city})
        except Exception:
            insights[rt] = None

    city_comparison = {}
    for in_city, us_c in INDIAN_CITY_MAP.items():
        try:
            coords = INDIAN_COORDS[in_city]
            city_comparison[in_city] = run_prediction(**{
                **base, "room_type": form.get("room_type"), "city": us_c,
                "latitude": coords[0], "longitude": coords[1]
            })
        except Exception:
            city_comparison[in_city] = None

    valid_prices = [p for p in city_comparison.values() if p is not None]
    max_city_price = max(valid_prices) if valid_prices else 1
    return insights, city_comparison, max_city_price

def save_prediction(form, amenities_list, result, us_city):
    user_id = session.get('user_id')
    pred = Prediction(
        user_id=user_id,
        session_id=session.get('session_id', str(uuid.uuid4())),
        property_type=form.get("property_type"),
        room_type=form.get("room_type"),
        amenities=len(amenities_list),
        accommodates=int(form.get("accommodates") or 0),
        bathrooms=float(form.get("bathrooms") or 0),
        bed_type=form.get("bed_type"),
        cancellation_policy=form.get("cancellation_policy"),
        cleaning_fee=form.get("cleaning_fee"),
        city=form.get("city"),
        host_has_profile_pic=form.get("host_has_profile_pic"),
        host_identity_verified=form.get("host_identity_verified"),
        host_response_rate=int(form.get("host_response_rate") or 0),
        instant_bookable=form.get("instant_bookable"),
        latitude=float(form.get("latitude") or 0),
        longitude=float(form.get("longitude") or 0),
        number_of_reviews=int(form.get("number_of_reviews") or 0),
        review_scores_rating=int(form.get("review_scores_rating") or 0),
        bedrooms=int(form.get("bedrooms") or 0),
        beds=int(form.get("beds") or 0),
        amenities_list=",".join(amenities_list),
        predicted_price=result
    )
    db.session.add(pred)
    db.session.commit()
    return pred

# ─── Auth ────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if not username or not email or not password:
            flash("All fields are required", "error")
            return render_template("register.html")
        if User.query.filter_by(username=username).first():
            flash("Username already taken", "error")
            return render_template("register.html")
        if User.query.filter_by(email=email).first():
            flash("Email already registered", "error")
            return render_template("register.html")
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash("Invalid username or password", "error")
            return render_template("login.html")
        session["user_id"] = user.id
        session["username"] = user.username
        flash(f"Welcome back, {user.username}!", "success")
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("google_token", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

# ─── Google Auth ──────────────────────────────────────────────────────

@app.route("/auth/google")
def google_login():
    redirect_uri = url_for('google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route("/auth/google/callback")
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        resp = oauth.google.get('https://www.googleapis.com/oauth2/v1/userinfo')
        user_info = resp.json()
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0])

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                username=name,
                email=email,
                password_hash=generate_password_hash(str(uuid.uuid4()))
            )
            db.session.add(user)
            db.session.commit()

        session["user_id"] = user.id
        session["username"] = user.username
        session["google_token"] = token
        flash(f"Welcome, {user.username}!", "success")
        return redirect(url_for("home"))

    except Exception as e:
        flash(f"Google login failed: {str(e)}", "error")
        return redirect(url_for("login"))

# ─── Home (Landing) ──────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("index.html")

# ─── About ──────────────────────────────────────────────────────────

@app.route("/about")
def about():
    return render_template("about.html")

# ─── Predict ────────────────────────────────────────────────────────

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    if request.method == "POST":
        try:
            amenities_list = request.form.getlist("amenities")
            amenities_count = len(amenities_list)
            indian_city = request.form.get("city")
            us_city = INDIAN_CITY_MAP.get(indian_city, "NYC")
            lat = request.form.get("latitude")
            lng = request.form.get("longitude")

            result = run_prediction(
                property_type=request.form.get("property_type"),
                room_type=request.form.get("room_type"),
                amenities=amenities_count,
                accommodates=request.form.get("accommodates"),
                bathrooms=request.form.get("bathrooms"),
                bed_type=request.form.get("bed_type"),
                cancellation_policy=request.form.get("cancellation_policy"),
                cleaning_fee=request.form.get("cleaning_fee"),
                city=us_city,
                host_has_profile_pic=request.form.get("host_has_profile_pic"),
                host_identity_verified=request.form.get("host_identity_verified"),
                host_response_rate=request.form.get("host_response_rate"),
                instant_bookable=request.form.get("instant_bookable"),
                latitude=lat, longitude=lng,
                number_of_reviews=request.form.get("number_of_reviews"),
                review_scores_rating=request.form.get("review_scores_rating"),
                bedrooms=request.form.get("bedrooms"),
                beds=request.form.get("beds")
            )

            pred = save_prediction(request.form, amenities_list, result, us_city)
            session["last_prediction_id"] = pred.id

            insights, city_comparison, max_city_price = get_insights(
                request.form, us_city, lat, lng, amenities_count
            )

            live_prices = {}
            all_cities = [c for state_cities in INDIAN_STATES.values() for c in state_cities]
            for city in all_cities:
                lp = fetch_live_prices(city)
                if lp:
                    live_prices[city] = lp

            return render_template("predict.html", final_result=result,
                                   insights=insights, city_comparison=city_comparison,
                                   selected_city=indian_city, max_city_price=max_city_price,
                                   prediction_id=pred.id, live_prices=live_prices,
                                   indian_states=INDIAN_STATES)

        except Exception as e:
            flash(f"Prediction error: {str(e)}", "error")
            return render_template("predict.html", final_result=None,
                                   insights=None, city_comparison=None,
                                   selected_city=None, max_city_price=None,
                                   prediction_id=None, live_prices={},
                                   indian_states=INDIAN_STATES)

    return render_template("predict.html", final_result=None,
                           insights=None, city_comparison=None,
                           selected_city=None, max_city_price=None,
                           prediction_id=None, live_prices={},
                           indian_states=INDIAN_STATES)

# ─── Dashboard ──────────────────────────────────────────────────────

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to view the dashboard.", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    predictions = Prediction.query.filter_by(user_id=user_id).order_by(Prediction.created_at.desc()).all()

    if not predictions:
        return render_template("dashboard.html", predictions=[], stats={}, city_data=[],
                               room_data=[], monthly_data=[], user=session.get("username"))

    total = len(predictions)
    avg_price = sum(p.predicted_price for p in predictions) / total
    cities = set(p.city for p in predictions if p.city)
    avg_reviews = sum(p.number_of_reviews or 0 for p in predictions) / total

    city_counts = {}
    city_prices = {}
    for p in predictions:
        if p.city:
            city_counts[p.city] = city_counts.get(p.city, 0) + 1
            if p.city not in city_prices:
                city_prices[p.city] = []
            city_prices[p.city].append(p.predicted_price)

    city_data = [
        {"city": c, "count": city_counts[c], "avg_price": round(sum(city_prices[c])/len(city_prices[c]), 2)}
        for c in city_counts
    ]

    room_counts = {}
    for p in predictions:
        if p.room_type:
            room_counts[p.room_type] = room_counts.get(p.room_type, 0) + 1
    room_data = [{"room_type": k, "count": v} for k, v in room_counts.items()]

    monthly = {}
    for p in predictions:
        if p.created_at:
            key = p.created_at.strftime("%Y-%m")
            if key not in monthly:
                monthly[key] = {"count": 0, "total_price": 0}
            monthly[key]["count"] += 1
            monthly[key]["total_price"] += p.predicted_price
    monthly_data = [
        {"month": k, "count": v["count"], "avg_price": round(v["total_price"]/v["count"], 2)}
        for k, v in sorted(monthly.items())
    ]

    stats = {
        "total_predictions": total,
        "avg_price": round(avg_price, 2),
        "unique_cities": len(cities),
        "avg_reviews": round(avg_reviews, 1)
    }

    return render_template("dashboard.html", predictions=predictions, stats=stats,
                           city_data=json.dumps(city_data), room_data=json.dumps(room_data),
                           monthly_data=json.dumps(monthly_data), user=session.get("username"))

# ─── History ─────────────────────────────────────────────────────────

@app.route("/history")
def history():
    user_id = session.get("user_id")
    page = request.args.get("page", 1, type=int)
    city_filter = request.args.get("city", "")
    room_filter = request.args.get("room_type", "")

    query = Prediction.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    else:
        sid = session.get("session_id")
        if sid:
            query = query.filter(Prediction.session_id == sid, Prediction.user_id.is_(None))
        else:
            query = query.filter(False)

    if city_filter:
        query = query.filter(Prediction.city == city_filter)
    if room_filter:
        query = query.filter(Prediction.room_type == room_filter)

    predictions = query.order_by(Prediction.created_at.desc()).all()
    cities = sorted(set(p.city for p in predictions if p.city))
    room_types = sorted(set(p.room_type for p in predictions if p.room_type))

    return render_template("history.html", predictions=predictions,
                           cities=cities, room_types=room_types,
                           city_filter=city_filter, room_filter=room_filter,
                           user=session.get("username"))

@app.route("/history/export")
def export_history():
    user_id = session.get("user_id")
    query = Prediction.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    else:
        sid = session.get("session_id")
        if sid:
            query = query.filter(Prediction.session_id == sid, Prediction.user_id.is_(None))
        else:
            query = query.filter(False)

    predictions = query.order_by(Prediction.created_at.desc()).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Date", "City", "Property Type", "Room Type", "Bedrooms", "Beds",
                     "Accommodates", "Bathrooms", "Amenities", "Predicted Price (USD)"])
    for p in predictions:
        writer.writerow([
            p.id, p.created_at.strftime("%Y-%m-%d %H:%M") if p.created_at else "",
            p.city, p.property_type, p.room_type, p.bedrooms, p.beds,
            p.accommodates, p.bathrooms, p.amenities, p.predicted_price
        ])

    resp = make_response(output.getvalue())
    resp.headers["Content-Type"] = "text/csv"
    resp.headers["Content-Disposition"] = f"attachment; filename=airbnb_predictions_{datetime.now().strftime('%Y%m%d')}.csv"
    return resp

# ─── Report ──────────────────────────────────────────────────────────

@app.route("/report/<int:prediction_id>")
def report(prediction_id):
    pred = Prediction.query.get_or_404(prediction_id)
    return render_template("report.html", pred=pred)

# ─── API ─────────────────────────────────────────────────────────────

@app.route("/api/predict", methods=["POST"])
def api_predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        required = ["property_type", "room_type", "city", "bedrooms", "beds",
                     "accommodates", "bathrooms", "latitude", "longitude"]
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        amenities_list = data.get("amenities", [])
        if isinstance(amenities_list, list):
            amenities_count = len(amenities_list)
        else:
            amenities_count = int(amenities_list)

        indian_city = data.get("city")
        us_city = INDIAN_CITY_MAP.get(indian_city, "NYC")

        result = run_prediction(
            property_type=data["property_type"], room_type=data["room_type"],
            amenities=amenities_count,
            accommodates=data["accommodates"], bathrooms=data["bathrooms"],
            bed_type=data.get("bed_type", "Real Bed"),
            cancellation_policy=data.get("cancellation_policy", "flexible"),
            cleaning_fee=data.get("cleaning_fee", "False"),
            city=us_city,
            host_has_profile_pic=data.get("host_has_profile_pic", "t"),
            host_identity_verified=data.get("host_identity_verified", "t"),
            host_response_rate=data.get("host_response_rate", 90),
            instant_bookable=data.get("instant_bookable", "t"),
            latitude=data["latitude"], longitude=data["longitude"],
            number_of_reviews=data.get("number_of_reviews", 0),
            review_scores_rating=data.get("review_scores_rating", 0),
            bedrooms=data["bedrooms"], beds=data["beds"]
        )

        return jsonify({
            "success": True,
            "predicted_price_usd": result,
            "predicted_price_inr": round(result * 83, 2),
            "city": indian_city,
            "currency": "USD",
            "model_version": "1.0"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/batch-predict", methods=["POST"])
def api_batch_predict():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        file = request.files["file"]
        if not file.filename.endswith(".csv"):
            return jsonify({"error": "Only CSV files supported"}), 400

        content = file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        results = []
        errors = []
        for idx, row in enumerate(reader):
            try:
                amenities_count = len(row.get("amenities", "").split(",")) if row.get("amenities") else 0
                indian_city = row.get("city", "Mumbai")
                us_city = INDIAN_CITY_MAP.get(indian_city, "NYC")

                price = run_prediction(
                    property_type=row.get("property_type", "Apartment"),
                    room_type=row.get("room_type", "Entire home/apt"),
                    amenities=amenities_count,
                    accommodates=int(row.get("accommodates", 2)),
                    bathrooms=float(row.get("bathrooms", 1)),
                    bed_type=row.get("bed_type", "Real Bed"),
                    cancellation_policy=row.get("cancellation_policy", "flexible"),
                    cleaning_fee=row.get("cleaning_fee", "False"),
                    city=us_city,
                    host_has_profile_pic=row.get("host_has_profile_pic", "t"),
                    host_identity_verified=row.get("host_identity_verified", "t"),
                    host_response_rate=int(row.get("host_response_rate", 90)),
                    instant_bookable=row.get("instant_bookable", "t"),
                    latitude=float(row.get("latitude", 19.076)),
                    longitude=float(row.get("longitude", 72.8777)),
                    number_of_reviews=int(row.get("number_of_reviews", 0)),
                    review_scores_rating=int(row.get("review_scores_rating", 0)),
                    bedrooms=int(row.get("bedrooms", 1)),
                    beds=int(row.get("beds", 1))
                )
                results.append({"row": idx + 1, "city": row.get("city"), "price_usd": price})
            except Exception as e:
                errors.append({"row": idx + 1, "error": str(e)})

        return jsonify({"success": True, "total": len(results), "results": results, "errors": errors})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stats")
def api_stats():
    total = Prediction.query.count()
    avg = db.session.query(db.func.avg(Prediction.predicted_price)).scalar()
    city_stats = db.session.query(
        Prediction.city, db.func.count(Prediction.id), db.func.avg(Prediction.predicted_price)
    ).group_by(Prediction.city).all()
    return jsonify({
        "total_predictions": total,
        "average_price_usd": round(avg, 2) if avg else 0,
        "cities": [{"city": c, "count": cnt, "avg_price": round(p, 2)} for c, cnt, p in city_stats]
    })

# ─── Run ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host="0.0.0.0", port=8080, debug=debug_mode)
