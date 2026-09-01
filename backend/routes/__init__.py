# backend/routes/__init__.py
from .auth import auth_bp
from .dashboard import dashboard_bp
from .ubicaciones import ubicaciones_bp
from .insumos import insumos_bp
from .productos import productos_bp
from .movimientos import movimientos_bp
from .alertas import alertas_bp
from .produccion import produccion_bp

blueprints = [
    auth_bp,
    dashboard_bp,
    ubicaciones_bp,
    insumos_bp,
    productos_bp,
    movimientos_bp,
    alertas_bp,
    produccion_bp,
]

def register_blueprints(app):
    for bp in blueprints:
        app.register_blueprint(bp)