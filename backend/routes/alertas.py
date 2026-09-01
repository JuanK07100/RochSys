from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from backend.models import Insumo
from backend.utils import stock_insumo_total

alertas_bp = Blueprint('alertas', __name__, url_prefix='/api/alertas')

@alertas_bp.route('', methods=['GET'])
@jwt_required()
def alertas():
    resultado = []
    for i in Insumo.query.filter_by(activo=True).all():
        stock = stock_insumo_total(i.id)
        if stock <= i.punto_reorden:
            resultado.append({
                "id": i.id,
                "codigo": i.codigo,
                "nombre": i.nombre,
                "cantidad": stock,
                "unidad": i.unidad,
                "punto_reorden": i.punto_reorden
            })
    return jsonify(resultado)