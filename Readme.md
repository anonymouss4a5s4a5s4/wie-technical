# Farm Worker Portal

A comprehensive web platform designed to protect agricultural workers' rights through certification, anonymous complaint systems, and employer rating mechanisms.

## 🎯 Project Overview

The Farm Worker Portal is a full-stack web application that addresses labor rights issues in agriculture by providing:

- **Certificate Management System**: Verify ethical farming practices with Gold/Silver/Bronze certifications
- **Anonymous Complaint System**: Workers can safely report workplace issues
- **Employer Rating System**: Transparent feedback mechanism for working conditions
- **Face Recognition Login**: Secure biometric authentication (demonstration mode)
- **Admin Dashboard**: Comprehensive management and analytics tools
- **Multi-role Access**: Separate portals for Workers, Farmers, and Administrators

## 🏗️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLite**: Lightweight database for data persistence
- **JWT**: Token-based authentication
- **Python 3.8+**: Core programming language

### Frontend
- **HTML5/CSS3**: Structure and styling
- **Bootstrap 5**: Responsive UI framework
- **JavaScript/jQuery**: Dynamic interactions
- **Face-API.js**: Face recognition (demonstration)
- **Chart.js**: Data visualization

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher ([Download here](https://www.python.org/downloads/))
- pip (Python package manager - comes with Python)
- A modern web browser (Chrome, Firefox, Safari, or Edge)
- Git ([Download here](https://git-scm.com/downloads))

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/farm-worker-portal.git
cd farm-worker-portal
```

### Step 2: Install Python Dependencies

```bash
pip install fastapi uvicorn[standard] pyjwt python-multipart pydantic
```

**Or install from requirements file (if provided):**
```bash
pip install -r requirements.txt
```

### Step 3: Initialize the Database

The database will be created automatically on first run. The backend includes demo data with the following test accounts:

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**Worker Account:**
- Username: `worker1`
- Password: `worker123`

**Farmer Account:**
- Username: `farmer1`
- Password: `farmer123`

### Step 4: Start the Backend Server

```bash
python main.py
```

You should see output similar to:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The API will be available at `http://localhost:8000`

### Step 5: Open the Frontend

1. Open a new terminal/command prompt
2. Navigate to the project directory
3. Start a simple HTTP server:

**Python 3:**
```bash
python -m http.server 8080
```

**Python 2:**
```bash
python -m SimpleHTTPServer 8080
```

**Or use any other local server of your choice**

4. Open your browser and navigate to:
```
http://localhost:8080/role-selection.html
```

## 📂 Project Structure

```
farm-worker-portal/
├── main.py                      # FastAPI backend server
├── api.js                       # Frontend API client
├── farm_portal.db              # SQLite database (auto-generated)
├── style.css                   # Global styles
│
├── Admin Pages
│   ├── admin-login.html        # Admin authentication
│   ├── admin-dashboard.html    # Admin overview
│   ├── manage-certificates.html # Certificate CRUD operations
│   ├── admin-complaints.html   # Complaint management
│   └── analytics.html          # System analytics
│
├── Worker Pages
│   ├── worker-dashboard.html   # Worker home
│   ├── submit-complaint.html   # File complaints
│   ├── my-complaints.html      # Track complaint status
│   ├── rate-employer.html      # Rate farming employers
│   └── certified-farmers.html  # View verified farmers
│
├── Farmer Pages
│   ├── farmer-dashboard.html   # Farmer home
│   └── view-complaints.html    # View feedback
│
└── Shared Pages
    ├── role-selection.html     # Login page
    ├── face-recognition.html   # Biometric login demo
    └── qr-verification.html    # Certificate verification
```

## 🔧 Configuration

### API URL Configuration

The frontend connects to the backend via `api.js`. The default API URL is:
```javascript
const API_URL = 'http://localhost:8000';
```

If you're running the backend on a different port or host, update this value in `api.js`.

### CORS Settings

The backend is configured to accept requests from any origin (for development):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    ...
)
```

For production, restrict this to your specific domain.

## 👥 User Roles & Features

### Admin
- Issue and revoke certificates
- View all complaints
- Update complaint status
- Access system analytics
- Manage users

### Worker
- View certified farmers
- Submit anonymous complaints
- Track complaint status
- Rate employers
- View working condition statistics

### Farmer
- View certification status
- Access complaint summaries
- Monitor ratings
- Download reports

## 🔑 Demo Credentials

Use these accounts to test different role functionalities:

| Role   | Username | Password   | Access Level |
|--------|----------|------------|--------------|
| Admin  | admin    | admin123   | Full system access |
| Worker | worker1  | worker123  | Worker portal |
| Farmer | farmer1  | farmer123  | Farmer portal |

## 📡 API Endpoints

### Authentication
- `POST /auth/login` - User authentication
- `GET /auth/me` - Get current user info

### Certificates
- `GET /certificates` - List all certificates
- `POST /certificates` - Issue new certificate (admin only)
- `GET /certificates/{cert_number}` - Verify certificate
- `DELETE /certificates/{cert_number}` - Revoke certificate (admin only)

### Complaints
- `POST /complaints` - Submit complaint
- `GET /complaints` - List complaints
- `PATCH /complaints/{complaint_id}` - Update complaint status (admin only)

### Ratings
- `POST /ratings` - Submit employer rating
- `GET /ratings/farmer/{farmer_id}` - Get farmer ratings

### Analytics
- `GET /analytics/stats` - System statistics (admin only)

## 🧪 Testing the Application

1. **Test Certificate Management:**
   - Login as admin
   - Navigate to "Manage Certificates"
   - Issue a new certificate
   - Verify the certificate using QR Verification

2. **Test Complaint System:**
   - Login as worker1
   - Submit a complaint
   - Login as admin
   - Review and update complaint status

3. **Test Rating System:**
   - Login as worker1
   - Navigate to "Rate Employer"
   - Submit ratings for different categories

## 🐛 Troubleshooting

### Backend Issues

**Error: "Address already in use"**
- Another process is using port 8000
- Kill the process or change the port in `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

**Error: "Module not found"**
- Install missing dependencies:
```bash
pip install fastapi uvicorn pyjwt python-multipart pydantic
```

**Database errors:**
- Delete `farm_portal.db` and restart the server to recreate with fresh demo data

### Frontend Issues

**Error: "Failed to fetch"**
- Ensure the backend server is running on port 8000
- Check the API_URL in `api.js`
- Check browser console for CORS errors

**Login not working:**
- Verify you're using the correct demo credentials
- Check browser console for error messages
- Clear browser cache and try again

## 🔒 Security Notes

**This is a demonstration project. For production use:**

1. Change the SECRET_KEY in `main.py`
2. Use proper password hashing (bcrypt instead of SHA256)
3. Implement rate limiting
4. Add input validation and sanitization
5. Use HTTPS for all communications
6. Restrict CORS to specific domains
7. Implement proper session management
8. Add SQL injection protection (use parameterized queries - already implemented)

## 📊 Database Schema

The application uses SQLite with the following tables:

- **users**: User accounts and authentication
- **certificates**: Farmer certifications
- **complaints**: Worker complaints and status
- **ratings**: Employer ratings from workers
- **face_encodings**: Face recognition data (demo)

## 🌐 Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📝 License

[Add your license here - MIT, Apache 2.0, etc.]

## 👨‍💻 Author

[Your Name/Team Name]

## 🤝 Contributing

This is a challenge submission project. For questions or issues, please contact [your contact info].



Built  to address agricultural worker rights and promote ethical farming practices.
