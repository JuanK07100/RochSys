import sys
import traceback
import os
from flask import Flask, render_template
from backend.config import Config
from backend.extensions import db, jwt, cors
from backend.routes import register_blueprints
from backend.init_db import initialize

def create_app():
    print("🔹 Creando app...", file=sys.stderr)
    # Obtén la ruta absoluta de backend/
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Templates: sube un nivel (../templates) desde backend/
    template_dir = os.path.join(base_dir, '..', 'templates')
    # Estáticos: sube un nivel y entra a frontend/static (../frontend/static)
    static_dir = os.path.join(base_dir, '..', 'frontend', 'static')
    
    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
        static_url_path='/static'   # Para que sirva en /static/
    )
    app.config.from_object(Config)

    print("🔹 Inicializando extensiones...", file=sys.stderr)
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    print("🔹 Registrando blueprints...", file=sys.stderr)
    register_blueprints(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    print("🔹 Inicializando base de datos...", file=sys.stderr)
    with app.app_context():
        initialize()

    print("✅ App creada exitosamente.", file=sys.stderr)
    return app

if __name__ == "__main__":
    try:
        print("🚀 Iniciando servidor...", file=sys.stderr)
        app = create_app()
        print("🌐 Ejecutando en http://localhost:5000", file=sys.stderr)
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"❌ ERROR: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)