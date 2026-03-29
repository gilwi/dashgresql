import psycopg2

from app.crypto import decrypt_password


def check_pg_connection(db_instance):
    try:
        conn = psycopg2.connect(
            host=db_instance.host,
            port=db_instance.port,
            user=db_instance.db_user,
            password=decrypt_password(db_instance._password),
            dbname=db_instance.name,
            connect_timeout=5,
        )

        with conn.cursor() as cur:
            # Active connection count
            cur.execute(
                """
                SELECT count(*)
                FROM pg_stat_activity
                WHERE datname = %s
                AND pid <> pg_backend_pid()
            """,
                (db_instance.name,),
            )
            connection_count = cur.fetchone()[0]

            # Human-readable database size
            cur.execute(
                """
                SELECT pg_size_pretty(pg_database_size(%s))
            """,
                (db_instance.name,),
            )
            size = cur.fetchone()[0]

        conn.close()

        return {
            "status": "Active",
            "connection_count": connection_count,
            "size": size,
            "error": None,
        }

    except psycopg2.OperationalError as e:
        return {
            "status": "Unreachable",
            "connection_count": 0,
            "size": None,
            "error": str(e).strip(),
        }
    except Exception as e:
        return {
            "status": "Error",
            "connection_count": 0,
            "size": None,
            "error": str(e).strip(),
        }
