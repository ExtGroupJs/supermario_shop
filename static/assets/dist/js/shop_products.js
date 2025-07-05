// Variable con el token
const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

// url del endpoint principal
let selectedShopId = localStorage.getItem("selectedShopId");
let url = "/business-gestion/shop-products/";
if (selectedShopId) {
  url = `/business-gestion/shop-products/?shop=${selectedShopId}`;
}

let load = document.getElementById("load");

$(function () {
  // bsCustomFileInput.init();
  $("#filter-form")[0].reset();
  poblarListas();
});

// Inicializar DataTable
$(document).ready(function () {
  const table = $("#tabla-de-Datos").DataTable({
    autoWidth: true,
    responsive: true,
    lengthMenu: [
      [10, 25, 50, 100, -1], // Valores
      [10, 25, 50, 100, "Todos"], // Etiquetas
    ],

    dom: '<"top"l>Bfrtip',
    buttons: [
      {
        text: "Crear",
        className: "btn btn-primary btn-info",
        action: function (e, dt, node, config) {
          $("#modal-crear-shop-products").modal("show");
        },
      },
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
      const filters = $("#filter-form").serializeArray();
      dir = "";
      if (data.order[0].dir == "desc") {
        dir = "-";
      }
      const params = {};
      ("");
      filters.forEach((filter) => {
        if (filter.value) {
          params[filter.name] = filter.value;
        }
      });

      if (myDateStart !== null && myDateStart !== null) {
        params["updated_timestamp__gte"] = myDateStart;
        params["updated_timestamp__lte"] = myDateEnd;
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
          load.hidden = true;
        })
        .catch((error) => {
          load.hidden = true;
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
      { data: "cost_price", title: "Precio de Costo" },
      { data: "sell_price", title: "Precio de Venta" },
      { data: "updated_timestamp", title: "Fecha" },
      { data: "extra_info", title: "Información Extra" },
      {
        data: "id",
        title: "Acciones",
        render: (data, type, row) => {
          return `<div class="btn-group">
           <button type="button" title="Agregar Cantidad" class="btn bg-olive" onclick="agregarCantidad('${row.id}','${row.quantity}')">
                <i class="fas fa-plus"></i>
              </button>
           <button type="button" title="Marcar como New" class="btn bg-olive" onclick="marcarComoNew('${row.id}')">
               <i class="nav-icon fas fa-clipboard-check"></i>
              </button>
                    <button type="button" title="edit" class="btn bg-olive active" data-toggle="modal" data-target="#modal-crear-shop-products" data-id="${row.id}" data-type="edit" data-name="${row.product}" id="${row.id}">
                      <i class="fas fa-edit"></i>
                    </button>
                    <button type="button" title="delete" class="btn bg-olive" onclick="function_delete('${row.id}','${row.product_name}','${row.shop_name}')" >
                      <i class="fas fa-trash"></i>
                    </button>
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

    order: [[6, "desc"]],
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

// Otras funciones existentes...

let selected_id;

$("#modal-crear-shop-products").on("hide.bs.modal", (event) => {
  const form = event.currentTarget.querySelector("form");
  form.reset();
  edit_shopProducts = false;
  const elements = [...form.elements];
  elements.forEach((elem) => elem.classList.remove("is-invalid"));
});

let form = document.getElementById("form-create-shop-products");
let edit_shopProducts = false;
$("#modal-crear-shop-products").on("show.bs.modal", function (event) {
  var button = $(event.relatedTarget); // Button that triggered the modal

  var modal = $(this);
  if (button.data("type") == "edit") {
    var dataName = button.data("name"); // Extract info from data-* attributes
    selected_id = button.data("id"); // Extract info from data-* attributes

    edit_shopProducts = true;

    load.hidden = false;
    // Realizar la petición con Axios

    axios
      .get(`${url}` + selected_id + "/")
      .then(function (response) {
        // Recibir la respuesta
        const shopProduct = response.data;
        modal.find(".modal-title").text("Editar " + shopProduct.product_name);
        form.elements.quantity.value = shopProduct.quantity;
        form.elements.cost_price.value = shopProduct.cost_price;
        form.elements.sell_price.value = shopProduct.sell_price;
        form.elements.extra_info.value = shopProduct.extra_info;
        form.elements.shop.value = shopProduct.shop;
        form.elements.product.value = shopProduct.product.id;
        $("#product").val(shopProduct.product.id).trigger("change.select2");
        load.hidden = true;
      })
      .catch(function (error) {});
  } else {
    modal.find(".modal-title").text("Crear Entrada de Producto");
    let selectedShopId = localStorage.getItem("selectedShopId");
    if (selectedShopId) {
      form.elements.shop.value = selectedShopId;
    }
  }
});

// form validator
$(function () {
  $.validator.setDefaults({
    language: "es",
    submitHandler: function () {
      // alert("Form successful submitted!");
    },
  });

  $("#form-create-shop-products").validate({
    rules: {
      quantity: {
        required: true,
        digits: true, // Solo números
      },
      cost_price: {
        required: true,
        number: true, // Solo números
      },
      sell_price: {
        required: true,
        number: true, // Solo números
        greaterThan: "#cost_price", // El precio de venta debe ser mayor que el precio de costo
      },
      extra_info: {
        required: false, // Campo no obligatorio
      },
    },
    messages: {
      quantity: {
        required: "Este campo es obligatorio.",
        digits: "Por favor, introduzca solo números.",
      },
      cost_price: {
        required: "Este campo es obligatorio.",
        number: "Por favor, introduzca un número válido.",
      },
      sell_price: {
        required: "Este campo es obligatorio.",
        number: "Por favor, introduzca un número válido.",
        greaterThan:
          "El precio de venta debe ser mayor que el precio de costo.",
      },
    },
    submitHandler: function (form) {
      load.hidden = false;
      event.preventDefault();
      var table = $("#tabla-de-Datos").DataTable();
      const csrfToken = document.cookie
        .split(";")
        .find((c) => c.trim().startsWith("csrftoken="))
        ?.split("=")[1];
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      let data = new FormData();
      data.append("shop", document.getElementById("shop").value);
      data.append("product", document.getElementById("product").value);
      data.append("quantity", document.getElementById("quantity").value);
      data.append("cost_price", document.getElementById("cost_price").value);
      data.append("sell_price", document.getElementById("sell_price").value);
      data.append("extra_info", document.getElementById("extra_info").value);

      if (edit_shopProducts) {
        axios
          .patch(`${url}` + selected_id + "/", data)
          .then((response) => {
            if (response.status === 200) {
              load.hidden = true;
              $("#modal-crear-shop-products").modal("hide");
              Swal.fire({
                icon: "success",
                title: "Entrada de Producto actualizada con éxito",
                showConfirmButton: false,
                timer: 1500,
              });
              table.ajax.reload();

              edit_shopProducts = false;
            }
          })
          .catch((error) => {
            load.hidden = true;
            let dict = error.response.data;
            let textError = "Revise los siguientes campos: ";
            for (const key in dict) {
              textError = textError + ", " + key;
            }

            Swal.fire({
              icon: "error",
              title: "Error al crear la Entrada de Producto",
              text: textError,
              showConfirmButton: false,
              timer: 1500,
            });
          });
      } else {
        axios
          .post(`${url}`, data)
          .then((response) => {
            if (response.status === 201) {
              load.hidden = true;
              Swal.fire({
                icon: "success",
                title: "Entrada de Producto creada con éxito",
                showConfirmButton: false,
                timer: 1500,
              });
              table.ajax.reload();
              $("#modal-crear-shop-products").modal("hide");
            }
          })
          .catch((error) => {
            load.hidden = true;
            let dict = error.response.data;
            let textError = "Revise los siguientes campos: ";
            for (const key in dict) {
              textError = textError + ", " + key;
            }

            Swal.fire({
              icon: "error",
              title: "Error al crear la Entrada de Producto",
              text: textError,
              showConfirmButton: false,
              timer: 1500,
            });
          });
      }
    },

    errorElement: "span",
    errorPlacement: function (error, element) {
      error.addClass("invalid-feedback");
      element.closest(".form-group").append(error);
    },
    highlight: function (element, errorClass, validClass) {
      $(element).addClass("is-invalid");
    },
    unhighlight: function (element, errorClass, validClass) {
      $(element).removeClass("is-invalid");
    },
  });
});

// Método para validar que el precio de venta sea mayor que el precio de costo
$.validator.addMethod(
  "greaterThan",
  function (value, element, param) {
    return this.optional(element) || Number(value) > Number($(param).val());
  },
  "El precio de venta debe ser mayor que el precio de costo."
);

function poblarListas() {
  // Poblar la lista de tiendas
  var $shop = document.getElementById("shop");
  axios.get("/business-gestion/shops/").then(function (response) {
    response.data.results.forEach(function (element) {
      var option = new Option(element.name, element.id);
      $shop.add(option);
    });
  });

  // Poblar la lista de productos
  var $product = document.getElementById("product");
  axios
    .get("/business-gestion/products/")
    .then(function (response) {
      response.data.results.forEach(function (element) {
        var option = new Option(element.__str__, element.id);
        $product.add(option);
      });
    })
    .then(() => {
      if ($product.value != null) {
        cargarProductoEspecifico($product.value);
      }
    });
}

function function_delete(id, name, shop) {
  const table = $("#tabla-de-Datos").DataTable();
  Swal.fire({
    title: "Eliminar",
    text: `¿Está seguro que desea eliminar el producto ${name} de la tienda  ${shop}?`,
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Sí, Eliminar",
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
              text: "Elemento eliminado satisfactoriamente",
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

function agregarCantidad(shopProductId, cantidad_actual) {
  Swal.fire({
    title: "Agregar Cantidad",
    text: "¿Cuántas unidades deseas agregar al producto?",
    input: "number",
    inputAttributes: {
      step: 1,
    },
    showCancelButton: true,
    confirmButtonText: "Agregar",
    cancelButtonText: "Cancelar",
    preConfirm: (cantidad) => {
      if (!cantidad || cantidad <= 0) {
        Swal.showValidationMessage(`Por favor, introduce una cantidad válida.`);
      }
      return cantidad;
    },
  }).then((result) => {
    if (result.isConfirmed) {
      load.hidden = false;
      const cantidadResultante = Number(result.value) + Number(cantidad_actual);
      const table = $("#tabla-de-Datos").DataTable();
      // Realizar la petición para actualizar la cantidad
      axios
        .patch(`${url}${shopProductId}/`, { quantity: cantidadResultante })
        .then((response) => {
          if (response.status === 200) {
            load.hidden = true;
            Swal.fire({
              icon: "success",
              title: "¡Éxito!",
              text: `Se han agregado ${result.value} unidades al producto. Quedan ${cantidadResultante} en inventario`,
              showConfirmButton: false,
              timer: 3000, // Mensaje de éxito por 2 segundos
            });
            // Recargar la tabla para reflejar los cambios
            table.ajax.reload();
          }
        })
        .catch((error) => {
          load.hidden = true;
          Swal.fire({
            icon: "error",
            title: "Error",
            text: "No se pudo actualizar la cantidad. Intente nuevamente.",
            showConfirmButton: true,
          });
        });
    }
  });
}
function marcarComoNew(shopProductId) {
  const table = $("#tabla-de-Datos").DataTable();
  // Realizar la petición para actualizar la cantidad
  axios
    .patch(`${url}${shopProductId}/`, {})
    .then((response) => {
      if (response.status === 200) {
        Swal.fire({
          icon: "success",
          title: "¡Éxito!",
          text: `Se han marcado como nuevo el producto seleccionado.`,
          showConfirmButton: false,
          timer: 2000, // Mensaje de éxito por 2 segundos
        });
        // Recargar la tabla para reflejar los cambios
        table.ajax.reload();
      }
    })
    .catch((error) => {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "No se pudo marcar como nuevo.",
        showConfirmButton: true,
      });
    });
}

function esNegativo(num) {
  return num < 0;
}

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

  const logsTable = $("#tabla-de-logs").DataTable({
    responsive: true,
    ajax: {
      url: "/business-gestion/shop-products-logs/",
      data: {
        object_id: shopProductId,
        performed_action: "U", // Filtrar solo por performed_action "U"
        ordering: "-created_timestamp",
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
        data: "init_value",
        title: "Valor Inicial",
        render: function (data) {
          return data;
        },
      },
      {
        data: "new_value",
        title: "Valor final",
        render: function (data) {
          return data;
        },
      },
      {
        data: "info",
        title: "Acción",
        render: function (data) {
          return data; // Mostrar acción y diferencia
        },
      },
      {
        data: "created_by",
        title: "Por",
        render: function (data) {
          return data;
        },
      },
    ],
    createdRow: function (row, data, dataIndex) {
      if (data.info.includes("entrado")) {
        $(row).addClass("table-success"); // Rojo
      } else if (data.quantity === 1) {
        // $(row).addClass("table-warning"); // Amarillo
      }
    },
    // order: [[0, "desc"]],
    columnDefs: [{ className: "primera_col", targets: 0 }],
    destroy: true, // Permite reinicializar el DataTable
    ordering: false, // Esto deshabilitará completamente el ordenamiento
  });
  $("#modal-logs-label").text("Logs del Producto " + name);
  // Mostrar el modal
  $("#modal-logs").modal("show");
}

let especificProducto;
function cargarProductoEspecifico(id) {
  axios
    .get("/business-gestion/products/" + id + "/")
    .then((res) => {
      especificProducto = res.data;
      var nuevaUrl = especificProducto.image;
      document.getElementById("productImagen").src = nuevaUrl;
      load.hidden = true;
    })
    .catch((error) => {
      load.hidden = true;
      console.error("Error al cargar productos:", error);
    });
}

$(document).on("click", "#productImagen", function () {
  load.hidden = false;
  const fullsizeImage = $(this).attr("src"); // Obtiene la URL de la imagen
  console.log("✌️fullsizeImage --->", fullsizeImage);

  Swal.fire({
    imageUrl: fullsizeImage,
    imageWidth: 400, // Ajusta el ancho según sea necesario
    imageHeight: 300, // Ajusta la altura según sea necesario
    imageAlt: "Image",
    showCloseButton: false,
    showConfirmButton: true,
  });
  load.hidden = true;
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
