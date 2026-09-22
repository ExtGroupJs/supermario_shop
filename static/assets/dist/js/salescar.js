var load = document.getElementById("load");
const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];

let selectedShopId = localStorage.getItem("selectedShopId");
let url = "/business-gestion/shop-products/";

let productosSeleccionados = [];
let importe_total = 0;
const defaultProductImage = document.getElementById("productImagen")?.src || "";

function buildComprobanteText({
  saleId,
  productos,
  paymentMethod,
  discount,
  extraInfo,
}) {
  const paymentMethodName = paymentMethod === "Z" ? "Zelle" : "USD";
  const grossTotal = productos.reduce(
    (acc, item) => acc + Number(item.precio || 0) * Number(item.cantidad || 0),
    0,
  );
  const netTotal = Math.max(grossTotal - Number(discount || 0), 0);
  const dateStr = new Date().toLocaleString("es-VE");

  const productLines = productos
    .map((item, index) => {
      const unitPrice = Number(item.precio || 0);
      const quantity = Number(item.cantidad || 0);
      const subtotal = unitPrice * quantity;
      return [
        `${index + 1}. ${item.producto}`,
        `   Cantidad: ${quantity}`,
        `   Precio: $${unitPrice.toFixed(2)}`,
        `   Subtotal: $${subtotal.toFixed(2)}`,
      ].join("\n");
    })
    .join("\n\n");

  return [
    "COMPROBANTE DE VENTA",
    `Nro: ${String(saleId || "N/A")}`,
    `Fecha: ${dateStr}`,
    `Metodo de pago: ${paymentMethodName}`,
    "------------------------------",
    "PRODUCTOS:",
    productLines,
    "------------------------------",
    `Subtotal: $${grossTotal.toFixed(2)}`,
    `Descuento: $${Number(discount || 0).toFixed(2)}`,
    `Total: $${netTotal.toFixed(2)}`,
    `Notas: ${extraInfo || ""}`,
  ].join("\n");
}

function buildComprobanteHtml(comprobanteText) {
  return `
    <div id="sale-comprobante" style="text-align:left;max-height:360px;overflow:auto;">
      <pre style="white-space:pre-wrap;font-family:monospace;margin:0;">${escapeHtml(comprobanteText)}</pre>
    </div>
  `;
}

async function copiarComprobante(comprobanteText) {
  const text = (comprobanteText || "").trim();

  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    }

    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    const successful = document.execCommand("copy");
    document.body.removeChild(textarea);
    return successful;
  } catch (error) {
    return false;
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.innerText = text;
  return div.innerHTML;
}

// Cargar productos al inicio
$(document).ready(function () {
  cargarProductos();
});

// Función para cargar productos
function cargarProductos() {
  load.hidden = false;
  const params = {};
  params.quantity__gte = 1;
  params.shop = selectedShopId;
  axios
    .get(url, { params })
    .then((res) => {
      const productos = res.data.results;

      productos.forEach((producto) => {
        if (producto.quantity > 0) {
          $("#producto").append(
            new Option(`${producto.__repr__}`, producto.id, false, false),
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
  if (!id) {
    load.hidden = true;
    return;
  }

  axios
    .get(url + id + "/")
    .then((res) => {
      especificProducto = res.data;
      $("#productoDescripcionExt").text(
        `Existencia: ${especificProducto.quantity}`,
      );
      $("#productoDescripcionPrec").text(
        `Precio: $${especificProducto.sell_price}`,
      );
      const imageElement = document.getElementById("productImagen");
      const nuevaUrl = especificProducto?.product?.image;

      if (imageElement) {
        imageElement.src =
          nuevaUrl && nuevaUrl !== "null" ? nuevaUrl : defaultProductImage;
      }

      load.hidden = true;
    })
    .catch((error) => {
      const imageElement = document.getElementById("productImagen");
      if (imageElement && defaultProductImage) {
        imageElement.src = defaultProductImage;
      }
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
  importe_total = 0;
  const tbody = $("#productosTable tbody");
  const showimport = document.getElementById("impTotal");
  tbody.empty();

  productosSeleccionados.forEach((item) => {
    importe_total += item.importe;
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
  showimport.innerText = `Importe total: ${importe_total}$`;
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

  const descuento = parseInt($("#descuento").val()) || 0;
  const extraInfo = $("#extra_info").val() || "";
  const paymentMethod = $("#payment_method").val();
  const sellerId = localStorage.getItem("id");

  const payload = {
    discount: descuento,
    extra_info: extraInfo,
    payment_method: paymentMethod,
    seller: sellerId,
    sells: productosSeleccionados.map((item) => ({
      shop_product: item.id,
      quantity: item.cantidad,
      extra_info: extraInfo,
    })),
  };

  axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
  axios
    .post("/business-gestion/sell-groups/", payload)
    .then(async (response) => {
      load.hidden = true;

      const comprobanteText = buildComprobanteText({
        saleId: response.data?.id,
        productos: productosSeleccionados,
        paymentMethod,
        discount: descuento,
        extraInfo,
      });
      const comprobanteHtml = buildComprobanteHtml(comprobanteText);

      const result = await Swal.fire({
        icon: "success",
        title: "Venta creada con éxito",
        html: comprobanteHtml,
        width: 700,
        showDenyButton: true,
        confirmButtonText: "Copiar comprobante",
        denyButtonText: "Cerrar",
      });

      if (result.isConfirmed) {
        const copied = await copiarComprobante(comprobanteText);
        if (copied) {
          await Swal.fire({
            icon: "success",
            title: "Comprobante copiado",
            text: "El comprobante se copio al portapapeles.",
          });
        } else {
          await Swal.fire({
            icon: "error",
            title: "No se pudo copiar",
            text: "No fue posible copiar el comprobante automaticamente.",
          });
        }
      }

      productosSeleccionados = [];
      $("#productosTable tbody").empty();
      $("#descuento").val("");
      $("#extra_info").val("");
      $("#payment_method").val("U"); // Restablecer a USD por defecto
    })
    .catch((error) => {
      load.hidden = true;
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Error al completar la venta: " + error.message,
      });
    });
});
