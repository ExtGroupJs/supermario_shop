// Edicion de foto de producto desde movil
const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

const productsUrl = "/business-gestion/products/";
const shopProductsUrl = "/business-gestion/shop-products/";
const selectedShopId = localStorage.getItem("selectedShopId");
const load = document.getElementById("load");
const productSelect = document.getElementById("product-select");
const btnTakePhoto = document.getElementById("btn-take-photo");
const btnRotate = document.getElementById("btn-rotate");
const btnRetake = document.getElementById("btn-retake");
const btnUpload = document.getElementById("btn-upload");
const cameraInput = document.getElementById("camera-input");
const galleryInput = document.getElementById("gallery-input");
const cropImage = document.getElementById("crop-image");
const pendingCount = document.getElementById("pending-count");
const productInfoCard = document.getElementById("product-info-card");
const editorCard = document.getElementById("editor-card");
const currentImage = document.getElementById("current-image");

let allProducts = [];
let currentProduct = null;
let cropper = null;
let webpReady = false;
const isLikelyMobile = /Android|iPhone|iPad|iPod|IEMobile|Opera Mini/i.test(navigator.userAgent || "");

$(function () {
  $("#btn-take-photo").on("click", abrirSelectorImagen);
  $("#btn-rotate").on("click", function () { if (cropper) cropper.rotate(90); });
  $("#btn-retake").on("click", function () {
    abrirSelectorImagen();
  });
  $("#btn-upload").on("click", subirFoto);

  cameraInput.addEventListener("change", handleFileSelected);
  galleryInput.addEventListener("change", handleFileSelected);
  $(productSelect).on("change", onProductSelected);

  cargarProductos();
});

function abrirSelectorImagen() {
  if (!currentProduct) {
    Swal.fire({ icon: "info", title: "Selecciona un producto", text: "Primero elige el producto al que quieres asignar la foto." });
    productSelect.focus();
    return;
  }

  Swal.fire({
    title: "Origen de la imagen",
    text: "Puedes tomar una foto o elegir una imagen de tu dispositivo.",
    icon: "question",
    showDenyButton: true,
    showCancelButton: true,
    confirmButtonText: "Camara",
    denyButtonText: "Galeria",
    cancelButtonText: "Cancelar",
  }).then(function (result) {
    if (result.isConfirmed) {
      abrirEntradaImagen(true);
      return;
    }
    if (result.isDenied) {
      abrirEntradaImagen(false);
    }
  });
}

function abrirEntradaImagen(preferCamera) {
  if (preferCamera && isLikelyMobile) {
    if (typeof cameraInput.showPicker === "function") {
      cameraInput.showPicker();
      return;
    }
    cameraInput.click();
    return;
  }

  if (preferCamera && !isLikelyMobile) {
    Swal.fire({
      icon: "info",
      title: "Camara no disponible",
      text: "En escritorio se abrira el selector de archivos.",
      timer: 1300,
      showConfirmButton: false,
    });
  }

  if (typeof galleryInput.showPicker === "function") {
    galleryInput.showPicker();
    return;
  }
  galleryInput.click();
}

function setVisible(element, visible) {
  if (!element) return;
  element.hidden = !visible;
}

function cargarProductos() {
  if (!selectedShopId) {
    allProducts = [];
    renderProductOptions();
    Swal.fire({
      icon: "warning",
      title: "Tienda no seleccionada",
      text: "Debes seleccionar una tienda para listar sus productos.",
    });
    return;
  }

  load.hidden = false;
  axios.get(shopProductsUrl, { params: { shop: selectedShopId } })
    .then(function (response) {
      const shopProducts = Array.isArray(response.data)
        ? response.data
        : (response.data.results || []);

      allProducts = mapShopProductsToProducts(shopProducts);
      renderProductOptions();

      if (allProducts.length === 0) {
        Swal.fire({
          icon: "info",
          title: "Sin productos",
          text: "La tienda seleccionada no tiene productos cargados.",
        });
      }
    })
    .catch(function () {
      Swal.fire({ icon: "error", title: "Error", text: "No se pudieron cargar los productos de la tienda seleccionada." });
    })
    .finally(function () {
      load.hidden = true;
    });
}

function mapShopProductsToProducts(shopProducts) {
  const uniqueProducts = [];
  const seenProductIds = new Set();

  shopProducts.forEach(function (shopProduct) {
    const product = shopProduct && shopProduct.product;
    if (!product || !product.id) return;

    const productId = String(product.id);
    if (seenProductIds.has(productId)) return;

    seenProductIds.add(productId);
    uniqueProducts.push(product);
  });

  return uniqueProducts.sort(function (a, b) {
    const textA = String(a.__str__ || a.name || "");
    const textB = String(b.__str__ || b.name || "");
    return textA.localeCompare(textB);
  });
}

function renderProductOptions() {
  const selectedId = currentProduct ? String(currentProduct.id) : String(productSelect.value || "");
  const withoutPhoto = allProducts.filter((p) => !p.image);
  const withPhoto = allProducts.filter((p) => p.image);

  const buildOptions = (list) => list
    .map((p) => `<option value="${p.id}">${escapeHtml(p.__str__ || p.name)}${p.image ? " ✔" : ""}</option>`)
    .join("");

  let html = "";
  html += '<option value="">Selecciona un producto</option>';
  if (withoutPhoto.length) {
    html += `<optgroup label="Sin foto (${withoutPhoto.length})">${buildOptions(withoutPhoto)}</optgroup>`;
  }
  if (withPhoto.length) {
    html += `<optgroup label="Con foto (${withPhoto.length})">${buildOptions(withPhoto)}</optgroup>`;
  }
  productSelect.innerHTML = html;

  if (selectedId && allProducts.some((p) => String(p.id) === selectedId)) {
    productSelect.value = selectedId;
  } else if (withoutPhoto.length > 0) {
    productSelect.value = String(withoutPhoto[0].id);
  }

  $(productSelect).trigger("change");

  pendingCount.textContent = `${withoutPhoto.length} sin foto`;
  pendingCount.className = "badge float-right pending-badge " +
    (withoutPhoto.length > 0 ? "badge-warning" : "badge-success");
}

function onProductSelected(event) {
  const id = event && event.target ? event.target.value : productSelect.value;
  if (!id) {
    currentProduct = null;
    setVisible(productInfoCard, false);
    setVisible(editorCard, false);
    resetEditor();
    return;
  }
  currentProduct = allProducts.find((p) => String(p.id) === String(id)) || null;
  if (!currentProduct) return;

  document.getElementById("product-info-name").textContent = currentProduct.__str__ || currentProduct.name;
  document.getElementById("product-info-model").textContent = currentProduct.model_name || "";
  document.getElementById("product-info-status").textContent = currentProduct.image ? "Ya tiene foto" : "Sin foto";

  currentImage.src = currentProduct.image || "";
  currentImage.classList.toggle("photo-preview--empty", !currentProduct.image);

  setVisible(productInfoCard, true);
  resetEditor();

  // Si el producto ya tiene foto, cargarla en el editor para previsualizar/editar
  if (currentProduct && currentProduct.image) {
    cargarImagenEditor(currentProduct.image);
  }
}

function handleFileSelected(event) {
  const file = event.target.files && event.target.files[0];
  event.target.value = "";
  if (!file) return;

  // Si aun no hay producto seleccionado, tomar el primer pendiente (el mas
  // comun en flujo movil: primero se toma la foto y luego se elige el producto).
  if (!currentProduct && !seleccionarPrimerPendiente()) {
    Swal.fire({ icon: "warning", title: "Sin productos", text: "No hay productos disponibles para asignar la foto." });
    return;
  }

  const reader = new FileReader();
  reader.onload = function (e) {
    cargarImagenEditor(e.target.result);
  };
  reader.readAsDataURL(file);
}

function seleccionarPrimerPendiente() {
  const next = allProducts.find((p) => !p.image);
  if (!next) return false;
  currentProduct = next;
  $(productSelect).val(String(next.id)).trigger("change");
  btnTakePhoto.focus();
  return true;
}

function cargarImagenEditor(dataUrl) {
  resetEditor();

  if (typeof Cropper === "undefined") {
    Swal.fire({ icon: "error", title: "Editor no disponible", text: "No se pudo cargar la libreria de recorte (Cropper)." });
    return;
  }

  // Registrar el manejador ANTES de asignar src para no perder la carga cuando
  // la imagen ya esta en cache (load sincrono).
  cropImage.onload = function () {
    if (!currentProduct) return;
    setVisible(editorCard, true);
    cropper = new Cropper(cropImage, {
      viewMode: 1,
      aspectRatio: 1,
      autoCropArea: 1,
      responsive: true,
      background: false,
      modal: true,
      guides: true,
      ready: function () {
        webpReady = true;
        btnUpload.disabled = false;
      },
    });
  };

  cropImage.onerror = function () {
    webpReady = false;
    btnUpload.disabled = true;
    Swal.fire({ icon: "error", title: "Imagen invalida", text: "No se pudo cargar la imagen seleccionada para recortarla." });
  };

  cropImage.src = dataUrl; // asignar al final
  setVisible(editorCard, true);
}

function resetEditor() {
  if (cropper) {
    cropper.destroy();
    cropper = null;
  }
  webpReady = false;
  btnUpload.disabled = true;
  cropImage.removeAttribute("src");
}

function subirFoto() {
  if (!currentProduct || !cropper || !webpReady) return;

  const canvas = cropper.getCroppedCanvas({ width: 768, height: 768, imageSmoothingQuality: "high" });
  if (!canvas) {
    Swal.fire({ icon: "error", title: "Error", text: "No se pudo preparar el recorte de la imagen." });
    return;
  }

  btnUpload.disabled = true;
  load.hidden = false;

  canvas.toBlob(function (blob) {
    if (!blob) {
      load.hidden = true;
      Swal.fire({ icon: "error", title: "Error", text: "No se pudo generar la imagen WEBP." });
      btnUpload.disabled = false;
      return;
    }

    const fileName = `product_${currentProduct.id}_${Date.now()}.webp`;
    const file = new File([blob], fileName, { type: "image/webp" });

    const data = new FormData();
    data.append("image", file);

    axios
      .patch(`${productsUrl}${currentProduct.id}/`, data)
      .then(function (response) {
        currentProduct.image = response.data.image;
        renderProductOptions();
        resetEditor();
        setVisible(editorCard, false);

        Swal.fire({
          icon: "success",
          title: "Foto subida",
          text: "Formato WEBP guardado.",
          showConfirmButton: false,
          timer: 900,
        });

        irAlSiguientePendiente();
      })
      .catch(function (error) {
        Swal.fire({ icon: "error", title: "Error al subir", text: error.response?.data ? JSON.stringify(error.response.data) : error.message });
      })
      .finally(function () {
        load.hidden = true;
        btnUpload.disabled = false;
      });
  }, "image/webp", 0.9);
}

function irAlSiguientePendiente() {
  const next = allProducts.find((p) => !p.image);
  if (!next) {
    Swal.fire({ icon: "success", title: "Todos los productos tienen foto", showConfirmButton: false, timer: 1200 });
    return;
  }
  $(productSelect).val(String(next.id)).trigger("change");
  btnTakePhoto.focus();
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.innerText = text == null ? "" : String(text);
  return div.innerHTML;
}