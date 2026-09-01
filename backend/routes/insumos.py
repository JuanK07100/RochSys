from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from backend.extensions import db
from backend.models import Insumo, StockInsumo, Ubicacion
from backend.utils import stock_insumo_total, requiere_rol, registrar_movimiento

insumos_bp = Blueprint('insumos', __name__, url_prefix='/api/insumos')

@insumos_bp.route('', methods=['GET'])
@jwt_required()
def get_insumos():
    resultado = []
    for i in Insumo.query.filter_by(activo=True).order_by(Insumo.nombre).all():
        stocks = StockInsumo.query.filter_by(insumo_id=i.id).all()
        detalle = []
        for s in stocks:
            u = db.session.get(Ubicacion, s.ubicacion_id)
            detalle.append({
                "ubicacion_id": u.id,
                "ubicacion": u.nombre,
                "cantidad": s.cantidad
            })
        total = stock_insumo_total(i.id)
        resultado.append({
            "id": i.id,
            "codigo": i.codigo,
            "nombre": i.nombre,
            "unidad": i.unidad,
            "categoria": i.categoria,
            "descripcion": i.descripcion,
            "cantidad": total,
            "punto_reorden": i.punto_reorden,
            "stock_maximo": i.stock_maximo,
            "proveedor": i.proveedor,
            "costo_unitario": i.costo_unitario,
            "ubicaciones": detalle
        })
    return jsonify(resultado)

@insumos_bp.route('', methods=['POST'])
@requiere_rol("Administrador")
def crear_insumo():
    data = request.get_json() or {}
    required = ["codigo", "nombre", "unidad", "cantidad_inicial", "ubicacion_id"]
    missing = [x for x in required if data.get(x) in (None, "")]
    if missing:
        return jsonify({"error": "Faltan campos obligatorios", "campos": missing}), 400

    codigo = data["codigo"].strip()
    nombre = data["nombre"].strip()
    unidad = data["unidad"].strip()

    if Insumo.query.filter_by(codigo=codigo).first():
        return jsonify({"error": "El código interno ya existe"}), 409
    if Insumo.query.filter_by(nombre=nombre, unidad=unidad).first():
        return jsonify({"error": "Ya existe un insumo con el mismo nombre y unidad"}), 409

    ubicacion = db.session.get(Ubicacion, int(data["ubicacion_id"]))
    if not ubicacion or ubicacion.tipo not in ("MP", "MIXTA"):
        return jsonify({"error": "La ubicación no está habilitada para materia prima"}), 400

    cantidad = float(data["cantidad_inicial"])
    i = Insumo(
        codigo=codigo,
        nombre=nombre,
        unidad=unidad,
        categoria=data.get("categoria", "General"),
        descripcion=data.get("descripcion", ""),
        punto_reorden=float(data.get("punto_reorden", 0) or 0),
        stock_maximo=float(data.get("stock_maximo", 0) or 0),
        proveedor=data.get("proveedor", ""),
        costo_unitario=float(data.get("costo_unitario", 0) or 0)
    )
    db.session.add(i)
    db.session.flush()

    stock = StockInsumo(
        insumo_id=i.id,
        ubicacion_id=ubicacion.id,
        cantidad=cantidad
    )
    db.session.add(stock)

    registrar_movimiento(
        "Entrada inicial",
        "insumo",
        i.id,
        cantidad,
        motivo="Registro de materia prima",
        referencia=data.get("referencia_entrada", ""),
        destino=ubicacion.id
    )
    db.session.commit()
    return jsonify({"message": "Materia prima registrada", "id": i.id}), 201

@insumos_bp.route('/entrada', methods=['POST'])
@requiere_rol("Administrador", "Operario")
def entrada_insumo():
    data = request.get_json() or {}
    try:
        insumo_id = int(data["insumo_id"])
        ubicacion_id = int(data["ubicacion_id"])
        cantidad = float(data["cantidad"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Datos de entrada inválidos"}), 400

    if cantidad <= 0:
        return jsonify({"error": "La cantidad debe ser mayor que cero"}), 400

    insumo = db.session.get(Insumo, insumo_id)
    ubicacion = db.session.get(Ubicacion, ubicacion_id)
    if not insumo or not insumo.activo:
        return jsonify({"error": "Materia prima no válida"}), 404
    if not ubicacion or ubicacion.tipo not in ("MP", "MIXTA"):
        return jsonify({"error": "Ubicación no válida para materia prima"}), 400

    stock = StockInsumo.query.filter_by(insumo_id=insumo_id, ubicacion_id=ubicacion_id).first()
    if not stock:
        stock = StockInsumo(insumo_id=insumo_id, ubicacion_id=ubicacion_id, cantidad=0)
        db.session.add(stock)

    stock.cantidad += cantidad
    registrar_movimiento(
        "Entrada",
        "insumo",
        insumo_id,
        cantidad,
        motivo=data.get("motivo", "Ingreso de materia prima"),
        referencia=data.get("referencia", ""),
        destino=ubicacion_id
    )
    db.session.commit()
    return jsonify({"message": "Entrada registrada"})

@insumos_bp.route('/consumo', methods=['POST'])
@requiere_rol("Administrador", "Operario")
def consumo_insumo():
    data = request.get_json() or {}
    try:
        insumo_id = int(data["insumo_id"])
        ubicacion_id = int(data["ubicacion_id"])
        cantidad = float(data["cantidad"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Datos de consumo inválidos"}), 400

    if cantidad <= 0:
        return jsonify({"error": "La cantidad debe ser mayor que cero"}), 400

    insumo = db.session.get(Insumo, insumo_id)
    stock = StockInsumo.query.filter_by(insumo_id=insumo_id, ubicacion_id=ubicacion_id).first()
    if not insumo or not insumo.activo:
        return jsonify({"error": "Materia prima no válida"}), 404
    if not stock or stock.cantidad < cantidad:
        disponible = stock.cantidad if stock else 0
        return jsonify({
            "error": f"Stock insuficiente. Disponible: {disponible} {insumo.unidad}"
        }), 400

    stock.cantidad -= cantidad
    registrar_movimiento(
        "Consumo producción",
        "insumo",
        insumo_id,
        -cantidad,
        motivo=data.get("motivo", "Consumo"),
        referencia=data.get("referencia", ""),
        origen=ubicacion_id
    )
    db.session.commit()
    return jsonify({"message": "Consumo registrado"})