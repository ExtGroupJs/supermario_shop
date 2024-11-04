const csrfToken = document.cookie
  .split(";")
  .find((c) => c.trim().startsWith("csrftoken="))
  ?.split("=")[1];
  axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

// url del endpoint principal
// const url = "/business-gestion/dashboard/shop-product-investment/";
$(document).ready(function () {
  
smallboxdataInvestment();
smallboxdataInvestmentLastMonth();
smallboxdataInvestmentCurrentMonth();
smallboxdataSellCurrentWeek();
smallboxdataSellCurrentMonth();
smallboxdataSellProfits();
smallboxdataSellProfitsCurrentMonth();
smallboxdataSellProfitsLastMonth();
smallboxdataSellProfitsCurrentWeek(),
smallboxdataSellProfitsLastWeek()
});

function smallboxdataInvestment() {
    axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
    axios.post("/business-gestion/dashboard/shop-product-investment/")
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


function smallboxdataInvestmentLastMonth() {
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

function smallboxdataInvestmentCurrentMonth() {
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

function smallboxdataSellCurrentWeek() {
    // Obtener la fecha actual
    const today = new Date();
    
    // Calcular el primer día de la semana actual (domingo)
    const firstDayOfCurrentWeek = new Date(today);
    firstDayOfCurrentWeek.setDate(today.getDate() - today.getDay());

    // Calcular el último día de la semana actual (sábado)
    const lastDayOfCurrentWeek = new Date(today);
    lastDayOfCurrentWeek.setDate(today.getDate() + (6 - today.getDay()));
    
    // Formatear las fechas a YYYY-MM-DD
    const startDate = firstDayOfCurrentWeek.toISOString().split('T')[0];
    const endDate = lastDayOfCurrentWeek.toISOString().split('T')[0];

    // Parámetros para la solicitud
    const params = {
        "updated_timestamp__gte": startDate,
        "updated_timestamp__lte": endDate,
        "frequency": "week"
        
    };

    axios.post('/business-gestion/dashboard/shop-product-sells-count/', params)
        .then(response => {
            // Obtener el valor de ventas de la respuesta
            const sellCount =  response.data.result[0] ? response.data.result[0].total : 0;
            // Modificar el contenido del small-box con el valor de las ventas
            const smallBox = document.getElementById('sellweek');
            if (smallBox) {
                smallBox.textContent = sellCount + " Ventas";
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

function smallboxdataSellCurrentMonth() {
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
        "updated_timestamp__lte": endDate,
        "frequency": "month",        
    };

    axios.post('/business-gestion/dashboard/shop-product-sells-count/', params)
        .then(response => {
            // Obtener el valor de ventas de la respuesta
            
            const sellCount =  response.data.result[0] ? response.data.result[0].total : 0;
            // Modificar el contenido del small-box con el valor de las ventas
            const smallBox = document.getElementById('sellmount');
            if (smallBox) {
                smallBox.textContent = sellCount + " Ventas";
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

function smallboxdataSellProfits() {
    axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
    axios.post('/business-gestion/dashboard/sell-profits/')
        .then(response => {
            // Obtener el valor de inversiones de la respuesta
            const sellProfitsValue = response.data.result.total;

            // Modificar el contenido del small-box con el valor de la inversión
            const smallBox = document.getElementById('sell-profits-total');
            if (smallBox) {
                smallBox.textContent = sellProfitsValue+"$";
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

function smallboxdataSellProfitsLastMonth() {
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

    axios.post('/business-gestion/dashboard/sell-profits/', params)
        .then(response => {
            // Obtener el valor de inversiones de la respuesta
            const investmentValue = response.data.result.total;

            // Modificar el contenido del small-box con el valor de la inversión
            const smallBox = document.getElementById('gananciaslastmes');
            if (smallBox) {
                smallBox.textContent = investmentValue+"$";
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

function smallboxdataSellProfitsCurrentMonth() {
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

    axios.post('/business-gestion/dashboard/sell-profits/', params)
        .then(response => {
            // Obtener el valor de inversiones de la respuesta
            const SellProfitsValue = response.data.result.total;
console.log('✌️SellProfitsValue --->', SellProfitsValue);

            // Modificar el contenido del small-box con el valor de la inversión
            const smallBox = document.getElementById('gananciascurrentmes');
            if (smallBox) {
                smallBox.textContent = SellProfitsValue + "$";
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

// function smallboxdataSellProfitsCurrentWeek() {
//     // Obtener la fecha actual
//     const today = new Date();
    
//     // Calcular el primer día de la semana actual (domingo)
//     const firstDayOfCurrentWeek = new Date(today);
//     firstDayOfCurrentWeek.setDate(today.getDate() - today.getDay());

//     // Calcular el último día de la semana actual (sábado)
//     const lastDayOfCurrentWeek = new Date(today);
//     lastDayOfCurrentWeek.setDate(today.getDate() + (6 - today.getDay()));
    
//     // Formatear las fechas a YYYY-MM-DD
//     const startDate = firstDayOfCurrentWeek.toISOString().split('T')[0];
//     const endDate = lastDayOfCurrentWeek.toISOString().split('T')[0];

//     // Parámetros para la solicitud
//     const params = {
//         "updated_timestamp__gte": startDate,
//         "updated_timestamp__lte": endDate,
//         "frequency": "week"
        
//     };

//     axios.post('/business-gestion/dashboard/shop-product-sells-count/', params)
//         .then(response => {
//             // Obtener el valor de ventas de la respuesta
//             const sellCount =  response.data.result[0] ? response.data.result[0].total : 0;
//             // Modificar el contenido del small-box con el valor de las ventas
//             const smallBox = document.getElementById('sellweek');
//             if (smallBox) {
//                 smallBox.textContent = sellCount + "";
//             }
//         })
//         .catch(error => {
//             console.error('Error fetching data:', error);
//         });
// }



function smallboxdataSellProfitsCurrentWeek() {
    // Obtener la fecha actual
    const today = new Date();
    
    // Calcular el primer día de la semana actual (domingo)
    const firstDayOfCurrentWeek = new Date(today);
    firstDayOfCurrentWeek.setDate(today.getDate() - today.getDay());

    // Calcular el último día de la semana actual (sábado)
    const lastDayOfCurrentWeek = new Date(today);
    lastDayOfCurrentWeek.setDate(today.getDate() + (6 - today.getDay()));
    
    // Formatear las fechas a YYYY-MM-DD
    const startDate = firstDayOfCurrentWeek.toISOString().split('T')[0];
    const endDate = lastDayOfCurrentWeek.toISOString().split('T')[0];

    // Parámetros para la solicitud
    const params = {
        "updated_timestamp__gte": startDate,
        "updated_timestamp__lte": endDate,
        "frequency": "week"
        
    };

    axios.post('/business-gestion/dashboard/sell-profits/', params)
        .then(response => {
            // Obtener el valor de ventas de la respuesta
            const sellCount =  response.data.result[0] ? response.data.result[0].total : 0;
            // Modificar el contenido del small-box con el valor de las ventas
            const smallBox = document.getElementById('SellProfitscurrentweek');
            if (smallBox) {
                smallBox.textContent = sellCount + " $";
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}
function smallboxdataSellProfitsLastWeek() {
    // Obtener la fecha actual
    const today = new Date();
    
    // Calcular el primer día de la semana anterior (domingo)
    const firstDayOfLastWeek = new Date(today);
    firstDayOfLastWeek.setDate(today.getDate() - today.getDay() - 7);

    // Calcular el último día de la semana anterior (sábado)
    const lastDayOfLastWeek = new Date(today);
    lastDayOfLastWeek.setDate(today.getDate() - today.getDay() - 1);

    // Formatear las fechas a YYYY-MM-DD
    const startDate = firstDayOfLastWeek.toISOString().split('T')[0];
    const endDate = lastDayOfLastWeek.toISOString().split('T')[0];

    // Parámetros para la solicitud
    const params = {
        "updated_timestamp__gte": startDate,
        "updated_timestamp__lte": endDate,
        "frequency": "day"  // Cambiamos a "day" para obtener datos diarios
    };

    axios.post('/business-gestion/dashboard/sell-profits/', params)
        .then(response => {
            // Procesar las ganancias por día
            const dailyProfits = response.data.result; // Asumiendo que la respuesta es un array de objetos con ganancias por día
            
            // Limpiar datos anteriores
            profitsChart.data.labels = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
            profitsChart.data.datasets[0].data = [];

            // Llenar datos de la gráfica
            dailyProfits.forEach(day => {
                // profitsChart.data.labels.push(day.date); // Asegúrate de que 'date' es la propiedad correcta
                profitsChart.data.datasets[0].data.push(day.total); // Asegúrate de que 'total' es la propiedad correcta
            });

            // Actualizar la gráfica
            profitsChart.update();
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

