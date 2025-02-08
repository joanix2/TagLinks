# Connexion à la base MongoDB
from src.duckdb_connection import connect_to_duckdb

def create_tables(conn):
    """
    Vérifie et crée les tables si elles n'existent pas dans la base de données.
    """

    # DuckDB ne supporte pas AUTOINCREMENT, on utilise plutôt une SEQUENCE pour générer les IDs
    conn.execute("CREATE SEQUENCE IF NOT EXISTS users_seq")
    conn.execute("CREATE SEQUENCE IF NOT EXISTS links_seq")
    conn.execute("CREATE SEQUENCE IF NOT EXISTS tags_seq")

    tables = {
        "users": """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY DEFAULT nextval('users_seq'),
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """,
        "links": """
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY DEFAULT nextval('links_seq'),
                name TEXT NOT NULL,
                description TEXT,
                url TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """,
        "tags": """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY DEFAULT nextval('tags_seq'),
                name TEXT UNIQUE NOT NULL,
                color TEXT NOT NULL
            )
        """,
        "links_tags": """
            CREATE TABLE IF NOT EXISTS links_tags (
                link_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                FOREIGN KEY (link_id) REFERENCES links(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id),
                PRIMARY KEY (link_id, tag_id)
            )
        """
    }

    for table_name, create_query in tables.items():
        try:
            conn.execute(create_query)
            print(f"✅ Table '{table_name}' vérifiée/créée avec succès.")
        except Exception as e:
            print(f"❌ Erreur lors de la création de la table '{table_name}' :", e)


# Connexion à DuckDB
CONNECTION = connect_to_duckdb()

if CONNECTION:
    create_tables(CONNECTION)
    print("🚀 Base de données DuckDB initialisée avec succès.")
