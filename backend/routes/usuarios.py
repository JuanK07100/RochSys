from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from backend.extensions import db
from backend.models import User
from backend.utils import requiere_rol

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')

@usuarios_bp.route('', methods=['GET'])
@requiere_rol("Administrador")
def listar_usuarios():
    usuarios = User.query.all()
    return jsonify([{
        "id": u.id,
        "username": u.username,
        "rol": u.rol
    } for u in usuarios])

@usuarios_bp.route('', methods=['POST'])
@requiere_rol("Administrador")
def crear_usuario():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    rol = data.get("rol", "Operario")

    if not username or not password:
        return jsonify({"error": "Usuario y contraseña son obligatorios"}), 400
    if rol not in ("Administrador", "Operario"):
        return jsonify({"error": "Rol inválido"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "El nombre de usuario ya existe"}), 409

    nuevo = User(
        username=username,
        password_hash=generate_password_hash(password),
        rol=rol
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"message": "Usuario creado", "id": nuevo.id}), 201

@usuarios_bp.route('/<int:user_id>', methods=['PUT'])
@requiere_rol("Administrador")
def actualizar_usuario(user_id):
    data = request.get_json() or {}
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Actualizar rol si se envía
    if "rol" in data:
        rol = data["rol"]
        if rol not in ("Administrador", "Operario"):
            return jsonify({"error": "Rol inválido"}), 400
        user.rol = rol

    # Actualizar contraseña si se envía
    if "password" in data and data["password"]:
        user.password_hash = generate_password_hash(data["password"])

    db.session.commit()
    return jsonify({"message": "Usuario actualizado"})

@usuarios_bp.route('/<int:user_id>', methods=['DELETE'])
@requiere_rol("Administrador")
def eliminar_usuario(user_id):
    # No permitir eliminar a sí mismo
    from flask_jwt_extended import get_jwt_identity
    current_user_id = int(get_jwt_identity())
    if user_id == current_user_id:
        return jsonify({"error": "No puedes eliminar tu propio usuario"}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Usuario eliminado"})