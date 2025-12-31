import os
from flask import Flask, request, jsonify
from flask_cors import CORS
# FIXED: Added missing imports for JWT
from flask_jwt_extended import (
    JWTManager, create_access_token, 
    jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import timedelta
from sqlalchemy.pool import NullPool

# Import the database object and models from your models.py
from models import db, User, Track, Podcast, Playlist 

load_dotenv()
app = Flask(__name__)

# 1. CORS Setup - Allowing all origins for cross-platform compatibility
CORS(app, resources={r"/*": {"origins": "*"}})

# 2. Database Configuration
db_url = os.getenv('DATABASE_URL')
if not db_url:
    # Fallback to your direct connection string if environment variable is missing
    db_url = "postgresql://postgres.ssydihjxkkabjhmomdfq:Aakshu&teju12@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Essential for Supabase free tier to prevent "Too many clients" errors
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "poolclass": NullPool,
    "connect_args": {
        "options": "-c client_encoding=utf8",
        "connect_timeout": 10,
        "prepare_threshold": None
    }
}

# 3. JWT Security Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', '7625F73F-7455-4886-82A3-C02D51F3CA4C')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize Plugins
db.init_app(app)
jwt = JWTManager(app)

# Create tables if they don't exist in Supabase
with app.app_context():
    db.create_all()
    print("🚀 Database tables verified and ready in Supabase!")

# --- AUTHENTICATION ROUTES ---

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    
    # Secure password hashing
    hashed_pw = generate_password_hash(password)
    new_user = User(
        username=username, 
        email=email, # Fixed: Includes email to avoid NotNullViolation
        password_hash=hashed_pw
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and check_password_hash(user.password_hash, data.get('password')):
        # Identity must be a string for JWT identity
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token), 200
    
    return jsonify({"error": "Invalid username or password"}), 401

# --- CONTENT ROUTES ---

@app.route('/tracks', methods=['GET'])
def get_tracks():
    """Fetch music tracks and format keys for the Player GUI"""
    try:
        tracks = Track.query.all()
        return jsonify([{
            "id": t.id,
            "title": t.title, 
            "artist": t.artist,
            "url": t.audio_url,     # Key matched to Player.jsx
            "cover_url": t.cover_image, # Key matched to Player.jsx
            "category": t.category
        } for t in tracks]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- PLAYLIST ROUTES ---

@app.route('/playlists', methods=['GET'])
@jwt_required()
def get_playlists():
    """Fetch playlists owned by the logged-in user"""
    user_id = get_jwt_identity()
    user_playlists = Playlist.query.filter_by(user_id=user_id).all()
    return jsonify([{"id": p.id, "name": p.name} for p in user_playlists]), 200

@app.route('/playlists', methods=['POST'])
@jwt_required()
def create_playlist():
    """Create a new manual playlist"""
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name')
    
    if not name:
        return jsonify({"error": "Playlist name is required"}), 400

    new_playlist = Playlist(name=name, user_id=user_id)
    try:
        db.session.add(new_playlist)
        db.session.commit()
        return jsonify({"id": new_playlist.id, "name": new_playlist.name}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return {"status": "online", "message": "Echo Music API is active"}

# 4. Production Entry Point for Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)