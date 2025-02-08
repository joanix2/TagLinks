import duckdb
import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.init_db import CONNECTION

tags_bp = Blueprint("tags", __name__)

@tags_bp.route("/tags", methods=["POST"])
@jwt_required()
def create_tag():
    """Créer un nouveau tag"""
    data = request.get_json(force=True)
    name = data.get("name")
    color = data.get("color")

    if not name or not color:
        return jsonify({"error": "Le nom et la couleur sont obligatoires"}), 400

    # Vérifier si le tag existe déjà
    existing = CONNECTION.execute("SELECT * FROM tags WHERE name = ?", [name]).fetchone()
    if existing:
        return jsonify({"error": "Un tag avec ce nom existe déjà"}), 400

    tag_id = str(uuid.uuid4())  # Générer un UUID
    CONNECTION.execute("INSERT INTO tags (id, name, color) VALUES (?, ?, ?)", [tag_id, name, color])

    return jsonify({"message": "Tag créé avec succès", "tag": {"id": tag_id, "name": name, "color": color}}), 201


@tags_bp.route("/tags", methods=["GET"])
@jwt_required()
def get_all_tags():
    """Récupérer tous les tags"""
    tags = CONNECTION.execute("SELECT * FROM tags").fetchall()
    tag_list = [{"id": row[0], "name": row[1], "color": row[2]} for row in tags]
    return jsonify(tag_list), 200


@tags_bp.route("/tags/<string:tag_id>", methods=["GET"])
@jwt_required()
def get_tag(tag_id):
    """Récupérer un tag par son ID"""
    tag = CONNECTION.execute("SELECT * FROM tags WHERE id = ?", [tag_id]).fetchone()
    if not tag:
        return jsonify({"error": "Tag non trouvé"}), 404

    return jsonify({"id": tag[0], "name": tag[1], "color": tag[2]}), 200


@tags_bp.route("/tags/<string:tag_id>", methods=["PUT"])
@jwt_required()
def update_tag(tag_id):
    """Mettre à jour un tag par son ID"""
    data = request.get_json(force=True)
    new_name = data.get("name")
    new_color = data.get("color")

    if not new_name and not new_color:
        return jsonify({"error": "Au moins un champ (nom ou couleur) doit être fourni"}), 400

    existing = CONNECTION.execute("SELECT * FROM tags WHERE id = ?", [tag_id]).fetchone()
    if not existing:
        return jsonify({"error": "Tag non trouvé"}), 404

    # Mettre à jour les champs
    if new_name:
        CONNECTION.execute("UPDATE tags SET name = ? WHERE id = ?", [new_name, tag_id])
    if new_color:
        CONNECTION.execute("UPDATE tags SET color = ? WHERE id = ?", [new_color, tag_id])

    updated_tag = CONNECTION.execute("SELECT * FROM tags WHERE id = ?", [tag_id]).fetchone()
    return jsonify({"message": "Tag mis à jour avec succès", "tag": {"id": updated_tag[0], "name": updated_tag[1], "color": updated_tag[2]}}), 200


@tags_bp.route("/tags/<string:tag_id>", methods=["DELETE"])
@jwt_required()
def delete_tag(tag_id):
    """Supprimer un tag par son ID"""
    existing = CONNECTION.execute("SELECT * FROM tags WHERE id = ?", [tag_id]).fetchone()
    if not existing:
        return jsonify({"error": "Tag non trouvé"}), 404

    CONNECTION.execute("DELETE FROM tags WHERE id = ?", [tag_id])
    return jsonify({"message": "Tag supprimé avec succès"}), 200
