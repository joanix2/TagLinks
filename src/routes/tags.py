from bson.objectid import ObjectId

@app.route('/tags', methods=['POST'])
@jwt_required()
def create_tag():
    """
    Endpoint pour créer un nouveau tag.
    Nécessite un token JWT valide.
    """
    data = request.get_json(force=True)
    name = data.get("name")
    color = data.get("color")

    if not name or not color:
        return jsonify({"error": "Le nom et la couleur sont obligatoires"}), 400

    # Vérifier si le tag existe déjà
    if tags_collection.find_one({"name": name}):
        return jsonify({"error": "Un tag avec ce nom existe déjà"}), 400

    # Créer le tag
    tag = {"name": name, "color": color}
    result = tags_collection.insert_one(tag)
    tag["_id"] = str(result.inserted_id)  # Convertir ObjectId en chaîne pour la réponse

    return jsonify({"message": "Tag créé avec succès", "tag": tag}), 201


@app.route('/tags', methods=['GET'])
@jwt_required()
def get_all_tags():
    """
    Endpoint pour récupérer tous les tags.
    Nécessite un token JWT valide.
    """
    tags = list(tags_collection.find({}, {"_id": 1, "name": 1, "color": 1}))
    # Convertir ObjectId en chaînes dans les résultats
    for tag in tags:
        tag["_id"] = str(tag["_id"])

    return jsonify(tags), 200


@app.route('/tags/<string:tag_id>', methods=['GET'])
@jwt_required()
def get_tag(tag_id):
    """
    Endpoint pour récupérer un tag par son ID.
    Nécessite un token JWT valide.
    """
    try:
        tag = tags_collection.find_one({"_id": ObjectId(tag_id)}, {"_id": 1, "name": 1, "color": 1})
    except Exception:
        return jsonify({"error": "ID invalide"}), 400

    if not tag:
        return jsonify({"error": "Tag non trouvé"}), 404

    # Convertir ObjectId en chaîne pour la réponse
    tag["_id"] = str(tag["_id"])

    return jsonify(tag), 200


@app.route('/tags/<string:tag_id>', methods=['PUT'])
@jwt_required()
def update_tag(tag_id):
    """
    Endpoint pour mettre à jour un tag par son ID.
    Nécessite un token JWT valide.
    """
    try:
        tag = tags_collection.find_one({"_id": ObjectId(tag_id)})
    except Exception:
        return jsonify({"error": "ID invalide"}), 400

    if not tag:
        return jsonify({"error": "Tag non trouvé"}), 404

    data = request.get_json(force=True)
    new_name = data.get("name")
    new_color = data.get("color")

    if not new_name and not new_color:
        return jsonify({"error": "Au moins un champ (nom ou couleur) doit être fourni"}), 400

    # Mettre à jour les champs fournis
    update_data = {}
    if new_name:
        update_data["name"] = new_name
    if new_color:
        update_data["color"] = new_color

    tags_collection.update_one({"_id": ObjectId(tag_id)}, {"$set": update_data})

    updated_tag = tags_collection.find_one({"_id": ObjectId(tag_id)}, {"_id": 1, "name": 1, "color": 1})
    updated_tag["_id"] = str(updated_tag["_id"])

    return jsonify({"message": "Tag mis à jour avec succès", "tag": updated_tag}), 200


@app.route('/tags/<string:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    """
    Endpoint pour supprimer un tag par son ID.
    Nécessite un token JWT valide.
    """
    try:
        tag = tags_collection.find_one({"_id": ObjectId(tag_id)})
    except Exception:
        return jsonify({"error": "ID invalide"}), 400

    if not tag:
        return jsonify({"error": "Tag non trouvé"}), 404

    tags_collection.delete_one({"_id": ObjectId(tag_id)})
    return jsonify({"message": "Tag supprimé avec succès"}), 200
