from backend.extensions import db

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

class Receta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_referencia = db.Column(db.String(50), nullable=False)
    insumo_id = db.Column(db.Integer, db.ForeignKey("insumo.id"), nullable=False)
    cantidad_necesaria = db.Column(db.Float, nullable=False)