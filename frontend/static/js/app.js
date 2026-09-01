let token = localStorage.getItem("rochsis_token");
let currentUser = JSON.parse(localStorage.getItem("rochsis_user") || "null");

let insumos = [];
let productos = [];
let ubicaciones = [];

function authHeaders() {
    return {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
    };
}

async function api(url, options = {}) {
    const config = {...options, headers: {...authHeaders(), ...(options.headers || {})}};
    const res = await fetch(url, config);

    if (res.status === 401 || res.status === 403) {
        logout();
        return null;
    }

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
        alert(data.error || "Ocurrió un error");
        return null;
    }

    return data;
}

function showSection(section) {
    document.querySelectorAll(".section").forEach(s => s.classList.remove("active-section"));
    document.getElementById(section).classList.add("active-section");

    document.querySelectorAll(".menu-item").forEach(b => b.classList.remove("active"));
    document.querySelector(`.menu-item[data-section="${section}"]`)?.classList.add("active");

    if (section === "inventario") {
        renderInsumos();
        renderProductos();
    }
    if (section === "movimientos") cargarMovimientos();
    if (section === "alertas") cargarAlertas();
    if (section === "configuracion") cargarUbicaciones();
}

document.querySelectorAll(".menu-item").forEach(btn => {
    btn.addEventListener("click", () => showSection(btn.dataset.section));
});

function openModal(id) {
    cargarUbicaciones();
    if (id === "modalEntrada") cargarSelectEntrada();
    if (id === "modalNuevaMP") cargarSelectNuevaMP();
    if (id === "modalNuevoPT") cargarSelectNuevoPT();
    bootstrap.Modal.getOrCreateInstance(document.getElementById(id)).show();
}

function closeModal(id) {
    bootstrap.Modal.getOrCreateInstance(document.getElementById(id)).hide();
}

async function login() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, password})
    });

    const data = await res.json();

    if (!res.ok) {
        document.getElementById("loginError").textContent = data.error || "Error de autenticación";
        return;
    }

    token = data.token;
    currentUser = data.user;

    localStorage.setItem("rochsis_token", token);
    localStorage.setItem("rochsis_user", JSON.stringify(currentUser));

    document.getElementById("loginView").classList.add("d-none");
    document.getElementById("appView").classList.remove("d-none");
    document.getElementById("userInfo").textContent = `${currentUser.username} · ${currentUser.rol}`;

    aplicarPermisos();
    await cargarTodo();
}

function logout() {
    localStorage.removeItem("rochsis_token");
    localStorage.removeItem("rochsis_user");
    token = null;
    currentUser = null;
    location.reload();
}

function aplicarPermisos() {
    if (currentUser?.rol !== "Administrador") {
        document.querySelectorAll(".admin-only").forEach(el => el.remove());
    }
}

async function cargarTodo() {
    await Promise.all([
        cargarInsumos(),
        cargarProductos(),
        cargarUbicaciones(),
        cargarDashboard(),
        cargarMovimientos()
    ]);

    cargarSelectConsumo();
    cargarSelectVerificacion();
}

async function cargarDashboard() {
    const data = await api("/api/dashboard");
    if (!data) return;

    document.getElementById("statInsumos").textContent = data.total_insumos;
    document.getElementById("statProductos").textContent = data.total_productos;
    document.getElementById("statAlertas").textContent = data.alertas.length;

    renderMovimientos(data.movimientos, "dashboardMovimientos");
}

async function cargarInsumos() {
    insumos = await api("/api/insumos") || [];
    renderInsumos();
}

function renderInsumos() {
    const container = document.getElementById("tablaInsumos");
    if (!container) return;

    const q = (document.getElementById("buscarMP")?.value || "").toLowerCase();

    const data = insumos.filter(i =>
        i.nombre.toLowerCase().includes(q) ||
        i.codigo.toLowerCase().includes(q)
    );

    if (!data.length) {
        container.innerHTML = `<div class="text-muted">No hay materias primas.</div>`;
        return;
    }

    container.innerHTML = `
        <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>Código</th>
                    <th>Materia prima</th>
                    <th>Unidad</th>
                    <th>Stock</th>
                    <th>Reorden</th>
                    <th>Ubicación</th>
                    <th>Proveedor</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(i => `
                    <tr>
                        <td><strong>${i.codigo}</strong></td>
                        <td>${i.nombre}<br><small class="text-muted">${i.categoria}</small></td>
                        <td>${i.unidad}</td>
                        <td class="${i.cantidad <= i.punto_reorden ? "status-low" : "status-ok"}">
                            ${i.cantidad} ${i.unidad}
                        </td>
                        <td>${i.punto_reorden}</td>
                        <td>${i.ubicaciones.map(u => `${u.ubicacion}: ${u.cantidad}`).join("<br>") || "—"}</td>
                        <td>${i.proveedor || "—"}</td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
        </div>
    `;
}

async function cargarProductos() {
    productos = await api("/api/productos") || [];
    renderProductos();
}

function renderProductos() {
    const container = document.getElementById("tablaProductos");
    if (!container) return;

    const q = (document.getElementById("buscarPT")?.value || "").toLowerCase();

    const data = productos.filter(p =>
        p.nombre.toLowerCase().includes(q) ||
        p.referencia.toLowerCase().includes(q)
    );

    container.innerHTML = `
        <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>Referencia</th>
                    <th>Producto</th>
                    <th>Stock total</th>
                    <th>Ubicaciones</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(p => `
                    <tr>
                        <td><strong>${p.referencia}</strong></td>
                        <td>${p.nombre}</td>
                        <td><strong>${p.cantidad}</strong> unidades</td>
                        <td>${p.ubicaciones.map(u => `${u.ubicacion}: ${u.cantidad}`).join("<br>") || "—"}</td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
        </div>
    `;
}

function mostrarInventario(tipo, btn) {
    document.querySelectorAll("#inventario .nav-link").forEach(x => x.classList.remove("active"));
    btn.classList.add("active");

    document.getElementById("inventarioMP").classList.toggle("d-none", tipo !== "mp");
    document.getElementById("inventarioPT").classList.toggle("d-none", tipo !== "pt");
}

async function cargarUbicaciones() {
    ubicaciones = await api("/api/ubicaciones") || [];
    renderUbicaciones();
}

function renderUbicaciones() {
    const c = document.getElementById("tablaUbicaciones");
    if (!c) return;

    c.innerHTML = `
        <div class="table-responsive">
        <table class="table table-hover">
            <thead><tr><th>Nombre</th><th>Tipo</th><th>Descripción</th></tr></thead>
            <tbody>
                ${ubicaciones.map(u => `
                    <tr>
                        <td>${u.nombre}</td>
                        <td><span class="badge text-bg-secondary">${u.tipo}</span></td>
                        <td>${u.descripcion || "—"}</td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
        </div>
    `;
}

function llenarSelect(selectId, items, textFn) {
    const select = document.getElementById(selectId);
    if (!select) return;
    select.innerHTML = items.map(x => `<option value="${x.id}">${textFn(x)}</option>`).join("");
}

function cargarSelectNuevaMP() {
    llenarSelect(
        "mpUbicacion",
        ubicaciones.filter(u => u.tipo === "MP" || u.tipo === "MIXTA"),
        u => u.nombre
    );
}

function cargarSelectEntrada() {
    llenarSelect(
        "entradaInsumo",
        insumos,
        i => `${i.codigo} · ${i.nombre} (${i.cantidad} ${i.unidad})`
    );
    llenarSelect(
        "entradaUbicacion",
        ubicaciones.filter(u => u.tipo === "MP" || u.tipo === "MIXTA"),
        u => u.nombre
    );
}

function cargarSelectNuevoPT() {
    llenarSelect(
        "ptUbicacion",
        ubicaciones.filter(u => u.tipo === "PT" || u.tipo === "MIXTA"),
        u => u.nombre
    );
}

async function crearInsumo() {
    const payload = {
        codigo: document.getElementById("mpCodigo").value.trim(),
        nombre: document.getElementById("mpNombre").value.trim(),
        unidad: document.getElementById("mpUnidad").value,
        categoria: document.getElementById("mpCategoria").value.trim(),
        proveedor: document.getElementById("mpProveedor").value.trim(),
        cantidad_inicial: parseFloat(document.getElementById("mpCantidad").value) || 0,
        punto_reorden: parseFloat(document.getElementById("mpReorden").value) || 0,
        stock_maximo: parseFloat(document.getElementById("mpMaximo").value) || 0,
        costo_unitario: parseFloat(document.getElementById("mpCosto").value) || 0,
        ubicacion_id: document.getElementById("mpUbicacion").value,
        descripcion: document.getElementById("mpDescripcion").value.trim()
    };

    const res = await api("/api/insumos", {
        method: "POST",
        body: JSON.stringify(payload)
    });

    if (res) {
        closeModal("modalNuevaMP");
        await cargarTodo();
        alert("Materia prima registrada correctamente.");
    }
}

async function registrarEntrada() {
    const payload = {
        insumo_id: document.getElementById("entradaInsumo").value,
        ubicacion_id: document.getElementById("entradaUbicacion").value,
        cantidad: parseFloat(document.getElementById("entradaCantidad").value),
        referencia: document.getElementById("entradaReferencia").value.trim(),
        motivo: document.getElementById("entradaMotivo").value.trim()
    };

    if (!payload.cantidad || payload.cantidad <= 0) {
        alert("Introduce una cantidad válida.");
        return;
    }

    const res = await api("/api/insumos/entrada", {
        method: "POST",
        body: JSON.stringify(payload)
    });

    if (res) {
        closeModal("modalEntrada");
        await cargarTodo();
        alert("Entrada registrada.");
    }
}

async function crearProducto() {
    const payload = {
        referencia: document.getElementById("ptRef").value.trim(),
        nombre: document.getElementById("ptNombre").value.trim(),
        cantidad_inicial: parseFloat(document.getElementById("ptCantidad").value) || 0,
        ubicacion_id: document.getElementById("ptUbicacion").value,
        descripcion: document.getElementById("ptDescripcion").value.trim()
    };

    const res = await api("/api/productos", {
        method: "POST",
        body: JSON.stringify(payload)
    });

    if (res) {
        closeModal("modalNuevoPT");
        await cargarTodo();
        alert("Producto terminado registrado.");
    }
}

function cargarSelectConsumo() {
    llenarSelect(
        "consumoInsumo",
        insumos,
        i => `${i.codigo} · ${i.nombre} (${i.cantidad} ${i.unidad})`
    );
    cargarUbicacionesConsumo();
}

function cargarUbicacionesConsumo() {
    const insumoId = Number(document.getElementById("consumoInsumo")?.value);
    const insumo = insumos.find(i => i.id === insumoId);

    const select = document.getElementById("consumoUbicacion");
    if (!select) return;

    select.innerHTML = (insumo?.ubicaciones || [])
        .filter(u => u.cantidad > 0)
        .map(u => `<option value="${u.ubicacion_id}">${u.ubicacion} · ${u.cantidad} ${insumo.unidad}</option>`)
        .join("");
}

async function registrarConsumo() {
    const payload = {
        insumo_id: document.getElementById("consumoInsumo").value,
        ubicacion_id: document.getElementById("consumoUbicacion").value,
        cantidad: parseFloat(document.getElementById("consumoCantidad").value),
        motivo: document.getElementById("consumoMotivo").value.trim()
    };

    if (!payload.cantidad || payload.cantidad <= 0) {
        alert("Introduce una cantidad válida.");
        return;
    }

    const res = await api("/api/insumos/consumo", {
        method: "POST",
        body: JSON.stringify(payload)
    });

    const result = document.getElementById("consumoResultado");

    if (res) {
        result.innerHTML = `<div class="alert alert-success">Consumo registrado correctamente.</div>`;
        document.getElementById("consumoCantidad").value = "";
        document.getElementById("consumoMotivo").value = "";
        await cargarTodo();
    } else {
        result.innerHTML = `<div class="alert alert-danger">No fue posible registrar el consumo.</div>`;
    }
}

function cargarSelectVerificacion() {
    llenarSelect(
        "verifProducto",
        productos,
        p => `${p.referencia} · ${p.nombre}`
    );
}

async function verificarPedido() {
    const referencia = document.getElementById("verifProducto").value;
    const cantidad = parseFloat(document.getElementById("verifCantidad").value);

    const res = await api("/api/produccion/verificar", {
        method: "POST",
        body: JSON.stringify({
            pedidos: [{referencia, cantidad}]
        })
    });

    const c = document.getElementById("verificacionResultado");

    if (!res || !res.length) {
        c.innerHTML = `<div class="alert alert-warning">No hay una lista de materiales configurada para este producto.</div>`;
        return;
    }

    const viable = res.every(x => x.suficiente);

    c.innerHTML = `
        <div class="alert ${viable ? "alert-success" : "alert-danger"}">
            <strong>${viable ? "✓ Pedido viable" : "✕ Pedido no viable"}</strong>
            ${viable ? " Hay suficiente materia prima." : " Hay materiales insuficientes."}
        </div>

        <div class="table-responsive">
        <table class="table">
            <thead>
                <tr>
                    <th>Insumo</th>
                    <th>Disponible</th>
                    <th>Necesario</th>
                    <th>Diferencia</th>
                    <th>Estado</th>
                </tr>
            </thead>
            <tbody>
                ${res.map(x => `
                    <tr class="${x.suficiente ? "table-success" : "table-danger"}">
                        <td>${x.codigo} · ${x.nombre}</td>
                        <td>${x.stock} ${x.unidad}</td>
                        <td>${x.necesario} ${x.unidad}</td>
                        <td>${x.diferencia} ${x.unidad}</td>
                        <td>${x.suficiente ? "✓ Suficiente" : "✕ Faltante"}</td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
        </div>
    `;
}

async function cargarMovimientos() {
    const data = await api("/api/movimientos");
    if (data) renderMovimientos(data, "tablaMovimientos");
}

function renderMovimientos(data, containerId) {
    const c = document.getElementById(containerId);
    if (!c) return;

    if (!data.length) {
        c.innerHTML = `<div class="text-muted">No hay movimientos registrados.</div>`;
        return;
    }

    c.innerHTML = `
        <div class="table-responsive">
        <table class="table table-hover table-sm">
            <thead>
                <tr>
                    <th>Fecha</th>
                    <th>Tipo</th>
                    <th>Referencia</th>
                    <th>Cantidad</th>
                    <th>Ubicación</th>
                    <th>Usuario</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(m => `
                    <tr>
                        <td>${m.fecha_hora}</td>
                        <td>${m.tipo}</td>
                        <td>${m.referencia || "—"}</td>
                        <td>${m.cantidad}</td>
                        <td>${m.origen && m.destino ? `${m.origen} → ${m.destino}` : (m.origen || m.destino || "—")}</td>
                        <td>${m.usuario}</td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
        </div>
    `;
}

async function cargarAlertas() {
    const data = await api("/api/alertas");
    const c = document.getElementById("alertasLista");
    if (!c || !data) return;

    if (!data.length) {
        c.innerHTML = `<div class="alert alert-success">No hay materias primas por debajo del punto de reorden.</div>`;
        return;
    }

    c.innerHTML = data.map(a => `
        <div class="alert-card">
            <strong><i class="fa-solid fa-triangle-exclamation text-danger"></i> ${a.codigo} · ${a.nombre}</strong>
            <div class="mt-2">
                Stock actual: <strong>${a.cantidad} ${a.unidad}</strong>
                · Punto de reorden: <strong>${a.punto_reorden} ${a.unidad}</strong>
            </div>
        </div>
    `).join("");
}

async function crearUbicacion() {
    const payload = {
        nombre: document.getElementById("ubicNombre").value.trim(),
        tipo: document.getElementById("ubicTipo").value,
        descripcion: document.getElementById("ubicDescripcion").value.trim()
    };

    const res = await api("/api/ubicaciones", {
        method: "POST",
        body: JSON.stringify(payload)
    });

    if (res) {
        document.getElementById("ubicNombre").value = "";
        document.getElementById("ubicDescripcion").value = "";
        await cargarUbicaciones();
        alert("Ubicación creada.");
    }
}

if (token && currentUser) {
    document.getElementById("loginView").classList.add("d-none");
    document.getElementById("appView").classList.remove("d-none");
    document.getElementById("userInfo").textContent = `${currentUser.username} · ${currentUser.rol}`;
    aplicarPermisos();
    cargarTodo();
}
