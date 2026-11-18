from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import os
import json
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

import db

app = Flask(__name__, template_folder="template", static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY', 'temple_management_secret_key_change_in_production')

db.init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash("Please sign in to access your devotee bookings.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id') or session.get('user_role') != 'admin':
            flash("Access restricted to Temple Board Administrative Staff.", "danger")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_user():
    user = None
    if session.get('user_id'):
        user = db.get_user_by_id(session['user_id'])
    return dict(current_user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = db.authenticate_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user['role']
            flash(f"Welcome back, {user['name']}! Blessed darshan.", "success")
            
            next_url = request.args.get('next')
            if next_url:
                return redirect(next_url)
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('my_bookings'))
        else:
            flash("Invalid email or password. Please verify and try again.", "error")
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        aadhar = request.form.get('aadhar', '').strip()
        city = request.form.get('city', '').strip()
        password = request.form.get('password', '')
        
        user_id, err = db.create_user(name, email, phone, aadhar, city, password, role='devotee')
        if user_id:
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_email'] = email.lower()
            session['user_role'] = 'devotee'
            flash("Registration successful! Your pilgrim profile is active.", "success")
            return redirect(url_for('my_bookings'))
        else:
            flash(f"Registration failed: {err}", "error")
            
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out successfully. Om Namo Venkateshaya.", "info")
    return redirect(url_for('home'))

@app.route('/my-bookings')
@app.route('/profile')
@login_required
def my_bookings():
    user = db.get_user_by_id(session['user_id'])
    bookings = db.get_user_bookings(user_id=session['user_id'], email=session.get('user_email'))
    return render_template('my_bookings.html', user=user, bookings=bookings)

@app.route('/admin')
@admin_required
def admin_dashboard():
    temple = request.args.get('temple', 'all')
    status = request.args.get('status', 'all')
    search = request.args.get('q', '').strip()
    
    stats = db.get_admin_dashboard_stats()
    bookings = db.get_all_bookings(filter_temple=temple, filter_status=status, search_term=search)
    return render_template('admin.html', stats=stats, bookings=bookings, current_temple=temple, current_status=status, current_query=search)

@app.route('/receipt/<booking_ref>')
def receipt(booking_ref):
    booking = db.get_booking_by_ref(booking_ref)
    if not booking:
        booking = db.get_latest_booking()
    if not booking:
        flash("Pass reference not found.", "warning")
        return redirect(url_for('home'))
    return render_template('receipt.html', booking=booking)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/confirmation')
def confirmation():
    ref = request.args.get('ref')
    booking = None
    if ref:
        booking = db.get_booking_by_ref(ref)
    if not booking and session.get('user_id'):
        booking = db.get_latest_booking(user_id=session.get('user_id'))
    if not booking and session.get('user_email'):
        booking = db.get_latest_booking(email=session.get('user_email'))
    if not booking:
        booking = db.get_latest_booking()
        
    return render_template('confirmation.html', booking=booking)

@app.route('/tc')
def tc():
    return render_template('tc.html')

@app.route('/kanaka_durgamma')
def kanaka_durgamma():
    return render_template("kanaka_durgamma.html")

@app.route('/tirupathi_deva')
def tirupathi_deva():
    return render_template("tirupathi_deva.html")

@app.route('/srilakshmitirupathiamma')
def srilakshmitirupathiamma():
    return render_template("srilakshmitirupathiamma.html")

@app.route('/paiddarshan')
@app.route('/paid_darshan')
def paid_darshan():
    return render_template("paiddarshan.html")

@app.route('/vip_darshan')
def vip_darshan():
    return render_template("vip_darshan.html")

@app.route('/free_darshan')
def free_darshan():
    return render_template("free_darshan.html")

@app.route('/roombooking')
def room_booking():
    return render_template("roombooking.html")

@app.route('/prasadbooking')
def prasad_booking():
    return render_template("prasadbooking.html")

@app.route('/foodbooking')
def food_booking():
    return render_template("foodbooking.html")

@app.route('/taxibooking')
def taxi_booking():
    return render_template("taxibooking.html")

@app.route('/vehicle')
def vehicle_parking():
    return render_template("vehicle.html")

@app.route('/paid_payment')
def paid_payment():
    return render_template('paidpayment.html')

@app.route('/room_payment')
def room_payment():
    return render_template('room_payment.html')

@app.route('/vehicle_payment')
def vehicle_payment():
    return render_template('vehicle_payment.html')

@app.route('/save_booking', methods=['POST'])
def save_booking():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            data = request.form.to_dict()
            
        user_id = session.get('user_id')
        booking = db.create_booking(data, user_id=user_id)
        
        return jsonify({
            'message': 'Booking details saved successfully!',
            'booking_ref': booking['booking_ref'],
            'booking': booking
        }), 200
    except Exception as e:
        print("Error saving booking:", e)
        return jsonify({'error': f'Failed to save booking: {str(e)}'}), 500

@app.route('/api/checkin/<booking_ref>', methods=['POST'])
def api_checkin(booking_ref):
    booking = db.get_booking_by_ref(booking_ref)
    if not booking:
        return jsonify({'success': False, 'error': f'Booking reference {booking_ref} not found.'}), 404
        
    if booking['booking_status'] == 'Cancelled':
        return jsonify({'success': False, 'error': 'This booking was cancelled and cannot be admitted.'}), 400
        
    success = db.update_booking_status(booking_ref, 'Checked-In')
    updated = db.get_booking_by_ref(booking_ref)
    return jsonify({'success': success, 'booking': updated})

@app.route('/api/cancel/<booking_ref>', methods=['POST'])
def api_cancel(booking_ref):
    booking = db.get_booking_by_ref(booking_ref)
    if not booking:
        return jsonify({'success': False, 'error': 'Booking not found.'}), 404
        
    success = db.update_booking_status(booking_ref, 'Cancelled')
    return jsonify({'success': success, 'booking_ref': booking_ref})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 4450))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1')
    app.run(host='0.0.0.0', port=port, debug=debug_mode, use_reloader=False)
