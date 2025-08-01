from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, ParkingLot, ParkingSpot, Reservation
from config import Config
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.config.from_object(Config)

# Initialize database
db.init_app(app)

def create_admin_user():
    """Create default admin user if not exists, and ensure admin flag is set."""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@parking.com',
            is_admin=True,
            phone='9999999999'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("Default admin user created: username=admin, password=admin123")
    # FIX: Ensure the existing admin user has admin privileges
    elif not admin.is_admin:
        admin.is_admin = True
        print("Updated existing 'admin' user to have admin privileges.")
    
    # FIX: Commit session to save any changes
    db.session.commit()

# Replaced deprecated @app.before_first_request with the recommended approach.
# This block will run once when the application starts.
with app.app_context():
    db.create_all()
    create_admin_user()

# Helper functions
def login_required(f):
    # FIX: Added @wraps for decorator robustness
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    # FIX: Added @wraps for decorator robustness
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            flash(f'Welcome, {user.username}!', 'success')
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email, phone=phone)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    lots = ParkingLot.query.all()
    users = User.query.filter_by(is_admin=False).all()
    
    # Summary statistics
    total_lots = len(lots)
    total_spots = sum(lot.maximum_spots for lot in lots)
    occupied_spots = sum(lot.occupied_spots_count for lot in lots)
    available_spots = total_spots - occupied_spots
    
    stats = {
        'total_lots': total_lots,
        'total_spots': total_spots,
        'occupied_spots': occupied_spots,
        'available_spots': available_spots,
        'occupancy_rate': round((occupied_spots / total_spots * 100) if total_spots > 0 else 0, 1)
    }
    
    return render_template('admin_dashboard.html', 
                           lots=lots, users=users, stats=stats)

@app.route('/admin/create_lot', methods=['GET', 'POST'])
@admin_required
def create_lot():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        pin_code = request.form['pin_code']
        price = float(request.form['price'])
        max_spots = int(request.form['max_spots'])
        
        # Create parking lot
        lot = ParkingLot(
            prime_location_name=name,
            address=address,
            pin_code=pin_code,
            price_per_hour=price,
            maximum_spots=max_spots
        )
        
        db.session.add(lot)
        db.session.commit()
        
        # Create parking spots
        for i in range(1, max_spots + 1):
            spot = ParkingSpot(
                lot_id=lot.id,
                spot_number=f"S{i:03d}",
                status='A'
            )
            db.session.add(spot)
        
        db.session.commit()
        
        flash(f'Parking lot "{name}" created with {max_spots} spots!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_lot.html')

@app.route('/admin/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
@admin_required
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    
    if request.method == 'POST':
        lot.prime_location_name = request.form['name']
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        lot.price_per_hour = float(request.form['price'])
        
        new_max_spots = int(request.form['max_spots'])
        current_spots = len(lot.spots)
        
        if new_max_spots > current_spots:
            # Add new spots
            for i in range(current_spots + 1, new_max_spots + 1):
                spot = ParkingSpot(
                    lot_id=lot.id,
                    spot_number=f"S{i:03d}",
                    status='A'
                )
                db.session.add(spot)
        elif new_max_spots < current_spots:
            # Remove spots (only if they're available)
            spots_to_remove = lot.spots[new_max_spots:]
            for spot in spots_to_remove:
                if spot.status == 'O':
                    flash('Cannot reduce spots while some are occupied!', 'error')
                    return render_template('edit_lot.html', lot=lot)
                db.session.delete(spot)
        
        lot.maximum_spots = new_max_spots
        db.session.commit()
        
        flash('Parking lot updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_lot.html', lot=lot)

@app.route('/admin/delete_lot/<int:lot_id>')
@admin_required
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    
    # Check if any spots are occupied
    if lot.occupied_spots_count > 0:
        flash('Cannot delete lot with occupied spots!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    db.session.delete(lot)
    db.session.commit()
    
    flash(f'Parking lot "{lot.prime_location_name}" deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    user = User.query.get(session['user_id'])
    if user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    # Get available lots
    lots = ParkingLot.query.all()
    available_lots = [lot for lot in lots if lot.available_spots_count > 0]
    
    # Get user's current and past reservations
    current_reservations = Reservation.query.filter_by(
        user_id=user.id, 
        leaving_timestamp=None
    ).all()
    
    past_reservations = Reservation.query.filter_by(user_id=user.id)\
        .filter(Reservation.leaving_timestamp.isnot(None))\
        .order_by(Reservation.leaving_timestamp.desc())\
        .limit(10).all()
    
    return render_template('user_dashboard.html', 
                           lots=available_lots,
                           current_reservations=current_reservations,
                           past_reservations=past_reservations)

@app.route('/user/book_spot/<int:lot_id>', methods=['POST'])
@login_required
def book_spot(lot_id):
    user = User.query.get(session['user_id'])
    lot = ParkingLot.query.get_or_404(lot_id)
    vehicle_number = request.form['vehicle_number']
    
    # Find first available spot
    available_spot = ParkingSpot.query.filter_by(
        lot_id=lot_id, 
        status='A'
    ).first()
    
    if not available_spot:
        flash('No available spots in this lot!', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Create reservation
    reservation = Reservation(
        spot_id=available_spot.id,
        user_id=user.id,
        vehicle_number=vehicle_number.upper(),
        parking_timestamp=datetime.utcnow()
    )
    
    # Update spot status
    available_spot.status = 'O'
    
    db.session.add(reservation)
    db.session.commit()
    
    flash(f'Spot {available_spot.spot_number} booked successfully!', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/user/release_spot/<int:reservation_id>')
@login_required
def release_spot(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    user = User.query.get(session['user_id'])
    
    # Check if user owns this reservation
    if reservation.user_id != user.id:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Update reservation
    reservation.leaving_timestamp = datetime.utcnow()
    reservation.calculate_cost()
    
    # Update spot status
    spot = ParkingSpot.query.get(reservation.spot_id)
    spot.status = 'A'
    
    db.session.commit()
    
    flash(f'Spot released! Total cost: ₹{reservation.parking_cost}', 'success')
    return redirect(url_for('user_dashboard'))

# API Routes (Optional)
@app.route('/api/lots')
def api_lots():
    lots = ParkingLot.query.all()
    return jsonify([{
        'id': lot.id,
        'name': lot.prime_location_name,
        'address': lot.address,
        'price_per_hour': lot.price_per_hour,
        'total_spots': lot.maximum_spots,
        'available_spots': lot.available_spots_count,
        'occupied_spots': lot.occupied_spots_count
    } for lot in lots])

@app.route('/api/lot/<int:lot_id>/spots')
def api_lot_spots(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = [{
        'id': spot.id,
        'spot_number': spot.spot_number,
        'status': spot.status,
        'current_reservation': {
            'vehicle_number': spot.current_reservation.vehicle_number,
            'user': spot.current_reservation.user.username,
            'duration': spot.current_reservation.duration_str
        } if spot.current_reservation else None
    } for spot in lot.spots]
    
    return jsonify(spots)

if __name__ == '__main__':
    app.run(debug=True)