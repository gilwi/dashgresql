import logging
import os
from logging.handlers import RotatingFileHandler

import click
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()

login = LoginManager()
login.login_view = "main.login"

jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Allow requests from your Vue dev server only
    raw_origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173")
    allowed_origins = [o.strip() for o in raw_origins.split(",")]
    CORS(
        app,
        origins=allowed_origins,
    )

    jwt.init_app(app)

    from .auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    from .databases import databases_bp

    app.register_blueprint(databases_bp, url_prefix="/api/databases")

    # --- Custom Command: Reset Database ---

    @app.cli.command("reset-db")
    @click.option(
        "--force", "-f", is_flag=True, help="Force reset without confirmation"
    )
    def reset_db(force):
        """Drop all tables and recreate them."""
        # Skip confirmation if force flag is used
        if force or click.confirm(
            "This will delete all data. Are you sure you want to reset the database?"
        ):
            db.drop_all()
            db.create_all()
            click.echo("Database has been reset.")

    # --------------------------------------
    # --- Custom Command: Create test User ---
    @app.cli.command("create-user")
    def create_user(name):
        """Create a new user example."""
        # You can access your database models here because
        # 'db' and 'models' are imported in this file.
        from app import models  # Local import to avoid circular issues

        print(f"Creating user: {name}")
        u = models.User(username=name)
        u.set_password("test")
        db.session.add(u)
        db.session.commit()

    # -----------------------------------------
    # --- Custom Command: Create test data ---
    @app.cli.command("create-test-data")
    @click.argument("name", default="test")
    def create_test_data(name):
        """Create a new user example."""
        # You can access your database models here because
        # 'db' and 'models' are imported in this file.
        from app import models  # Local import to avoid circular issues

        print(f"Creating user: {name}")
        u = models.User(username=name)
        u.set_password("test")

        print(f"Creating test databases")
        db1 = models.Database(
            name="ecommerce",
            host="localhost",
            port=5433,
            db_user="admin",
            password="admin123",
            pg_version="16",
            owner_id="1",
        )
        db2 = models.Database(
            name="hr",
            host="localhost",
            port=5434,
            db_user="admin",
            password="admin123",
            pg_version="16",
            owner_id="1",
        )
        db3 = models.Database(
            name="analytics",
            host="localhost",
            port=5435,
            db_user="admin",
            password="admin123",
            pg_version="16",
            owner_id="1",
        )
        db.session.add(u)
        db.session.add(db1)
        db.session.add(db2)
        db.session.add(db3)
        db.session.commit()

    # -----------------------------------------

    if not app.debug and not app.testing:
        if app.config["LOG_TO_STDOUT"]:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists("logs"):
                os.mkdir("logs")
            file_handler = RotatingFileHandler(
                "logs/dashgresql.log", maxBytes=10240, backupCount=10
            )
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
                )
            )
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("dashgresql startup")

    return app


from app import models
