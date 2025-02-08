from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.init_db import CONNECTION

# Création du Blueprint Flask
links_bp = Blueprint('links', __name__)

@links_bp.route('/links', methods=['POST'])
@jwt_required()
def create_link():
    """
    Endpoint pour créer un nouveau link.
    Nécessite un token JWT valide.
    """
    data = request.get_json(force=True)
    name = data.get("name")
    description = data.get("description")
    url = data.get("url")
    user_id = get_jwt_identity()
    tag_ids = data.get("tag_ids", [])

    if not name or not url:
        return jsonify({"error": "Le nom et l'URL sont obligatoires"}), 400

    # Vérifier que tous les tags existent
    existing_tags = {tag_id for tag_id, in CONNECTION.execute("SELECT id FROM tags").fetchall()}
    invalid_tags = [tag_id for tag_id in tag_ids if tag_id not in existing_tags]

    if invalid_tags:
        return jsonify({"error": f"Certains tags sont invalides : {invalid_tags}"}), 400

    # Insérer le link
    result = CONNECTION.execute(
        "INSERT INTO links (name, description, url, user_id) VALUES (?, ?, ?, ?) RETURNING id",
        [name, description, url, user_id]
    ).fetchone()

    link_id = result[0]

    # Associer les tags
    for tag_id in tag_ids:
        CONNECTION.execute("INSERT INTO links_tags (link_id, tag_id) VALUES (?, ?)", [link_id, tag_id])

    return jsonify({"message": "Link créé avec succès", "link_id": link_id}), 201

@links_bp.route('/links', methods=['GET'])
@jwt_required()
def get_all_links():
    """
    Endpoint pour récupérer tous les links d'un utilisateur.
    """
    user_id = get_jwt_identity()
    links = CONNECTION.execute("""
        SELECT l.id, l.name, l.description, l.url,
            (SELECT GROUP_CONCAT(t.id) FROM links_tags lt JOIN tags t ON lt.tag_id = t.id WHERE lt.link_id = l.id) AS tag_ids
        FROM links l
        WHERE l.user_id = ?
    """, [user_id]).fetchall()

    results = []
    for link in links:
        results.append({
            "id": link[0],
            "name": link[1],
            "description": link[2],
            "url": link[3],
            "tag_ids": link[4].split(",") if link[4] else []
        })

    return jsonify(results), 200

@links_bp.route('/links/<int:link_id>', methods=['GET'])
@jwt_required()
def get_link(link_id):
    """
    Endpoint pour récupérer un link par son ID.
    """
    user_id = get_jwt_identity()
    link = CONNECTION.execute("""
        SELECT l.id, l.name, l.description, l.url,
            (SELECT GROUP_CONCAT(t.id) FROM links_tags lt JOIN tags t ON lt.tag_id = t.id WHERE lt.link_id = l.id) AS tag_ids
        FROM links l
        WHERE l.id = ? AND l.user_id = ?
    """, [link_id, user_id]).fetchone()

    if not link:
        return jsonify({"error": "Link non trouvé"}), 404

    return jsonify({
        "id": link[0],
        "name": link[1],
        "description": link[2],
        "url": link[3],
        "tag_ids": link[4].split(",") if link[4] else []
    }), 200

@links_bp.route('/links/<int:link_id>', methods=['PUT'])
@jwt_required()
def update_link(link_id):
    """
    Endpoint pour mettre à jour un link par son ID.
    """
    user_id = get_jwt_identity()
    data = request.get_json(force=True)

    new_name = data.get("name")
    new_description = data.get("description")
    new_url = data.get("url")
    new_tag_ids = data.get("tag_ids", [])

    existing_link = CONNECTION.execute(
        "SELECT id FROM links WHERE id = ? AND user_id = ?", [link_id, user_id]
    ).fetchone()

    if not existing_link:
        return jsonify({"error": "Link non trouvé"}), 404

    # Vérifier si les tags existent
    existing_tags = {tag_id for tag_id, in CONNECTION.execute("SELECT id FROM tags").fetchall()}
    invalid_tags = [tag_id for tag_id in new_tag_ids if tag_id not in existing_tags]

    if invalid_tags:
        return jsonify({"error": f"Certains tags sont invalides : {invalid_tags}"}), 400

    # Mettre à jour les données
    CONNECTION.execute("""
        UPDATE links
        SET name = COALESCE(?, name),
            description = COALESCE(?, description),
            url = COALESCE(?, url)
        WHERE id = ? AND user_id = ?
    """, [new_name, new_description, new_url, link_id, user_id])

    # Mettre à jour les tags associés
    CONNECTION.execute("DELETE FROM links_tags WHERE link_id = ?", [link_id])
    for tag_id in new_tag_ids:
        CONNECTION.execute("INSERT INTO links_tags (link_id, tag_id) VALUES (?, ?)", [link_id, tag_id])

    return jsonify({"message": "Link mis à jour avec succès"}), 200

@links_bp.route('/links/<int:link_id>', methods=['DELETE'])
@jwt_required()
def delete_link(link_id):
    """
    Endpoint pour supprimer un link par son ID.
    """
    user_id = get_jwt_identity()
    existing_link = CONNECTION.execute(
        "SELECT id FROM links WHERE id = ? AND user_id = ?", [link_id, user_id]
    ).fetchone()

    if not existing_link:
        return jsonify({"error": "Link non trouvé"}), 404

    CONNECTION.execute("DELETE FROM links_tags WHERE link_id = ?", [link_id])
    CONNECTION.execute("DELETE FROM links WHERE id = ?", [link_id])

    return jsonify({"message": "Link supprimé avec succès"}), 200


# @links_bp.route('/links/search-by-tags', methods=['POST'])
# @jwt_required()
# def search_links_by_tags():
#     """
#     Endpoint pour rechercher des liens par tags.
#     Nécessite un token JWT valide.
#     """
#     data = request.get_json(force=True)
#     tag_ids = data.get("tag_ids", [])
#     limit = data.get("limit", None)  # Limite optionnelle du nombre de liens à inclure

#     if not tag_ids:
#         return jsonify({"error": "Une liste de tag_ids est requise"}), 400

#     # Convertir les tag_ids en ObjectId
#     tag_ids = [ObjectId(tag_id) for tag_id in tag_ids]

#     user_id = get_jwt_identity()  # Utilise l'utilisateur authentifié

#     # Trouver tous les liens de l'utilisateur
#     links = list(links_collection.find({"user_id": user_id}))

#     # Table de hash pour regrouper les liens par score
#     hash_table = {}

#     for link in links:
#         # Calculer le nombre de tags en commun avec la liste fournie
#         matching_tags_count = len(set(link["tag_ids"]) & set(tag_ids))

#         if matching_tags_count > 0:  # Ignorer les liens avec un score de 0
#             if matching_tags_count not in hash_table:
#                 hash_table[matching_tags_count] = []
#             hash_table[matching_tags_count].append(link)

#     # Aplatir la table de hash en une liste triée par score (décroissant)
#     sorted_links = []
#     for score in sorted(hash_table.keys(), reverse=True):
#         for link in hash_table[score]:
#             # Convertir ObjectId en chaîne pour la réponse
#             link["_id"] = str(link["_id"])
#             link["tag_ids"] = [str(tag_id) for tag_id in link["tag_ids"]]
#             sorted_links.append(link)

#     return jsonify(sorted_links), 200

