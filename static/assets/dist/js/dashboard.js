const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];
  axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

// url del endpoint principal
const url = "/business-gestion/dashboard/shop-product-investment/";
$(document).ready(function () {
  // Llama a la función para ejecutar la solicitud
smallboxdata();
// Llama a la función para ejecutar la solicitud
smallboxdataLastMonth();
// Llama a la función para ejecutar la solicitud
smallboxdataCurrentMonth();
});

function smallboxdata() {
    axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
    axios.post(url)
        .then(response => {
            // Obtener el valor de inversiones de la respuesta
            const investmentValue = response.data.investments;

            // Modificar el contenido del small-box con el valor de la inversión
            const smallBox = document.getElementById('inversion');
            if (smallBox) {
                smallBox.textContent = investmentValue+"$";
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}


function smallboxdataLastMonth() {
    // Obtener la fecha actual
    const today = new Date();
    
    // Calcular el primer día del mes actual
    const firstDayOfCurrentMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    
    // Calcular el último día del mes anterior
    const lastDayOfLastMonth = new Date(firstDayOfCurrentMonth - 1);
    
    // Calcular el primer día del mes anterior
    const firstDayOfLastMonth = new Date(lastDayOfLastMonth.getFullYear(), lastDayOfLastMonth.getMonth(), 1);
    
    // Formatear las fechas a YYYY-MM-DD
    const startDate = firstDayOfLastMonth.toISOString().split('T')[0];
    const endDate = lastDayOfLastMonth.toISOString().split('T')[0];

    // Parámetros para la solicitud
    const params = {
        "updated_timestamp__gte": startDate,
        "updated_timestamp__lte": endDate
    };

    axios.post('/business-gestion/dashboard/shop-product-investment/', params)
        .then(response => {
            // Obtener el valor de inversiones de la respuesta
            const investmentValue = response.data.investments;

            // Modificar el contenido del small-box con el valor de la inversión
            const smallBox = document.getElementById('inversionxmes');
            if (smallBox) {
                smallBox.textContent = investmentValue+"$";
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

function smallboxdataCurrentMonth() {
    // Obtener la fecha actual
    const today = new Date();
    
    // Calcular el primer día del mes actual
    const firstDayOfCurrentMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    
    // Calcular el último día del mes actual
    const lastDayOfCurrentMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    
    // Formatear las fechas a YYYY-MM-DD
    const startDate = firstDayOfCurrentMonth.toISOString().split('T')[0];
    const endDate = lastDayOfCurrentMonth.toISOString().split('T')[0];

    // Parámetros para la solicitud
    const params = {
        "updated_timestamp__gte": startDate,
        "updated_timestamp__lte": endDate
    };

    axios.post('/business-gestion/dashboard/shop-product-investment/', params)
        .then(response => {
            // Obtener el valor de inversiones de la respuesta
            const investmentValue = response.data.investments;

            // Modificar el contenido del small-box con el valor de la inversión
            const smallBox = document.getElementById('inversioncurrentmes');
            if (smallBox) {
                smallBox.textContent = investmentValue + "$";
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

// Llama a la función para ejecutar la solicitud
smallboxdataCurrentMonth();





