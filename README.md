# RochSis - Mockup funcional

## Estructura

```text
rochsis_mockup/
├── backend/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── alertas.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── insumos.py
│   │   ├── movimientos.py
│   │   ├── produccion.py
│   │   ├── productos.py
│   │   ├── recetas.py
│   │   ├── ubicaciones.py
│   │   └── usuarios.py
│   ├── app.py
│   ├── config.py
│   ├── extensions.py
│   ├── init_db.py
│   ├── models.py
│   ├── routes.py
│   └── utils.py
├── frontend/
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           ├── alertas.js
│           ├── api.js
│           ├── auth.js
│           ├── dashboard.js
│           ├── insumos.js
│           ├── main.js
│           ├── movimientos.js
│           ├── produccion.js
│           ├── productos.js
│           ├── recetas.js
│           ├── render.js
│           ├── ubicaciones.js
│           ├── ui.js
│           └── usuarios.js
├── templates/
│   └── index.html
├── requirements.txt
└── README.md
```

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir:

http://127.0.0.1:5000

Usuarios demo:

- admin / 1234
- operario / 1234

La base SQLite `rochsis.db` se crea automáticamente.

## Nota

Esta es una versión de mockup funcional para demostración. Antes de producción hay que cambiar la clave JWT, validar entradas con mayor profundidad, usar PostgreSQL, implementar backups, HTTPS y completar la auditoría y gestión de usuarios.
