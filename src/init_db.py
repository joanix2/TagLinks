# Connexion à la base MongoDB
client = connect_to_mongo()
DATABASE_NAME = "db"
# Users
USERS_COLLECTION_NAME = "users"
users_collection = get_or_create_collection(client, DATABASE_NAME, USERS_COLLECTION_NAME)
# Tags
TAGS_COLLECTION_NAME = "tags"
tags_collection = get_or_create_collection(client, DATABASE_NAME, TAGS_COLLECTION_NAME)
# Links
LINKS_COLLECTION_NAME = "links"
links_collection = get_or_create_collection(client, DATABASE_NAME, LINKS_COLLECTION_NAME)