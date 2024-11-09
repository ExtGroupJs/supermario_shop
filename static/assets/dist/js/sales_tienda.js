// Variable con el token
const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
// url del endpoint principal
const url = "/business-gestion/sell-products/";

$(function () {
  bsCustomFileInput.init();
  $("#filter-form")[0].reset();
});

$(document).ready(function () {
  const table = $("#tabla-de-Datos").DataTable({
    responsive: true,
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
    //Adding server-side processing
    serverSide: true,
    search: {
      return: true,
    },
    processing: true,
    ajax: function (data, callback, settings) {
      const filters = $("#filter-form").serializeArray();
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

      axios
        .get(`${url}`, { params })
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
      { data: "product_name", title: "Producto" },
      { data: "quantity", title: "Cantidad" },
      { data: "sell_price", title: "Precio unitario" },
      { data: "total_priced", title: "Monto total" },
      { data: "seller__first_name", title: "Vendedor" },
      { data: "created_timestamp", title: "Fecha" },
      {
        data: "id",
        title: "Acciones",
        render: (data, type, row) => {
          return `<button type="button" title="delete" class="btn bg-olive" onclick="function_delete('${row.id}','${row.shop_product__product__name}','${row.quantity}','${row.created_timestamp}','${row.seller__first_name}')" >

                          <i class="fas fa-trash"></i>
                        </button>                                          
                      </div>`;
        },
      },
    ],
    order: [[5, "desc"]],
    //  esto es para truncar el texto de las celdas
    columnDefs: [],
  });

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
    console.log("✌️function --->");

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
        .delete(`${url}${id}/`)
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
function verificarGroups(numeros, verificarTodos = false) {
  // Recuperar el grupo de números almacenados en localStorage
  const grupos = JSON.parse(localStorage.getItem("groups")) || [];

  // Convertir el argumento 'numeros' en un array si no lo es
  const numerosArray = Array.isArray(numeros) ? numeros : [numeros];

  // Verificar coincidencias
  if (verificarTodos) {
    // Verificar que todos los números pasados estén en el grupo
    return numerosArray.every((num) => grupos.includes(num));
  } else {
    // Verificar si al menos uno de los números pasa está en el grupo
    return numerosArray.some((num) => grupos.includes(num));
  }
}
