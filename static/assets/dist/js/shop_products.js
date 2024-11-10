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
   lengthMenu: [
      [10, 25, 50, 100, -1], // Valores
      [10, 25, 50, 100, 'Todos'] // Etiquetas
  ],
    responsive: true,
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

      filters.forEach((filter) => {
        if (filter.value) {
          params[filter.name] = filter.value;
        }
      });
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
        render: (data,type, row) => {          
          if (data) {
            return `<div style="text-align: center;"><img src="${row.product.image}" alt="image" style="width: 50px; height: auto;" class="thumbnail" data-fullsize="${row.product.image}"></div>`;
        
          } else{return `<div style="text-align: center;"><i class="nav-icon fas fa-car-crash text-danger"></i></div>`;} 
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
    order: [[6, 'desc']],
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

// Otras funciones existentes...

let selected_id;

$("#modal-crear-shop-products").on("hide.bs.modal", (event) => {
  const form = event.currentTarget.querySelector("form");
  form.reset();
  edit_shopProducts = false;
  const elements = [...form.elements];
  elements.forEach((elem) => elem.classList.remove("is-invalid"));
});

let edit_shopProducts = false;
$("#modal-crear-shop-products").on("show.bs.modal", function (event) {
  var button = $(event.relatedTarget); // Button that triggered the modal

  var modal = $(this);
  if (button.data("type") == "edit") {
    var dataName = button.data("name"); // Extract info from data-* attributes
    selected_id = button.data("id"); // Extract info from data-* attributes
    edit_shopProducts = true;

    modal.find(".modal-title").text("Editar Entrada de Producto ");
    load.hidden = false;
    // Realizar la petición con Axios
    axios
      .get(`${url}` + selected_id + "/")
      .then(function (response) {
        // Recibir la respuesta
        const shopProduct = response.data;
        form.elements.quantity.value = shopProduct.quantity;
        form.elements.cost_price.value = shopProduct.cost_price;
        form.elements.sell_price.value = shopProduct.sell_price;
        form.elements.extra_info.value = shopProduct.extra_info;
        form.elements.shop.value = shopProduct.shop;
        form.elements.product.value = shopProduct.product;
        $("#product").val(shopProduct.product).trigger("change");
        load.hidden = true;
      })
      .catch(function (error) {});
  } else {
    modal.find(".modal-title").text("Crear Entrada de Producto");
  }
});

// form validator
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

// crear Entrada de Producto

// let form = document.getElementById("form-create-shop-products");
// form.addEventListener("submit", function (event) {
//   event.preventDefault();
//   var table = $("#tabla-de-Datos").DataTable();
//   const csrfToken = document.cookie
//     .split(";")
//     .find((c) => c.trim().startsWith("csrftoken="))
//     ?.split("=")[1];
//   axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
//   let data = new FormData();
//   data.append("shop", document.getElementById("shop").value);
//   data.append("product", document.getElementById("product").value);
//   data.append("quantity", document.getElementById("quantity").value);
//   data.append("cost_price", document.getElementById("cost_price").value);
//   data.append("sell_price", document.getElementById("sell_price").value);
//   data.append("extra_info", document.getElementById("extra_info").value);

//   if (edit_shopProducts) {
//     axios
//       .patch(`${url}` + selected_id + "/", data)
//       .then((response) => {
//         if (response.status === 200) {
//           $("#modal-crear-shop-products").modal("hide");
//           Swal.fire({
//             icon: "success",
//             title: "Entrada de Producto actualizada con éxito",
//             showConfirmButton: false,
//             timer: 1500,
//           });
//           table.ajax.reload();

//           edit_shopProducts = false;
//         }
//       })
//       .catch((error) => {
//         let dict = error.response.data;
//         let textError = "Revise los siguientes campos: ";
//         for (const key in dict) {
//           textError = textError + ", " + key;
//         }

//         Swal.fire({
//           icon: "error",
//           title: "Error al crear la Entrada de Producto",
//           text: textError,
//           showConfirmButton: false,
//           timer: 1500,
//         });
//       });
//   } else {
//     axios
//       .post(`${url}`, data)
//       .then((response) => {
//         if (response.status === 201) {
//           Swal.fire({
//             icon: "success",
//             title: "Entrada de Producto creada con éxito",
//             showConfirmButton: false,
//             timer: 1500,
//           });
//           table.ajax.reload();
//           $("#modal-crear-shop-products").modal("hide");
//         }
//       })
//       .catch((error) => {
//         let dict = error.response.data;
//         let textError = "Revise los siguientes campos: ";
//         for (const key in dict) {
//           textError = textError + ", " + key;
//         }

//         Swal.fire({
//           icon: "error",
//           title: "Error al crear la Entrada de Producto",
//           text: textError,
//           showConfirmButton: false,
//           timer: 1500,
//         });
//       });
//   }
// });

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
  axios.get("/business-gestion/products/").then(function (response) {
    response.data.results.forEach(function (element) {
      var option = new Option(element.__str__, element.id);
      $product.add(option);
    });
  }) .then(() => {
   cargarProductoEspecifico($product.value)
    
  })
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
      const cantidadAgregada = Number(result.value) + Number(cantidad_actual);
      const table = $("#tabla-de-Datos").DataTable();
      // Realizar la petición para actualizar la cantidad
      axios
        .patch(`${url}${shopProductId}/`, { quantity: cantidadAgregada })
        .then((response) => {
          if (response.status === 200) {
            Swal.fire({
              icon: "success",
              title: "¡Éxito!",
              text: `Se han agregado ${cantidadAgregada} unidades al producto.`,
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
            text: "No se pudo actualizar la cantidad. Intente nuevamente.",
            showConfirmButton: true,
          });
        });
    }
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

  // Configurar el DataTable para los logs
  const logsTable = $("#tabla-de-logs").DataTable({
    responsive: true,
    ajax: {
      url: "/common/logs/",
      data: {
        object_id: shopProductId,
        performed_action: "U", // Filtrar solo por performed_action "U"
      },
      dataSrc: "results",
    },

    columns: [
      {
        data: "created_timestamp",
        title: "Fecha",
        render: function (data) {
          return formatDate(data); // Formatear la fecha
        },
      },
      {
        data: "details",
        title: "Existencia",
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
        title: "Entrada",
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
              action = "Venta";
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
    columnDefs: [{ className: "primera_col", targets: 0 }],
    destroy: true, // Permite reinicializar el DataTable
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
document.getElementById('productImagen').src = nuevaUrl;
      load.hidden = true;
    })
    .catch((error) => {
      load.hidden = true;
      console.error("Error al cargar productos:", error);
    });
}


$(document).on("click", "#productImagen", function () {
  load.hidden = false;
  const fullsizeImage = $(this).attr('src'); // Obtiene la URL de la imagen
  console.log('✌️fullsizeImage --->', fullsizeImage);

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