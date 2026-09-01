from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from backend.extensions import db
from backend.models import Ubicacion
from backend.utils import requiere_rol

ubicaciones_bp = Blueprint('ubicaciones', __name__, url_prefix='/api/ubicaciones')

@ubicaciones_bp.route('', methods=['GET'])
@jwt_required()
def get_ubicaciones():
    return jsonify([{
        "id": u.id,
        "nombre": u.nombre,
        "tipo": u.tipo,
        "descripcion": u.descripcion
    } for u in Ubicacion.query.filter_by(activa=True).order_by(Ubicacion.nombre).all()])

@ubicaciones_bp.route('', methods=['POST'])
@requiere_rol("Administrador")
def crear_ubicacion():
    data = request.get_json() or {}
    nombre = data.get("nombre", "").strip()
    tipo = data.get("tipo", "MIXTA")

    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400
    if tipo not in ("MP", "PT", "MIXTA"):
        return jsonify({"error": "Tipo de ubicación inválido"}), 400
    if Ubicacion.query.filter_by(nombre=nombre).first():
        return jsonify({"error": "La ubicación ya existe"}), 409

    u = Ubicacion(
        nombre=nombre,
        tipo=tipo,
        descripcion=data.get("descripcion", "")
    )
    db.session.add(u)
    db.session.commit()
    return jsonify({"message": "Ubicación creada", "id": u.id}), 201