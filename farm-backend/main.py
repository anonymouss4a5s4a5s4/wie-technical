from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import sqlite3
import hashlib
from fastapi import File, UploadFile
import base64
import json
import jwt
from contextlib import contextmanager

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

app = FastAPI(title="Farm Worker Portal API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Database setup
@contextmanager
def get_db():
    conn = sqlite3.connect('farm_portal.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Certificates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS certificates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cert_number TEXT UNIQUE NOT NULL,
                farmer_name TEXT NOT NULL,
                farm_name TEXT NOT NULL,
                level TEXT NOT NULL,
                status TEXT DEFAULT 'Active',
                issued_date DATE NOT NULL,
                valid_until DATE NOT NULL,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Complaints table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                complaint_id TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                category TEXT NOT NULL,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'New',
                ai_classification TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Ratings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                farmer_id INTEGER NOT NULL,
                transport_rating INTEGER,
                conditions_rating INTEGER,
                equipment_rating INTEGER,
                wages_rating INTEGER,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (farmer_id) REFERENCES users(id)
            )
        ''')
        cursor.execute('''
    CREATE TABLE IF NOT EXISTS face_encodings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        face_encoding TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')
        
        conn.commit()
        
        # Insert demo data
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # Hash password (simple hash for demo - use bcrypt in production)
            admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
            worker_pass = hashlib.sha256("worker123".encode()).hexdigest()
            farmer_pass = hashlib.sha256("farmer123".encode()).hexdigest()
            
            cursor.execute("INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
                         ("admin", admin_pass, "admin", "Admin User"))
            cursor.execute("INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
                         ("worker1", worker_pass, "worker", "John Worker"))
            cursor.execute("INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
                         ("farmer1", farmer_pass, "farmer", "Ahmed Ben Salem"))
            
            # Insert demo certificates
            cursor.execute("""
                INSERT INTO certificates (cert_number, farmer_name, farm_name, level, status, issued_date, valid_until, user_id)
                VALUES ('CERT-2025-001', 'Ahmed Ben Salem', 'Green Valley Farm', 'Gold', 'Active', '2025-01-01', '2025-12-31', 3)
            """)
            
            cursor.execute("""
                INSERT INTO certificates (cert_number, farmer_name, farm_name, level, status, issued_date, valid_until)
                VALUES ('CERT-2025-002', 'Fatima Khelifi', 'Sunrise Orchards', 'Gold', 'Active', '2025-01-05', '2025-12-31')
            """)
            
            # Insert demo complaints
            cursor.execute("""
                INSERT INTO complaints (complaint_id, user_id, category, subject, description, status, ai_classification)
                VALUES ('CPL-001', 2, 'Transportation', 'Vehicle Overcrowding', 'Too many workers in one vehicle', 'New', 'Safety Risk - High Priority')
            """)
            
            conn.commit()

# Pydantic models
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class ComplaintCreate(BaseModel):
    category: str
    subject: str
    description: str

class ComplaintUpdate(BaseModel):
    status: str

class RatingCreate(BaseModel):
    farmer_id: int
    transport_rating: int
    conditions_rating: int
    equipment_rating: int
    wages_rating: int
    comments: Optional[str] = None

class CertificateCreate(BaseModel):
    farmer_name: str
    farm_name: str
    level: str
    valid_until: str

# Helper functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (payload.get("user_id"),))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return dict(user)

# Routes
@app.on_event("startup")
def startup():
    init_db()

@app.post("/auth/login", response_model=Token)
def login(credentials: UserLogin):
    with get_db() as conn:
        cursor = conn.cursor()
        hashed_password = hashlib.sha256(credentials.password.encode()).hexdigest()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                      (credentials.username, hashed_password))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token({
            "user_id": user["id"],
            "username": user["username"],
            "role": user["role"]
        })
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": user["role"]
        }

@app.get("/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

# Complaints endpoints
@app.post("/complaints")
def create_complaint(complaint: ComplaintCreate, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        complaint_id = f"CPL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cursor.execute("""
            INSERT INTO complaints (complaint_id, user_id, category, subject, description, status)
            VALUES (?, ?, ?, ?, ?, 'New')
        """, (complaint_id, current_user["id"], complaint.category, complaint.subject, complaint.description))
        
        conn.commit()
        return {"complaint_id": complaint_id, "status": "submitted"}

@app.get("/complaints")
def get_complaints(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        
        if current_user["role"] == "admin":
            cursor.execute("SELECT * FROM complaints ORDER BY created_at DESC")
        else:
            cursor.execute("SELECT * FROM complaints WHERE user_id = ? ORDER BY created_at DESC", 
                          (current_user["id"],))
        
        complaints = [dict(row) for row in cursor.fetchall()]
        return complaints

@app.patch("/complaints/{complaint_id}")
def update_complaint(complaint_id: str, update: ComplaintUpdate, 
                     current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update complaints")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE complaints SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE complaint_id = ?
        """, (update.status, complaint_id))
        conn.commit()
        
        return {"message": "Complaint updated successfully"}

# Certificates endpoints
@app.get("/certificates")
def get_certificates(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM certificates WHERE status = 'Active'")
        certificates = [dict(row) for row in cursor.fetchall()]
        return certificates

@app.get("/certificates/{cert_number}")
def verify_certificate(cert_number: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM certificates WHERE cert_number = ?", (cert_number,))
        cert = cursor.fetchone()
        
        if not cert:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        return dict(cert)

@app.post("/certificates")
def create_certificate(cert: CertificateCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can issue certificates")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cert_number = f"CERT-{datetime.now().strftime('%Y')}-{cursor.execute('SELECT COUNT(*) FROM certificates').fetchone()[0] + 1:03d}"
        
        cursor.execute("""
            INSERT INTO certificates (cert_number, farmer_name, farm_name, level, issued_date, valid_until)
            VALUES (?, ?, ?, ?, DATE('now'), ?)
        """, (cert_number, cert.farmer_name, cert.farm_name, cert.level, cert.valid_until))
        
        conn.commit()
        return {"cert_number": cert_number, "status": "issued"}

@app.delete("/certificates/{cert_number}")
def revoke_certificate(cert_number: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can revoke certificates")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE certificates SET status = 'Revoked' WHERE cert_number = ?", (cert_number,))
        conn.commit()
        
        return {"message": "Certificate revoked"}

# Ratings endpoints
@app.post("/ratings")
def create_rating(rating: RatingCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "worker":
        raise HTTPException(status_code=403, detail="Only workers can submit ratings")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ratings (user_id, farmer_id, transport_rating, conditions_rating, 
                               equipment_rating, wages_rating, comments)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (current_user["id"], rating.farmer_id, rating.transport_rating, 
              rating.conditions_rating, rating.equipment_rating, 
              rating.wages_rating, rating.comments))
        
        conn.commit()
        return {"message": "Rating submitted successfully"}

@app.get("/ratings/farmer/{farmer_id}")
def get_farmer_ratings(farmer_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT AVG(transport_rating) as avg_transport,
                   AVG(conditions_rating) as avg_conditions,
                   AVG(equipment_rating) as avg_equipment,
                   AVG(wages_rating) as avg_wages,
                   COUNT(*) as total_ratings
            FROM ratings WHERE farmer_id = ?
        """, (farmer_id,))
        
        result = cursor.fetchone()
        return dict(result) if result else {}

# Analytics endpoint
@app.get("/analytics/stats")
def get_analytics(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view analytics")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM certificates WHERE status = 'Active'")
        active_certs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'worker'")
        total_workers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as total FROM complaints WHERE status IN ('New', 'In Review')")
        pending_complaints = cursor.fetchone()[0]
        
        cursor.execute("SELECT category, COUNT(*) as count FROM complaints GROUP BY category")
        complaints_by_category = [dict(row) for row in cursor.fetchall()]
        
        return {
            "active_certificates": active_certs,
            "total_workers": total_workers,
            "pending_complaints": pending_complaints,
            "complaints_by_category": complaints_by_category
        }
@app.post("/face/register")
async def register_face(user_id: int, face_data: str, current_user: dict = Depends(get_current_user)):
    """Store face encoding for a user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO face_encodings (user_id, face_encoding)
            VALUES (?, ?)
        """, (user_id, face_data))
        conn.commit()
        return {"message": "Face registered successfully"}

@app.post("/face/verify")
async def verify_face(face_data: str):
    """Verify face against stored encodings"""
    # In production, you would:
    # 1. Extract face encoding from face_data
    # 2. Compare with stored encodings
    # 3. Find best match using face comparison algorithm
    
    # For demo, we'll simulate verification
    with get_db() as conn:
        cursor = conn.cursor()
        # Simple simulation - in production use face_recognition library
        cursor.execute("""
            SELECT u.*, fe.face_encoding 
            FROM users u 
            JOIN face_encodings fe ON u.id = fe.user_id
            LIMIT 1
        """)
        user = cursor.fetchone()
        
        if user:
            # Simulate successful match
            access_token = create_access_token({
                "user_id": user["id"],
                "username": user["username"],
                "role": user["role"]
            })
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "role": user["role"],
                "username": user["username"]
            }
        else:
            raise HTTPException(status_code=404, detail="No matching face found")

@app.get("/face/users")
async def get_face_registered_users(current_user: dict = Depends(get_current_user)):
    """Get list of users with registered faces"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.username, u.full_name, u.role, COUNT(fe.id) as face_count
            FROM users u
            LEFT JOIN face_encodings fe ON u.id = fe.user_id
            GROUP BY u.id
        """)
        users = [dict(row) for row in cursor.fetchall()]
        return users

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)