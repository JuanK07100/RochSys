from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import timedelta

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///rochsis.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "cambia-esta-clave-en-produccion"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)


# =========================
# MODELOS
# =========================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), nullable=False)


class Ubicacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # MP, PT, MIXTA
    descripcion = db.Column(db.String(200), default="")
    activa = db.Column(db.Boolean, default=True)


class Insumo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    unidad = db.Column(db.String(20), nullable=False)
    categoria = db.Column(db.String(50), default="General")
    descripcion = db.Column(db.String(250), default="")
    punto_reorden = db.Column(db.Float, default=0)
    stock_maximo = db.Column(db.Float, default=0)
    proveedor = db.Column(db.String(120), default="")
    costo_unitario = db.Column(db.Float, default=0)
    activo = db.Column(db.Boolean, default=True)


class StockInsumo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    insumo_id = db.Column(db.Integer, db.ForeignKey("insumo.id"), nullable=False)
    ubicacion_id = db.Column(db.Integer, db.ForeignKey("ubicacion.id"), nullable=False)
    cantidad = db.Column(db.Float, default=0)


class ProductoTerminado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referencia = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(250), default="")
    activo = db.Column(db.Boolean, default=True)


class StockPT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("producto_terminado.id"), nullable=False)
    ubicacion_id = db.Column(db.Integer, db.ForeignKey("ubicacion.id"), nullable=False)
    cantidad = db.Column(db.Float, default=0)


class Movimiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    entidad_tipo = db.Column(db.String(20), nullable=False)
    entidad_id = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    motivo = db.Column(db.String(250), default="")
    usuario_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    ubicacion_origen_id = db.Column(db.Integer, nullable=True)
    ubicacion_destino_id = db.Column(db.Integer, nullable=True)
    referencia = db.Column(db.String(100), default="")
    fecha_hora = db.Column(db.DateTime, server_default=db.func.now())


class BOM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_referencia = db.Column(db.String(50), nullable=False)
    insumo_id = db.Column(db.Integer, db.ForeignKey("insumo.id"), nullable=False)
    cantidad_necesaria = db.Column(db.Float, nullable=False)


# =========================
# UTILIDADES
# =========================

def usuario_actual():
    uid = int(get_jwt_identity())
    return db.session.get(User, uid)


def requiere_rol(*roles):
    def deco(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = usuario_actual()
            if not user or user.rol not in roles:
                return jsonify({"error": "No tienes permisos para esta acción"}), 403
            return func(*args, **kwargs)
        return wrapper
    return deco


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


# =========================
# VISTAS
# =========================

@app.route("/")
def index():
    return render_template("index.html")


# =========================
# AUTENTICACIÓN
# =========================

@app.post("/api/auth/login")
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(username=data.get("username", "")).first()

    if not user or not check_password_hash(
        user.password_hash, data.get("password", "")
    ):
        return jsonify({"error": "Usuario o contraseña inválidos"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "rol": user.rol
        }
    })


# =========================
# DASHBOARD
# =========================

@app.get("/api/dashboard")
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


# =========================
# UBICACIONES
# =========================

@app.get("/api/ubicaciones")
@jwt_required()
def get_ubicaciones():
    return jsonify([{
        "id": u.id,
        "nombre": u.nombre,
        "tipo": u.tipo,
        "descripcion": u.descripcion
    } for u in Ubicacion.query.filter_by(activa=True).order_by(Ubicacion.nombre).all()])


@app.post("/api/ubicaciones")
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


# =========================
# INSUMOS / MATERIA PRIMA
# =========================

@app.get("/api/insumos")
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


@app.post("/api/insumos")
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


# =========================
# ENTRADAS DE MATERIA PRIMA
# =========================

@app.post("/api/insumos/entrada")
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

    stock = StockInsumo.query.filter_by(
        insumo_id=insumo_id,
        ubicacion_id=ubicacion_id
    ).first()

    if not stock:
        stock = StockInsumo(
            insumo_id=insumo_id,
            ubicacion_id=ubicacion_id,
            cantidad=0
        )
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


# =========================
# CONSUMO DE MATERIA PRIMA
# =========================

@app.post("/api/insumos/consumo")
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
    stock = StockInsumo.query.filter_by(
        insumo_id=insumo_id,
        ubicacion_id=ubicacion_id
    ).first()

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


# =========================
# PRODUCTOS TERMINADOS
# =========================

@app.get("/api/productos")
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


@app.post("/api/productos")
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

    stock = StockPT(
        producto_id=p.id,
        ubicacion_id=ubicacion.id,
        cantidad=cantidad
    )
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


@app.post("/api/productos/transferir")
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

    stock_origen = StockPT.query.filter_by(
        producto_id=producto_id,
        ubicacion_id=origen_id
    ).first()

    if not stock_origen or stock_origen.cantidad < cantidad:
        disponible = stock_origen.cantidad if stock_origen else 0
        return jsonify({"error": f"Stock insuficiente en origen. Disponible: {disponible}"}), 400

    stock_destino = StockPT.query.filter_by(
        producto_id=producto_id,
        ubicacion_id=destino_id
    ).first()

    if not stock_destino:
        stock_destino = StockPT(
            producto_id=producto_id,
            ubicacion_id=destino_id,
            cantidad=0
        )
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


# =========================
# BOM / VERIFICACIÓN
# =========================

@app.post("/api/produccion/verificar")
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

        bom_items = BOM.query.filter_by(
            producto_referencia=referencia
        ).all()

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


# =========================
# MOVIMIENTOS
# =========================

def movimientos_data(limit=50):
    movs = Movimiento.query.order_by(
        Movimiento.fecha_hora.desc()
    ).limit(limit).all()

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


@app.get("/api/movimientos")
@jwt_required()
def get_movimientos():
    return jsonify(movimientos_data(50))


# =========================
# ALERTAS
# =========================

@app.get("/api/alertas")
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


# =========================
# SEMILLA
# =========================

def inicializar():
    db.create_all()

    if User.query.count() > 0:
        return

    admin = User(
        username="admin",
        password_hash=generate_password_hash("1234"),
        rol="Administrador"
    )
    operario = User(
        username="operario",
        password_hash=generate_password_hash("1234"),
        rol="Operario"
    )
    db.session.add_all([admin, operario])

    ubicaciones = [
        Ubicacion(nombre="Bodega MP 1", tipo="MP", descripcion="Materia prima principal"),
        Ubicacion(nombre="Bodega MP 2", tipo="MP", descripcion="Materia prima secundaria"),
        Ubicacion(nombre="Bodega PT 1", tipo="PT", descripcion="Producto terminado"),
        Ubicacion(nombre="Bodega PT 2", tipo="PT", descripcion="Producto terminado"),
        Ubicacion(nombre="Vitrina", tipo="PT", descripcion="Exhibición"),
    ]
    db.session.add_all(ubicaciones)
    db.session.flush()

    bodega_mp1 = ubicaciones[0]
    bodega_mp2 = ubicaciones[1]
    bodega_pt1 = ubicaciones[2]
    bodega_pt2 = ubicaciones[3]
    vitrina = ubicaciones[4]

    insumos = [
        Insumo(
            codigo="TEL-ALG-001", nombre="Tela Algodón", unidad="m",
            categoria="Tela", descripcion="Tela de algodón para confección",
            punto_reorden=30, stock_maximo=250, proveedor="Proveedor Textil",
            costo_unitario=12000
        ),
        Insumo(
            codigo="HIL-NEG-001", nombre="Hilo Negro", unidad="unidad",
            categoria="Hilo", descripcion="Hilo negro para confección",
            punto_reorden=10, stock_maximo=100, proveedor="Hilos Colombia",
            costo_unitario=2500
        ),
        Insumo(
            codigo="BOT-15-001", nombre="Botón 15 mm", unidad="unidad",
            categoria="Accesorio", descripcion="Botón plástico de 15 mm",
            punto_reorden=50, stock_maximo=500, proveedor="Accesorios Rochy",
            costo_unitario=350
        ),
        Insumo(
            codigo="CIE-MET-001", nombre="Cierre Metálico", unidad="unidad",
            categoria="Accesorio", descripcion="Cierre metálico",
            punto_reorden=15, stock_maximo=150, proveedor="Cierres SAS",
            costo_unitario=1800
        ),
        Insumo(
            codigo="TEL-POL-001", nombre="Tela Poliéster", unidad="m",
            categoria="Tela", descripcion="Tela de poliéster",
            punto_reorden=20, stock_maximo=200, proveedor="Proveedor Textil",
            costo_unitario=9500
        ),
    ]
    db.session.add_all(insumos)
    db.session.flush()

    stocks_mp = [
        StockInsumo(insumo_id=insumos[0].id, ubicacion_id=bodega_mp1.id, cantidad=150),
        StockInsumo(insumo_id=insumos[1].id, ubicacion_id=bodega_mp1.id, cantidad=45),
        StockInsumo(insumo_id=insumos[2].id, ubicacion_id=bodega_mp1.id, cantidad=200),
        StockInsumo(insumo_id=insumos[3].id, ubicacion_id=bodega_mp2.id, cantidad=80),
        StockInsumo(insumo_id=insumos[4].id, ubicacion_id=bodega_mp2.id, cantidad=0),
    ]
    db.session.add_all(stocks_mp)

    productos = [
        ProductoTerminado(
            referencia="CAM-001",
            nombre="Camisa Manga Larga",
            descripcion="Camisa de dotación"
        ),
        ProductoTerminado(
            referencia="PAN-002",
            nombre="Pantalón Drill",
            descripcion="Pantalón industrial"
        ),
        ProductoTerminado(
            referencia="DEL-003",
            nombre="Delantal Industrial",
            descripcion="Delantal para línea industrial"
        ),
    ]
    db.session.add_all(productos)
    db.session.flush()

    stocks_pt = [
        StockPT(producto_id=productos[0].id, ubicacion_id=bodega_pt1.id, cantidad=15),
        StockPT(producto_id=productos[0].id, ubicacion_id=vitrina.id, cantidad=10),
        StockPT(producto_id=productos[1].id, ubicacion_id=bodega_pt2.id, cantidad=12),
        StockPT(producto_id=productos[2].id, ubicacion_id=bodega_pt2.id, cantidad=40),
    ]
    db.session.add_all(stocks_pt)

    bom = [
        BOM(producto_referencia="CAM-001", insumo_id=insumos[0].id, cantidad_necesaria=2.5),
        BOM(producto_referencia="CAM-001", insumo_id=insumos[1].id, cantidad_necesaria=3),
        BOM(producto_referencia="PAN-002", insumo_id=insumos[0].id, cantidad_necesaria=3),
        BOM(producto_referencia="PAN-002", insumo_id=insumos[3].id, cantidad_necesaria=1),
    ]
    db.session.add_all(bom)

    db.session.commit()
    print("Base de datos RochSis inicializada.")


with app.app_context():
    inicializar()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
