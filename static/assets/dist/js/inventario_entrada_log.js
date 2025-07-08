// Variable con el token
const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;



// url del endpoint principal
let selectedShopId = localStorage.getItem("selectedShopId");
let urlSell = "/business-gestion/shop-products-logs/";
if (selectedShopId) {
  urlSell = `/business-gestion/shop-products-logs/?shop=${selectedShopId}`;
}

$(function () {
  bsCustomFileInput.init();
  $("#filter-form")[0].reset();
 // $("#reservationdatetime").datetimepicker({ icons: { time: "far fa-clock" } });
});

$(function () {
  bsCustomFileInput.init();
});

// Inicializar DataTable
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
            exportOptions: {
              columns: [1,2,3,4,5,6],
              stripHtml: false, // No eliminar imágenes
            },
        },
        {
            extend: "print",
            text: "Print",
        },
    ],
    serverSide: true,
    // search: {
    //     return: true,
    // },
    processing: true,
    ajax: function (data, callback, settings) {
        const filters = $("#filter-form").serializeArray();
        dir = "";
        if (data.order[0].dir == "desc") {
            dir = "-";
        }
         const params = {};
         filters.forEach((filter) => {
            if (filter.value) {
                 params[filter.name] = filter.value;
            }
        });

        if (myDateStart !== null && myDateStart !== null) {
          params["created_timestamp__gte"] = myDateStart;
          params["created_timestamp__lte"] = myDateEnd;
        }
       
        params.page_size = data.length;
        params.page = data.start / data.length + 1;
        params.ordering = dir + data.columns[data.order[0].column].data;
        params.search = data.search.value;
        params.entries=true;

        axios
            .get(selectedShopId ? urlSell+`?shop=${selectedShopId}` : urlSell, { params })
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
        data: "object_id",
        title: "Foto",
        render: (data, type, row) => {
          if (data) {
            return `<div style="text-align: center;"><img src="${row.product_image}" alt="image" style="width: 50px; height: auto;" class="thumbnail" data-fullsize="${row.product_image}"></div>`;
          } else {
            return `<div style="text-align: center;"><i class="nav-icon fas fa-car-crash text-danger"></i></div>`;
          }
        },
      },   
        { data: "shop_product_name", title: "Producto" },     
        { data: "created_timestamp", title: "Fecha" },
        { data: "init_value", title: "Existencia" },
        { data: "info", title: "Cambio" },
        { data: "new_value", title: "Valor actual" },
        { data: "created_by", title: "Responsable" },
         ],
    order: [[2, 'desc'],[1, 'desc']], // Primero ordena por grupo, luego por fecha
   
   
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
     myDateStart = null;
 myDateEnd = null;
    table.ajax.reload();
  });

  // Mostrar/Ocultar filtros
  $("#toggle-filters").on("click", function () {
    $("#filter-section").toggle();
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

let myDateStart = null;
let myDateEnd = null;
$(function () {
  //Date range as a button
  $("#daterange-btn").daterangepicker(
    {
      ranges: {
        Todos: [moment("2000-01-01"), moment()],
        Hoy: [moment(), moment()],
        Ayer: [moment().subtract(1, "days"), moment().subtract(1, "days")],
        "Últimos 7 Días": [moment().subtract(6, "days"), moment()],
        "Últimos 30 Días": [moment().subtract(29, "days"), moment()],
        "Este Mes": [moment().startOf("month"), moment().endOf("month")],
        "El Mes Pasado": [
          moment().subtract(1, "month").startOf("month"),
          moment().subtract(1, "month").endOf("month"),
        ],
      },
      startDate: moment().subtract(29, "days"),
      endDate: moment(),
    },
    function (start, end) {
      $("#reportrange span").html(
        start.format("MMMM D, YYYY") + " - " + end.format("MMMM D, YYYY")
      );
      myDateStart = start.format("YYYY-MM-DD HH:mm:ss");
      myDateEnd = end.format("YYYY-MM-DD HH:mm:ss");
      //  daterangeSellProfits(selectedStartDate,selectedEndDate);
    }
  );
});