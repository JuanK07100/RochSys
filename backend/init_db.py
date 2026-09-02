from werkzeug.security import generate_password_hash
from backend.extensions import db
from backend.models import (
    User, Ubicacion, Insumo, StockInsumo,
    ProductoTerminado, StockPT, Receta
)

def initialize():
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

    recetas = [
        Receta(producto_referencia="CAM-001", insumo_id=insumos[0].id, cantidad_necesaria=2.5),
        Receta(producto_referencia="CAM-001", insumo_id=insumos[1].id, cantidad_necesaria=3),
        Receta(producto_referencia="PAN-002", insumo_id=insumos[0].id, cantidad_necesaria=3),
        Receta(producto_referencia="PAN-002", insumo_id=insumos[3].id, cantidad_necesaria=1),
    ]
    db.session.add_all(recetas)

    db.session.commit()
    print("Base de datos RochSis inicializada.")