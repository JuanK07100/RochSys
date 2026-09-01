import { api } from './api.js';

export async function verificarPedido() {
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