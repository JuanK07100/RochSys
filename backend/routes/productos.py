from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from backend.extensions import db
from backend.models import ProductoTerminado, StockPT, Ubicacion
from backend.utils import stock_pt_total, requiere_rol, registrar_movimiento

productos_bp = Blueprint('productos', __name__, url_prefix='/api/productos')

@productos_bp.route('', methods=['GET'])
@jwt_required()
def get_productos():
    resultado = []
    for p in ProductoTerminado.query.filter_by(activo=True).order_by(ProductoTerminado.nombre).all():
        stocks = StockPT.query.filter_by(producto_id=p.id).all()
        detalle = []
        for s in stocks:
            u = db.session.get(Ubicacion, s.ubicacion_id)
            detalle.append({
                "ubicacion_id": u.id,
                "ubicacion": u.nombre,
                "cantidad": s.cantidad
            })
        resultado.append({
            "id": p.id,
            "referencia": p.referencia,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "cantidad": stock_pt_total(p.id),
            "ubicaciones": detalle
        })
    return jsonify(resultado)

@productos_bp.route('', methods=['POST'])
@requiere_rol("Administrador")
def crear_producto():
    data = request.get_json() or {}
    required = ["referencia", "nombre", "cantidad_inicial", "ubicacion_id"]
    missing = [x for x in required if data.get(x) in (None, "")]
    if missing:
        return jsonify({"error": "Faltan campos obligatorios", "campos": missing}), 400

    referencia = data["referencia"].strip()
    if ProductoTerminado.query.filter_by(referencia=referencia).first():
        return jsonify({"error": "La referencia ya existe"}), 409

    ubicacion = db.session.get(Ubicacion, int(data["ubicacion_id"]))
    if not ubicacion or ubicacion.tipo not in ("PT", "MIXTA"):
        return jsonify({"error": "La ubicación no está habilitada para producto terminado"}), 400

    p = ProductoTerminado(
        referencia=referencia,
        nombre=data["nombre"].strip(),
        descripcion=data.get("descripcion", "")
    )
    db.session.add(p)
    db.session.flush()

    cantidad = float(data["cantidad_inicial"])
    stock = StockPT(producto_id=p.id, ubicacion_id=ubicacion.id, cantidad=cantidad)
    db.session.add(stock)

    registrar_movimiento(
        "Entrada PT",
        "producto",
        p.id,
        cantidad,
        motivo="Registro de producto terminado",
        referencia=referencia,
        destino=ubicacion.id
    )
    db.session.commit()
    return jsonify({"message": "Producto registrado", "id": p.id}), 201

@productos_bp.route('/transferir', methods=['POST'])
@requiere_rol("Administrador", "Operario")
def transferir_producto():
    data = request.get_json() or {}
    try:
        producto_id = int(data["producto_id"])
        origen_id = int(data["origen_id"])
        destino_id = int(data["destino_id"])
        cantidad = float(data["cantidad"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Datos de transferencia inválidos"}), 400

    if origen_id == destino_id:
        return jsonify({"error": "Origen y destino deben ser diferentes"}), 400
    if cantidad <= 0:
        return jsonify({"error": "La cantidad debe ser mayor que cero"}), 400

    origen = db.session.get(Ubicacion, origen_id)
    destino = db.session.get(Ubicacion, destino_id)
    producto = db.session.get(ProductoTerminado, producto_id)
    if not producto or not origen or not destino:
        return jsonify({"error": "Producto o ubicación inválidos"}), 404
    if origen.tipo not in ("PT", "MIXTA") or destino.tipo not in ("PT", "MIXTA"):
        return jsonify({"error": "Las ubicaciones deben aceptar producto terminado"}), 400

    stock_origen = StockPT.query.filter_by(producto_id=producto_id, ubicacion_id=origen_id).first()
    if not stock_origen or stock_origen.cantidad < cantidad:
        disponible = stock_origen.cantidad if stock_origen else 0
        return jsonify({"error": f"Stock insuficiente en origen. Disponible: {disponible}"}), 400

    stock_destino = StockPT.query.filter_by(producto_id=producto_id, ubicacion_id=destino_id).first()
    if not stock_destino:
        stock_destino = StockPT(producto_id=producto_id, ubicacion_id=destino_id, cantidad=0)
        db.session.add(stock_destino)

    stock_origen.cantidad -= cantidad
    stock_destino.cantidad += cantidad

    registrar_movimiento(
        "Transferencia PT",
        "producto",
        producto_id,
        cantidad,
        motivo=data.get("motivo", "Transferencia"),
        referencia=producto.referencia,
        origen=origen_id,
        destino=destino_id
    )
    db.session.commit()
    return jsonify({"message": "Transferencia realizada"})