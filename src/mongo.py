import os
from pymongo import MongoClient

# Lire les variables d'environnement
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")  # Valeur par défaut : localhost
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))  # Valeur par défaut : 27017
MONGO_USER = os.getenv("MONGO_USER", "admin")  # Valeur par défaut : admin
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "password")  # Valeur par défaut : password

def connect_to_mongo():
    """
    Connecte au serveur MongoDB et retourne une instance de la base de données.
    """
    try:
        # Crée une URI de connexion
        mongo_uri = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
        
        # Crée un client MongoDB
        client = MongoClient(mongo_uri)

        # Teste la connexion en listant les bases de données
        print("Connexion réussie ! Bases de données disponibles :", client.list_database_names())

        # Retourne l'objet client
        return client
    except Exception as e:
        print("Erreur lors de la connexion à MongoDB :", e)
        return None
    
def get_or_create_collection(client, database_name, collection_name):
    """
    Vérifie si une base de données et une collection existent dans MongoDB.
    Les crée si elles n'existent pas et retourne l'objet collection.

    :param client: Instance MongoClient connectée à MongoDB.
    :param database_name: Nom de la base de données.
    :param collection_name: Nom de la collection.
    :return: Objet pymongo.collection.Collection.
    """
    try:
        # Vérifier si la base de données existe
        db_list = client.list_database_names()
        if database_name not in db_list:
            print(f"Base de données '{database_name}' inexistante. Création en cours...")
        db = client[database_name]  # MongoDB crée la base automatiquement à la première interaction

        # Vérifier si la collection existe
        if collection_name not in db.list_collection_names():
            print(f"Collection '{collection_name}' inexistante. Création en cours...")
            collection = db[collection_name]
            # Insérer un document "dummy" pour forcer la création
            collection.insert_one({"_id": 0, "placeholder": True})
            # Supprimer le document "dummy" après création
            collection.delete_one({"_id": 0})
            print(f"Collection '{collection_name}' créée avec succès.")
        else:
            print(f"Collection '{collection_name}' déjà existante.")
            collection = db[collection_name]

        return collection
    except Exception as e:
        print(f"Erreur lors de la gestion de la base de données ou de la collection : {e}")
        return None