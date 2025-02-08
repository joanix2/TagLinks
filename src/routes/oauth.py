from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

from src.init_db import CONNECTION

# Création du Blueprint Flask
users_bp = Blueprint('users', __name__)

@users_bp.route('/signup', methods=['POST'])
def signup():
    """
    Endpoint pour créer un nouvel utilisateur.
    """
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")

    # Vérifier si l'utilisateur existe déjà
    existing_user = CONNECTION.execute(
        "SELECT * FROM users WHERE username = ?", [username]
    ).fetchone()

    if existing_user:
        return jsonify({"error": "Nom d'utilisateur déjà pris"}), 400

    # Hacher le mot de passe avant de le stocker
    hashed_password = generate_password_hash(password)

    # Insérer l'utilisateur dans DuckDB
    CONNECTION.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)", [username, hashed_password]
    )

    return jsonify({"message": "Utilisateur créé avec succès"}), 201

@users_bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint pour s'authentifier et obtenir un token JWT.
    """
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")

    # Vérifier si l'utilisateur existe
    user = CONNECTION.execute(
        "SELECT * FROM users WHERE username = ?", [username]
    ).fetchone()

    if not user:
        return jsonify({"error": "Nom d'utilisateur ou mot de passe incorrect"}), 401

    user_id, db_username, db_password = user

    # Vérifier le mot de passe
    if not check_password_hash(db_password, password):
        return jsonify({"error": "Nom d'utilisateur ou mot de passe incorrect"}), 401

    # Créer un token JWT
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

@users_bp.route('/check-duckdb', methods=['GET'])
def check_duckdb():
    """
    Vérifie la connexion à la base de données DuckDB.
    """
    try:
        # Tester la connexion en listant les tables
        tables = CONNECTION.execute("SHOW TABLES").fetchall()
        return jsonify({
            "message": "Connexion à DuckDB réussie.",
            "tables": [table[0] for table in tables]
        }), 200
    except Exception as e:
        return jsonify({
            "message": "Impossible de se connecter à DuckDB.",
            "error": str(e)
        }), 500
