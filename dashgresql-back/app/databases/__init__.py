import psycopg2
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from psycopg2.extensions import quote_ident

from app import db
from app.crypto import decrypt_password
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


def get_db_connection(database):
    return psycopg2.connect(
        host=database.host,
        port=database.port,
        user=database.db_user,
        password=decrypt_password(database._password),
        dbname=database.name,
        connect_timeout=5,
    )


@databases_bp.route("/<string:db_id>/schemas", methods=["GET"])
@jwt_required()
def get_schemas(db_id):
    user_id = get_jwt_identity()
    database = Database.query.filter_by(id=db_id, owner_id=user_id).first()
    if not database:
        return jsonify({"error": "Database not found"}), 404

    ESTIMATE_THRESHOLD = 100_000  # use COUNT(*) below this, estimate above

    try:
        conn = get_db_connection(database)
        with conn.cursor() as cur:

            # First pass: get all tables with fast stats
            cur.execute("""
                SELECT
                    t.table_schema,
                    t.table_name,
                    pg_size_pretty(pg_total_relation_size(
                        quote_ident(t.table_schema) || '.' || quote_ident(t.table_name)
                    )) AS size,
                    COALESCE(s.n_live_tup, 0) AS estimated_rows
                FROM information_schema.tables t
                LEFT JOIN pg_stat_user_tables s
                    ON s.schemaname = t.table_schema
                    AND s.relname   = t.table_name
                WHERE t.table_type   = 'BASE TABLE'
                  AND t.table_schema NOT IN ('pg_catalog', 'information_schema')
                ORDER BY t.table_schema, t.table_name
            """)
            rows = cur.fetchall()

            # Second pass: exact COUNT(*) only for small tables
            results = []
            for schema, table, size, estimated_rows in rows:
                if estimated_rows < ESTIMATE_THRESHOLD:
                    cur.execute(
                        f"SELECT COUNT(*) FROM {quote_ident(schema, conn)}.{quote_ident(table, conn)}"
                    )
                    row_count = cur.fetchone()[0]
                    is_estimate = False
                else:
                    row_count = estimated_rows
                    is_estimate = True

                results.append((schema, table, size, row_count, is_estimate))

        conn.close()

        # Group by schema
        schemas = {}
        for schema, table, size, row_count, is_estimate in results:
            if schema not in schemas:
                schemas[schema] = {"name": schema, "tables": []}
            schemas[schema]["tables"].append(
                {
                    "name": table,
                    "size": size,
                    "row_count": row_count,
                    "is_estimate": is_estimate,
                }
            )

        return jsonify(list(schemas.values())), 200

    except psycopg2.OperationalError as e:
        return jsonify({"error": str(e).strip()}), 503


@databases_bp.route(
    "/<string:db_id>/schemas/<string:schema>/tables/<string:table>", methods=["GET"]
)
@jwt_required()
def get_table_details(db_id, schema, table):
    """Returns columns, constraints and indexes for a specific table."""
    user_id = get_jwt_identity()
    database = Database.query.filter_by(id=db_id, owner_id=user_id).first()
    if not database:
        return jsonify({"error": "Database not found"}), 404

    try:
        conn = get_db_connection(database)
        with conn.cursor() as cur:

            # Columns + types + nullability + defaults
            cur.execute(
                """
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
            """,
                (schema, table),
            )
            columns = [
                {
                    "name": row[0],
                    "type": row[1],
                    "nullable": row[2] == "YES",
                    "default": row[3],
                }
                for row in cur.fetchall()
            ]

            # Constraints (PK, FK, UNIQUE, CHECK)
            cur.execute(
                """
                SELECT
                    tc.constraint_name,
                    tc.constraint_type,
                    kcu.column_name,
                    ccu.table_name  AS foreign_table,
                    ccu.column_name AS foreign_column
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                   AND tc.table_schema    = kcu.table_schema
                LEFT JOIN information_schema.constraint_column_usage ccu
                    ON tc.constraint_name = ccu.constraint_name
                   AND tc.table_schema    = ccu.table_schema
                WHERE tc.table_schema = %s AND tc.table_name = %s
                ORDER BY tc.constraint_type, kcu.column_name
            """,
                (schema, table),
            )
            constraints = [
                {
                    "name": row[0],
                    "type": row[1],
                    "column": row[2],
                    "foreign_table": row[3],
                    "foreign_column": row[4],
                }
                for row in cur.fetchall()
            ]

            # Indexes
            cur.execute(
                """
                SELECT
                    indexname,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = %s AND tablename = %s
                ORDER BY indexname
            """,
                (schema, table),
            )
            indexes = [{"name": row[0], "definition": row[1]} for row in cur.fetchall()]

        conn.close()
        return (
            jsonify(
                {
                    "columns": columns,
                    "constraints": constraints,
                    "indexes": indexes,
                }
            ),
            200,
        )

    except psycopg2.OperationalError as e:
        return jsonify({"error": str(e).strip()}), 503
