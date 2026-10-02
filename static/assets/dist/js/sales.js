// Variable con el token
const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
// url del endpoint principal

// url del endpoint principal
let selectedShopId = localStorage.getItem("selectedShopId");
let urlSell = "/business-gestion/sell-products/";

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
    search: {
      return: true,
    },
    processing: true,

    ajax: function (data, callback, settings) {
      const filters = $("#filter-form").serializeArray();
      if (filters[1].value != "") {
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
      params.shop_product__shop = selectedShopId;

      axios
        .get(urlSell, { params })
        .then((res) => {
          callback({
            recordsTotal: res.data.count,
            recordsFiltered: res.data.count,
            data: res.data.results,
          });
        })
        .catch((error) => {
          alert(error);
        });
    },
    columns: [
      {
        data: "sell_group",
        title: "Grupo de Venta",
        visible: false, // La columna estará oculta ya que se usa solo para agrupar
      },
      { data: "product_name", title: "Producto" },
      { data: "quantity", title: "Cantidad" },
      { data: "sell_price", title: "Precio unitario" },
      { data: "total_priced", title: "Monto total" },
      { data: "profits", title: "Ganancia" },
      { data: "seller__first_name", title: "Vendedor" },
      { data: "created_timestamp", title: "Fecha" },
      {
        data: "id",
        title: "Acciones",
        render: (data, type, row) => {
          return `<button type="button" title="delete" class="btn bg-olive" onclick="function_delete('${row.id}','${row.product_name}','${row.quantity}','${row.created_timestamp}','${row.seller__first_name}')" >
                    <i class="fas fa-trash"></i>
                    </button>`;
        },
      },
    ],
    order: [[7, "desc"]], // Primero ordena por grupo, luego por fecha
    rowGroup: {
      dataSrc: "sell_group",
      startRender: function (rows, group) {
        // Group level data is the same on every row of the group, so the first one
        // carries everything needed to build the header.
        const first = rows.data()[0];
        const discount = Number(first.discounts || 0);
        const total = Number(first.group_total || 0);
        const clientName = (first.client_name || "").trim();
        const clientLabel = clientName
          ? `Venta ${group} (${clientName}):`
          : `Venta ${group}:`;

        let header = `${clientLabel} Importe: $${total.toFixed(2)}`;
        if (discount > 0) {
          // The net amount only makes sense once the discount is taken off the gross.
          header += ` ($${(total - discount).toFixed(2)}) | Descuento: $${discount.toFixed(2)}`;
        }
        const note = (first.group_extra_info || "").trim();
        if (note) {
          header += ` | Nota: ${note}`;
        }
        // The label is escaped and kept apart from the button markup; the flex
        // wrapper pushes the button to the right edge of the full width group row.
        return `
          <div class="d-flex justify-content-between align-items-center w-100">
            <span class="flex-grow-1 mr-2">${escapeHtml(header)}</span>
            <button type="button" class="btn btn-sm btn-outline-primary text-nowrap" onclick="generarInformeVenta(${group})">
              <i class="nav-icon fas fa-file-invoice"></i> Generar informe
            </button>
          </div>
        `;
      },
    },
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
