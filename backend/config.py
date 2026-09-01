import os
from datetime import timedelta

class Config:
    # Obtén el directorio donde está este archivo (backend/)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Crea la base de datos dentro de backend/
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'rochsis.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "cambia-esta-clave-en-produccion")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)