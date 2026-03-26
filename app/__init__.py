from flask import Flask
from config import Config

app = Flask(__name__)
# config.py
app.config.from_object(Config)
from app import routes
