const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

const shopProductsUrl = "/business-gestion/shop-products/";
const moveBatchUrl = "/business-gestion/shop-products/move-to-another-shop-batch/";
const load = document.getElementById("load");
const parsedResultsList = document.getElementById("parsed-results-list");
const moveButton = document.getElementById("btn-create-movements");
const thresholdInput = document.getElementById("similarityThreshold");
const thresholdValue = document.getElementById("similarityValue");
const originShopSelect = document.getElementById("originShop");
const destinationShopSelect = document.getElementById("destinationShop");

let parsedEntries = [];
let sourceShopProducts = [];
let allShops = [];

$(function () {
  bindEvents();
  poblarTiendas();
});

function bindEvents() {
  $("#form-parse-message").on("submit", async function (event) {
    event.preventDefault();
    await analizarMensaje();
  });

  $("#btn-create-movements").on("click", async function () {
    await crearMovimientos();
  });

  $("#similarityThreshold").on("input", function () {
    thresholdValue.textContent = `${this.value}%`;
  });

  $("#originShop").on("change", async function () {
    repoblarTiendasDestino();
    parsedEntries = [];
    renderNoResults("Cambia de tienda y analiza nuevamente");
    await cargarProductosOrigen();
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

    const statusWrap = document.querySelector(`.entry-status[data-index="${index}"]`);
    if (statusWrap) {
      statusWrap.innerHTML = renderStatus(entry);
    }

    updateMoveButtonState();
  });

  $(document).on("change", ".entry-check", function () {
    updateMoveButtonState();
  });
}

async function poblarTiendas() {
  try {
    const selectedShopId = localStorage.getItem("selectedShopId");
    const response = await axios.get("/business-gestion/shops/");
    allShops = response.data.results || [];

    originShopSelect.innerHTML = "";
    allShops.forEach((shop) => {
      const isSelected = selectedShopId && Number(shop.id) === Number(selectedShopId);
      const option = new Option(shop.name, shop.id, isSelected, isSelected);
      originShopSelect.add(option);
    });

    if (!originShopSelect.value && originShopSelect.options.length > 0) {
      originShopSelect.value = originShopSelect.options[0].value;
    }

    $(originShopSelect).trigger("change.select2");
    repoblarTiendasDestino();
    await cargarProductosOrigen();
  } catch (error) {
    Swal.fire({
      icon: "error",
      title: "Error",
      text: "No se pudieron cargar las tiendas.",
    });
  }
}

function repoblarTiendasDestino() {
  const originShopId = Number(originShopSelect.value);
  destinationShopSelect.innerHTML = "";

  allShops
    .filter((shop) => Number(shop.id) !== originShopId)
    .forEach((shop, index) => {
      const option = new Option(shop.name, shop.id, index === 0, index === 0);
      destinationShopSelect.add(option);
    });

  $(destinationShopSelect).trigger("change.select2");
}

async function cargarProductosOrigen() {
  const shopId = originShopSelect.value;
  if (!shopId) {
    sourceShopProducts = [];
    return;
  }

  sourceShopProducts = (await cargarShopProducts(shopId)).sort((a, b) =>
    a.displayName.localeCompare(b.displayName)
  );
}

async function analizarMensaje() {
  const originShopId = originShopSelect.value;
  const destinationShopId = destinationShopSelect.value;
  const message = document.getElementById("messageInput").value || "";

  if (!originShopId || !destinationShopId) {
    Swal.fire({
      icon: "warning",
      title: "Selecciona tiendas",
      text: "Debes seleccionar tienda origen y tienda destino.",
    });
    return;
  }

  load.hidden = false;
  moveButton.disabled = true;
  parsedEntries = [];

  try {
    await cargarProductosOrigen();

    const lines = message
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    if (lines.length === 0) {
      renderNoResults("No hay lineas para procesar");
      return;
    }

    const threshold = Number(thresholdInput.value) / 100;

    parsedEntries = lines.map((line, index) => {
      const parsedLine = parseLine(line, index + 1);
      if (!parsedLine.valid) {
        return {
          ...parsedLine,
          status: "formato_invalido",
          matches: [],
          chosenMatch: null,
        };
      }

      const matches = findMatches(parsedLine.productText, sourceShopProducts, threshold);
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
      candidateText,
      normalizedCandidate: normalizeText(candidateText),
    };
  });
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

  const rows = parsedEntries.map((entry, index) => {
    const canMove = canMoveEntry(entry);
    const statusHtml = renderStatus(entry);
    const matchesHtml = renderMatches(entry);

    return `
      <div class="entry-card">
        <div class="entry-head">
          <label class="m-0" style="font-weight: 600;">
            <input type="checkbox" class="entry-check mr-2" data-index="${index}" ${canMove ? "checked" : "disabled"}>
            Mover
          </label>
          <div class="entry-status" data-index="${index}">${statusHtml}</div>
        </div>
        <div class="entry-product">${escapeHtml(entry.productText)}</div>
        <div class="entry-sub">Cantidad solicitada: ${entry.quantity || "-"}</div>
        ${renderCurrentStock(entry)}
        ${matchesHtml}
      </div>
    `;
  });

  parsedResultsList.innerHTML = rows.join("");
  initializeManualSelects();
  updateMoveButtonState();
}

function renderMatches(entry) {
  if (entry.status === "no_encontrado") {
    const entryIndex = parsedEntries.indexOf(entry);

    const options = [
      '<option value="">Selecciona un shop-product manualmente</option>',
      ...sourceShopProducts.map(
        (match, index) =>
          `<option value="${index}">${escapeHtml(match.displayName)} (${escapeHtml(
            match.modelBrand
          )}) | Stock: ${escapeHtml(match.currentQuantity)}</option>`
      ),
    ].join("");

    return `
      <div class="text-danger small mb-2">Sin coincidencias automáticas</div>
      <select class="form-control form-control-sm manual-match-select" data-index="${entryIndex}">
        ${options}
      </select>
    `;
  }

  if (entry.status === "ambiguo") {
    const options = [
      '<option value="">Selecciona una coincidencia</option>',
      ...entry.matches.map(
        (match, index) =>
          `<option value="${index}">${escapeHtml(match.displayName)} (${escapeHtml(
            match.modelBrand
          )}) - ${Math.round(match.score * 100)}% | Stock: ${escapeHtml(match.currentQuantity)}</option>`
      ),
    ].join("");

    return `
      <select class="form-control form-control-sm manual-match-select" data-index="${parsedEntries.indexOf(
        entry
      )}">
        ${options}
      </select>
    `;
  }

  return entry.matches
    .map(
      (match) =>
        `<div class="small">Coincide con: ${escapeHtml(match.displayName)} (${escapeHtml(
          match.modelBrand
        )}) - ${Math.round(match.score * 100)}% | Stock: ${escapeHtml(match.currentQuantity)}</div>`
    )
    .join("");
}

function renderCurrentStock(entry) {
  const stock = entry?.chosenMatch?.currentQuantity;
  if (typeof stock !== "number") {
    return "";
  }

  return `<div class="entry-sub">Stock actual: ${escapeHtml(stock)}</div>`;
}

function renderStatus(entry) {
  if (entry.status === "encontrado") {
    return '<span class="badge badge-success">Encontrado</span>';
  }
  if (entry.status === "seleccionado_manualmente") {
    return '<span class="badge badge-info">Manual</span>';
  }
  if (entry.status === "ambiguo") {
    return '<span class="badge badge-warning">Ambiguo</span>';
  }
  if (entry.status === "no_encontrado") {
    return '<span class="badge badge-danger">No encontrado</span>';
  }
  return '<span class="badge badge-secondary">Formato invalido</span>';
}

function renderNoResults(message) {
  parsedResultsList.innerHTML = `<div class="text-center text-muted">${escapeHtml(message)}</div>`;
  moveButton.disabled = true;
}

function canMoveEntry(entry) {
  return ["encontrado", "seleccionado_manualmente"].includes(entry.status) && Boolean(entry.chosenMatch);
}

function getManualSelectionCandidates(entry) {
  if (!entry) {
    return [];
  }

  if (entry.originalStatus === "no_encontrado" || entry.status === "no_encontrado") {
    return sourceShopProducts;
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

function updateMoveButtonState() {
  const checkedEntries = Array.from(document.querySelectorAll(".entry-check:checked"));
  moveButton.disabled = checkedEntries.length === 0;
}

async function crearMovimientos() {
  const selectedIndexes = Array.from(document.querySelectorAll(".entry-check:checked")).map(
    (checkbox) => Number(checkbox.dataset.index)
  );

  if (!selectedIndexes.length) {
    Swal.fire({
      icon: "warning",
      title: "Sin filas seleccionadas",
      text: "Selecciona al menos una fila encontrada para mover productos.",
    });
    return;
  }

  const destinationShopId = destinationShopSelect.value;
  if (!destinationShopId) {
    Swal.fire({
      icon: "warning",
      title: "Sin tienda destino",
      text: "Debes seleccionar una tienda destino.",
    });
    return;
  }

  const payloadProducts = selectedIndexes
    .map((index) => parsedEntries[index])
    .filter((entry) => entry && entry.chosenMatch)
    .map((entry) => ({
      shop_product: entry.chosenMatch.id,
      quantity: Number(entry.quantity),
    }));

  if (!payloadProducts.length) {
    Swal.fire({
      icon: "warning",
      title: "Sin filas válidas",
      text: "No hay movimientos válidos para enviar.",
    });
    return;
  }

  const confirm = await Swal.fire({
    icon: "question",
    title: "Confirmar movimiento",
    text: `Se moverán ${payloadProducts.length} productos a la tienda destino.`,
    showCancelButton: true,
    confirmButtonText: "Sí, mover",
    cancelButtonText: "Cancelar",
  });

  if (!confirm.isConfirmed) {
    return;
  }

  load.hidden = false;

  try {
    await axios.post(moveBatchUrl, {
      shop: Number(destinationShopId),
      shop_products: payloadProducts,
    });

    const receiptText = buildMovementReceiptText(selectedIndexes, payloadProducts);
    load.hidden = true;
    await showMovementReceiptModal(receiptText, payloadProducts.length);
  } catch (error) {
    Swal.fire({
      icon: "error",
      title: "Error procesando movimientos",
      text: "No se pudieron ejecutar los movimientos. Revisa cantidades y vuelve a intentar.",
    });
  } finally {
    load.hidden = true;
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.innerText = text;
  return div.innerHTML;
}

function formatDateTime(dateObj) {
  return new Intl.DateTimeFormat("es-DO", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(dateObj);
}

function getSelectedText(selectEl) {
  if (!selectEl) {
    return "-";
  }
  const option = selectEl.options[selectEl.selectedIndex];
  return option ? option.text : "-";
}

function buildMovementReceiptText(selectedIndexes, payloadProducts) {
  const now = new Date();
  const originShopName = getSelectedText(originShopSelect);
  const destinationShopName = getSelectedText(destinationShopSelect);

  const detailLines = selectedIndexes
    .map((index) => parsedEntries[index])
    .filter((entry) => entry && entry.chosenMatch)
    .map((entry) => {
      const productName = entry.chosenMatch.displayName || entry.productText;
      return `- ${entry.quantity} x ${productName}`;
    });

  const totalUnits = payloadProducts.reduce((acc, item) => acc + Number(item.quantity || 0), 0);

  return [
    "COMPROBANTE DE MOVIMIENTO ENTRE TIENDAS",
    `Fecha: ${formatDateTime(now)}`,
    `Origen: ${originShopName}`,
    `Destino: ${destinationShopName}`,
    "",
    "Detalle:",
    ...detailLines,
    "",
    `Lineas: ${payloadProducts.length}`,
    `Unidades totales: ${totalUnits}`,
  ].join("\n");
}

async function copyTextToClipboard(text) {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
    return;
  }

  const helper = document.createElement("textarea");
  helper.value = text;
  helper.style.position = "fixed";
  helper.style.opacity = "0";
  document.body.appendChild(helper);
  helper.focus();
  helper.select();
  document.execCommand("copy");
  document.body.removeChild(helper);
}

async function showMovementReceiptModal(receiptText, movementCount) {
  const receiptHtml = `
    <p class="mb-2">Se procesaron ${movementCount} movimientos correctamente.</p>
    <textarea id="movement-receipt-text" class="swal2-textarea" style="height:220px; width:100%; margin:0;"></textarea>
    <small class="text-muted d-block mt-2">Puedes copiar este comprobante para compartirlo en tu grupo de trabajo.</small>
  `;

  const result = await Swal.fire({
    icon: "success",
    title: "Movimientos realizados",
    html: receiptHtml,
    showCancelButton: true,
    confirmButtonText: "Copiar comprobante",
    cancelButtonText: "Cerrar",
    didOpen: () => {
      const receiptInput = document.getElementById("movement-receipt-text");
      if (receiptInput) {
        receiptInput.value = receiptText;
      }
    },
    preConfirm: async () => {
      try {
        await copyTextToClipboard(receiptText);
      } catch (error) {
        Swal.showValidationMessage("No se pudo copiar el comprobante.");
      }
    },
  });

  if (result.isConfirmed) {
    Swal.fire({
      icon: "success",
      title: "Comprobante copiado",
      timer: 1400,
      showConfirmButton: false,
    });
  }
}
