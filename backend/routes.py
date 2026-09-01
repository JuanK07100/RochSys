# backend/routes.py
from routes import blueprints

def register_blueprints(app):
    for bp in blueprints:
        app.register_blueprint(bp)