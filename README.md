# ⚙️ Echo - Backend API

This is the Flask-based REST API for **Echo**, a full-stack music streaming application. It manages user authentication, music metadata, and playlist relationships using a PostgreSQL database.

## 🛠️ Tech Stack

* **Python/Flask**: Core web framework.
* **SQLAlchemy**: ORM for PostgreSQL database management.
* **Flask-JWT-Extended**: Secure authentication and identity management.
* **Supabase (PostgreSQL)**: Managed cloud database with connection pooling.
* **Render**: Automated web service deployment.

## 🗄️ Database Schema

The database consists of five main tables to handle the streaming logic:

1.  **Users**: Stores hashed credentials and profile data.
2.  **Tracks**: Contains audio URLs and song metadata.
3.  **Playlists**: Stores user-created playlist names.
4.  **PlaylistTracks**: A join table linking tracks to playlists for many-to-many relationships.
5.  **RecentlyPlayed**: Tracks user history.



## 📡 API Endpoints

### Authentication
* `POST /register` - Creates a new user with hashed passwords.
* `POST /login` - Returns a JWT access token.

### Tracks
* `GET /tracks` - Fetches the global music library.

### Playlists (JWT Protected)
* `GET /playlists` - Fetches all playlists for the logged-in user.
* `POST /playlists` - Creates a new empty playlist.
* `GET /playlists/<id>/tracks` - Fetches tracks within a specific playlist.
* `POST /playlists/<id>/tracks` - Adds a song to a playlist (prevents duplicates).
* `DELETE /playlists/<id>/tracks/<id>` - Removes a song from a specific playlist.

## 🚀 Deployment

The API is configured with `NullPool` to ensure compatibility with Supabase's transaction pooler, preventing "Too many clients" errors during high traffic.

**Production URL:** `https://echo-backend-0rw1.onrender.com`
