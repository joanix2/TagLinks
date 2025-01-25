from flask import request, jsonify
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)
from bson.objectid import ObjectId
from src.collections import tags_collection, links_collection

@app.route('/links', methods=['POST'])
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
    user_id = get_jwt_identity()  # Utilise l'utilisateur authentifié
    tag_ids = data.get("tag_ids", [])

    if not name or not url:
        return jsonify({"error": "Le nom et l'URL sont obligatoires"}), 400

    # Vérifier que tous les tags existent
    invalid_tags = [tag_id for tag_id in tag_ids if not tags_collection.find_one({"_id": ObjectId(tag_id)})]
    if invalid_tags:
        return jsonify({"error": f"Certains tags sont invalides : {invalid_tags}"}), 400

    # Créer le link
    link = {
        "name": name,
        "description": description,
        "url": url,
        "user_id": user_id,
        "tag_ids": [ObjectId(tag_id) for tag_id in tag_ids]
    }
    result = links_collection.insert_one(link)
    link["_id"] = str(result.inserted_id)  # Convertir ObjectId en chaîne pour la réponse

    return jsonify({"message": "Link créé avec succès", "link": link}), 201


@app.route('/links', methods=['GET'])
@jwt_required()
def get_all_links():
    """
    Endpoint pour récupérer tous les links d'un utilisateur.
    Nécessite un token JWT valide.
    """
    user_id = get_jwt_identity()
    links = list(links_collection.find({"user_id": user_id}, {"_id": 1, "name": 1, "description": 1, "url": 1, "tag_ids": 1}))
    
    # Convertir ObjectId en chaînes dans les résultats
    for link in links:
        link["_id"] = str(link["_id"])
        link["tag_ids"] = [str(tag_id) for tag_id in link["tag_ids"]]

    return jsonify(links), 200


@app.route('/links/<string:link_id>', methods=['GET'])
@jwt_required()
def get_link(link_id):
    """
    Endpoint pour récupérer un link par son ID.
    Nécessite un token JWT valide.
    """
    user_id = get_jwt_identity()
    link = links_collection.find_one({"_id": ObjectId(link_id), "user_id": user_id})
    if not link:
        return jsonify({"error": "Link non trouvé"}), 404

    # Convertir ObjectId en chaîne pour la réponse
    link["_id"] = str(link["_id"])
    link["tag_ids"] = [str(tag_id) for tag_id in link["tag_ids"]]

    return jsonify(link), 200


@app.route('/links/<string:link_id>', methods=['PUT'])
@jwt_required()
def update_link(link_id):
    """
    Endpoint pour mettre à jour un link par son ID.
    Nécessite un token JWT valide.
    """
    user_id = get_jwt_identity()
    data = request.get_json(force=True)

    new_name = data.get("name")
    new_description = data.get("description")
    new_url = data.get("url")
    new_tag_ids = data.get("tag_ids")

    link = links_collection.find_one({"_id": ObjectId(link_id), "user_id": user_id})
    if not link:
        return jsonify({"error": "Link non trouvé"}), 404

    # Vérifier que tous les tags existent (si fournis)
    if new_tag_ids:
        invalid_tags = [tag_id for tag_id in new_tag_ids if not tags_collection.find_one({"_id": ObjectId(tag_id)})]
        if invalid_tags:
            return jsonify({"error": f"Certains tags sont invalides : {invalid_tags}"}), 400

    # Mettre à jour les champs fournis
    update_data = {}
    if new_name:
        update_data["name"] = new_name
    if new_description:
        update_data["description"] = new_description
    if new_url:
        update_data["url"] = new_url
    if new_tag_ids is not None:
        update_data["tag_ids"] = [ObjectId(tag_id) for tag_id in new_tag_ids]

    links_collection.update_one({"_id": ObjectId(link_id), "user_id": user_id}, {"$set": update_data})

    updated_link = links_collection.find_one({"_id": ObjectId(link_id)}, {"_id": 1, "name": 1, "description": 1, "url": 1, "tag_ids": 1})
    updated_link["_id"] = str(updated_link["_id"])
    updated_link["tag_ids"] = [str(tag_id) for tag_id in updated_link["tag_ids"]]

    return jsonify({"message": "Link mis à jour avec succès", "link": updated_link}), 200


@app.route('/links/<string:link_id>', methods=['DELETE'])
@jwt_required()
def delete_link(link_id):
    """
    Endpoint pour supprimer un link par son ID.
    Nécessite un token JWT valide.
    """
    user_id = get_jwt_identity()
    link = links_collection.find_one({"_id": ObjectId(link_id), "user_id": user_id})
    if not link:
        return jsonify({"error": "Link non trouvé"}), 404

    links_collection.delete_one({"_id": ObjectId(link_id), "user_id": user_id})
    return jsonify({"message": "Link supprimé avec succès"}), 200


@app.route('/links/search-by-tags', methods=['POST'])
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

    # Convertir les tag_ids en ObjectId
    tag_ids = [ObjectId(tag_id) for tag_id in tag_ids]

    user_id = get_jwt_identity()  # Utilise l'utilisateur authentifié

    # Trouver tous les liens de l'utilisateur
    links = list(links_collection.find({"user_id": user_id}))

    # Table de hash pour regrouper les liens par score
    hash_table = {}

    for link in links:
        # Calculer le nombre de tags en commun avec la liste fournie
        matching_tags_count = len(set(link["tag_ids"]) & set(tag_ids))

        if matching_tags_count > 0:  # Ignorer les liens avec un score de 0
            if matching_tags_count not in hash_table:
                hash_table[matching_tags_count] = []
            hash_table[matching_tags_count].append(link)

    # Aplatir la table de hash en une liste triée par score (décroissant)
    sorted_links = []
    for score in sorted(hash_table.keys(), reverse=True):
        for link in hash_table[score]:
            # Convertir ObjectId en chaîne pour la réponse
            link["_id"] = str(link["_id"])
            link["tag_ids"] = [str(tag_id) for tag_id in link["tag_ids"]]
            sorted_links.append(link)

    return jsonify(sorted_links), 200

