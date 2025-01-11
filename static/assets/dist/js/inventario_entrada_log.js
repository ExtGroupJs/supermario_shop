// Variable con el token
const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
// url del endpoint principal
const urlSell = "/business-gestion/sell-products/";
$(function () {
  bsCustomFileInput.init();
  $("#filter-form")[0].reset();
  $("#reservationdatetime").datetimepicker({ icons: { time: "far fa-clock" } });
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
        axios
            .get(`${urlSell}`, { params })
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
            visible: false  // La columna estará oculta ya que se usa solo para agrupar
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
                return `<button type="button" title="delete" class="btn bg-olive" onclick="function_delete('${row.id}','${row.shop_product__product__name}','${row.quantity}','${row.created_timestamp}','${row.seller__first_name}')" >
                    <i class="fas fa-trash"></i>
                    </button>`;
            },
        },
    ],
    order: [[0, 'asc'], [7, "desc"]], // Primero ordena por grupo, luego por fecha
    rowGroup: {
        dataSrc: 'sell_group',
        startRender: function(rows, group) {
            return 'Grupo de Venta: ' + group;
        }
    },
    columnDefs: []
});
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
