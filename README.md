# RochSis - Mockup funcional

## Estructura

```text
rochsis_mockup/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
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
