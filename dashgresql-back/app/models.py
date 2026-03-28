import uuid
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login
from app.crypto import decrypt_password, encrypt_password


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Database(db.Model):
    __tablename__ = "databases"

    id = db.Column(
        db.String(36), primary_key=True, default=lambda: f"db-{uuid.uuid4().hex[:8]}"
    )
    name = db.Column(db.String(128), nullable=False, unique=True)
    max_connections = db.Column(db.Integer, default=100)
    connection_count = db.Column(db.Integer, default=0)
    size = db.Column(db.String(32), default="0 GB")
    pg_version = db.Column(db.String(16), nullable=False)

    # Connection credentials
    host = db.Column(db.String(253), nullable=False)
    port = db.Column(db.Integer, default=5432, nullable=False)
    db_user = db.Column(db.String(128), nullable=False)
    _password = db.Column("password", db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    owner = db.relationship("User", backref="databases")

    # Encrypt on set, decrypt on get — password never touches the DB in plain text
    @property
    def password(self):
        return decrypt_password(self._password)

    @password.setter
    def password(self, plain: str):
        self._password = encrypt_password(plain)

    def to_dict(self):
        """Never exposes password or its encrypted form."""
        return {
            "id": self.id,
            "name": self.name,
            "max_connections": self.max_connections,
            "connection_count": self.connection_count,
            "size": self.size,
            "pg_version": self.pg_version,
            "host": self.host,
            "port": self.port,
            "db_user": self.db_user,
            "owner": self.owner.username,
            "created_at": self.created_at.isoformat(),
        }
