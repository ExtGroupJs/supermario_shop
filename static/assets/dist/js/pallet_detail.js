const palletApiUrl = "/business-gestion/pallets/";
const shopProductsApiUrl = "/business-gestion/shop-products/";

$(function () {
  const palletId = document.getElementById("palletId")?.value;
  if (!palletId) {
    return;
  }

  loadPalletHeader(palletId);
  initShopProductsTable(palletId);
});

function loadPalletHeader(palletId) {
  axios
    .get(`${palletApiUrl}${palletId}/`)
    .then((response) => {
      const pallet = response.data;
      document.getElementById("pallet-title").innerText =
        `Pallet ${pallet.rack}${pallet.section}${pallet.number}`;
      document.getElementById("pallet-subtitle").innerText =
        `Tienda: ${pallet.shop_name || "-"}`;
    })
    .catch(() => {
      document.getElementById("pallet-title").innerText =
        "Pallet no encontrado";
      document.getElementById("pallet-subtitle").innerText =
        "No se pudo cargar la información del pallet.";
    });
}

function initShopProductsTable(palletId) {
  $("#tabla-shop-products").DataTable({
    responsive: true,
    dom: '<"top"l>Bfrtip',
    buttons: [
      { extend: "excel", text: "Excel" },
      { extend: "pdf", text: "PDF" },
      { extend: "print", text: "Print" },
    ],
    serverSide: true,
    processing: true,
    ajax: function (data, callback) {
      let dir = "";
      if (data.order[0].dir === "desc") {
        dir = "-";
      }

      axios
        .get(shopProductsApiUrl, {
          params: {
            pallet: palletId,
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
        .catch(() => {
          callback({
            recordsTotal: 0,
            recordsFiltered: 0,
            data: [],
          });
        });
    },
    columns: [
      { data: "product_name", title: "Producto" },
      { data: "model_brand", title: "Marca / Modelo" },
      { data: "shop_name", title: "Tienda" },
      { data: "quantity", title: "Cantidad" },
      { data: "sell_price", title: "Precio Venta" },
      { data: "wholesale_price", title: "Precio Mayor" },
    ],
  });
}
