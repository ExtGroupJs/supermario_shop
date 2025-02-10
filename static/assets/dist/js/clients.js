// Variable con el token
const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
// url del endpoint principal
const url = "/client-gestion/clients/";

$(function () {
  bsCustomFileInput.init();
  poblarListas();
});

$(document).ready(function () {
  const classes = ["bg-primary", "bg-info", "bg-success", "bg-danger"];
  $("table")
    .addClass("table table-hover")
    .DataTable({
      responsive: true,
      dom: '<"top"l>Bfrtip',
      buttons: [
        {
          text: "Crear",
          className: " btn btn-primary btn-info",
          action: function (e, dt, node, config) {
            $("#modal-crear-clients").modal("show");
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
        { data: "name", title: "Nombre" },
        { data: "phone", title: "Teléfono" },
        { data: "shop", title: "Tienda" },
        {
          data: "models",
          title: "Modelos",
          render: function (models) {
            return models
              .map((model) => {
                const randomClass =
                  classes[Math.floor(Math.random() * classes.length)];
                return `<span class="float-right badge ${randomClass}">${model.name}</span>`;
              })
              .join(" ");
          },
        },

        {
          data: "id",
          title: "Acciones",
          render: (data, type, row) => {
            return `<div class="btn-group">
                        <button type="button" title="edit" class="btn bg-olive active" data-toggle="modal" data-target="#modal-crear-clients" data-id="${row.id}" data-type="edit" data-name="${row.name}" id="${row.id}"  >
                          <i class="fas fa-edit"></i>
                        </button>  
                        <button type="button" title="delete" class="btn bg-olive" onclick="function_delete('${row.id}','${row.name}')" >
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

let selected_id;

$("#modal-crear-clients").on("hide.bs.modal", (event) => {
  // The form element is selected from the event trigger and its value is reset.
  const form = event.currentTarget.querySelector("form");
  form.reset();
  // The 'edit_clients' flag is set to false.
  edit_clients = false;
  // An array 'elements' is created containing all the HTML elements found inside the form element.
  const elements = [...form.elements];
  // A forEach loop is used to iterate through each element in the array.
  elements.forEach((elem) => elem.classList.remove("is-invalid"));
});

let edit_clients = false;
$("#modal-crear-clients").on("show.bs.modal", function (event) {
  var button = $(event.relatedTarget); // Button that triggered the modal

  var modal = $(this);
  if (button.data("type") == "edit") {
    var dataName = button.data("name"); // Extract info from data-* attributes
    selected_id = button.data("id"); // Extract info from data-* attributes
    edit_clients = true;

    modal.find(".modal-title").text("Editar Cliente " + dataName);

    // Realizar la petición con Axios
    axios
      .get(`${url}` + selected_id + "/")
      .then(function (response) {
        const client = response.data; // Cambié 'clients' a 'client' para reflejar que es un solo cliente

        // Asignar los valores a los campos del formulario
        form.elements.name.value = client.name;
        form.elements.phone.value = client.phone; // Asumiendo que tienes un campo para el teléfono

        form.elements.shop.value = client.shop;

        // // Asignar los valores del multiselect para los modelos
        const modelSelect = form.elements.models;

        const selectedModels = client.models.map((model) => model.id); // Asumiendo que 'nombre' es el campo que contiene el nombre del modelo

        for (let i = 0; i < modelSelect.options.length; i++) {
          modelSelect.options[i].selected = existeEnArreglo(
            selectedModels,
            modelSelect.options[i].value
          );
        }

        // Cambiar el título del modal para indicar que se está editando
        modal.find(".modal-title").text("Editar Cliente");
      })
      .catch(function (error) {});
  } else {
    modal.find(".modal-title").text("Crear Marca");
  }
});

function existeEnArreglo(arreglo, numero) {
  for (let i = 0; i < arreglo.length; i++) {
    if (arreglo[i] == numero) {
      return true; // Retorna verdadero si el número se encuentra
    }
  }
  return false; // Retorna falso si no se encuentra
}

// form validator
$(function () {
  $.validator.setDefaults({
    language: "es",
    submitHandler: function () {
      // alert("Form successful submitted!");
    },
  });

  $("#form-create-clients").validate({
    rules: {
      name: {
        required: true,
      },
      phone: {
        required: true,
      },
    },
    submitHandler: function (form) {},

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

// crear marca

let form = document.getElementById("form-create-clients");
form.addEventListener("submit", function (event) {
  event.preventDefault();
  var table = $("#tabla-de-Datos").DataTable();
  const csrfToken = document.cookie
    .split(";")
    .find((c) => c.trim().startsWith("csrftoken="))
    ?.split("=")[1];
  axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
  // Captura el valor del nombre
  const name = document.getElementById("name").value;

  // Captura el valor del teléfono
  const phone = document.getElementById("phone").value;

  // Captura el valor de la tienda seleccionada
  const shop = parseInt(document.getElementById("shop").value, 10); // Convierte a entero

  // Captura los modelos seleccionados como un array
  const models = Array.from(
    document.getElementById("models").selectedOptions
  ).map((option) => parseInt(option.value, 10));
  const data = {
    name: name,
    phone: phone,
    shop: shop,
    models: models, // Este campo será un array
  };

  if (edit_clients) {
    axios
      .patch(`${url}` + selected_id + "/", data)
      .then((response) => {
        if (response.status === 200) {
          $("#modal-crear-clients").modal("hide");
          Swal.fire({
            icon: "success",
            title: "Marca actualizada con éxito  ",
            showConfirmButton: false,
            timer: 1500,
          });
          table.ajax.reload();

          edit_clients = false;
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
          title: "Error al crear la Marca",
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
            title: "Marca creada con exito",
            showConfirmButton: false,
            timer: 1500,
          });
          table.ajax.reload();
          $("#modal-crear-clients").modal("hide");
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
          title: "Error al crear la marca",
          text: textError,
          showConfirmButton: false,
          timer: 1500,
        });
      });
  }
});

function function_delete(id, name) {
  const table = $("#tabla-de-Datos").DataTable();
  Swal.fire({
    title: "Eliminar",
    text: `¿Está seguro que desea eliminar el elemento ${name}?`,
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
function poblarListas() {
  // Poblar la lista de modelos
  var $model = document.getElementById("models");
  axios.get("/business-gestion/models/").then(function (response) {
    response.data.results.forEach(function (element) {
      var option = new Option(element.name, element.id);
      $model.add(option);
      var option = new Option(element.name, element.id);
    });
  });

  // Poblar la lista de tiendas
  var $shop = document.getElementById("shop");
  axios.get("/business-gestion/shops/").then(function (response) {
    response.data.results.forEach(function (element) {
      var option = new Option(element.name, element.id);
      $shop.add(option);
    });
  });
}
