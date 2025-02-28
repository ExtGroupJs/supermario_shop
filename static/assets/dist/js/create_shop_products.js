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
            title: "Error al crear la Entrada de Producto",
            text: textError,
            showConfirmButton: false,
            timer: 1500,
          });
        });
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
      cargarProductoEspecifico($product.value);
    });
}

function esNegativo(num) {
  return num < 0;
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
