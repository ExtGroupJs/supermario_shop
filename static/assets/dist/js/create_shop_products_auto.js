const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

const shopProductsUrl = "/business-gestion/shop-products/";
const load = document.getElementById("load");
const parsedResultsBody = document.getElementById("parsed-results-body");
const createButton = document.getElementById("btn-create-entries");
const thresholdInput = document.getElementById("similarityThreshold");
const thresholdValue = document.getElementById("similarityValue");

let parsedEntries = [];
let globalExtraInfo = "";
let selectedShopProducts = [];
let allProducts = [];
let pendingProductCreation = null;

$(function () {
  poblarTiendas();
  bindEvents();
});

function bindEvents() {
  $("#form-parse-message").on("submit", async function (event) {
    event.preventDefault();
    await analizarMensaje();
  });

  $("#btn-create-entries").on("click", async function () {
    await crearEntradas();
  });

  $("#similarityThreshold").on("input", function () {
    thresholdValue.textContent = `${this.value}%`;
  });

  $(document).on("change", ".manual-match-select", function () {
    const index = Number(this.dataset.index);
    const selectedValue = this.value;
    const entry = parsedEntries[index];

    if (!entry) {
      return;
    }

    entry.originalStatus = entry.originalStatus || entry.status;

    if (selectedValue === "") {
      entry.chosenMatch = null;
      entry.status = entry.originalStatus;
    } else if (selectedValue.startsWith("existing_")) {
      const productId = Number(selectedValue.replace("existing_", ""));
      const product = allProducts.find(p => p.id === productId);
      if (product) {
        abrirModalCrearShopProduct(index, productId, product.displayName);
        return;
      }
    } else {
      const selectedMatchIndex = Number(selectedValue);
      const candidateSource = getManualSelectionCandidates(entry);
      entry.chosenMatch = candidateSource[selectedMatchIndex] || null;
      entry.status = entry.chosenMatch ? "seleccionado_manualmente" : entry.originalStatus;
    }

    const checkbox = document.querySelector(`.entry-check[data-index="${index}"]`);
    if (checkbox) {
      checkbox.disabled = !entry.chosenMatch;
      checkbox.checked = Boolean(entry.chosenMatch);
    }

    const statusCell = document.querySelector(`.entry-status[data-index="${index}"]`);
    if (statusCell) {
      statusCell.innerHTML = renderStatus(entry);
    }

    updateCreateButtonState();
  });

  $(document).on("change", ".entry-check", function () {
    updateCreateButtonState();
  });

  $(document).on("click", "#btn-use-existing-product", function () {
    usarProductoExistenteDesdeModal();
  });
}

function poblarTiendas() {
  const selectedShopId = localStorage.getItem("selectedShopId");
  const shopSelect = document.getElementById("shop");
  axios.get("/business-gestion/shops/").then(function (response) {
    response.data.results.forEach(function (shop) {
      const isSelected = selectedShopId && Number(shop.id) === Number(selectedShopId);
      const option = new Option(shop.name, shop.id, isSelected, isSelected);
      shopSelect.add(option);
    });

    if (!shopSelect.value && shopSelect.options.length > 0) {
      shopSelect.value = shopSelect.options[0].value;
    }
  });
}

async function analizarMensaje() {
  const shopId = document.getElementById("shop").value;
  const message = document.getElementById("messageInput").value || "";

  if (!shopId) {
    Swal.fire({
      icon: "warning",
      title: "Selecciona una tienda",
      text: "Debes seleccionar una tienda antes de analizar el mensaje.",
    });
    return;
  }

  load.hidden = false;
  createButton.disabled = true;
  parsedEntries = [];

  try {
    selectedShopProducts = (await cargarShopProducts(shopId)).sort((a, b) =>
      a.displayName.localeCompare(b.displayName)
    );
    allProducts = await cargarTodosProductos();

    const lines = message
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    if (lines.length === 0) {
      renderNoResults("No hay lineas para procesar");
      return;
    }

    globalExtraInfo = lines[0];
    const itemLines = lines.slice(1);

    if (itemLines.length === 0) {
      renderNoResults("No se detectaron lineas de productos en el mensaje");
      return;
    }

    const threshold = Number(thresholdInput.value) / 100;

    parsedEntries = itemLines.map((line, index) => {
      const parsedLine = parseLine(line, index + 2);
      if (!parsedLine.valid) {
        return {
          ...parsedLine,
          status: "formato_invalido",
          matches: [],
          chosenMatch: null,
        };
      }

      const matches = findMatches(parsedLine.productText, selectedShopProducts, threshold);
      if (matches.length === 0) {
        return {
          ...parsedLine,
          status: "no_encontrado",
          originalStatus: "no_encontrado",
          matches,
          chosenMatch: null,
        };
      }

      if (matches.length > 1) {
        return {
          ...parsedLine,
          status: "ambiguo",
          originalStatus: "ambiguo",
          matches,
          chosenMatch: null,
        };
      }

      return {
        ...parsedLine,
        status: "encontrado",
        matches,
        chosenMatch: matches[0],
      };
    });

    renderParsedResults();
  } catch (error) {
    renderNoResults("Ocurrio un error analizando el mensaje");
    Swal.fire({
      icon: "error",
      title: "Error",
      text: "No se pudo analizar el mensaje. Intenta nuevamente.",
    });
  } finally {
    load.hidden = true;
  }
}

function parseLine(line, lineNumber) {
  const regex = /^\s*(\d+)\s*-\s*(.+)\s*$/;
  const match = line.match(regex);
  if (!match) {
    return {
      lineNumber,
      rawLine: line,
      valid: true,
      quantity: 1,
      productText: line.trim(),
    };
  }

  return {
    lineNumber,
    rawLine: line,
    valid: true,
    quantity: Number(match[1]),
    productText: match[2].trim(),
  };
}

async function cargarShopProducts(shopId) {
  const response = await axios.get(shopProductsUrl, {
    params: {
      shop: shopId,
    },
  });

  const results = response.data.results || [];
  return results.map((item) => {
    const candidateText = [
      item.product_name || "",
      item.model_brand || "",
      item.extra_info || "",
      item.__repr__ || "",
    ]
      .join(" ")
      .trim();

    return {
      id: item.id,
      currentQuantity: Number(item.quantity || 0),
      displayName: item.product_name || "Sin nombre",
      modelBrand: item.model_brand || "",
      sellPrice: item.sell_price,
      costPrice: item.cost_price,
      productId: item.product.id,
      candidateText,
      normalizedCandidate: normalizeText(candidateText),
    };
  });
}

async function cargarTodosProductos() {
  const response = await axios.get("/business-gestion/products/");
  return (response.data.results || []).map((item) => ({
    id: item.id,
    name: item.__str__ || item.name,
    displayName: item.name,
  }));
}

function getProductosNoEnTienda() {
  const shopProductIds = new Set(selectedShopProducts.map(p => p.productId));
  return allProducts.filter(p => !shopProductIds.has(p.id));
}

function findMatches(inputText, candidates, threshold) {
  const normalizedInput = normalizeText(inputText);
  const scored = candidates
    .map((candidate) => {
      const score = scoreSimilarity(normalizedInput, candidate.normalizedCandidate);
      return {
        ...candidate,
        score,
      };
    })
    .filter((candidate) => candidate.score >= threshold)
    .sort((a, b) => b.score - a.score)
    .slice(0, 3);

  if (scored.length <= 1) {
    return scored;
  }

  const bestScore = scored[0].score;
  return scored.filter((item) => bestScore - item.score <= 0.08);
}

function scoreSimilarity(a, b) {
  if (!a || !b) {
    return 0;
  }

  const containsBoost = b.includes(a) ? 1 : 0;
  const levenshtein = levenshteinSimilarity(a, b);
  const token = tokenOverlapScore(a, b);

  return 0.6 * levenshtein + 0.3 * token + 0.1 * containsBoost;
}

function normalizeText(text) {
  return (text || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function levenshteinSimilarity(a, b) {
  const distance = levenshteinDistance(a, b);
  const maxLen = Math.max(a.length, b.length);
  if (maxLen === 0) {
    return 1;
  }
  return 1 - distance / maxLen;
}

function levenshteinDistance(a, b) {
  const matrix = Array.from({ length: a.length + 1 }, () => Array(b.length + 1).fill(0));
  for (let i = 0; i <= a.length; i++) {
    matrix[i][0] = i;
  }
  for (let j = 0; j <= b.length; j++) {
    matrix[0][j] = j;
  }

  for (let i = 1; i <= a.length; i++) {
    for (let j = 1; j <= b.length; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      matrix[i][j] = Math.min(
        matrix[i - 1][j] + 1,
        matrix[i][j - 1] + 1,
        matrix[i - 1][j - 1] + cost
      );
    }
  }

  return matrix[a.length][b.length];
}

function tokenOverlapScore(a, b) {
  const aTokens = a.split(" ").filter(Boolean);
  const bTokens = b.split(" ").filter(Boolean);
  if (!aTokens.length || !bTokens.length) {
    return 0;
  }

  let matches = 0;
  for (const token of aTokens) {
    if (bTokens.includes(token)) {
      matches += 1;
    }
  }

  return matches / aTokens.length;
}

function renderParsedResults() {
  if (!parsedEntries.length) {
    renderNoResults("Sin resultados todavia");
    return;
  }

  const rows = parsedEntries
    .map((entry, index) => {
      const canCreate = canCreateEntry(entry);
      const statusHtml = renderStatus(entry);
      const matchesHtml = renderMatches(entry);

      return `
        <tr>
          <td class="text-center">
            <input type="checkbox" class="entry-check" data-index="${index}" ${canCreate ? "checked" : "disabled"}>
          </td>
          <td>${entry.quantity || "-"}</td>
          <td>${escapeHtml(entry.productText)}</td>
          <td>${matchesHtml}</td>
          <td class="entry-status" data-index="${index}">${statusHtml}</td>
        </tr>
      `;
    })
    .join("");

  parsedResultsBody.innerHTML = rows;
  initializeManualSelects();
  updateCreateButtonState();
}

function renderMatches(entry) {
  if (entry.status === "no_encontrado") {
    const entryIndex = parsedEntries.indexOf(entry);

    const options = [
      '<option value="">Selecciona un shop-product manualmente</option>',
      ...selectedShopProducts.map(
        (match, index) =>
          `<option value="${index}">${escapeHtml(match.displayName)} (${escapeHtml(
            match.modelBrand
          )}) | Precio: ${escapeHtml(match.sellPrice)} | Stock: ${escapeHtml(match.currentQuantity)}</option>`
      ),
    ].join("");

    return `
      <div>
        <div class="text-danger small mb-1">Sin coincidencias automáticas</div>
        <div style="display: flex; gap: 6px; align-items: flex-start;">
          <select class="form-control form-control-sm manual-match-select" data-index="${entryIndex}" style="flex: 1;">
            ${options}
          </select>
          <button type="button" class="btn btn-sm btn-outline-primary" onclick="abrirModalCrearProducto(${entryIndex})">
            <i class="fas fa-plus"></i>
          </button>
        </div>
      </div>
    `;
  }

  if (entry.status === "ambiguo") {
    const options = [
      '<option value="">Selecciona una coincidencia</option>',
      ...entry.matches.map(
        (match, index) =>
          `<option value="${index}">${escapeHtml(match.displayName)} (${escapeHtml(
            match.modelBrand
          )}) - ${Math.round(match.score * 100)}%</option>`
      ),
    ].join("");

    return `
      <div>
        <select class="form-control form-control-sm manual-match-select" data-index="${parsedEntries.indexOf(
          entry
        )}">
          ${options}
        </select>
      </div>
    `;
  }

  return entry.matches
    .map(
      (match) =>
        `${escapeHtml(match.displayName)} (${escapeHtml(match.modelBrand)}) - ${Math.round(
          match.score * 100
        )}%`
    )
    .join("<br>");
}

function renderStatus(entry) {
  if (entry.status === "encontrado") {
    return '<span class="badge badge-success">Encontrado</span>';
  }
  if (entry.manuallyCreated) {
    return '<span class="badge badge-primary">Agregado automaticamente al sistema</span>';
  }
  if (entry.status === "seleccionado_manualmente") {
    return '<span class="badge badge-info">Seleccionado manualmente</span>';
  }
  if (entry.status === "ambiguo") {
    return '<span class="badge badge-warning">Ambiguo: revisar</span>';
  }
  if (entry.status === "no_encontrado") {
    return '<span class="badge badge-danger">No existe shop-product (crear manualmente)</span>';
  }
  return '<span class="badge badge-secondary">Formato invalido</span>';
}

function renderNoResults(message) {
  parsedResultsBody.innerHTML = `
    <tr>
      <td colspan="5" class="text-center text-muted">${escapeHtml(message)}</td>
    </tr>
  `;
  createButton.disabled = true;
}

function canCreateEntry(entry) {
  return ["encontrado", "seleccionado_manualmente"].includes(entry.status) && Boolean(entry.chosenMatch);
}

function getManualSelectionCandidates(entry) {
  if (!entry) {
    return [];
  }

  if (entry.originalStatus === "no_encontrado" || entry.status === "no_encontrado") {
    return selectedShopProducts;
  }

  return entry.matches || [];
}

function initializeManualSelects() {
  $(".manual-match-select").select2({
    theme: "bootstrap4",
    width: "100%",
    placeholder: "Selecciona un producto",
  });
}

function updateCreateButtonState() {
  const checkedEntries = Array.from(document.querySelectorAll(".entry-check:checked"));
  createButton.disabled = checkedEntries.length === 0;
}

async function crearEntradas() {
  const selectedIndexes = Array.from(document.querySelectorAll(".entry-check:checked")).map(
    (checkbox) => Number(checkbox.dataset.index)
  );

  if (!selectedIndexes.length) {
    Swal.fire({
      icon: "warning",
      title: "Sin filas seleccionadas",
      text: "Selecciona al menos una fila encontrada para crear entradas.",
    });
    return;
  }

  const confirmText = `Se crearan ${selectedIndexes.length} entradas de inventario.`;
  const confirm = await Swal.fire({
    icon: "question",
    title: "Confirmar creacion",
    text: confirmText,
    showCancelButton: true,
    confirmButtonText: "Si, crear",
    cancelButtonText: "Cancelar",
  });

  if (!confirm.isConfirmed) {
    return;
  }

  load.hidden = false;

  let successCount = 0;
  let errorCount = 0;

  for (const index of selectedIndexes) {
    const entry = parsedEntries[index];
    if (!entry || !entry.chosenMatch) {
      continue;
    }

    try {
      const nextQuantity = Number(entry.chosenMatch.currentQuantity) + Number(entry.quantity);
      await axios.patch(`${shopProductsUrl}${entry.chosenMatch.id}/`, {
        quantity: nextQuantity,
      });
      successCount += 1;
    } catch (error) {
      errorCount += 1;
    }
  }

  load.hidden = true;

  if (errorCount === 0) {
    Swal.fire({
      icon: "success",
      title: "Entradas creadas",
      text: `Se actualizaron ${successCount} productos correctamente.`,
    });
  } else {
    Swal.fire({
      icon: "warning",
      title: "Proceso completado con incidencias",
      text: `Exitos: ${successCount}. Fallos: ${errorCount}.`,
    });
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.innerText = text;
  return div.innerHTML;
}

function abrirModalCrearProducto(entryIndex) {
  pendingProductCreation = { entryIndex };
  document.getElementById("form-create-product").reset();
  poblarProductosExistentesEnModal();
  $("#modal-create-product").modal("show");
}

function poblarProductosExistentesEnModal() {
  const select = document.getElementById("existing-product-select");
  if (!select) {
    return;
  }

  const productosNoEnTienda = getProductosNoEnTienda();
  const options = [
    '<option value="">Selecciona un producto existente</option>',
    ...productosNoEnTienda.map(
      (product) => `<option value="${product.id}">${escapeHtml(product.displayName)}</option>`
    ),
  ];

  select.innerHTML = options.join("");
  $(select).val("").trigger("change");
}

function usarProductoExistenteDesdeModal() {
  if (!pendingProductCreation) {
    return;
  }

  const selectedValue = document.getElementById("existing-product-select")?.value;
  if (!selectedValue) {
    Swal.fire({
      icon: "warning",
      title: "Selecciona un producto",
      text: "Debes seleccionar un producto existente para continuar.",
    });
    return;
  }

  const productId = Number(selectedValue);
  const product = allProducts.find((p) => p.id === productId);
  if (!product) {
    Swal.fire({
      icon: "error",
      title: "Producto no encontrado",
      text: "No se pudo identificar el producto seleccionado.",
    });
    return;
  }

  $("#modal-create-product").modal("hide");
  abrirModalCrearShopProduct(pendingProductCreation.entryIndex, product.id, product.displayName);
}

function abrirModalCrearShopProduct(entryIndex, productId, productName) {
  pendingProductCreation = { entryIndex, productId, productName };
  document.getElementById("form-create-shop-product").reset();
  document.getElementById("sp-product-name").textContent = productName;
  
  const entry = parsedEntries[entryIndex];
  if (entry) {
    document.getElementById("sp-quantity").value = entry.quantity || 1;
  }
  
  $("#modal-create-shop-product").modal("show");
}

$(document).ready(function () {
  poblarModelos();
  
  $("#form-create-product").validate({
    rules: {
      name: { required: true },
      model: { required: true },
    },
    submitHandler: function (form) {
      crearProducto(form);
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

  $("#form-create-shop-product").validate({
    rules: {
      quantity: { required: true, digits: true, min: 1 },
      cost_price: { required: true, number: true, min: 0 },
      sell_price: { required: true, number: true, min: 0 },
      sell_price_for_catalog: { number: true, min: 0 },
    },
    submitHandler: function (form) {
      crearShopProduct(form);
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

function poblarModelos() {
  const $model = document.getElementById("product-model");
  axios.get("/business-gestion/models/").then(function (response) {
    response.data.results.forEach(function (model) {
      const option = new Option(model.name, model.id);
      $model.add(option);
    });
    if ($model.options.length > 1) {
      $model.value = $model.options[1].value;
    }
  });
}

async function crearProducto(form) {
  const formData = new FormData(form);
  load.hidden = false;

  try {
    const response = await axios.post("/business-gestion/products/", formData);
    if (response.status === 201) {
      const newProduct = response.data;
      allProducts.push({
        id: newProduct.id,
        name: newProduct.__str__ || newProduct.name,
        displayName: newProduct.name,
      });

      $("#modal-create-product").modal("hide");
      abrirModalCrearShopProduct(
        pendingProductCreation.entryIndex,
        newProduct.id,
        newProduct.name
      );
    }
  } catch (error) {
    Swal.fire({
      icon: "error",
      title: "Error creando producto",
      text: "No se pudo crear el producto. Intente nuevamente.",
      showConfirmButton: true,
    });
  } finally {
    load.hidden = true;
  }
}

async function crearShopProduct(form) {
  const { entryIndex, productId, productName } = pendingProductCreation;
  const entry = parsedEntries[entryIndex];
  
  if (!entry) {
    Swal.fire({
      icon: "error",
      title: "Error",
      text: "No se pudo identificar la entrada.",
    });
    return;
  }

  const shopId = document.getElementById("shop").value;
  const data = {
    shop: shopId,
    product: productId,
    quantity: document.getElementById("sp-quantity").value,
    cost_price: document.getElementById("sp-cost-price").value,
    sell_price: document.getElementById("sp-sell-price").value,
    sell_price_for_catalog: document.getElementById("sp-catalog-price").value || null,
    extra_info: document.getElementById("sp-extra-info").value || "",
  };

  load.hidden = false;

  try {
    const response = await axios.post(shopProductsUrl, data);
    if (response.status === 201) {
      const newShopProduct = response.data;
      
      const shopProductObj = {
        id: newShopProduct.id,
        currentQuantity: Number(newShopProduct.quantity),
        displayName: productName,
        modelBrand: newShopProduct.model_brand || "",
        sellPrice: newShopProduct.sell_price,
        costPrice: newShopProduct.cost_price,
        productId: productId,
        candidateText: productName,
        normalizedCandidate: normalizeText(productName),
      };
      
      selectedShopProducts.push(shopProductObj);
      selectedShopProducts.sort((a, b) => a.displayName.localeCompare(b.displayName));
      
      entry.chosenMatch = shopProductObj;
      entry.status = "seleccionado_manualmente";
      entry.manuallyCreated = true;
      
      const checkbox = document.querySelector(`.entry-check[data-index="${entryIndex}"]`);
      if (checkbox) {
        checkbox.disabled = true;
        checkbox.checked = false;
      }
      
      const statusCell = document.querySelector(`.entry-status[data-index="${entryIndex}"]`);
      if (statusCell) {
        statusCell.innerHTML = renderStatus(entry);
      }
      
      updateCreateButtonState();
      $("#modal-create-shop-product").modal("hide");
      
      Swal.fire({
        icon: "success",
        title: "Producto agregado a tienda",
        text: `${productName} ha sido agregado correctamente.`,
        showConfirmButton: false,
        timer: 1500,
      });
    }
  } catch (error) {
    Swal.fire({
      icon: "error",
      title: "Error creando shop-product",
      text: "No se pudo agregar el producto a la tienda.",
      showConfirmButton: true,
    });
  } finally {
    load.hidden = true;
  }
}
