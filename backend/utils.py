# backend/utils.py
from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import User, Movimiento, Ubicacion, StockInsumo, StockPT

def usuario_actual():
    uid = int(get_jwt_identity())
    return db.session.get(User, uid)

def requiere_rol(*roles):
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = usuario_actual()
            if not user or user.rol not in roles:
                return jsonify({"error": "No tienes permisos para esta acción"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

def stock_insumo_total(insumo_id):
    return db.session.query(
        db.func.coalesce(db.func.sum(StockInsumo.cantidad), 0)
    ).filter(StockInsumo.insumo_id == insumo_id).scalar() or 0

def stock_pt_total(producto_id):
    return db.session.query(
        db.func.coalesce(db.func.sum(StockPT.cantidad), 0)
    ).filter(StockPT.producto_id == producto_id).scalar() or 0

def registrar_movimiento(tipo, entidad_tipo, entidad_id, cantidad, motivo="",
                         referencia="", origen=None, destino=None):
    m = Movimiento(
        tipo=tipo,
        entidad_tipo=entidad_tipo,
        entidad_id=entidad_id,
        cantidad=cantidad,
        motivo=motivo,
        referencia=referencia,
        usuario_id=int(get_jwt_identity()),
        ubicacion_origen_id=origen,
        ubicacion_destino_id=destino
    )
    db.session.add(m)

def movimientos_data(limit=50):
    movs = Movimiento.query.order_by(Movimiento.fecha_hora.desc()).limit(limit).all()
    resultado = []
    for m in movs:
        user = db.session.get(User, m.usuario_id)
        origen = db.session.get(Ubicacion, m.ubicacion_origen_id) if m.ubicacion_origen_id else None
        destino = db.session.get(Ubicacion, m.ubicacion_destino_id) if m.ubicacion_destino_id else None
        resultado.append({
            "id": m.id,
            "tipo": m.tipo,
            "entidad_tipo": m.entidad_tipo,
            "cantidad": m.cantidad,
            "motivo": m.motivo,
            "referencia": m.referencia,
            "usuario": user.username if user else "Desconocido",
            "origen": origen.nombre if origen else "",
            "destino": destino.nombre if destino else "",
            "fecha_hora": m.fecha_hora.strftime("%Y-%m-%d %H:%M") if m.fecha_hora else ""
        })
    return resultado