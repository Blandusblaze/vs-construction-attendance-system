# VS Construction - Attendance Management System

"You Dream It, We Build It!"

## Features

- 📸 **Dual Camera Capture** - Front and rear camera photos
- 📍 **GPS Location Tracking** - Automatic location capture with city name
- 👥 **User Management** - Admin panel to add/manage users
- ✅ **Check-in/Check-out** - Easy attendance tracking
- 📊 **Dashboard** - View attendance history and reports
- 🔒 **Secure** - Role-based access control

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **APIs**: HTML5 Geolocation, MediaDevices API

## Local Setup

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/vs-construction-attendance.git
cd vs-construction-attendance

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

Access at: `http://localhost:5000`

**Default Admin Login:**
- Username: `admin`
- Password: `admin123`

## Deployment

### Deployed on Render.com

Live URL: `https://vs-construction-attendance.onrender.com`

### Environment Variables

- `SECRET_KEY` - Flask secret key (auto-generated on Render)
- `DATABASE_URL` - PostgreSQL connection string (optional)

## Usage

### Admin
1. Login with admin credentials
2. Add users via "Add New User" form
3. View all attendance records
4. Monitor team check-ins/check-outs

### Users
1. Login with provided credentials
2. Click "Check In Now"
3. Allow camera and location permissions
4. Follow 3-step process (Front camera → Rear camera → Location)
5. Check out when done

## Project Structure

```
vs-construction-attendance/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── render.yaml              # Render deployment config
├── templates/               # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── admin_dashboard.html
│   ├── user_dashboard.html
│   └── checkin.html
└── static/                  # Static files
    ├── logo.png
    └── uploads/             # User photos
```

## Security

- Passwords are hashed using Werkzeug
- Session-based authentication with Flask-Login
- Role-based access control (Admin/User)
- HTTPS enforced in production

## Browser Requirements

- Chrome/Edge (Recommended)
- Firefox
- Safari (iOS may have camera limitations)
- Requires camera and location permissions

## License

Proprietary - VS Construction

## Support

For issues or questions, contact: your.email@example.com

---

**VS Construction** - Building Tomorrow, Today! 🏗️