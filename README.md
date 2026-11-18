# Temple Management System (TMS)

A modern, full-stack Temple Management web application built with **Python (Flask)**, **MongoDB**, and **Bootstrap 5**. Designed for temple devasthanams and pilgrimage trust boards to provide seamless digital services for devotees and robust operational controls for temple administration staff.

---

## 🌟 Key Features

### 1. Devotee Portal & Authentication
- **Secure Authentication:** User registration (`/signup`) and authentication (`/login`) with session management and password hashing via Werkzeug.
- **My Bookings Dashboard:** Devotees can view their past and upcoming darshan passes, service tickets, and live check-in statuses at `/my-bookings`.
- **Clean Devotee Experience:** Clean, minimal, non-cluttered user interface free of administrative controls or intrusive elements.

### 2. Pilgrim Booking Services
- **Darshan Options:**
  - **Free Dharma Darshan:** Queue token allotment with dynamic reporting slots.
  - **Special Entry Darshan (₹350):** Fast-track darshan with quota availability indicators.
  - **VIP Protocol Darshan (₹1,000):** Sanctum sanctorum access with priority accompaniment.
- **Temple Amenities & Sevas:**
  - **Prasadam Seva:** Laddu, Vada, and Pulihora counter pre-booking.
  - **Annadanam (Nitya Anna Prasadam):** Complimentary food token issuing.
  - **Guest House & Cottages:** Room reservations across various pilgrim choultries.
  - **Transport & Vehicles:** Temple taxi dispatch and gated parking slot passes.

### 3. Official Digital E-Pass (Receipt)
- **Gate Pass Generation:** Printable, official digital entry pass (`/receipt/<ref>`).
- **Security Codes:** Dynamic 2D QR Code and Code-128 barcode referencing the booking ID (e.g., `TTD-78214`).
- **Reporting Details:** Devotee credentials, allotted gate, reporting time, and verification instructions.

### 4. Administrative Command Center (`/admin`)
- **Protected Access:** Strictly restricted via `@admin_required` access control.
- **Executive Telemetry:** Real-time metrics for total bookings, footfall, revenue collected (₹), today's darshan volume, and checked-in counts.
- **Gate Security Scanner:** Allows temple gate officers to verify and check in pilgrims in real time (`/api/checkin/<booking_ref>`).
- **Master Registry & Audit:** Filterable, searchable booking registry with instant CSV export and print view.

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/naveen-044/temple-management-tms-.git
cd temple-management-tms-
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Update `.env` with your MongoDB URI:
```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=temple_management
SECRET_KEY=your_secret_key_here
PORT=4450
```

### 5. Run the Application
```bash
python app.py
```
Open your browser at `http://127.0.0.1:4450`.

---

## 🔐 Administrative Credentials

The system seeds a default administrator account upon database initialization:

- **Login URL:** `/login`
- **Email:** `admin@temple.org`
- **Password:** `admin123`
- **Admin Dashboard:** `/admin`

---

## 📂 Project Structure

```text
├── app.py                  # Core Flask application, routing, and security decorators
├── db.py                   # MongoDB data abstraction layer and schema initialization
├── requirements.txt        # Python package dependencies
├── Procfile                # Production deployment process configuration
├── .env.example            # Sample configuration file for environment variables
├── .gitignore              # Git ignore rules (secrets, caches, databases)
├── static/                 # Static assets (stylesheets, logos, temple imagery, audio)
│   ├── css/style.css       # Clean, modern, responsive styling
│   └── ...
└── template/               # Jinja2 HTML templates
    ├── base.html           # Unified navigation bar and layout frame
    ├── index.html          # Homepage with temple showcase and services
    ├── login.html          # Devotee & staff authentication portal
    ├── signup.html         # Pilgrim account registration
    ├── my_bookings.html    # Devotee personal booking ledger
    ├── admin.html          # Temple administration dashboard
    ├── receipt.html        # Official printable digital pass
    └── ...
```

---

## 🛡️ Security & Privacy

- All sensitive keys and database connection strings are managed strictly through environment variables (`.env`).
- Devotee passwords are cryptographically hashed using PBKDF2/SHA256 (`werkzeug.security`).
- Session hijacking prevention with secure server-side session cookies.

---

## 📜 License

Licensed under the MIT License.
