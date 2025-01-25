from flask import Flask
from flask_jwt_extended import JWTManager
from src.routes.oauth import users_bp
from src.routes.tags import tags_bp
from src.routes.links import links_bp

app = Flask(__name__)

# Configuration de la clé secrète pour JWT
app.config["JWT_SECRET_KEY"] = "votre_cle_secrete_pour_jwt"  # Changez cette clé pour quelque chose de sécurisé
jwt = JWTManager(app)

# Enregistrer le Blueprint
app.register_blueprint(users_bp)
app.register_blueprint(tags_bp)
app.register_blueprint(links_bp)

    
if __name__ == '__main__':
    # Par défaut, Flask écoute sur le port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
