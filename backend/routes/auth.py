import sys
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from backend.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")
    
    print(f"🔍 Intento de login: {username}", file=sys.stderr)
    
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f"❌ Usuario no encontrado: {username}", file=sys.stderr)
        return jsonify({"error": "Usuario o contraseña inválidos"}), 401

    print(f"✅ Usuario encontrado: {user.username}", file=sys.stderr)
    print(f"Hash almacenado: {user.password_hash}", file=sys.stderr)
    
    if not check_password_hash(user.password_hash, password):
        print(f"❌ Contraseña incorrecta para {username}", file=sys.stderr)
        return jsonify({"error": "Usuario o contraseña inválidos"}), 401

    token = create_access_token(identity=str(user.id))
    print(f"✅ Login exitoso para {username}", file=sys.stderr)
    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "rol": user.rol
        }
    })