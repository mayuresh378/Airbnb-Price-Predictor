from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    predictions = db.relationship('Prediction', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Prediction(db.Model):
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(64), nullable=True)
    property_type = db.Column(db.String(50))
    room_type = db.Column(db.String(50))
    amenities = db.Column(db.Integer)
    accommodates = db.Column(db.Integer)
    bathrooms = db.Column(db.Float)
    bed_type = db.Column(db.String(50))
    cancellation_policy = db.Column(db.String(50))
    cleaning_fee = db.Column(db.String(10))
    city = db.Column(db.String(50))
    host_has_profile_pic = db.Column(db.String(5))
    host_identity_verified = db.Column(db.String(5))
    host_response_rate = db.Column(db.Integer)
    instant_bookable = db.Column(db.String(5))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    number_of_reviews = db.Column(db.Integer)
    review_scores_rating = db.Column(db.Integer)
    bedrooms = db.Column(db.Integer)
    beds = db.Column(db.Integer)
    amenities_list = db.Column(db.Text, nullable=True)
    predicted_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'property_type': self.property_type,
            'room_type': self.room_type,
            'amenities': self.amenities,
            'accommodates': self.accommodates,
            'bathrooms': self.bathrooms,
            'bed_type': self.bed_type,
            'cancellation_policy': self.cancellation_policy,
            'cleaning_fee': self.cleaning_fee,
            'city': self.city,
            'bedrooms': self.bedrooms,
            'beds': self.beds,
            'predicted_price': self.predicted_price,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
