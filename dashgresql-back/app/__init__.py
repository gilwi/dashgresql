import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

import click
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

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
    CORS(app, origins=["http://localhost:5173"])
    jwt.init_app(app)

    from app.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    # Register your existing blueprints...
    from .auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # --- Custom Command: Reset Database ---
    @app.cli.command("reset-db")
    def reset_db():
        """Drop all tables and recreate them."""
        # Safety check: Ask the user for confirmation
        if click.confirm(
            "This will delete all data. Are you sure you want to reset the database?"
        ):
            db.drop_all()
            db.create_all()
            click.echo("Database has been reset.")

    # --------------------------------------
    # --- Custom Command: Create test User ---
    @app.cli.command("create-user")
    @click.argument("name", default="lwi")
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
                    "%(asctime)s %(levelname)s: %(message)s "
                    "[in %(pathname)s:%(lineno)d]"
                )
            )
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("dashgresql startup")

    return app


from app import models
