const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];

axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

const palletUrl = "/business-gestion/pallets/";
const shopUrl = "/business-gestion/shops/";
const shopProductsApiUrl = "/business-gestion/shop-products/";

let selectedId = null;
let editPallet = false;
let warnedMissingShop = false;
let shopProductsOptions = [];

$(function () {
  $(".select2").select2({ theme: "bootstrap4", width: "100%" });
  $("#shop-products").on("change", renderSelectedShopProductsList);
  $("#shop").on("change", async function () {
    if (!editPallet) {
      return;
    }
    const shopId = this.value;
    if (!shopId) {
      clearShopProductsSelect();
      return;
    }
    await loadShopProductsForShop(shopId, selectedId);
  });
  populateShops();
  initTable();
});

function initTable() {
  $("#tabla-de-Datos").DataTable({
    responsive: true,
    dom: '<"top"l>Bfrtip',
    buttons: [
      {
        text: "Crear",
        className: "btn btn-primary btn-info",
        action: function () {
          editPallet = false;
          selectedId = null;
          resetForm();
          $("#modal-crear-pallets .modal-title").text("Adicionar Pallet");
          $("#modal-crear-pallets").modal("show");
        },
      },
      { extend: "excel", text: "Excel" },
      { extend: "pdf", text: "PDF" },
      { extend: "print", text: "Print" },
    ],
    serverSide: true,
    processing: true,
    ajax: function (data, callback) {
      const selectedShopId = localStorage.getItem("selectedShopId");

      if (!selectedShopId) {
        showMissingShopWarning();
        callback({
          recordsTotal: 0,
          recordsFiltered: 0,
          data: [],
        });
        return;
      }

      hideMissingShopWarning();
      let dir = "";
      if (data.order[0].dir === "desc") {
        dir = "-";
      }

      axios
        .get(palletUrl, {
          params: {
            shop: selectedShopId,
            page_size: data.length,
            page: data.start / data.length + 1,
            search: data.search.value,
            ordering: dir + data.columns[data.order[0].column].data,
          },
        })
        .then((res) => {
          callback({
            recordsTotal: res.data.count,
            recordsFiltered: res.data.count,
            data: res.data.results,
          });
        })
        .catch((error) => {
          alert(error);
        });
    },
    columns: [
      { data: "pallet_label", title: "Pallet" },
      {
        data: "shop_products_count",
        title: "ShopProducts",
        defaultContent: null,
        render: (data, type, row) => {
          const count = data ?? row?.shop_products_count ?? 0;
          if (!count) {
            return "Vacío";
          }
          return count;
        },
      },
      { data: "rack", title: "Rack" },
      { data: "section", title: "Sección" },
      { data: "number", title: "Número" },
      {
        data: "id",
        title: "Acciones",
        orderable: false,
        render: (data, type, row) => {
          return `<div class="btn-group">
            <a href="/pallets/${row.id}/detalle/" class="btn btn-info" title="Ver detalle">
              <i class="fas fa-list"></i>
            </a>
            <button type="button" title="Editar" class="btn bg-olive active" onclick="editPalletById('${row.id}')">
              <i class="fas fa-edit"></i>
            </button>
            <button type="button" title="Eliminar" class="btn bg-olive" onclick="deletePallet('${row.id}','${row.rack}${row.section}${row.number}')">
              <i class="fas fa-trash"></i>
            </button>
          </div>`;
        },
      },
    ],
  });
}

function resetForm() {
  const form = document.getElementById("form-create-pallets");
  form.reset();
  $("#shop").val("").trigger("change");
  clearShopProductsSelect();
  document.getElementById("shop-products-linked-section").style.display =
    "none";
}

function populateShops() {
  const select = document.getElementById("shop");
  const selectedShopId = localStorage.getItem("selectedShopId");
  select.innerHTML = "<option value=''>Seleccione una tienda</option>";

  axios
    .get(shopUrl, { params: { page_size: 1000 } })
    .then((response) => {
      response.data.results.forEach((shop) => {
        const option = new Option(shop.name, shop.id);
        select.add(option);
      });
      if (selectedShopId) {
        $("#shop").val(selectedShopId).trigger("change");
      }
      $("#shop").trigger("change");
    })
    .catch(() => {
      Swal.fire({
        icon: "error",
        title: "No se pudieron cargar las tiendas",
        timer: 1500,
        showConfirmButton: false,
      });
    });
}

function showMissingShopWarning() {
  const warning = document.getElementById("shop-selection-warning");
  if (warning) {
    warning.style.display = "block";
  }
  if (!warnedMissingShop) {
    warnedMissingShop = true;
    Swal.fire({
      icon: "warning",
      title: "Debe seleccionar una tienda",
      text: "Seleccione una tienda en el selector global para listar los pallets.",
      timer: 2000,
      showConfirmButton: false,
    });
  }
}

function hideMissingShopWarning() {
  const warning = document.getElementById("shop-selection-warning");
  if (warning) {
    warning.style.display = "none";
  }
}

function clearShopProductsSelect() {
  shopProductsOptions = [];
  const select = document.getElementById("shop-products");
  select.innerHTML = "";
  $("#shop-products").val([]).trigger("change");
  renderSelectedShopProductsList();
}

async function loadShopProductsForShop(shopId, palletId) {
  clearShopProductsSelect();
  const select = document.getElementById("shop-products");

  try {
    const response = await axios.get(shopProductsApiUrl, {
      params: {
        shop: shopId,
      },
    });

    const rows = response.data?.results || [];
    const selectedValues = [];

    rows.forEach((item) => {
      const optionLabel = `${item.product_name || "Producto"} - ${item.model_brand || "-"} (Cant: ${item.quantity || 0})`;
      const option = new Option(optionLabel, item.id);
      select.add(option);
      if (item.pallet === palletId) {
        selectedValues.push(String(item.id));
      }
    });

    shopProductsOptions = rows;
    $("#shop-products").val(selectedValues).trigger("change");
    renderSelectedShopProductsList();
  } catch (error) {
    Swal.fire({
      icon: "error",
      title: "No se pudieron cargar los shop products",
      timer: 1500,
      showConfirmButton: false,
    });
  }
}

function renderSelectedShopProductsList() {
  const container = document.getElementById("shop-products-selected-list");
  const selectedValues = $("#shop-products").val() || [];

  if (!selectedValues.length) {
    container.innerHTML =
      '<span class="text-muted">Sin shop products seleccionados</span>';
    return;
  }

  const cards = selectedValues
    .map((id) => {
      const item = shopProductsOptions.find(
        (opt) => String(opt.id) === String(id),
      );
      const label = item
        ? `${item.product_name || "Producto"} - ${item.model_brand || "-"} (Cant: ${item.quantity || 0})`
        : `ShopProduct #${id}`;

      return `<span class="badge badge-light border mr-1 mb-1 p-2" style="font-size: 0.85rem;">
        ${label}
        <button type="button" class="btn btn-xs btn-danger ml-2" onclick="removeSelectedShopProduct('${id}')">
          <i class="fas fa-times"></i>
        </button>
      </span>`;
    })
    .join("");

  container.innerHTML = cards;
}

function removeSelectedShopProduct(id) {
  const selectedValues = $("#shop-products").val() || [];
  const filtered = selectedValues.filter(
    (value) => String(value) !== String(id),
  );
  $("#shop-products").val(filtered).trigger("change");
}

async function syncPalletShopProducts(palletId, shopId) {
  const selectedValues = ($("#shop-products").val() || []).map((value) =>
    Number(value),
  );

  const currentLinkedResponse = await axios.get(shopProductsApiUrl, {
    params: {
      shop: shopId,
      pallet: palletId,
    },
  });
  const currentLinked = currentLinkedResponse.data?.results || [];
  const currentLinkedIds = currentLinked.map((item) => item.id);

  const toAssign = selectedValues.filter(
    (id) => !currentLinkedIds.includes(id),
  );
  const toUnassign = currentLinkedIds.filter(
    (id) => !selectedValues.includes(id),
  );

  const assignRequests = toAssign.map((id) =>
    axios.patch(`${shopProductsApiUrl}${id}/`, { pallet: palletId }),
  );
  const unassignRequests = toUnassign.map((id) =>
    axios.patch(`${shopProductsApiUrl}${id}/`, { pallet: null }),
  );

  await Promise.all([...assignRequests, ...unassignRequests]);
}

function editPalletById(id) {
  axios
    .get(`${palletUrl}${id}/`)
    .then(async (response) => {
      const pallet = response.data;
      selectedId = pallet.id;
      editPallet = true;

      document.getElementById("rack").value = pallet.rack;
      document.getElementById("section").value = pallet.section;
      document.getElementById("number").value = pallet.number;
      $("#shop").val(pallet.shop).trigger("change");
      document.getElementById("shop-products-linked-section").style.display =
        "block";

      $("#modal-crear-pallets .modal-title").text(
        `Editar Pallet ${pallet.rack}${pallet.section}${pallet.number}`,
      );
      $("#modal-crear-pallets").modal("show");
    })
    .catch(() => {
      Swal.fire({
        icon: "error",
        title: "No se pudo cargar el pallet",
        timer: 1500,
        showConfirmButton: false,
      });
    });
}

function deletePallet(id, label) {
  Swal.fire({
    title: "¿Eliminar pallet?",
    text: `Se eliminará el pallet ${label}`,
    icon: "warning",
    showCancelButton: true,
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar",
  }).then((result) => {
    if (!result.isConfirmed) {
      return;
    }

    axios
      .delete(`${palletUrl}${id}/`)
      .then(() => {
        Swal.fire({
          icon: "success",
          title: "Pallet eliminado",
          timer: 1200,
          showConfirmButton: false,
        });
        $("#tabla-de-Datos").DataTable().ajax.reload();
      })
      .catch(() => {
        Swal.fire({
          icon: "error",
          title: "No se pudo eliminar",
          timer: 1500,
          showConfirmButton: false,
        });
      });
  });
}

$("#modal-crear-pallets").on("hide.bs.modal", () => {
  editPallet = false;
  selectedId = null;
  resetForm();
});

$("#form-create-pallets").on("submit", function (event) {
  event.preventDefault();

  const payload = {
    shop: document.getElementById("shop").value,
    rack: Number(document.getElementById("rack").value),
    section: document.getElementById("section").value.trim().toUpperCase(),
    number: Number(document.getElementById("number").value),
  };

  if (!payload.shop || !payload.section) {
    Swal.fire({
      icon: "warning",
      title: "Complete los campos requeridos",
      timer: 1500,
      showConfirmButton: false,
    });
    return;
  }

  const request = editPallet
    ? axios.patch(`${palletUrl}${selectedId}/`, payload)
    : axios.post(palletUrl, payload);

  request
    .then(async (response) => {
      const palletId = editPallet ? selectedId : response?.data?.id;
      if (editPallet && palletId) {
        await syncPalletShopProducts(palletId, payload.shop);
      }

      Swal.fire({
        icon: "success",
        title: editPallet ? "Pallet actualizado" : "Pallet creado",
        timer: 1200,
        showConfirmButton: false,
      });
      $("#modal-crear-pallets").modal("hide");
      $("#tabla-de-Datos").DataTable().ajax.reload();
    })
    .catch((error) => {
      let message = "Revise los datos enviados";
      if (error?.response?.data) {
        message = JSON.stringify(error.response.data);
      }
      Swal.fire({
        icon: "error",
        title: "No se pudo guardar",
        text: message,
      });
    });
});
