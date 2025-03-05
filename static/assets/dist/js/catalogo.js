// Variables globales
let currentPage = 1;
let productsPerPage = 12;
let totalProducts = 0; // Cambia esto si deseas mostrar más o menos productos por página
let totalPages = 0; // Variable global para almacenar la cantidad de páginas
let product__model = "";
let searchValue = "";
let shopValue = "";
let orderingValue = "";
let product__model__brand= "";

// Función para cargar productos
function loadProducts(page) {
  currentPage = page;
  const url = "/business-gestion/shop-products/catalog/"; // Asegúrate de que esta URL sea correcta
  const params = {
    page_size: productsPerPage === "all" ? Infinity : productsPerPage, // Ajustar según la selección
    page: page,
    search: searchValue, // Aquí puedes agregar la lógica para manejar la búsqueda si es necesario
    ordering: orderingValue, // Aquí puedes agregar la lógica para manejar el ordenamiento si es necesario
    product__model: product__model,
    product__model__brand:product__model__brand,
    shop: shopValue,
  };

  axios
    .get(url, { params })
    .then((res) => {
      const { count, results } = res.data; // Desestructuramos la respuesta
      totalProducts = count;
      renderProducts(results); // Renderiza los productos

      // Calcular el número total de páginas
      totalPages = Math.ceil(
        totalProducts / (productsPerPage === "all" ? 1 : productsPerPage)
      );

      // Actualizar el conteo de productos mostrados
      const start = (page - 1) * productsPerPage + 1;
      const end = Math.min(start + results.length - 1, count);
      updatePagination(); // Actualiza la paginación

      document.getElementById(
        "product-count"
      ).innerText = `mostrando ${start}-${end} de ${count} productos`;
    })
    .catch((error) => {
      alert("Error al cargar los productos: " + error.message);
    });
}

function renderProducts(products) {
  const productArea = document.querySelector(".shop-products-wrapper .row");
  productArea.innerHTML = ""; // Limpiar productos existentes

  products.forEach((product) => {
    const productHTML = `
        <div class="col-lg-4 col-md-4 col-sm-6 mt-40">
          <div class="single-product-wrap">
            <div class="product-image">
              <a>
                <img src="${product.product.image || '/static_output/assets/dist/img/producto-sin-imagen.jpg'}" alt="${product.product.name}">
              </a>
              ${product.is_new ? '<span class="sticker">New</span>' : ''}
            </div>
            <div class="product_desc">
              <div class="product_desc_info">
                <div class="product-review">
                  <h5 class="manufacturer">
                    <a>${product.product.model.brand.name} ${product.product.model.name}</a>
                  </h5>
                  <div class="rating-box">
                    <ul class="rating">
                      <li><i class="fa fa-star-o"></i></li>
                      <li><i class="fa fa-star-o"></i></li>
                      <li><i class="fa fa-star-o"></i></li>
                      <li><i class="fa fa-star-o"></i></li>
                      <li><i class="fa fa-star-o"></i></li>
                    </ul>
                  </div>
                </div>
                <h4><a class="product_name" href="#">${product.product.name}</a></h4>
                <div class="price-box">
                  <span class="new-price">$${product.sell_price}</span>
                </div>
              </div>
              <div class="add-actions">
                <ul class="add-actions-link">
                  <li><a href="#" title="quick view" class="quick-view-btn" data-toggle="modal" data-target="#exampleModalCenter" onclick="viewProductDetails(${product.id})"><i class="fa fa-eye"></i></a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>`;
    productArea.insertAdjacentHTML("beforeend", productHTML);
  });
}


// Función para actualizar la paginación
function updatePagination() {
  const paginationArea = document.querySelector(".pagination-box");
  paginationArea.innerHTML = ""; // Limpiar paginación existente

  if (currentPage - 1 > 0) {
    paginationArea.insertAdjacentHTML(
      "beforeend",
      `<li><a href="#" class="Previous" onclick="loadProducts(${
        currentPage - 1
      })"><i class="fa fa-chevron-left"></i> Previous</a></li>`
    );
  } else {
    paginationArea.insertAdjacentHTML("beforeend", ``);
  }

  const currentPageItem = `<li class="active"><a href="#">${currentPage}</a></li>`;
  paginationArea.insertAdjacentHTML("beforeend", currentPageItem);

  if (currentPage + 1 <= totalPages) {
    paginationArea.insertAdjacentHTML(
      "beforeend",
      `<li><a href="#" class="Next" onclick="loadProducts(${
        currentPage + 1
      })"> Next <i class="fa fa-chevron-right"></i></a></li>`
    );
  }
}

// Función para ver detalles del producto
function viewProductDetails(productId) {
  // Aquí puedes implementar la lógica para mostrar los detalles del producto en un modal
  console.log(`Ver detalles del producto con ID: ${productId}`);
  showProductDetails(productId);
  // Puedes cargar los detalles del producto y mostrarlos en el modal correspondiente
}

// Cargar productos al iniciar la página
document.addEventListener("DOMContentLoaded", () => {
  loadProducts(currentPage);
  loadModels("");
  loadBrands();
  populateShopsList();
});

function updateProductsPerPage() {
  const selectElement = document.getElementById("products-per-page");
  const selectedValue = selectElement.value;

  // Ajustar la cantidad de productos por página
  productsPerPage =
    selectedValue === "all" ? Infinity : parseInt(selectedValue);

  // Reiniciar a la primera página
  currentPage = 1;

  // Cargar productos de la primera página con el nuevo valor
  loadProducts(currentPage);

  // Mantener el valor seleccionado en el select
  selectElement.value = selectedValue;
}

function loadModels(id) {
  const params = {
    brand: id,
  };
  axios
    .get(`/business-gestion/models/catalog/`, { params })
    .then((res) => {
      const models = res.data.results;
      populateModelsList(models);
    })
    .catch((error) => {
      console.error("Error al cargar los modelos: ", error.message);
    });
}

function populateModelsList(models) {
  const modelList = document.getElementById("model-list");
  modelList.innerHTML = ""; // Limpiar opciones anteriores

  // Opción para mostrar todos los modelos
  const showAllItem = document.createElement("li");
  const showAllLink = document.createElement("a");
  showAllLink.href = "#"; // Prevenir el comportamiento por defecto
  showAllLink.textContent = "Todos";

  // Agregar evento para mostrar todos los productos
  showAllLink.addEventListener("click", (e) => {
    e.preventDefault(); // Prevenir el enlace por defecto
    loadProductsByModel(""); // Cargar todos los productos
  });

  showAllItem.appendChild(showAllLink);
  modelList.appendChild(showAllItem);

  models.forEach((model) => {
    const listItem = document.createElement("li");
    const link = document.createElement("a");
    link.href = "#"; // Prevenir el comportamiento por defecto
    link.textContent = model.name;

    // Agregar evento para filtrar productos por modelo
    link.addEventListener("click", (e) => {
      e.preventDefault(); // Prevenir el enlace por defecto
      loadProductsByModel(model.id); // Cargar productos por el modelo seleccionado
    });

    listItem.appendChild(link);
    modelList.appendChild(listItem);
  });
}

function loadProductsByModel(modelId) {
  const url = "/business-gestion/shop-products/catalog/";
  currentPage = 1;
  product__model = modelId;
  loadProducts(currentPage);
  // updatePagination();
}
function loadProductsByModel(modelId) {
  currentPage = 1;
  product__model = modelId;
  loadProducts(currentPage);
}
function searchProducts() {
  currentPage = 1;
  searchValue = document.getElementById("searchInput").value;
  loadProducts(currentPage);
}

function loadBrands() {
  axios
    .get("/business-gestion/brands/catalog/")
    .then((res) => {
      const brands = res.data.results;
      populateBrandsSelect(brands);
    })
    .catch((error) => {
      console.error("Error al cargar las marcas: ", error.message);
    });
}

function populateBrandsSelect(brands) {
  console.log("✌️brands --->", brands);
  const brandsSelect = document.getElementById("brandsSelect");
  brandsSelect.innerHTML = '<option value="">Seleccione una marca</option>'; // Limpiar opciones anteriores

  brands.forEach((brand) => {
    const option = document.createElement("option");
    option.value = brand.id; // Asignar el ID de la marca como valor
    option.textContent = brand.name; // Asignar el nombre de la marca como texto
    brandsSelect.appendChild(option);
  });

  // Agregar la clase nice-select al select
  brandsSelect.classList.add("nice-select");

  // Agregar evento para cargar modelos al seleccionar una marca
  brandsSelect.addEventListener("change", () => {
    const selectedId = brandsSelect.value; // Obtener el ID seleccionado
    loadModels(selectedId); // Pasar el ID a la función loadModels
    selectBrandInit(selectedId);
  });


}

function selectBrandInit(brandId) {
  product__model__brand = brandId;
  product__model='';
  currentPage = 1;
  loadProducts(currentPage);
}


function populateShopsList() {
  axios
    .get("/business-gestion/shops/catalog/")
    .then((response) => {
      const shops = response.data.results; // Obtener los datos de la respuesta
      console.log("Respuesta de shops:", shops); // Verificar la respuesta

      // Asegurarte de que shops sea un array
      if (Array.isArray(shops)) {
        const shopsList = document.getElementById("shopsList");
        shopsList.innerHTML = ""; // Limpiar la lista anterior

        shops.forEach((shop) => {
          const listItem = document.createElement("li");
          listItem.innerHTML = `
                        <input type="checkbox" name="product-category" id="shop-${shop.id}" class="shop-checkbox">
                        <label for="shop-${shop.id}">${shop.name}</label>
                    `;

          // Agregar evento para manejar la selección de la tienda
          listItem
            .querySelector("input")
            .addEventListener("change", function () {
              handleShopSelection(this); // Llamar a la función con el checkbox actual
            });

          shopsList.appendChild(listItem); // Agregar el elemento a la lista
        });
      } else {
        console.error("Se esperaba un array, pero se recibió:", shops);
      }
    })
    .catch((error) => {
      console.error("Error fetching shops:", error);
    });
}

// Función para manejar la selección de tiendas
function handleShopSelection(selectedCheckbox) {
  const checkboxes = document.querySelectorAll(".shop-checkbox");

  checkboxes.forEach((checkbox) => {
    if (checkbox !== selectedCheckbox) {
      checkbox.checked = false; // Desmarcar otros checkboxes
    }
  });

  // Lógica para manejar la tienda seleccionada
  if (selectedCheckbox.checked) {
    selectShop(selectedCheckbox.id.split("-")[1]); // Llamar al método selectShop con el ID de la tienda
  } else {
    selectShop(null); // Si se deselecciona, pasar null
  }
}

// Método selectShop para manejar la tienda seleccionada
function selectShop(shopId) {
  shopValue = shopId;
  currentPage = 1;
  loadProducts(currentPage);
}

// Función para capturar el valor seleccionado
function captureOrderingValue() {
  // Obtener el elemento select
  const selectElement = document.getElementById("selectOrdering");
  orderingValue = selectElement.value;
  currentPage = 1;
  loadProducts(currentPage);
}
// Función para mostrar los detalles del producto
async function showProductDetails(productId) {
  try {
    // Realizar la petición al endpoint
    const response = await axios.get(
      `/business-gestion/shop-products/${productId}/catalog-shop-product-detail/`
    );
    const product = response.data;

    // Actualizar los elementos de la modal con los datos del producto
    document.getElementById("modalProductImage").src = product.product.image;
    document.getElementById("modalProductName").textContent =
      product.product_name;
    document.getElementById("modalBrandName").textContent =
      product.product.model.brand.name;
    document.getElementById("modalModelName").textContent =
      product.product.model.__str__;
    document.getElementById(
      "modalPrice"
    ).textContent = `$${product.sell_price}`;
    document.getElementById("modalShopName").textContent = product.shop_name;
    document.getElementById("modalDescription").textContent =
      product.product.description || "Sin descripción";

    // Mostrar la modal
    const productModal = new bootstrap.Modal(
      document.getElementById("productDetailModal")
    );
    productModal.show();
  } catch (error) {
    console.error("Error al cargar los detalles del producto:", error);
    // Aquí puedes agregar algún manejo de error, como mostrar una alerta
    alert("Error al cargar los detalles del producto");
  }
}
