from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models import Database
from app.pg_utils import check_pg_connection

databases_bp = Blueprint("databases", __name__)

SUPPORTED_PG_VERSIONS = ["14", "15", "16", "17"]


@databases_bp.route("/", methods=["GET"])
@jwt_required()
def get_databases():
    user_id = get_jwt_identity()
    dbs = Database.query.filter_by(owner_id=user_id).all()
    return jsonify([d.to_dict() for d in dbs]), 200


@databases_bp.route("/", methods=["POST"])
@jwt_required()
def create_database():
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validation
    required = ["name", "host", "db_user", "password"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f'Missing fields: {", ".join(missing)}'}), 400

    if Database.query.filter_by(name=data["name"]).first():
        return jsonify({"error": "A database with this name already exists"}), 409

    pg_version = str(data.get("pg_version", "16"))
    if pg_version not in SUPPORTED_PG_VERSIONS:
        return (
            jsonify(
                {
                    "error": f"Unsupported PostgreSQL version. Supported: {SUPPORTED_PG_VERSIONS}"
                }
            ),
            400,
        )

    port = data.get("port", 5432)
    if not isinstance(port, int) or not (1 <= port <= 65535):
        return jsonify({"error": "Port must be a number between 1 and 65535"}), 400

    new_db = Database(
        name=data["name"],
        host=data["host"],
        port=port,
        db_user=data["db_user"],
        pg_version=pg_version,
        max_connections=data.get("max_connections", 100),
        owner_id=user_id,
    )
    new_db.password = data["password"]  # triggers the encrypt setter

    db.session.add(new_db)
    db.session.commit()

    return jsonify(new_db.to_dict()), 201


@databases_bp.route("/<string:db_id>/check", methods=["GET"])
@jwt_required()
def check_database(db_id):
    user_id = get_jwt_identity()
    database = Database.query.filter_by(id=db_id, owner_id=user_id).first()
    if not database:
        return jsonify({"error": "Database not found"}), 404

    result = check_pg_connection(database)
    database.connection_count = result["connection_count"]
    if result["size"]:
        database.size = result["size"]
    db.session.commit()

    return jsonify(result), 200


@databases_bp.route("/check-all", methods=["GET"])
@jwt_required()
def check_all_databases():
    user_id = get_jwt_identity()
    databases = Database.query.filter_by(owner_id=user_id).all()

    results = {}
    for database in databases:
        result = check_pg_connection(database)
        database.connection_count = result["connection_count"]
        if result["size"]:
            database.size = result["size"]
        results[database.id] = result

    db.session.commit()
    return jsonify(results), 200
