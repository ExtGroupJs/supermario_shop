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
  $("#filter-form")[0].reset();
  poblarListas();
});

// Inicializar DataTable
$(document).ready(function () {
  const table = $("#tabla-de-Datos").DataTable({
    responsive: true,
    dom: '<"top"l>Bfrtip',
    buttons: [],
    serverSide: true,
    processing: true,
    ajax: function (data, callback, settings) {
      const filters = $("#filter-form").serializeArray();

      const params = {};

      filters.forEach((filter) => {
        if (filter.value) {
          params[filter.name] = filter.value;
        }
      });
      // Añadir parámetros de paginación
      params.page_size = data.length;
      params.page = data.start / data.length + 1;
      params.ordering = data.columns[data.order[0].column].data;
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
      { data: "shop.name", title: "Tienda" },
      { data: "product.__str__", title: "Producto" },
      { data: "quantity", title: "Cantidad" },
      { data: "sell_price", title: "Precio de Venta" },
      { data: "extra_info", title: "Información Extra" },
      {
        data: "id",
        title: "Acciones",
        render: (data, type, row) => {
          return `<div class="btn-group">
                   <button type="button" title="Venta" class="btn bg-primary active"  data-id="${row.id}" data-name="${row.get_full_name}" id="${row.id}"  onclick="sellProduct(${row.id},${row.quantity})">
                      
                  <i class="nav-icon fas fa-cash-register"></i>
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
  function convertirFecha(fecha, hora) {
    // Dividir la fecha en partes
    const partes = fecha.split("/");

    // Verificar que la fecha tenga el formato correcto
    if (partes.length !== 3) {
      throw new Error("Formato de fecha incorrecto. Debe ser DD/MM/YYYY.");
    }

    // Crear un objeto Date con el formato YYYY, MM (0-indexado), DD
    const fechaDate = new Date(partes[2], partes[1] - 1, partes[0]);

    // Establecer la hora según el valor proporcionado
    if (hora === 0) {
      fechaDate.setHours(0, 0); // 00:00
    } else if (hora === 1) {
      fechaDate.setHours(13, 0); // 13:00
    } else {
      throw new Error("La hora debe ser 0 o 1.");
    }

    // Formatear la fecha en el formato deseado
    const fechaFormateada = fechaDate.toISOString().slice(0, 16);

    return fechaFormateada;
  }

  // Manejo del formulario de filtros
  $("#filter-form").on("submit", function (event) {
    event.preventDefault();
    console.log("✌️event --->", event);
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

// ------------------------------------------------
function sellProduct(shopProductId, availableQuantity) {
  var table = $("#tabla-de-Datos").DataTable();
  Swal.fire({
    title: "Venta de producto",
    html: `
           <div class="form-group col-md-12">
                    <label for="salesquantity">Cantidad</label>
                    <input id="salesquantity" type="number" min="1" max="${availableQuantity}" step="1"  class="form-control form-control-lg" />
                  </div>

     <div class="form-group col-md-12">
                    <label for="salesextra_info">Información adicional</label>
                    <textarea id="salesextra_info" type="text" placeholder="Información adicional (opcional)" class="form-control form-control-lg" /> </textarea>
                  </div>
     
    `,
    focusConfirm: false,
    showCancelButton: true,
    confirmButtonText: "Vender",
    cancelButtonText: "Cancelar",
    preConfirm: () => {
      const quantity = document.getElementById("salesquantity").value;
      const extraInfo = document.getElementById("salesextra_info").value;

      if (quantity < 1 || quantity > availableQuantity) {
        Swal.showValidationMessage(
          `La cantidad debe estar entre 1 y ${availableQuantity}.`
        );
      }
      return { quantity, extraInfo };
    },
  }).then((result) => {
    if (result.isConfirmed) {
      console.log("✌️result --->", result);
      const { quantity, extraInfo } = result.value;

      const payload = {
        shop_product: shopProductId,
        extra_info: extraInfo || "string", // Usar "string" si no se proporciona información
        quantity: quantity,
      };

      // Enviar los datos al servidor
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      axios
        .post("/business-gestion/sell-products/", payload)
        .then((response) => {
          Swal.fire({
            icon: "success",
            title: "¡Éxito!",
            text: `Se han vendido ${quantity} unidades del producto.`,
          });
          // Aquí puedes agregar código para recargar la tabla
          table.ajax.reload();
        })
        .catch((error) => {
          Swal.fire({
            icon: "error",
            title: "Error",
            text: "No se pudo completar la venta. Intente nuevamente.",
          });
        });
    }
  });
}
