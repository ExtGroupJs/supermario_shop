// Variable con el token
const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
// url del endpoint principal

// url del endpoint principal
let selectedShopId = localStorage.getItem("selectedShopId");
let urlSell = "/business-gestion/input-groups/";

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
      let dir = "";
      if (data.order[0].dir == "desc") {
        dir = "-";
      }
      params.page_size = data.length;
      params.page = data.start / data.length + 1;
      if (data.columns[data.order[0].column].name) {
        params.ordering = dir + data.columns[data.order[0].column].name;
      }
      params.search = data.search.value;

      axios
        .get(urlSell, { params })
        .then((res) => {
          const mappedRows = [];
          (res.data.results || []).forEach((group) => {
            const groupInputs = group.inputs || [];
            groupInputs.forEach((input) => {
              mappedRows.push({
                id: group.id,
                input_group: group.id,
                product_name:input.shop_product_name,
                quantity: input.quantity,
                created_timestamp: input.created_timestamp || group.for_date,
                seller__first_name: input.author_name,
                extra_info: group.extra_info || "",
              });
            });
          });
          callback({
            recordsTotal: res.data.count,
            recordsFiltered: res.data.count,
            data: mappedRows,
          });
        })
        .catch((error) => {
          alert(error);
        });
    },
    columns: [
      {
        data: "input_group",
        title: "Grupo de Entrada",
        visible: false,
      },
      { data: "product_name", title: "Producto", name: "product_name" },
      { data: "quantity", title: "Cantidad", name: "quantity" },
      { data: "extra_info", title: "Información Extra", name: "extra_info" },
      { data: "seller__first_name", title: "Autor", name: "seller__first_name" },
      { data: "created_timestamp", title: "Fecha", name: "created_timestamp" },
      {
        data: "id",
        title: "Acciones",
        render: (data, type, row) => {
          return `<button type="button" title="delete" class="btn bg-olive" onclick="function_delete('${row.id}','${row.created_timestamp}','${row.seller__first_name}')" >
                    <i class="fas fa-trash"></i>
                    </button>`;
        },
      },
    ],
    order: [[5, "desc"]],
    rowGroup: {
      dataSrc: "input_group",
      startRender: function (rows, group) {
        const extraInfo = rows.data()[0].extra_info || "Sin información extra";
        return "Grupo de Entrada: " + group + " | Info: " + extraInfo;
      },
    },
    columnDefs: [],
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

function function_delete(id, date, author) {
  const table = $("#tabla-de-Datos").DataTable();
  Swal.fire({
    title: "Confirmación requerida",
    text: `¿Está seguro que desea eliminar la entrada del autor ${author} con fecha ${date}?`,
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
            table.ajax.reload();
            Swal.fire({
              icon: "success",
              title: "Eliminar Elemento",
              text: "Entrada eliminada satisfactoriamente ",
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
