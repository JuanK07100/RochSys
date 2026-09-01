from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from backend.models import Insumo, ProductoTerminado
from backend.utils import stock_insumo_total, movimientos_data

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('', methods=['GET'])
@jwt_required()
def dashboard():
    insumos = Insumo.query.filter_by(activo=True).all()
    productos = ProductoTerminado.query.filter_by(activo=True).all()

    alertas = []
    for i in insumos:
        stock = stock_insumo_total(i.id)
        if stock <= i.punto_reorden:
            alertas.append({
                "id": i.id,
                "codigo": i.codigo,
                "nombre": i.nombre,
                "stock": stock,
                "unidad": i.unidad,
                "punto_reorden": i.punto_reorden
            })

    return jsonify({
        "total_insumos": len(insumos),
        "total_productos": len(productos),
        "alertas": alertas,
        "movimientos": movimientos_data(10)
    })