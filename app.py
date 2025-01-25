import os
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash

from src.mongo import connect_to_mongo, get_or_create_collection

app = Flask(__name__)

    
if __name__ == '__main__':
    # Par défaut, Flask écoute sur le port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
