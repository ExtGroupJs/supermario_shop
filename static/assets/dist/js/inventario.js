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
  
  poblarListas();
});

// Inicializar DataTable
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
    serverSide: true,
    processing: true,
    ajax: function (data, callback, settings) {
      

      const params = {};

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


function verLogs(shopProductId,name) {
  // Función para formatear la fecha
  function formatDate(timestamp) {
    const date = new Date(timestamp);
    const options = { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
    return date.toLocaleString('es-ES', options).replace(',', ' -');
  }

  // Configurar el DataTable para los logs
  const logsTable = $("#tabla-de-logs").DataTable({    
   responsive: true,
    ajax: {
      url: "/common/logs/",
      data: {
        object_id: shopProductId,
        performed_action: "U" // Filtrar solo por performed_action "U"
      },
      dataSrc: "results"
    },
   
    columns: [
      {
        data: "created_timestamp",
        title: "Fecha",
        render: function(data) {
          return formatDate(data); // Formatear la fecha
        }
      },
      {
        data: "details",
        title: "Valor Inicial",
        render: function(data) {          
          try {
            const formattedData = data.replace(/'/g, '"');
            const details = JSON.parse(formattedData);
            return details.quantity.old_value; // Mostrar old_value
          } catch (e) {
            console.error("Error al parsear details:", e);
            return "Error"; // Manejo de error
          }
        }
      },
      {
        data: "details",
        title: "Valor final",
        render: function(data) {
          try {
            const formattedData = data.replace(/'/g, '"');
            const details = JSON.parse(formattedData);
            return details.quantity.new_value; // Mostrar new_value
          } catch (e) {
            console.error("Error al parsear details:", e);
            return "Error"; // Manejo de error
          }
        }
      },
      {
        data: "details",
        title: "Acción",
        render: function(data) {
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
        }
      },
    ],
    columnDefs: [
      {className: "primera_col", targets: 0},
      
    ],
    destroy: true // Permite reinicializar el DataTable
  });
  $("#modal-logs-label").text("Logs del Producto "+name);
  // Mostrar el modal
  $("#modal-logs").modal("show");
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