from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

users_bp = Blueprint('users', __name__)

from src.collections import users_collection, client

@users_bp.route('/signup', methods=['POST'])
def signup():
    """
    Endpoint pour créer un nouvel utilisateur.
    """
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")

    # Vérifier si l'utilisateur existe déjà
    if users_collection.find_one({"username": username}):
        return jsonify({"error": "Nom d'utilisateur déjà pris"}), 400

    # Hacher le mot de passe avant de le stocker
    hashed_password = generate_password_hash(password)

    # Insérer l'utilisateur dans la base de données
    user = {"username": username, "password": hashed_password}
    users_collection.insert_one(user)

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
    user = users_collection.find_one({"username": username})
    if not user:
        return jsonify({"error": "Nom d'utilisateur ou mot de passe incorrect"}), 401

    # Vérifier le mot de passe
    if not check_password_hash(user["password"], password):
        return jsonify({"error": "Nom d'utilisateur ou mot de passe incorrect"}), 401

    # Créer un token JWT
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200
    
@users_bp.route('/check-mongo', methods=['GET'])
def check_mongo():
    """
    Vérifie la connexion à la base de données MongoDB.
    """
    try:
        # Test de connexion en listant les bases de données
        db_list = client.list_database_names()
        return jsonify({
            "message": "Connexion à MongoDB réussie.",
            # "databases": db_list
        }), 200
    except Exception as e:
        return jsonify({
            "message": "Impossible de se connecter à MongoDB.",
            "error": str(e)
        }), 500