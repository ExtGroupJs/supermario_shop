// Variable con el token
const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

// url del endpoint principal
const url = "/business-gestion/shop-products/";

$(function () {
  bsCustomFileInput.init();

  // poblarListas();
});

// Inicializar DataTable
$(document).ready(function () {
  const table = $("#tabla-de-Datos").DataTable({
    responsive: true,
    lengthMenu: [
      [10, 25, 50, 100, -1], // Valores
      [10, 25, 50, 100, "Todos"], // Etiquetas
    ],
    dom: '<"top"l>Bfrtip',
    buttons: [
      {
        extend: "excel",
        text: "Excel",
        exportOptions: {
          columns: [2, 3, 4, 5],
          stripHtml: false, // No eliminar imágenes
        },
      },
      {
        extend: "pdf",
        text: "PDF",
        exportOptions: {
          columns: [2, 3, 4, 5],
          stripHtml: false, // No eliminar imágenes
        },
      },
      {
        extend: "print",
        text: "Print",
        exportOptions: {
          columns: [2, 3, 4, 5],
          stripHtml: false, // No eliminar imágenes
        },
      },
    ],
    serverSide: true,
    processing: true,
    ajax: function (data, callback, settings) {
      const params = {};
      dir = "";

      if (data.order[0].dir == "desc") {
        dir = "-";
      }

      // Añadir parámetros de paginación
      params.page_size = data.length;
      params.page = data.start / data.length + 1;
      params.ordering = dir + data.columns[data.order[0].column].data;
      params.search = data.search.value;

      axios
        .get(url, { params })
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
      { data: "shop_name", title: "Tienda" },
      {
        data: "id",
        title: "Foto",
        render: (data, type, row) => {
          if (data) {
            return `<div style="text-align: center;"><img src="${row.product.image}" alt="image" style="width: 50px; height: auto;" class="thumbnail" data-fullsize="${row.product.image}"></div>`;
          } else {
            return `<div style="text-align: center;"><i class="nav-icon fas fa-car-crash text-danger"></i></div>`;
          }
        },
      },
      { data: "product_name", title: "Producto" },
      { data: "quantity", title: "Cantidad" },

      { data: "sell_price", title: "Precio de Venta" },
      { data: "extra_info", title: "Información Extra" },
      {
        data: "id",
        title: "Acciones",
        render: (data, type, row) => {
          return `<div class="btn-group">           
                    <button type="button" title="Ver Logs" class="btn bg-olive" onclick="verLogs('${row.id}','${row.product.name}')">
                <i class="fas fa-history"></i>
              </button>
                  </div>`;
        },
      },
    ],
    createdRow: function (row, data, dataIndex) {
      if (data.quantity === 0) {
        $(row).addClass("table-danger"); // Rojo
      } else if (data.quantity === 1) {
        $(row).addClass("table-warning"); // Amarillo
      }
    },
  });
});

$(document).on("click", ".thumbnail", function () {
  const fullsizeImage = $(this).data("fullsize");

  Swal.fire({
    imageUrl: fullsizeImage,
    imageWidth: 400, // Ajusta el ancho según sea necesario
    imageHeight: 300, // Ajusta la altura según sea necesario
    imageAlt: "Image",
    showCloseButton: false,
    showConfirmButton: true,
  });
});

function verLogs(shopProductId, name) {
  // Función para formatear la fecha
  function formatDate(timestamp) {
    const date = new Date(timestamp);
    const options = {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    };
    return date.toLocaleString("es-ES", options).replace(",", " -");
  }

  // Configurar el DataTable para los logs
  const logsTable = $("#tabla-de-logs").DataTable({
    responsive: true,
    ajax: {
      url: "/common/logs/",
      data: {
        object_id: shopProductId,
        performed_action: "U", // Filtrar solo por performed_action "U"
        //ordering:"-created_timestamp"
      },
      dataSrc: "results",
    },

    columns: [
      {
        data: "created_timestamp",
        title: "Fecha",
        // render: function (data) {
        //   return data; // Formatear la fecha
        // },
      },
      {
        data: "details",
        title: "Valor Inicial",
        render: function (data) {
          try {
            const formattedData = data.replace(/'/g, '"');
            const details = JSON.parse(formattedData);
            return details.quantity.old_value; // Mostrar old_value
          } catch (e) {
            console.error("Error al parsear details:", e);
            return "Error"; // Manejo de error
          }
        },
      },
      {
        data: "details",
        title: "Valor final",
        render: function (data) {
          try {
            const formattedData = data.replace(/'/g, '"');
            const details = JSON.parse(formattedData);
            return details.quantity.new_value; // Mostrar new_value
          } catch (e) {
            console.error("Error al parsear details:", e);
            return "Error"; // Manejo de error
          }
        },
      },
      {
        data: "details",
        title: "Acción",
        render: function (data) {
          try {
            const formattedData = data.replace(/'/g, '"');
            const details = JSON.parse(formattedData);
            const existencia = parseInt(details.quantity.old_value, 10);
            const entrada = parseInt(details.quantity.new_value, 10);
            let action = "";
            let difference = 0;
            if (entrada > existencia) {
              action = "Entrada";
              difference = entrada - existencia;
            } else {
              action = "Vendido";
              difference = existencia - entrada;
            }
            return `${action} ${difference}`; // Mostrar acción y diferencia
          } catch (e) {
            console.error("Error al parsear details:", e);
            return "Error"; // Manejo de error
          }
        },
      },
    ],
    // order: [[0, "desc"]],
    columnDefs: [{ className: "primera_col", targets: 0 }],
    destroy: true, // Permite reinicializar el DataTable
    ordering: false // Esto deshabilitará completamente el ordenamiento

  });
  $("#modal-logs-label").text("Logs del Producto " + name);
  // Mostrar el modal
  $("#modal-logs").modal("show");
}
