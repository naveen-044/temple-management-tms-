from pymongo import MongoClient
import certifi
import os
import json
import random
from datetime import datetime, date
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load local environment variables from .env
load_dotenv()

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/temple_management')
DB_NAME = os.environ.get('DB_NAME', 'temple_management')

client = None
db_conn = None

def get_mongo_db():
    global client, db_conn
    if db_conn is not None:
        return db_conn
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=6000)
        db_conn = client[DB_NAME]
        return db_conn
    except Exception as e:
        print("MongoDB connection error:", e)
        return None

def serialize_doc(doc):
    if not doc:
        return None
    doc = dict(doc)
    if '_id' in doc:
        doc['id'] = str(doc['_id'])
        doc['_id'] = str(doc['_id'])
    return doc

def init_db():
    db = get_mongo_db()
    if db is None:
        print("Warning: Could not connect to MongoDB during init_db.")
        return
        
    try:
        # Create indexes
        db.users.create_index("email", unique=True)
        db.bookings.create_index("booking_ref", unique=True)
        
        # Seed default admin user if not exists
        if not db.users.find_one({"email": "admin@temple.org"}):
            admin_hash = generate_password_hash("admin123")
            db.users.insert_one({
                "name": "Sri Temple Administrator",
                "email": "admin@temple.org",
                "phone": "9876543210",
                "aadhar": "999988887777",
                "city": "Tirupati",
                "password_hash": admin_hash,
                "role": "admin",
                "created_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            })
            
        print("MongoDB initialized successfully with collections: users, bookings")
    except Exception as e:
        print("MongoDB init error:", e)

def create_user(name, email, phone, aadhar, city, password, role='devotee'):
    db = get_mongo_db()
    if db is None:
        return None, "Database unavailable."
    try:
        clean_email = email.strip().lower()
        if db.users.find_one({"email": clean_email}):
            return None, "Email address is already registered."
            
        password_hash = generate_password_hash(password)
        res = db.users.insert_one({
            "name": name,
            "email": clean_email,
            "phone": phone,
            "aadhar": aadhar,
            "city": city,
            "password_hash": password_hash,
            "role": role,
            "created_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        })
        return str(res.inserted_id), None
    except Exception as e:
        return None, str(e)

def authenticate_user(email, password):
    db = get_mongo_db()
    if db is None:
        return None
    try:
        user = db.users.find_one({"email": email.strip().lower()})
        if user and check_password_hash(user.get('password_hash', ''), password):
            return serialize_doc(user)
        return None
    except Exception as e:
        print("Auth error:", e)
        return None

def get_user_by_id(user_id):
    db = get_mongo_db()
    if db is None or not user_id:
        return None
    try:
        if ObjectId.is_valid(user_id):
            user = db.users.find_one({"_id": ObjectId(user_id)})
        else:
            user = db.users.find_one({"id": user_id}) or db.users.find_one({"email": user_id})
        return serialize_doc(user)
    except Exception as e:
        print("get_user_by_id error:", e)
        return None

def generate_booking_ref(temple_name):
    prefix = "TMP"
    if "Tirupathi" in temple_name or "Tirupati" in temple_name or "TTD" in temple_name:
        prefix = "TTD"
    elif "Kanaka" in temple_name or "Durgamma" in temple_name:
        prefix = "KDK"
    elif "Lakshmi" in temple_name:
        prefix = "SLT"
    rand_num = random.randint(10000, 99999)
    return f"{prefix}-{rand_num}"

def create_booking(data, user_id=None):
    db = get_mongo_db()
    if db is None:
        raise Exception("Database connection failed.")
        
    temple = data.get('temple_name', 'Tirumala Tirupathi Devasthanam')
    booking_ref = generate_booking_ref(temple)
    
    service_type = data.get('service_type', 'Paid Darshan')
    qty = int(data.get('quantity', 1) or 1)
    unit_price = float(data.get('unit_price', 0.0) or 0.0)
    
    if unit_price == 0.0:
        if 'Paid' in service_type or 'Special Entry' in service_type:
            unit_price = 350.0
        elif 'VIP' in service_type:
            unit_price = 500.0
        elif 'Room' in service_type:
            unit_price = 1200.0
        elif 'Prasad' in service_type:
            unit_price = 50.0
        elif 'Taxi' in service_type:
            unit_price = 850.0
        elif 'Vehicle' in service_type:
            unit_price = 150.0
        elif 'Free' in service_type:
            unit_price = 0.0
            
    total_amount = float(data.get('total_amount', unit_price * qty))
    
    extra_details = data.get('extra_details')
    if isinstance(extra_details, str):
        try:
            extra_details = json.loads(extra_details)
        except Exception:
            extra_details = {}
    elif not isinstance(extra_details, dict):
        extra_details = {}
        
    doc = {
        "booking_ref": booking_ref,
        "user_id": str(user_id) if user_id else None,
        "devotee_name": data.get('name') or data.get('devotee_name', 'Devotee'),
        "email": (data.get('email') or '').strip().lower(),
        "phone": data.get('phone', ''),
        "aadhar": data.get('adhar') or data.get('aadhar', ''),
        "age": int(data.get('age', 30) or 30),
        "temple_name": temple,
        "service_type": service_type,
        "service_date": data.get('dates') or data.get('service_date', str(date.today())),
        "slot_time": data.get('slot_time', '09:00 AM - 11:00 AM'),
        "quantity": qty,
        "unit_price": unit_price,
        "total_amount": total_amount,
        "extra_details": extra_details,
        "payment_status": data.get('payment_status', 'Completed'),
        "payment_method": data.get('payment_method', 'UPI'),
        "booking_status": data.get('booking_status', 'Confirmed'),
        "checkin_time": None,
        "created_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    res = db.bookings.insert_one(doc)
    doc['id'] = str(res.inserted_id)
    doc['_id'] = str(res.inserted_id)
    return doc

def get_booking_by_ref(booking_ref):
    db = get_mongo_db()
    if db is None:
        return None
    doc = db.bookings.find_one({"booking_ref": booking_ref})
    return serialize_doc(doc)

def get_latest_booking(user_id=None, email=None):
    db = get_mongo_db()
    if db is None:
        return None
    query = {}
    if user_id:
        query["user_id"] = str(user_id)
    elif email:
        query["email"] = email.strip().lower()
    doc = db.bookings.find_one(query, sort=[("created_at", -1)])
    return serialize_doc(doc)

def get_user_bookings(user_id=None, email=None):
    db = get_mongo_db()
    if db is None:
        return []
    query = {}
    if user_id and email:
        query = {"$or": [{"user_id": str(user_id)}, {"email": email.strip().lower()}]}
    elif user_id:
        query = {"user_id": str(user_id)}
    elif email:
        query = {"email": email.strip().lower()}
        
    cursor = db.bookings.find(query).sort("created_at", -1)
    return [serialize_doc(d) for d in cursor]

def get_all_bookings(filter_temple=None, filter_status=None, search_term=None):
    db = get_mongo_db()
    if db is None:
        return []
    query = {}
    if filter_temple and filter_temple != 'all':
        query["temple_name"] = {"$regex": filter_temple, "$options": "i"}
    if filter_status and filter_status != 'all':
        query["booking_status"] = filter_status
    if search_term:
        query["$or"] = [
            {"booking_ref": {"$regex": search_term, "$options": "i"}},
            {"devotee_name": {"$regex": search_term, "$options": "i"}},
            {"phone": {"$regex": search_term, "$options": "i"}},
            {"email": {"$regex": search_term, "$options": "i"}}
        ]
        
    cursor = db.bookings.find(query).sort("created_at", -1)
    return [serialize_doc(d) for d in cursor]

def update_booking_status(booking_ref, status):
    db = get_mongo_db()
    if db is None:
        return False
    update_data = {"booking_status": status}
    if status == 'Checked-In':
        update_data["checkin_time"] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    res = db.bookings.update_one({"booking_ref": booking_ref}, {"$set": update_data})
    return res.modified_count > 0

def get_admin_dashboard_stats():
    db = get_mongo_db()
    if db is None:
        return {
            'total_bookings': 0, 'total_pilgrims': 0, 'total_revenue': 0.0,
            'today_bookings': 0, 'checked_in': 0, 'total_users': 0
        }
        
    total_bookings = db.bookings.count_documents({"booking_status": {"$ne": "Cancelled"}})
    pipeline_agg = [
        {"$match": {"booking_status": {"$ne": "Cancelled"}}},
        {"$group": {
            "_id": None,
            "total_pilgrims": {"$sum": "$quantity"},
            "total_revenue": {"$sum": "$total_amount"}
        }}
    ]
    agg_res = list(db.bookings.aggregate(pipeline_agg))
    total_pilgrims = agg_res[0]["total_pilgrims"] if agg_res else 0
    total_revenue = agg_res[0]["total_revenue"] if agg_res else 0.0
    
    today_str = str(date.today())
    today_bookings = db.bookings.count_documents({"service_date": {"$regex": today_str}})
    checked_in = db.bookings.count_documents({"booking_status": "Checked-In"})
    total_users = db.users.count_documents({"role": "devotee"})
    
    return {
        'total_bookings': total_bookings,
        'total_pilgrims': total_pilgrims,
        'total_revenue': total_revenue,
        'today_bookings': today_bookings,
        'checked_in': checked_in,
        'total_users': total_users
    }

# Initialize on import
init_db()
