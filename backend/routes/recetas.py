from flask import Blueprint, request, jsonify
from backend.extensions import db
from backend.models import ProductoTerminado, Insumo, Receta
from backend.utils import requiere_rol

recetas_bp = Blueprint('recetas', __name__, url_prefix='/api/recetas')

@recetas_bp.route('/<string:referencia>', methods=['GET'])
@requiere_rol("Administrador")
def obtener_receta(referencia):
    """Obtiene la receta de un producto."""
    producto = ProductoTerminado.query.filter_by(referencia=referencia).first()
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    items = Receta.query.filter_by(producto_referencia=referencia).all()
    resultado = []
    for item in items:
        insumo = db.session.get(Insumo, item.insumo_id)
        if insumo:
            resultado.append({
                "id": item.id,
                "insumo_id": item.insumo_id,
                "codigo": insumo.codigo,
                "nombre": insumo.nombre,
                "unidad": insumo.unidad,
                "cantidad_necesaria": item.cantidad_necesaria
            })
    return jsonify(resultado)

@recetas_bp.route('/<string:referencia>', methods=['POST'])
@requiere_rol("Administrador")
def guardar_receta(referencia):
    """Guarda o actualiza la receta de un producto."""
    data = request.get_json() or {}
    items = data.get("items", [])

    producto = ProductoTerminado.query.filter_by(referencia=referencia).first()
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    # Validar items
    if not isinstance(items, list):
        return jsonify({"error": "Formato inválido"}), 400

    # Eliminar receta anterior
    Receta.query.filter_by(producto_referencia=referencia).delete()

    # Crear nuevos items
    for item in items:
        insumo_id = item.get("insumo_id")
        cantidad = item.get("cantidad_necesaria")
        if not insumo_id or not cantidad:
            continue
        insumo = db.session.get(Insumo, insumo_id)
        if not insumo:
            continue
        nuevo = Receta(
            producto_referencia=referencia,
            insumo_id=insumo_id,
            cantidad_necesaria=float(cantidad)
        )
        db.session.add(nuevo)

    db.session.commit()
    return jsonify({"message": "Receta guardada correctamente"})

@recetas_bp.route('/<string:referencia>', methods=['DELETE'])
@requiere_rol("Administrador")
def eliminar_receta(referencia):
    """Elimina la receta de un producto."""
    producto = ProductoTerminado.query.filter_by(referencia=referencia).first()
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    Receta.query.filter_by(producto_referencia=referencia).delete()
    db.session.commit()
    return jsonify({"message": "Receta eliminada"})