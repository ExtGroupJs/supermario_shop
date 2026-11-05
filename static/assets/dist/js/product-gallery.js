// Utilidades compartidas para mostrar todas las imágenes de un producto
// (imagen principal + imágenes de la galería) en un carrusel de Bootstrap 4.

let contadorCarruselProducto = 0;

// Devuelve todas las imágenes de un producto: la principal y las de la galería
function imagenesProducto(producto) {
  if (!producto) {
    return [];
  }
  const galeria = Array.isArray(producto.gallery) ? producto.gallery : [];
  return [producto.image, ...galeria].filter(Boolean);
}

// Genera el HTML de un carrusel con todas las imágenes de un producto
function carruselProductoHtml(producto, opciones = {}) {
  const { altura = 120, imagenPorDefecto = "" } = opciones;
  const imagenes = imagenesProducto(producto);

  // Marco de tamaño fijo: mantiene la altura constante para que el resto de
  // la página (textos, precios) no se mueva al cambiar de imagen.
  const marco = (contenido) => `
    <div style="height: ${altura}px; width: 100%; display: flex; align-items: center; justify-content: center; background-color: #f8f9fa; overflow: hidden;">
      ${contenido}
    </div>`;

  const imagen = (src) => `
    <img src="${src}" alt="imagen del producto" class="d-block"
      style="max-width: 100%; max-height: 100%; width: auto; height: auto; object-fit: contain;">`;

  if (imagenes.length === 0) {
    return imagenPorDefecto
      ? marco(imagen(imagenPorDefecto))
      : marco(`<i class="nav-icon fas fa-car-crash text-danger"></i>`);
  }

  const id = `carrusel-producto-${++contadorCarruselProducto}`;

  const items = imagenes
    .map(
      (src, index) => `
        <div class="carousel-item text-center ${index === 0 ? "active" : ""}" style="height: ${altura}px;">
          ${marco(imagen(src))}
        </div>`
    )
    .join("");

  const indicadores =
    imagenes.length > 1
      ? `<ol class="carousel-indicators">${imagenes
          .map(
            (_, index) =>
              `<li data-target="#${id}" data-slide-to="${index}" class="${index === 0 ? "active" : ""}"></li>`
          )
          .join("")}</ol>`
      : "";

  const controles =
    imagenes.length > 1
      ? `<a class="carousel-control-prev" href="#${id}" role="button" data-slide="prev">
           <span class="carousel-control-prev-icon" aria-hidden="true"></span>
         </a>
         <a class="carousel-control-next" href="#${id}" role="button" data-slide="next">
           <span class="carousel-control-next-icon" aria-hidden="true"></span>
         </a>`
      : "";

  return `<div id="${id}" class="carousel slide" data-ride="carousel" style="height: ${altura}px; width: 100%;">${indicadores}<div class="carousel-inner" style="height: ${altura}px;">${items}</div>${controles}</div>`;
}

// Inicializa los carruseles generados dentro de un contenedor
function inicializarCarruselesProducto(contenedor) {
  $(contenedor)
    .find(".carousel")
    .each(function () {
      $(this).carousel({ interval: 5000 });
    });
}

// Abre el modal con el carrusel de imágenes de un producto
async function abrirModalImagenesProducto(productId, opciones = {}) {
  const { altura = 420 } = opciones;
  const modal = $("#modal-ver-imagenes-producto");
  const contenedor = modal.find("#contenedor-imagenes-producto");
  const mensaje = modal.find("#mensaje-imagenes-producto");

  contenedor.html("");
  mensaje.text("");

  try {
    const response = await axios.get(`/business-gestion/products/${productId}/`);

    if (imagenesProducto(response.data).length === 0) {
      mensaje.text("Este producto no tiene imágenes.");
    } else {
      contenedor.html(carruselProductoHtml(response.data, { altura }));
      inicializarCarruselesProducto(contenedor);
    }
  } catch (error) {
    mensaje.text("No se pudieron cargar las imágenes.");
  }

  modal.modal("show");
}

// Al hacer clic en la imagen principal se amplían todas las imágenes del producto
$(document).on("click", ".imagen-producto", function () {
  abrirModalImagenesProducto($(this).data("producto-id"));
});
