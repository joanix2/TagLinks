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


@links_bp.route('/links/search-by-tags', methods=['POST'])
@jwt_required()
def search_links_by_tags():
    """
    Endpoint pour rechercher des liens par tags.
    Nécessite un token JWT valide.
    """
    data = request.get_json(force=True)
    tag_ids = data.get("tag_ids", [])
    limit = data.get("limit", None)  # Limite optionnelle du nombre de liens à inclure

    if not tag_ids:
        return jsonify({"error": "Une liste de tag_ids est requise"}), 400

    user_id = get_jwt_identity()  # Identifiant de l'utilisateur authentifié

    # Construire la requête SQL pour trouver les liens correspondants aux tags fournis
    query = f"""
        SELECT l.id, l.name, l.description, l.url, 
               GROUP_CONCAT(t.id) AS tag_ids,
               COUNT(t.id) AS match_count
        FROM links l
        JOIN links_tags lt ON l.id = lt.link_id
        JOIN tags t ON lt.tag_id = t.id
        WHERE l.user_id = ?
          AND t.id IN ({','.join(['?'] * len(tag_ids))})
        GROUP BY l.id
        ORDER BY match_count DESC
    """

    params = [user_id] + tag_ids
    if limit:
        query += " LIMIT ?"
        params.append(limit)

    # Exécuter la requête et récupérer les résultats
    results = CONNECTION.execute(query, params).fetchall()

    # Formater les résultats
    links = []
    for row in results:
        links.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "url": row[3],
            "tag_ids": row[4].split(",") if row[4] else [],
            "match_count": row[5]
        })

    return jsonify(links), 200

