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

  if (imagenes.length === 0) {
    return imagenPorDefecto
      ? `<div class="text-center"><img src="${imagenPorDefecto}" alt="producto sin imagen" class="img-fluid"></div>`
      : `<div style="text-align: center;"><i class="nav-icon fas fa-car-crash text-danger"></i></div>`;
  }

  const id = `carrusel-producto-${++contadorCarruselProducto}`;

  const items = imagenes
    .map(
      (src, index) => `
        <div class="carousel-item ${index === 0 ? "active" : ""} text-center">
          <img src="${src}" alt="imagen del producto" class="d-block img-fluid"
            style="max-height: ${altura}px; object-fit: contain;">
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

  return `<div id="${id}" class="carousel slide" data-ride="carousel">${indicadores}<div class="carousel-inner">${items}</div>${controles}</div>`;
}

// Inicializa los carruseles generados dentro de un contenedor
function inicializarCarruselesProducto(contenedor) {
  $(contenedor)
    .find(".carousel")
    .each(function () {
      $(this).carousel({ interval: 5000 });
    });
}
