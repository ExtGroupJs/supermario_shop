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
});

$(document).ready(function () {
    $("table")
    .addClass("table table-hover")
    .DataTable({
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
        dir = "";
        if (data.order[0].dir == "desc") {
          dir = "-";
        }

        axios
          .get(`${url}`, {
            params: {
              page_size: data.length,
              page: data.start / data.length + 1,
              search: data.search.value,
              ordering: dir + data.columns[data.order[0].column].data,
            },
          })
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
        { data: "shop_product_name", title: "Producto" },
        { data: "quantity", title: "Cantidad" },
        { data: "unit_price", title: "Precio unitario" },
        { data: "total_priced", title: "Monto total" },
        { data: "seller_name", title: "Vendedor" },
        { data: "created_timestamp", title: "Fecha" },
        {
          data: "id",
          title: "Acciones",
          render: (data, type, row) => {
            return `<button type="button" title="delete" class="btn bg-olive" onclick="function_delete('${row.id}','${row.shop_product}')" >
                          <i class="fas fa-trash"></i>
                        </button>                                          
                      </div>`;
          },
        },
      ],
      //  esto es para truncar el texto de las celdas
      columnDefs: [],
    });
});

function function_delete(id, name) {
  const table = $("#tabla-de-Datos").DataTable();
  Swal.fire({
    title: "Eliminar",
    text: `Esta seguro que desea eliminar el elemento ${name}?`,
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
  const grupos = JSON.parse(localStorage.getItem('groups')) || [];

  // Convertir el argumento 'numeros' en un array si no lo es
  const numerosArray = Array.isArray(numeros) ? numeros : [numeros];

  // Verificar coincidencias
  if (verificarTodos) {
      // Verificar que todos los números pasados estén en el grupo
      return numerosArray.every(num => grupos.includes(num));
  } else {
      // Verificar si al menos uno de los números pasa está en el grupo
      return numerosArray.some(num => grupos.includes(num));
  }
}