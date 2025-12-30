import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import timedelta
from sqlalchemy.pool import NullPool

# Import the database object and models from your models.py
from models import db, User, Track, Podcast, Playlist 

load_dotenv()
app = Flask(__name__)

# 1. CORS Setup - Allowing your specific Vercel frontend
CORS(app, resources={r"/*": {"origins": "https://echo-music-one.vercel.app"}})

# 2. Database Configuration for Supabase Production
# Using the connection string from your environment variables
db_url = os.getenv('DATABASE_URL')


if not db_url:
    db_url = "postgresql://postgres.ssyidhjxkkabjhmomdfq:Aakshu&teju12@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"


app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    
# Essential for Supabase to prevent connection hanging on the free tier
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "poolclass": NullPool,
    "connect_args": {
        "options": "-c client_encoding=utf8",
        "connect_timeout": 10
    }
}

# 3. JWT Security Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', '7625F73F-7455-4886-82A3-C02D51F3CA4C')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize Plugins
db.init_app(app)
jwt = JWTManager(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()
    print("🚀 Database tables verified and ready in Supabase!")

# --- AUTHENTICATION ROUTES ---

@app.route('/register', methods=['POST'])
def register():
    """Handles new user registration with JSON payload"""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Missing username or password"}), 400

    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"error": "Username already exists"}), 400
    
    hashed_pw = generate_password_hash(data.get('password'))
    new_user = User(
        username=data.get('username'), 
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
    """Handles JWT login"""
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and check_password_hash(user.password_hash, data.get('password')):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token), 200
    
    return jsonify({"error": "Invalid username or password"}), 401

# --- CONTENT ROUTES ---

@app.route('/tracks', methods=['GET'])
def get_tracks():
    """Fetch music tracks from Supabase"""
    try:
        tracks = Track.query.all()
        return jsonify([{
            "id": t.id,
            "title": t.title, 
            "artist": t.artist,
            "audio_url": t.audio_url,
            "cover_image": t.cover_image,
            "category": t.category
        } for t in tracks]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return {"status": "online", "message": "Echo Music API is active"}

# 4. Production Entry Point for Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)