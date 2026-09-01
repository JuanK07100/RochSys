export function renderInsumos(data, containerId = "tablaInsumos", searchInputId = "buscarMP") {
    const container = document.getElementById(containerId);
    if (!container) return;

    const insumos = data || window.insumos || [];
    const q = (document.getElementById(searchInputId)?.value || "").toLowerCase();

    const filtered = insumos.filter(i =>
        i.nombre.toLowerCase().includes(q) ||
        i.codigo.toLowerCase().includes(q)
    );

    if (!filtered.length) {
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
                ${filtered.map(i => `
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

export function renderProductos(data, containerId = "tablaProductos", searchInputId = "buscarPT") {
    const container = document.getElementById(containerId);
    if (!container) return;

    const productos = data || window.productos || [];
    const q = (document.getElementById(searchInputId)?.value || "").toLowerCase();

    const filtered = productos.filter(p =>
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
                ${filtered.map(p => `
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

export function renderUbicaciones(data, containerId = "tablaUbicaciones") {
    const c = document.getElementById(containerId);
    if (!c) return;

    const ubicaciones = data || window.ubicaciones || [];

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

export function renderMovimientos(data, containerId) {
    const c = document.getElementById(containerId);
    if (!c) return;

    const movimientos = data || window.movimientos || [];

    if (!movimientos.length) {
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
                ${movimientos.map(m => `
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