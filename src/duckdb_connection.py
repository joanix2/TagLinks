import duckdb
import os

# Définition du fichier de base de données DuckDB
DB_FILE = "database.duckdb"

def connect_to_duckdb():
    """
    Connecte à la base de données DuckDB et retourne l'objet de connexion.
    """
    try:
        conn = duckdb.connect(database=DB_FILE, read_only=False)
        print("Connexion réussie à DuckDB !")
        return conn
    except Exception as e:
        print("Erreur lors de la connexion à DuckDB :", e)
        return None

def get_or_create_table(conn, table_name):
    """
    Vérifie si une table existe dans DuckDB. La crée si elle n'existe pas.

    :param conn: Instance de connexion DuckDB.
    :param table_name: Nom de la table.
    :return: Booléen (True si la table existe ou a été créée, False en cas d'erreur).
    """
    try:
        # Création d'une table générique si elle n'existe pas
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id UUID DEFAULT uuid_generate_v4(),
            data TEXT
        )
        """
        conn.execute(create_table_query)
        print(f"Table '{table_name}' prête à l'emploi.")
        return True
    except Exception as e:
        print(f"Erreur lors de la gestion de la table '{table_name}' : {e}")
        return False