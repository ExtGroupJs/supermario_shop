var load = document.getElementById("load");
const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];

const url = "/business-gestion/shop-products/";
let productosSeleccionados = [];
let importe_total = 0;
// Cargar productos al inicio
$(document).ready(function () {
  cargarProductos();
});

// Función para cargar productos
function cargarProductos() {
  load.hidden = false;
  axios
    .get(url)
    .then((res) => {
      const productos = res.data.results;

      productos.forEach((producto) => {
       if(producto.quantity>0){
        $("#producto").append(
          new Option(`${producto.__repr__}`, producto.id, false, false)
        );
       }
      
      });
      cargarProductoEspecifico($("#producto").val());
    })
    .catch((error) => {
      load.hidden = true;
      console.error("Error al cargar productos:", error);
    });
}
let especificProducto;
function cargarProductoEspecifico(id) {
  axios
    .get(url + id + "/")
    .then((res) => {
      especificProducto = res.data;
      $("#productoDescripcion").text(
        `Existencia: ${especificProducto.quantity}, Precio: $${especificProducto.sell_price}`
      );
      load.hidden = true;
    })
    .catch((error) => {
      load.hidden = true;
      console.error("Error al cargar productos:", error);
    });
}

// Agregar producto a la lista
$("#agregarProducto").on("click", function () {
  const productoId = $("#producto").val();

  const cantidad = $("#cantidad").val();

  if (!productoId || cantidad < 1 || cantidad > especificProducto.quantity) {
    $("#cantidad").focus().select().addClass("is-invalid");
    Swal.fire({
      icon: "error",
      title: "Error",
      text: `La cantidad debe estar entre 1 y ${especificProducto.quantity}.`,
    });

    return;
  } else {
    $("#cantidad").removeClass("is-invalid");
  }

  const producto = $("#producto option:selected").text();
  const precio = especificProducto.sell_price;
  const status = "preventa";
  const importe = especificProducto.sell_price * cantidad;

  if (!existe()) {
    productosSeleccionados.push({
      id: productoId,
      producto,
      cantidad,
      precio,
      importe,
      status,
    });
    actualizarTabla();
  } else {
    Swal.fire({
      icon: "error",
      title: "Error",
      text: `El producto ya fue agregado.`,
    });
  }
});

function existe() {
  let exist = false;
  productosSeleccionados.forEach((item) => {
    if (item.id === $("#producto").val()) {
      exist = true;
    }
  });
  return exist;
}

// Actualizar la tabla de productos seleccionados
function actualizarTabla() {
  importe_total=0;
  const tbody = $("#productosTable tbody");
  const showimport=document.getElementById("impTotal"); 
  tbody.empty();

  productosSeleccionados.forEach((item) => {
    importe_total+=item.importe;
    tbody.append(`
            <tr>
                <td>${item.producto}</td>
                <td>${item.cantidad}</td>
                <td>$${item.precio}</td>
                <td>$${item.importe}</td>
                <td><button type="button" title="delete" id="${item.id}" class="btn bg-olive" onclick="eliminarProducto('${item.id}')" ><i class="fas fa-trash"></i></button></td>
            </tr>
        `);
  });
  showimport.innerText=`Importe total:${importe_total}$`;
  $("#cantidad").focus().select().val("");
}

function eliminarProducto(id) {
  const index = productosSeleccionados.findIndex((item) => item.id === id);
  if (index > -1) {
    productosSeleccionados.splice(index, 1);
    actualizarTabla();
  }
}

// Crear venta
$("#crearVenta").on("click", function () {
  load.hidden = false;
  if (productosSeleccionados.length === 0) {
    Swal.fire({
      icon: "error",
      title: "Error",
      text: `No hay productos seleccionados para vender.`,
    });
    load.hidden = true; 
    return;
  }

  productosSeleccionados.forEach((item) => {
    const payload = {
      shop_product: item.id,
      quantity: item.cantidad,
    };
    axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
    axios
      .post("/business-gestion/sell-products/", payload)
      .then((response) => {
        item.status = "vendido";
        importe_total=0;
        actualizarTabla();
        $('#producto').empty();
        cargarProductos();
      })
      .catch((error) => {
        item.status = "error";
        load.hidden = true;
        Swal.fire({
          icon: "error",
          title: "Error",
          text: "Error al completar la venta: " + error.message,
        });

      });
  });

  let texto = "";
  html = "<hr><ul style='justify-content: left'>";
  productosSeleccionados.forEach((item) => {

    if (item.status === "error") {
      html += `<li class="text-danger">${item.producto} - ${item.cantidad} - <i class="icon fas fa-ban"></i> </li>`;
    } else {
      html += `<li class="text-success">${item.producto} - ${item.cantidad} - <i class="icon fas fa-check"></i> </li>`;
    }
  });
  html += `</ul><h4>Importe Total: ${importe_total}</h4><hr>`;
  Swal.fire({
    icon: "success",
    title: "Venta creada con éxito",
    html: `Productos vendidos: \n` + html,
  });
  // Limpiar la selección
  productosSeleccionados = [];
  $("#productosTable tbody").empty();
  load.hidden = true;
});
