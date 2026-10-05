// Variable con el token
const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
// url del endpoint principal

// url del endpoint principal
let selectedShopId = localStorage.getItem("selectedShopId");
let urlSell = "/business-gestion/group-sells/";

$(function () {
  bsCustomFileInput.init();
  $("#filter-form")[0].reset();
  // $("#reservationdatetime").datetimepicker({ icons: { time: "far fa-clock" } });
});

$(function () {
  bsCustomFileInput.init();
});

$(document).ready(function () {
  const table = $("#tabla-de-Datos").DataTable({
    responsive: true,
    lengthMenu: [
      [10, 25, 50, 100, -1],
      [10, 25, 50, 100, "Todos"],
    ],
    dom: '<"top"l>Bfrtip',
    buttons: [
      {
        extend: "excel",
        text: "Excel",
      },
      {
        extend: "pdf",
        text: "PDF",
      },
      {
        extend: "print",
        text: "Print",
      },
    ],
    serverSide: true,
    // Live search debounce is handled by serverSideAjax.
    searchDelay: 0,
    processing: true,

    ajax: serverSideAjax(function (data, callback, settings) {
      const filters = $("#filter-form").serializeArray();
      if (filters.length > 1 && filters[1].value != "") {
        filters[1].value += ":23:59";
      }
      const params = {};
      filters.forEach((filter) => {
        if (filter.value) {
          params[filter.name] = filter.value;
        }
      });
      dir = "";
      if (data.order[0].dir == "desc") {
        dir = "-";
      }
      params.page_size = data.length;
      params.page = data.start / data.length + 1;
      params.ordering = dir + data.columns[data.order[0].column].data;
      params.search = data.search.value;
      if (selectedShopId) {
        params.sells__shop_product__shop = selectedShopId;
      }

      axios
        .get(urlSell, { params })
        .then((res) => {
          callback({
            draw: data.draw,
            recordsTotal: res.data.count,
            recordsFiltered: res.data.count,
            data: res.data.results,
          });
        })
        .catch((error) => {
          alert(error);
        });
    }),
    columns: [
      {
        data: "id",
        title: "Grupo de Venta",
        visible: false,
      },
      { data: "id", title: "ID" },
      { data: "for_date_label", title: "Fecha" },
      { data: "client_name", title: "Cliente" },
      { data: "total", title: "Total" },
      { data: "discount", title: "Descuento" },
      { data: "net_total", title: "Total Neto" },
      { data: "payment_method_label", title: "Método de Pago" },
      {
        data: "id",
        title: "Acciones",
        render: (data, type, row) => {
          return `<button type="button" title="Ver detalle" class="btn bg-primary" onclick="toggleGroupSells(${data})">
                    <i class="nav-icon fas fa-plus"></i>
                    </button>
                    <button type="button" title="Generar informe" class="btn bg-info ml-1" onclick="generarInformeVenta('${data}')">
                    <i class="nav-icon fas fa-file-invoice"></i>
                    </button>`;
        },
      },
    ],
    
    // La columna Fecha se elimino de la tabla, asi que el orden descendente se
    // aplica sobre el grupo (columna oculta): los grupos mas recientes salen primero.
    order: [[0, "desc"]],
    rowGroup: null,
    columnDefs: [],
  });

  initPeriodReportButton();

  // Manejo del formulario de filtros
  $("#filter-form").on("submit", function (event) {
    event.preventDefault();
    table.ajax.reload();
  });

  // Restablecer filtros
  $("#reset-filters").on("click", function () {
    $("#filter-form")[0].reset();
    table.ajax.reload();
  });

  // Mostrar/Ocultar filtros
  $("#toggle-filters").on("click", function () {
    $("#filter-section").toggle();
  });
});

function function_delete(id, name, quantity, date, seller) {
  const table = $("#tabla-de-Datos").DataTable();
  Swal.fire({
    title: "Confirmación requerida",
    text: `¿Está seguro que desea eliminar la venta de ${quantity} ${name} hecha por ${seller} el día ${date}?`,
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Si, Eliminar",
  }).then((result) => {
    if (result.isConfirmed) {
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      axios
        .delete(`${urlSell}${id}/`)
        .then((response) => {
          if (response.status === 204) {
            table.row(`#${id}`).remove().draw();
            Swal.fire({
              icon: "success",
              title: "Eliminar Elemento",
              text: "Elemento eliminado satisfactoriamente ",
              showConfirmButton: false,
              timer: 1500,
            });
          }
        })
        .catch((error) => {
          Swal.fire({
            icon: "error",
            title: "Error eliminando elemento",
            text: error.response.data.detail,
            showConfirmButton: false,
            timer: 3000,
          });
        });
    }
  });
}

let urlSellGroup = "/business-gestion/sell-groups/";

/**
 * Reporte de ventas por periodo: lista los grupos de venta con su monto y el TOTAL.
 *
 * El rango se toma de los mismos datepickers de los filtros ("Ventas Desde" y
 * "Ventas Hasta"), asi no hay dos juegos de fechas que se contradigan. Sin fechas
 * el reporte cae en el dia de hoy.
 */
function initPeriodReportButton() {
  $("#period-report-button").on("click", function () {
    const filters = $("#filter-form").serializeArray();
    const valorDe = (name) => {
      const filtro = filters.find((item) => item.name === name);
      return filtro ? filtro.value : "";
    };

    generarReporteVentas(
      valorDe("created_timestamp__gte"),
      valorDe("created_timestamp__lte"),
    );
  });
}

// Generar el reporte de ventas de un periodo, por defecto el dia de hoy
async function generarReporteVentas(startDate, endDate) {
  if (startDate && endDate && startDate > endDate) {
    Swal.fire({
      icon: "warning",
      title: "Revise el periodo",
      text: "La fecha 'Ventas Desde' no puede ser mayor que la fecha 'Ventas Hasta'.",
    });
    return;
  }

  const reportButton = $("#period-report-button");
  const originalHtml = reportButton.html();
  reportButton.prop("disabled", true);
  reportButton.html('<i class="nav-icon fas fa-spinner fa-spin"></i> Generando...');

  const params = {};
  if (startDate) {
    params.start_date = startDate;
  }
  if (endDate) {
    params.end_date = endDate;
  }
  const shopId = localStorage.getItem("selectedShopId");
  if (shopId) {
    params.shop = shopId;
  }

  try {
    const response = await axios.get(`${urlSellGroup}period-report/`, { params });
    const reportText = (response.data?.report || "").trim();
    if (!reportText) {
      throw new Error("El reporte esta vacio");
    }

    const groups = Number(response.data?.groups || 0);
    const total = response.data?.total || "0.00";

    const result = await Swal.fire({
      icon: "success",
      title: `Reporte de ventas (${groups} ${groups === 1 ? "grupo" : "grupos"})`,
      html: buildInformeHtml(reportText),
      width: 700,
      showDenyButton: true,
      confirmButtonText: "Copiar reporte",
      denyButtonText: "Cerrar",
      didOpen: () => {
        const comprobante = document.getElementById("sale-comprobante");
        if (comprobante) {
          comprobante.scrollTop = 0;
        }
      },
    });

    if (result.isConfirmed) {
      const copied = await copiarComprobante(reportText);
      if (copied) {
        await Swal.fire({
          icon: "success",
          title: "Reporte copiado",
          text: `El reporte por $${total} se copio al portapapeles.`,
        });
      } else {
        await Swal.fire({
          icon: "error",
          title: "No se pudo copiar",
          text: "No fue posible copiar el reporte automaticamente.",
        });
      }
    }
  } catch (error) {
    Swal.fire({
      icon: "error",
      title: "Error generando el reporte",
      text:
        "No fue posible generar el reporte de ventas: " +
        (error.response?.data?.detail || error.message),
    });
  } finally {
    reportButton.prop("disabled", false);
    reportButton.html(originalHtml);
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.innerText = text == null ? "" : String(text);
  return div.innerHTML;
}

// Generar el comprobante de un grupo de ventas
function generarInformeVenta(sellGroupId) {
  const reportButton = event.target.closest("button");
  const originalHtml = reportButton ? reportButton.innerHTML : "";
  if (reportButton) {
    reportButton.disabled = true;
    reportButton.innerHTML =
      '<i class="nav-icon fas fa-spinner fa-spin"></i> Generando...';
  }

  axios
    .get(`${urlSellGroup}${sellGroupId}/report/`)
    .then(async (response) => {
      const reportText = (response.data?.report || "").trim();
      if (!reportText) {
        throw new Error("El informe esta vacio");
      }

      const result = await Swal.fire({
        icon: "success",
        title: `Comprobante de la venta ${sellGroupId}`,
        html: buildInformeHtml(reportText),
        width: 700,
        showDenyButton: true,
        confirmButtonText: "Copiar comprobante",
        denyButtonText: "Cerrar",
        didOpen: () => {
          const comprobante = document.getElementById("sale-comprobante");
          if (comprobante) {
            comprobante.scrollTop = 0;
          }
        },
      });

      if (result.isConfirmed) {
        const copied = await copiarComprobante(reportText);
        if (copied) {
          await Swal.fire({
            icon: "success",
            title: "Comprobante copiado",
            text: "El comprobante se copio al portapapeles.",
          });
        } else {
          await Swal.fire({
            icon: "error",
            title: "No se pudo copiar",
            text: "No fue posible copiar el comprobante automaticamente.",
          });
        }
      }
    })
    .catch((error) => {
      Swal.fire({
        icon: "error",
        title: "Error generando el informe",
        text:
          "No fue posible generar el comprobante: " +
          (error.response?.data?.detail || error.message),
      });
    })
    .finally(() => {
      if (reportButton) {
        reportButton.disabled = false;
        reportButton.innerHTML = originalHtml;
      }
    });
}

function buildInformeHtml(reportText) {
  return `
    <div id="sale-comprobante" style="text-align:left;max-height:360px;overflow:auto;">
      <pre style="white-space:pre-wrap;font-family:monospace;margin:0;">${escapeHtml(reportText)}</pre>
    </div>
  `;
}

async function copiarComprobante(text) {
  const content = (text || "").trim();

  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(content);
      return true;
    }

    const textarea = document.createElement("textarea");
    textarea.value = content;
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    const successful = document.execCommand("copy");
    document.body.removeChild(textarea);
    return successful;
  } catch (error) {
    return false;
  }
}

function toggleGroupSells(groupId) {
  const table = $("#tabla-de-Datos").DataTable();
  const row = table.rows().data().toArray().find((r) => r.id == groupId);
  if (!row || !row.sells) {
    return;
  }
  const sells = row.sells;
  const sellsHtml = sells
    .map(
      (s, i) => `
        <tr>
          <td>${i + 1}</td>
          <td>${escapeHtml(s.product_name || "")}</td>
          <td>${s.quantity}</td>
          <td>$${Number(s.sell_price || 0).toFixed(2)}</td>
          <td>$${Number(s.total_priced || 0).toFixed(2)}</td>
          <td>${escapeHtml(s.seller__first_name || "")}</td>
        </tr>
      `
    )
    .join("");
  Swal.fire({
    title: `Ventas del grupo ${groupId}`,
    html: `
      <div style="max-height:400px;overflow:auto;">
        <table class="table table-bordered table-sm" style="width:100%">
          <thead>
            <tr>
              <th>#</th>
              <th>Producto</th>
              <th>Cantidad</th>
              <th>Precio unitario</th>
              <th>Monto total</th>
              <th>Vendedor</th>
            </tr>
          </thead>
          <tbody>${sellsHtml}</tbody>
        </table>
      </div>
    `,
    width: 900,
    showCloseButton: true,
    confirmButtonText: "Cerrar",
  });
}
