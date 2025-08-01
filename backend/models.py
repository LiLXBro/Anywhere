from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # relationships
    reservations = db.relationship('Reservation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'
    
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    maximum_spots = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    spots = db.relationship('ParkingSpot', backref='lot', lazy=True, cascade='all, delete-orphan', order_by='ParkingSpot.spot_number')
    
    @property
    def available_spots_count(self):
        return len([spot for spot in self.spots if spot.status == 'A'])
    
    @property
    def occupied_spots_count(self):
        return len([spot for spot in self.spots if spot.status == 'O'])
    
    def __repr__(self):
        return f'<ParkingLot {self.prime_location_name}>'

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'
    
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    spot_number = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(1), default='A', nullable=False)  # A-Available, O-Occupied
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    reservations = db.relationship('Reservation', backref='spot', lazy=True)
    
    @property
    def current_reservation(self):
        return Reservation.query.filter_by(
            spot_id=self.id, 
            leaving_timestamp=None
        ).first()
    
    def __repr__(self):
        return f'<ParkingSpot {self.spot_number} - {self.status}>'

class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, nullable=True)
    
    def calculate_cost(self):
        if self.leaving_timestamp and self.parking_timestamp:
            duration = self.leaving_timestamp - self.parking_timestamp
            hours = duration.total_seconds() / 3600
            # assuming minimum 1 hour charge
            hours = max(1, hours)
            self.parking_cost = round(hours * self.spot.lot.price_per_hour, 2)
            return self.parking_cost
        return 0
    
    @property
    def duration_str(self):
        end_time = self.leaving_timestamp or datetime.utcnow()
        if self.parking_timestamp:
            duration = end_time - self.parking_timestamp
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            if not self.leaving_timestamp:
                return f"{hours}h {minutes}m (ongoing)"
            return f"{hours}h {minutes}m"
        return "N/A"

    @property
    def current_cost(self):
        if self.parking_timestamp and not self.leaving_timestamp:
            duration = datetime.utcnow() - self.parking_timestamp
            hours = duration.total_seconds() / 3600
            hours = max(1, hours) # assumed minimum charge of 1 hour
            return round(hours * self.spot.lot.price_per_hour, 2)
        return self.parking_cost or 0
    
    def __repr__(self):
        return f'<Reservation {self.vehicle_number} - Spot {self.spot_id}>'