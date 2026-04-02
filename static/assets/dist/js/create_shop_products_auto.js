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
    const selectedMatchIndex = selectedValue === "" ? null : Number(selectedValue);
    const entry = parsedEntries[index];

    if (!entry) {
      return;
    }

    const candidateSource = getManualSelectionCandidates(entry);
    entry.originalStatus = entry.originalStatus || entry.status;

    if (selectedMatchIndex === null || Number.isNaN(selectedMatchIndex)) {
      entry.chosenMatch = null;
      entry.status = entry.originalStatus;
    } else {
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
    selectedShopProducts = await cargarShopProducts(shopId);

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
    const options = [
      '<option value="">Selecciona manualmente un producto</option>',
      ...selectedShopProducts
        .slice()
        .sort((a, b) => a.displayName.localeCompare(b.displayName))
        .map(
          (match, index) =>
            `<option value="${index}">${escapeHtml(match.displayName)} (${escapeHtml(
              match.modelBrand
            )})</option>`
        ),
    ].join("");

    return `
      <div>
        <div class="text-danger small mb-1">Sin coincidencias automaticas</div>
        <select class="form-control form-control-sm manual-match-select" data-index="${parsedEntries.indexOf(
          entry
        )}">
          ${options}
        </select>
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
        extra_log_info: globalExtraInfo,
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
