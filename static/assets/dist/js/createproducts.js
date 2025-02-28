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

  poblarListas();
});

$(document).ready(function () {
 
});

let selected_id;



// $("#modal-crear-products").on("hide.bs.modal", (event) => {
//   const form = event.currentTarget.querySelector("form");
//   form.reset();
//   edit_products = false;
//   const elements = [...form.elements];
//   elements.forEach((elem) => elem.classList.remove("is-invalid"));
// });

let edit_products = false;


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
          form.reset();
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

function poblarListas() {
  // Poblar la lista de modelos
  var $model = document.getElementById("model"); 
  axios.get("/business-gestion/models/").then(function (response) {
    response.data.results.forEach(function (element) {
      var option = new Option(element.name, element.id);
      $model.add(option);
      var option = new Option(element.name, element.id);      
    });
  });
}


// Función para convertir una imagen a Base64
async function getBase64Image(url) {
  const response = await axios.get(url, { responseType: 'arraybuffer' });
  const base64String = btoa(
    new Uint8Array(response.data).reduce((data, byte) => data + String.fromCharCode(byte), '')
  );
  return `data:image/jpeg;base64,${base64String}`; // Cambia el tipo MIME si es necesario
}
