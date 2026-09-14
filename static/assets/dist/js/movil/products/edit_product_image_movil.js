// Edicion de foto de producto desde movil
const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

const productsUrl = "/business-gestion/products/";
const load = document.getElementById("load");
const productSelect = document.getElementById("product-select");
const btnNextPending = document.getElementById("btn-next-pending");
const btnTakePhoto = document.getElementById("btn-take-photo");
const btnGallery = document.getElementById("btn-gallery");
const btnRotate = document.getElementById("btn-rotate");
const btnRetake = document.getElementById("btn-retake");
const btnUpload = document.getElementById("btn-upload");
const cameraInput = document.getElementById("camera-input");
const galleryInput = document.getElementById("gallery-input");
const cropImage = document.getElementById("crop-image");
const pendingCount = document.getElementById("pending-count");

let allProducts = [];
let currentProduct = null;
let cropper = null;
let webpReady = false;

$(function () {
  $("#btn-take-photo").on("click", function () { cameraInput.click(); });
  $("#btn-gallery").on("click", function () { galleryInput.click(); });
  $("#btn-rotate").on("click", function () { if (cropper) cropper.rotate(90); });
  $("#btn-retake").on("click", function () { cameraInput.click(); });
  $("#btn-upload").on("click", subirFoto);
  $("#btn-next-pending").on("click", irAlSiguientePendiente);

  cameraInput.addEventListener("change", handleFileSelected);
  galleryInput.addEventListener("change", handleFileSelected);
  productSelect.addEventListener("change", onProductSelected);

  cargarProductos();
});

function cargarProductos() {
  load.hidden = false;
  axios.get(productsUrl)
    .then(function (response) {
      allProducts = response.data.results || [];
      renderProductOptions();
    })
    .catch(function () {
      Swal.fire({ icon: "error", title: "Error", text: "No se pudieron cargar los productos." });
    })
    .finally(function () {
      load.hidden = true;
    });
}

function renderProductOptions() {
  const withoutPhoto = allProducts.filter((p) => !p.image);
  const withPhoto = allProducts.filter((p) => p.image);

  const buildOptions = (list) => list
    .map((p) => `<option value="${p.id}">${escapeHtml(p.__str__ || p.name)}${p.image ? " ✔" : ""}</option>`)
    .join("");

  let html = "";
  if (withoutPhoto.length) {
    html += `<optgroup label="Sin foto (${withoutPhoto.length})">${buildOptions(withoutPhoto)}</optgroup>`;
  }
  if (withPhoto.length) {
    html += `<optgroup label="Con foto (${withPhoto.length})">${buildOptions(withPhoto)}</optgroup>`;
  }
  productSelect.innerHTML = html;
  $(productSelect).trigger("change.select2");

  pendingCount.textContent = `${withoutPhoto.length} sin foto`;
  pendingCount.className = "badge float-right pending-badge " +
    (withoutPhoto.length > 0 ? "badge-warning" : "badge-success");
}

function onProductSelected(event) {
  const id = event.target.value;
  if (!id) {
    currentProduct = null;
    $("#product-info-card").hide();
    $("#editor-card").hide();
    resetEditor();
    return;
  }
  currentProduct = allProducts.find((p) => String(p.id) === String(id)) || null;
  if (!currentProduct) return;

  document.getElementById("product-info-name").textContent = currentProduct.__str__ || currentProduct.name;
  document.getElementById("product-info-model").textContent = currentProduct.model_name || "";
  document.getElementById("product-info-status").textContent = currentProduct.image ? "Ya tiene foto" : "Sin foto";

  const currentImage = document.getElementById("current-image");
  currentImage.src = currentProduct.image || "";
  currentImage.classList.toggle("photo-preview--empty", !currentProduct.image);

  $("#product-info-card").show();
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
  if (!currentProduct) seleccionarPrimerPendiente();

  const reader = new FileReader();
  reader.onload = function (e) {
    cargarImagenEditor(e.target.result);
  };
  reader.readAsDataURL(file);
}

function seleccionarPrimerPendiente() {
  const next = allProducts.find((p) => !p.image);
  if (!next) return;
  currentProduct = next;
  $(productSelect).val(String(next.id)).trigger("change");
  btnTakePhoto.focus();
}

function cargarImagenEditor(dataUrl) {
  resetEditor();

  // Registrar el manejador ANTES de asignar src para no perder la carga cuando
  // la imagen ya esta en cache (load sincrono).
  cropImage.onload = function () {
    setTimeout(function () {
      if (!currentProduct) return;
      $("#editor-card").show();
      cropper = new Cropper(cropImage, {
        viewMode: 1,
        aspectRatio: 1,
        autoCropArea: 1,
        responsive: true,
        background: false,
        modal: true,
        guides: true,
      });
      webpReady = true;
      btnUpload.disabled = false;
    }, 50);
  };

  cropImage.src = dataUrl; // asignar al final
  $("#editor-card").show();
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
        $("#editor-card").hide();

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