import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import timedelta

# Import the database object and models from your models.py
from models import db, User, Track, Podcast, Playlist 

# 1. Day 1: Project Setup & Environment [cite: 44]
load_dotenv()
app = Flask(__name__)

# Flask-CORS setup to allow React frontend connection 
CORS(app, resources={r"/*": {"origins": "https://echo-music-one.vercel.app"}})

# 1. Ensure this import is at the very top of app.py
from sqlalchemy.pool import NullPool

# 2. Replace your current app.config for DB with this:
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. Add this SPECIFIC engine configuration for Supabase Poolers
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "poolclass": NullPool,
    "connect_args": {
        "options": "-c client_encoding=utf8",
        "connect_timeout": 10
    }
}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-JWT-Extended setup for Day 3 Authentication 
app.config['JWT_SECRET_KEY'] = 'super-secret-key-music-app' 
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize Database and JWT plugins
db.init_app(app)
jwt = JWTManager(app)

# Automatically create PostgreSQL tables in Supabase [cite: 58]
with app.app_context():
    db.create_all()
    print("🚀 Database tables (Users, Tracks, Podcasts, Playlists) created in Supabase!")

# --- Day 3: Authentication APIs [cite: 63] ---

@app.route('/register', methods=['POST'])
def register():
    """Register a new user with hashed password [cite: 65, 66]"""
    data = request.get_json()
    
    # Check if user already exists
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"msg": "Username already exists"}), 400
    
    # Securely hash the password [cite: 66]
    hashed_pw = generate_password_hash(data.get('password'))
    
    new_user = User(
        username=data.get('username'), 
        email=data.get('email'), 
        password_hash=hashed_pw
    )
    
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    """JWT-based login system [cite: 67]"""
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and check_password_hash(user.password_hash, data.get('password')):
        # Create token for authenticated access [cite: 70]
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token), 200
    
    return jsonify({"msg": "Invalid credentials"}), 401

# --- Day 4: Music & Podcast Listing APIs [cite: 72] ---

@app.route('/tracks', methods=['GET'])
def get_tracks():
    """Fetch all music tracks [cite: 74]"""
    tracks = Track.query.all()
    output = []
    for track in tracks:
        output.append({
            "id": track.id,
            "title": track.title, 
            "artist": track.artist,
            "audio_url": track.audio_url,
            "cover_image": track.cover_image,
            "category": track.category
        })
    return jsonify(output), 200

@app.route('/')
def home():
    return {"message": "Music App Backend is Running!"}

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
