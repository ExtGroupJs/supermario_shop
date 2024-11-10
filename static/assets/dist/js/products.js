// Variable con el token
const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
// url del endpoint principal
const url = "/business-gestion/products/";

$(function () {
  bsCustomFileInput.init();
  $("#filter-form")[0].reset();
  poblarListas();
});

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
          $("#modal-crear-products").modal("show");
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
        exportOptions: {
          columns: [0, 1],
          stripHtml: false, // No eliminar imágenes
        },

        customize: function (doc) {
          let icono = `<div style="text-align: center;"><i class="nav-icon fas fa-car-crash text-danger"></i></div>`;
          doc.content[1].table.body.forEach((row) => {
            if (row[1] && row[1].text.includes("src")) {
              const regex = /src="([^"]+)"/;
              const resultado = row[1].text.match(regex);

              const imgUrl = resultado[1]; // Extraer la URL
              getBase64Image(imgUrl)
                .then((base64Image) => {
                  row[1] = { image: base64Image, width: 500, height: 500 }; // Ajustar el tamaño si es necesario
                })
                .catch(() => {
                  row[1] = "sin imagen"; // Si falla la conversión, poner "sin imagen"
                });
            } else {
              row[1] = "sin imagen"; // Cambia a "sin imagen" si no hay imagen
            }
          });
        },
      },
    ],
    // Adding server-side processing
    serverSide: true,
    search: {
      return: true,
    },
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
      // Añadir parámetros de paginación
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
      { data: "name", title: "Nombre" },
      {
        data: "image",
        title: "Foto",
        render: (data) => {
          if (data) {
            return `<div style="text-align: center;"><img src="${data}" alt="image" style="width: 50px; height: auto;" class="thumbnail" data-fullsize="${data}"></div>`;
          } else {
            return `<div style="text-align: center;"><i class="nav-icon fas fa-car-crash text-danger"></i></div>`;
          }
        },
      },
      { data: "model_name", title: "Modelo" },
      { data: "description", title: "Descripción" },
      {
        data: "id",
        title: "Acciones",
        render: (data, type, row) => {
          return `<div class="btn-group">
                            <button type="button" title="edit" class="btn bg-olive active" data-toggle="modal" data-target="#modal-crear-products" data-id="${row.id}" data-type="edit" data-name="${row.name}" id="${row.id}">
                              <i class="fas fa-edit"></i>
                            </button>  
                            <button type="button" title="delete" class="btn bg-olive" onclick="function_delete('${row.id}','${row.name}','${row.model_name}')" >
                              <i class="fas fa-trash"></i>
                            </button>                                          
                          </div>`;
        },
      },
    ],

    //  esto es para truncar el texto de las celdas
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

let selected_id;

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

$("#modal-crear-products").on("hide.bs.modal", (event) => {
  const form = event.currentTarget.querySelector("form");
  form.reset();
  edit_products = false;
  const elements = [...form.elements];
  elements.forEach((elem) => elem.classList.remove("is-invalid"));
});

let edit_products = false;
$("#modal-crear-products").on("show.bs.modal", function (event) {
  var button = $(event.relatedTarget); // Button that triggered the modal

  var modal = $(this);
  if (button.data("type") == "edit") {
    var dataName = button.data("name"); // Extract info from data-* attributes
    selected_id = button.data("id"); // Extract info from data-* attributes
    edit_products = true;

    modal.find(".modal-title").text("Editar Producto " + dataName);

    // Realizar la petición con Axios
    axios
      .get(`${url}` + selected_id + "/")
      .then(function (response) {
        // Recibir la respuesta
        const product = response.data;
        form.elements.name.value = product.name;
        form.elements.description.value = product.description;
        form.elements.model.value = product.model;
        $("#model").val(product.model).trigger("change");
      })
      .catch(function (error) {});
  } else {
    modal.find(".modal-title").text("Crear Producto");
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

  $("#form-create-products").validate({
    rules: {
      name: {
        required: true,
      },
      description: {
        required: false,
      },
      model: {
        required: true,
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
      data.append("name", document.getElementById("name").value);
      data.append("description", document.getElementById("description").value);
      data.append("model", document.getElementById("model").value);
      if (document.getElementById("image").files[0] != null) {
        data.append("image", document.getElementById("image").files[0]);
      }
    
      if (edit_products) {
        axios
          .patch(`${url}` + selected_id + "/", data)
          .then((response) => {
            if (response.status === 200) {
              $("#modal-crear-products").modal("hide");
              Swal.fire({
                icon: "success",
                title: "Producto actualizado con éxito",
                showConfirmButton: false,
                timer: 1500,
              });
              table.ajax.reload();
    
              edit_products = false;
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
              title: "Error al crear el Producto",
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
                title: "Producto creado con éxito",
                showConfirmButton: false,
                timer: 1500,
              });
              table.ajax.reload();
              $("#modal-crear-products").modal("hide");
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
              title: "Error al crear el Producto",
              text: textError,
              showConfirmButton: false,
              timer: 1500,
            });
          });
      }


    },

    messages: {},
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

// crear Producto
let form = document.getElementById("form-create-products");

function poblarListas() {
  // Poblar la lista de modelos
  var $model = document.getElementById("model");
  var $filterModel = document.getElementById("filter-model");
  $filterModel.add(new Option("ninguno", ""));
  axios.get("/business-gestion/models/").then(function (response) {
    response.data.results.forEach(function (element) {
      var option = new Option(element.name, element.id);
      $model.add(option);
      var option = new Option(element.name, element.id);
      $filterModel.add(option);
    });
  });
}

function function_delete(id, name, model_name) {
  const table = $("#tabla-de-Datos").DataTable();
  Swal.fire({
    title: "Eliminar",
    text: `¿Está seguro que desea eliminar el Producto ${name} del modelo ${model_name}?`,
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

// Función para convertir una imagen a Base64
async function getBase64Image(url) {
  const response = await axios.get(url, { responseType: "arraybuffer" });
  const base64String = btoa(
    new Uint8Array(response.data).reduce(
      (data, byte) => data + String.fromCharCode(byte),
      ""
    )
  );
  return `data:image/jpeg;base64,${base64String}`; // Cambia el tipo MIME si es necesario
}
