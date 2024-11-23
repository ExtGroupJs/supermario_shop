// Variables globales
let currentPage = 1;
const productsPerPage = 12; // Cambia esto si deseas mostrar más o menos productos por página

// Función para cargar productos
function loadProducts(page) {
    axios.get(`/business-gestion/shop-products/?page=${page}`)
        .then(response => {
            const { results, next, previous } = response.data;
            renderProducts(results);
            updatePagination(next, previous);
        })
        .catch(error => {
            console.error("Error al cargar los productos:", error);
            alert("Error al cargar los productos. Por favor, intenta de nuevo más tarde.");
        });
}

// Función para renderizar productos en la interfaz
function renderProducts(products) {
    const productArea = document.querySelector('.shop-products-wrapper .row');
    productArea.innerHTML = ''; // Limpiar productos existentes

    products.forEach(product => {
console.log('✌️product --->', product);
      
        const productHTML = `
            <div class="col-lg-4 col-md-4 col-sm-6 mt-40">
                <div class="single-product-wrap">
                    <div class="product-image">
                        <a href="single-product.html">
                            <img src="${product.product.image}" alt="${product.product.name}">
                        </a>
                        <span class="sticker">New</span>
                    </div>
                    <div class="product_desc">
                        <div class="product_desc_info">
                            <div class="product-review">
                                <h5 class="manufacturer">
                                    <a href="product-details.html">${product.product.model.brand.name} ${product.product.model.name}</a>
                                </h5>
                                <div class="rating-box">
                                    <ul class="rating">
                                        <li><i class="fa fa-star-o"></i></li>
                                        <li><i class="fa fa-star-o"></i></li>
                                        <li><i class="fa fa-star-o"></i></li>
                                        <li class="no-star"><i class="fa fa-star-o"></i></li>
                                        <li class="no-star"><i class="fa fa-star-o"></i></li>
                                    </ul>
                                </div>
                            </div>
                            <h4><a class="product_name" href="single-product.html">${product.product.name}</a></h4>
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
        productArea.insertAdjacentHTML('beforeend', productHTML);
    });
}

// Función para actualizar la paginación
function updatePagination(next, previous) {
    const paginationArea = document.querySelector('.pagination-box');
    paginationArea.innerHTML = ''; // Limpiar paginación existente

    if (previous) {
        paginationArea.insertAdjacentHTML('beforeend', `<li><a href="#" class="Previous" onclick="loadProducts(${currentPage - 1})"><i class="fa fa-chevron-left"></i> Previous</a></li>`);
    }

    const currentPageItem = `<li class="active"><a href="#">${currentPage}</a></li>`;
    paginationArea.insertAdjacentHTML('beforeend', currentPageItem);

    if (next) {
        paginationArea.insertAdjacentHTML('beforeend', `<li><a href="#" class="Next" onclick="loadProducts(${currentPage + 1})"> Next <i class="fa fa-chevron-right"></i></a></li>`);
    }
}

// Función para ver detalles del producto
function viewProductDetails(productId) {
    // Aquí puedes implementar la lógica para mostrar los detalles del producto en un modal
    console.log(`Ver detalles del producto con ID: ${productId}`);
    // Puedes cargar los detalles del producto y mostrarlos en el modal correspondiente
}

// Cargar productos al iniciar la página
document.addEventListener('DOMContentLoaded', () => {
    loadProducts(currentPage);
});
