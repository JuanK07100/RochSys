from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from backend.extensions import db
from backend.models import BOM, Insumo
from backend.utils import stock_insumo_total

produccion_bp = Blueprint('produccion', __name__, url_prefix='/api/produccion')

@produccion_bp.route('/verificar', methods=['POST'])
@jwt_required()
def verificar():
    data = request.get_json() or {}
    pedidos = data.get("pedidos", [])
    resultados = {}

    for pedido in pedidos:
        referencia = pedido.get("referencia")
        cantidad_pedida = float(pedido.get("cantidad", 0))
        if cantidad_pedida <= 0:
            continue

        bom_items = BOM.query.filter_by(producto_referencia=referencia).all()
        for bom in bom_items:
            insumo = db.session.get(Insumo, bom.insumo_id)
            if not insumo:
                continue
            necesario = bom.cantidad_necesaria * cantidad_pedida
            if insumo.id not in resultados:
                resultados[insumo.id] = {
                    "codigo": insumo.codigo,
                    "nombre": insumo.nombre,
                    "unidad": insumo.unidad,
                    "stock": stock_insumo_total(insumo.id),
                    "necesario": 0
                }
            resultados[insumo.id]["necesario"] += necesario

    final = []
    for item in resultados.values():
        item["diferencia"] = item["stock"] - item["necesario"]
        item["suficiente"] = item["diferencia"] >= 0
        final.append(item)

    return jsonify(final)