const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

const shopProductsUrl = "/business-gestion/shop-products/";
const sellGroupsUrl = "/business-gestion/sell-groups/";
const load = document.getElementById("load");
const parsedResultsBody = document.getElementById("parsed-results-body");
const createButton = document.getElementById("btn-create-sales");
const thresholdInput = document.getElementById("similarityThreshold");
const thresholdValue = document.getElementById("similarityValue");

let parsedEntries = [];
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

  $("#btn-create-sales").on("click", async function () {
    await crearVentas();
  });

  $("#similarityThreshold").on("input", function () {
    thresholdValue.textContent = `${this.value}%`;
  });

  $("#shop").on("change", function () {
    localStorage.setItem("selectedShopId", this.value);
  });

  $(document).on("change", ".manual-match-select", function () {
    const index = Number(this.dataset.index);
    const selectedValue = this.value;
    const entry = parsedEntries[index];

    if (!entry) return;

    entry.originalStatus = entry.originalStatus || entry.status;

    if (selectedValue === "") {
      entry.status = entry.originalStatus;
      entry.chosenMatch = entry.matches && entry.matches.length === 1 ? entry.matches[0] : null;
    } else {
      const match = selectedShopProducts.find((p) => String(p.id) === String(selectedValue));
      if (match) {
        entry.chosenMatch = match;
        entry.status = "seleccionado_manualmente";
      }
    }

    const checkbox = document.querySelector(`.entry-check[data-index="${index}"]`);
    if (checkbox) {
      checkbox.checked = canCreateEntry(entry);
      checkbox.disabled = !canCreateEntry(entry);
    }

    const statusCell = document.querySelector(`.entry-status[data-index="${index}"]`);
    if (statusCell) statusCell.innerHTML = renderStatus(entry);

    updateCreateButtonState();
  });

  $(document).on("change", ".entry-check", function () {
    updateCreateButtonState();
  });
}

function poblarTiendas() {
  const selectedShopId = localStorage.getItem("selectedShopId");
  const shopSelect = document.getElementById("shop");
  shopSelect.innerHTML = "";

  axios
    .get("/business-gestion/shops/")
    .then(function (response) {
      const shops = response.data.results || response.data || [];
      shops.forEach(function (shop) {
        const option = document.createElement("option");
        option.value = shop.id;
        option.textContent = shop.name || shop.__str__ || shop.id;
        if (String(shop.id) === String(selectedShopId)) option.selected = true;
        shopSelect.appendChild(option);
      });

      if (!shopSelect.value && shopSelect.options.length > 0) {
        shopSelect.options[0].selected = true;
      }

      $(shopSelect).trigger("change");
    })
    .catch(function () {
      Swal.fire({ icon: "error", title: "Error", text: "No se pudieron cargar las tiendas." });
    });
}

function showLoader() {
  if (load) load.hidden = false;
}

function hideLoader() {
  if (load) load.hidden = true;
}

async function analizarMensaje() {
  const shopId = document.getElementById("shop").value;
  const message = document.getElementById("messageInput").value || "";

  if (!shopId) {
    Swal.fire({ icon: "warning", title: "Selecciona una tienda", text: "Debes seleccionar una tienda antes de analizar el mensaje." });
    return;
  }

  showLoader();
  createButton.disabled = true;
  parsedEntries = [];

  try {
    selectedShopProducts = (await cargarShopProducts(shopId)).sort((a, b) =>
      a.displayName.localeCompare(b.displayName)
    );

    const lines = message
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    if (lines.length === 0) {
      renderNoResults("El mensaje está vacío");
      return;
    }

    const itemLines = lines;

    const threshold = Number(thresholdInput.value) / 100;

    parsedEntries = itemLines.map((line, index) => {
      const parsed = parseLine(line, index + 1);
      const matches = findMatches(parsed.productText, selectedShopProducts, threshold);

      let status;
      let chosenMatch = null;

      if (matches.length === 0) {
        status = "no_encontrado";
      } else if (matches.length === 1) {
        status = "encontrado";
        chosenMatch = matches[0];
      } else {
        status = "ambiguo";
      }

      return { ...parsed, matches, status, chosenMatch };
    });

    renderParsedResults();
  } catch (error) {
    renderNoResults("Ocurrió un error analizando el mensaje");
    Swal.fire({ icon: "error", title: "Error", text: "No se pudo analizar el mensaje. Intenta nuevamente." });
  } finally {
    hideLoader();
  }
}

function parseLine(line, lineNumber) {
  const regex = /^\s*(\d+)\s*-\s*(.+)\s*$/;
  const match = line.match(regex);
  if (!match) {
    return { lineNumber, rawLine: line, valid: true, quantity: 1, productText: line.trim() };
  }
  return { lineNumber, rawLine: line, valid: true, quantity: Number(match[1]), productText: match[2].trim() };
}

async function cargarShopProducts(shopId) {
  const response = await axios.get(shopProductsUrl, {
    params: { shop: shopId, quantity__gte: 1 },
  });

  const results = response.data.results || [];
  return results.map((item) => ({
    id: item.id,
    displayName: item.__repr__ || item.__str__ || item.product?.name || String(item.id),
    productName: item.product?.name || "",
    modelBrand: item.product?.model_brand || "",
    stock: item.quantity,
    sellPrice: item.sell_price,
    normalizedName: normalizeText(item.__repr__ || item.product?.name || ""),
  }));
}

function findMatches(inputText, candidates, threshold) {
  const normalizedInput = normalizeText(inputText);
  const scored = candidates
    .map((candidate) => ({
      ...candidate,
      score: scoreSimilarity(normalizedInput, candidate.normalizedName),
    }))
    .filter((candidate) => candidate.score >= threshold)
    .sort((a, b) => b.score - a.score)
    .slice(0, 3);

  if (scored.length <= 1) return scored;

  const bestScore = scored[0].score;
  return scored.filter((item) => bestScore - item.score <= 0.08);
}

function scoreSimilarity(a, b) {
  if (!a || !b) return 0;
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
  if (maxLen === 0) return 1;
  return 1 - distance / maxLen;
}

function levenshteinDistance(a, b) {
  const matrix = Array.from({ length: a.length + 1 }, () => Array(b.length + 1).fill(0));
  for (let i = 0; i <= a.length; i++) matrix[i][0] = i;
  for (let j = 0; j <= b.length; j++) matrix[0][j] = j;
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
  if (!aTokens.length || !bTokens.length) return 0;
  let matches = 0;
  for (const token of aTokens) {
    if (bTokens.some((bt) => bt === token || bt.includes(token) || token.includes(bt))) {
      matches++;
    }
  }
  return matches / aTokens.length;
}

function renderParsedResults() {
  if (!parsedEntries.length) {
    renderNoResults("Sin resultados todavía");
    return;
  }

  const rows = parsedEntries
    .map((entry, index) => {
      const canCreate = canCreateEntry(entry);
      const stockInfo = entry.chosenMatch
        ? `<br><small class="text-muted">Stock: ${entry.chosenMatch.stock} | Precio: $${entry.chosenMatch.sellPrice}</small>`
        : "";
      return `
        <tr>
          <td class="text-center">
            <input type="checkbox" class="entry-check" data-index="${index}"
              ${canCreate ? "" : "disabled"}
              ${canCreate ? "checked" : ""}>
          </td>
          <td>${escapeHtml(String(entry.quantity))}</td>
          <td>${escapeHtml(entry.productText)}</td>
          <td>
            ${renderMatches(entry)}
            ${stockInfo}
          </td>
          <td class="entry-status" data-index="${index}">${renderStatus(entry)}</td>
        </tr>`;
    })
    .join("");

  parsedResultsBody.innerHTML = rows;
  initializeManualSelects();
  updateCreateButtonState();
}

function renderMatches(entry) {
  if (entry.status === "no_encontrado") {
    const options = selectedShopProducts
      .map((p) => `<option value="${p.id}">${escapeHtml(p.displayName)}</option>`)
      .join("");
    return `
      <select class="form-control form-control-sm manual-match-select" data-index="${parsedEntries.indexOf(entry)}">
        <option value="">Sin coincidencia - seleccionar manualmente</option>
        ${options}
      </select>`;
  }

  if (entry.status === "ambiguo") {
    const options = entry.matches
      .map((m) => `<option value="${m.id}">${escapeHtml(m.displayName)} (${Math.round(m.score * 100)}%)</option>`)
      .join("");
    const allOptions = selectedShopProducts
      .map((p) => `<option value="${p.id}">${escapeHtml(p.displayName)}</option>`)
      .join("");
    return `
      <select class="form-control form-control-sm manual-match-select" data-index="${parsedEntries.indexOf(entry)}">
        <option value="">Múltiples coincidencias - elige una</option>
        ${options}
        <optgroup label="Todos los productos">${allOptions}</optgroup>
      </select>`;
  }

  return entry.matches
    .map((match) => `${escapeHtml(match.displayName)} - ${Math.round(match.score * 100)}%`)
    .join("<br>");
}

function renderStatus(entry) {
  if (entry.status === "encontrado") return '<span class="badge badge-success">Encontrado</span>';
  if (entry.status === "seleccionado_manualmente") return '<span class="badge badge-info">Seleccionado</span>';
  if (entry.status === "ambiguo") return '<span class="badge badge-warning">Ambiguo</span>';
  if (entry.status === "no_encontrado") return '<span class="badge badge-danger">No encontrado</span>';
  return '<span class="badge badge-secondary">Formato inválido</span>';
}

function renderNoResults(message) {
  parsedResultsBody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">${escapeHtml(message)}</td></tr>`;
  createButton.disabled = true;
}

function canCreateEntry(entry) {
  return ["encontrado", "seleccionado_manualmente"].includes(entry.status) && Boolean(entry.chosenMatch);
}

function initializeManualSelects() {
  $(".manual-match-select").select2({ theme: "bootstrap4", width: "100%", placeholder: "Selecciona un producto" });
}

function updateCreateButtonState() {
  const checkedEntries = Array.from(document.querySelectorAll(".entry-check:checked"));
  createButton.disabled = checkedEntries.length === 0;
}

async function crearVentas() {
  if (createButton.disabled) {
    return;
  }

  const selectedIndexes = Array.from(document.querySelectorAll(".entry-check:checked")).map(
    (cb) => Number(cb.dataset.index)
  );

  if (!selectedIndexes.length) {
    Swal.fire({ icon: "warning", title: "Sin selección", text: "No hay productos seleccionados para vender." });
    return;
  }

  const discount = parseInt(document.getElementById("discount").value) || 0;
  const paymentMethod = document.getElementById("payment_method").value;
  const manualExtraInfo = document.getElementById("extra_info").value || "";
  const clientName = (document.getElementById("client").value || "").trim();
  const sellerId = localStorage.getItem("id");

  if (!clientName) {
    Swal.fire({
      icon: "warning",
      title: "Cliente obligatorio",
      text: "Debes escribir el nombre del cliente para crear la venta.",
    });
    return;
  }

  const composedExtraInfo = `Cliente: ${clientName}${manualExtraInfo ? ` | Nota: ${manualExtraInfo}` : ""}`;

  const sells = selectedIndexes
    .map((index) => parsedEntries[index])
    .filter((entry) => entry && entry.chosenMatch)
    .map((entry) => ({
      shop_product: entry.chosenMatch.id,
      quantity: Number(entry.quantity),
      extra_info: composedExtraInfo,
    }));

  if (!sells.length) {
    Swal.fire({ icon: "warning", title: "Sin ventas válidas", text: "No hay ventas válidas para crear." });
    return;
  }

  // Validar stock
  for (const sell of sells) {
    const shopProduct = selectedShopProducts.find((p) => p.id === sell.shop_product);
    if (shopProduct && sell.quantity > shopProduct.stock) {
      Swal.fire({
        icon: "error",
        title: "Stock insuficiente",
        text: `El producto "${shopProduct.displayName}" tiene stock ${shopProduct.stock}, pero se intentan vender ${sell.quantity}.`,
      });
      return;
    }
  }

  const totalItems = sells.reduce((sum, s) => sum + s.quantity, 0);
  const confirm = await Swal.fire({
    icon: "question",
    title: "Confirmar venta",
    text: `Se crearán ${sells.length} líneas de venta (${totalItems} unidades en total).`,
    showCancelButton: true,
    confirmButtonText: "Sí, crear venta",
    cancelButtonText: "Cancelar",
  });

  if (!confirm.isConfirmed) return;

  createButton.disabled = true;
  showLoader();

  const payload = {
    discount,
    extra_info: composedExtraInfo,
    payment_method: paymentMethod,
    seller: sellerId,
    sells,
  };

  try {
    const response = await axios.post(sellGroupsUrl, payload);
    hideLoader();

    const comprobanteText = buildComprobanteText({
      saleId: response.data?.id,
      sells,
      clientName,
      paymentMethod,
      discount,
      extraInfo: composedExtraInfo,
    });
    const comprobanteHtml = buildComprobanteHtml(comprobanteText);

    const result = await Swal.fire({
      icon: "success",
      title: "Venta creada",
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
          text: "El comprobante se copió al portapapeles.",
        });
      } else {
        await Swal.fire({
          icon: "error",
          title: "No se pudo copiar",
          text: "No fue posible copiar el comprobante automáticamente.",
        });
      }
    }

    // Reset
    document.getElementById("form-parse-message").reset();
    parsedEntries = [];
    renderNoResults("Sin resultados todavía");
    document.getElementById("discount").value = 0;
    document.getElementById("extra_info").value = "";
    document.getElementById("client").value = "";
    thresholdValue.textContent = `${thresholdInput.value}%`;
  } catch (error) {
    hideLoader();
    const detail = error.response?.data ? JSON.stringify(error.response.data) : error.message;
    Swal.fire({ icon: "error", title: "Error al crear venta", text: detail });
  } finally {
    updateCreateButtonState();
    hideLoader();
  }
}

function buildComprobanteText({ saleId, sells, clientName, paymentMethod, discount, extraInfo }) {
  const paymentMethodName = paymentMethod === "Z" ? "Zelle" : "USD";

  const grossTotal = sells.reduce((acc, sell) => {
    const sp = selectedShopProducts.find((p) => p.id === sell.shop_product);
    return acc + Number(sp?.sellPrice || 0) * sell.quantity;
  }, 0);
  const netTotal = Math.max(grossTotal - Number(discount || 0), 0);
  const dateStr = new Date().toLocaleString("es-VE");

  const productLines = sells
    .map((sell, index) => {
      const sp = selectedShopProducts.find((p) => p.id === sell.shop_product);
      const name = sp ? sp.displayName : String(sell.shop_product);
      const unitPrice = Number(sp?.sellPrice || 0);
      const subtotal = unitPrice * sell.quantity;
      return [
        `${index + 1}. ${name}`,
        `   Cantidad: ${sell.quantity}`,
        `   Precio: $${unitPrice.toFixed(2)}`,
        `   Subtotal: $${subtotal.toFixed(2)}`,
      ].join("\n");
    })
    .join("\n\n");

  const lines = [
    "COMPROBANTE DE VENTA",
    `Nro: ${String(saleId || "N/A")}`,
    `Fecha: ${dateStr}`,
    `Cliente: ${clientName}`,
    `Metodo de pago: ${paymentMethodName}`,
    "------------------------------",
    "PRODUCTOS:",
    productLines,
    "------------------------------",
    `Subtotal: $${grossTotal.toFixed(2)}`,
    `Descuento: $${Number(discount || 0).toFixed(2)}`,
    `Total: $${netTotal.toFixed(2)}`,
    `Notas: ${extraInfo || ""}`,
  ];

  return lines.join("\n");
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
