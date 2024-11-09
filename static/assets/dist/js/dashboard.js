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
chartSellProfitsLastWeek(),
chartSellProfitsThisWeek()
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
    firstDayOfLastMonth.setHours(0, 0, 0, 0);
    lastDayOfLastMonth.setHours(0, 0, 0, 0);
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
    firstDayOfCurrentMonth.setHours(0, 0, 0, 0);
    lastDayOfCurrentMonth.setHours(0, 0, 0, 0);
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
    firstDayOfCurrentWeek.setHours(0, 0, 0, 0);
    lastDayOfCurrentWeek.setHours(0, 0, 0, 0);
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
    firstDayOfLastMonth.setHours(0, 0, 0, 0);
    lastDayOfLastMonth.setHours(0, 0, 0, 0);
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
    firstDayOfCurrentMonth.setHours(0, 0, 0, 0);
    lastDayOfCurrentMonth.setHours(0, 0, 0, 0);
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

function smallboxdataSellProfitsCurrentWeek() {
    // Obtener la fecha actual
    const today = new Date();
    
    // Calcular el primer día de la semana actual (domingo)
    const firstDayOfCurrentWeek = new Date(today);
    firstDayOfCurrentWeek.setDate(today.getDate() - today.getDay());

    // Calcular el último día de la semana actual (sábado)
    const lastDayOfCurrentWeek = new Date(today);
    lastDayOfCurrentWeek.setDate(today.getDate() + (6 - today.getDay()+1));
    
    // Formatear las fechas a YYYY-MM-DD
    firstDayOfCurrentWeek.setHours(0, 0, 0, 0);
    const startDate = firstDayOfCurrentWeek.toISOString().split('T')[0];
    lastDayOfCurrentWeek.setHours(0, 0, 0, 0);
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

function daterangeSellProfits(startDate, endDate) {
    // Asegúrate de que las fechas están en el formato correcto
    const formattedStartDate = new Date(startDate);
    const formattedEndDate = new Date(endDate);

    // Formatear las fechas a YYYY-MM-DD
    formattedStartDate.setHours(0, 0, 0, 0);
    const start = formattedStartDate.toISOString().split('T')[0];
    formattedEndDate.setHours(23, 59, 59, 999);
    const end = formattedEndDate.toISOString().split('T')[0];

    // Parámetros para la solicitud
    const params = {
        "updated_timestamp__gte": start,
        "updated_timestamp__lte": end,
        "frequency": "day"
    };

    axios.post('/business-gestion/dashboard/sell-profits/', params)
        .then(response => {
            // Obtener el valor de ventas de la respuesta
            const results = response.data.result;
            let sellCount = 0; // Variable para la suma de totales
            let itemCount = 0; // Variable para contar elementos

            // Sumar los totales y contar los elementos
            if (results && results.length > 0) {
                results.forEach(item => {
                    sellCount += item.total || 0; // Sumar el total
                    itemCount++; // Contar el elemento
                });
            }
            // Modificar el contenido del small-box con el valor de las ventas
             const dateRangeProfits = document.getElementById('dateRangeProfits');
             const dateRangeSales = document.getElementById('dateRangeSales');
             if (dateRangeProfits && dateRangeSales) {
                dateRangeProfits.textContent = sellCount + " $";
                dateRangeSales.textContent =itemCount;
             }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}


// charts
function chartSellProfitsLastWeek() {
    // Obtener la fecha actual
    const today = new Date();  
    // Calcular el primer día de la semana anterior (domingo)
    const firstDayOfLastWeek = new Date(today);
    firstDayOfLastWeek.setDate(today.getDate() - today.getDay() - 7);
    // Calcular el último día de la semana anterior (sábado)
    const lastDayOfLastWeek = new Date(today);
    lastDayOfLastWeek.setDate(today.getDate() - today.getDay() - 1);
    // Formatear las fechas a YYYY-MM-DD
    firstDayOfLastWeek.setHours(0, 0, 0, 0);
    const startDate = firstDayOfLastWeek.toISOString().split('T')[0];
    lastDayOfLastWeek.setHours(0, 0, 0, 0);
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
            profitsChart.data.labels = [];
            profitsChart.data.datasets[0].data = [];

            // Llenar datos de la gráfica
            dailyProfits.forEach(day => {
                 profitsChart.data.labels.push(getDayOfWeek(day.frequency)); // Asegúrate de que 'date' es la propiedad correcta
                profitsChart.data.datasets[0].data.push(day.total); // Asegúrate de que 'total' es la propiedad correcta
            });

            // Actualizar la gráfica
            profitsChart.update();
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}
function chartSellProfitsThisWeek() {
    // Obtener la fecha actual
    const today = new Date();  
    // Calcular el primer día de la semana  (domingo)
    const firstDayOfThisWeek = new Date(today);
    firstDayOfThisWeek.setDate(today.getDate() - today.getDay());
    // Calcular el último día de la semana anterior (sábado)
    const lastDayOfThisWeek = new Date(today);
    lastDayOfThisWeek.setDate(today.getDate() - today.getDay() + 1);

    // Establecer la hora a medianoche en la zona horaria local
    firstDayOfThisWeek.setHours(0, 0, 0, 0);

    // Convertir a formato YYYY-MM-DD
    const startDate = firstDayOfThisWeek.toISOString().split('T')[0];

    lastDayOfThisWeek.setHours(23, 59, 0, 0);
    const endDate = lastDayOfThisWeek.toISOString().split('T')[0];

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
            profitsChartThisWeek.data.labels = [];
            profitsChartThisWeek.data.datasets[0].data = [];
            // Llenar datos de la gráfica
            dailyProfits.forEach(day => {
                profitsChartThisWeek.data.labels.push(getDayOfWeek(day.frequency)); // Asegúrate de que 'date' es la propiedad correcta
                profitsChartThisWeek.data.datasets[0].data.push(day.total); // Asegúrate de que 'total' es la propiedad correcta
            });

            // Actualizar la gráfica
            profitsChartThisWeek.update();
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

function getDayOfWeek(date) {
    // Crear un objeto Date si la entrada es una cadena
    const dateObj = typeof date === 'string' ? new Date(date) : date;

    // Asegurarse de que la fecha es válida
    if (isNaN(dateObj)) {
        throw new Error('Fecha inválida');
    }

    // Array con los nombres de los días de la semana
    const daysOfWeek = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];

    // Obtener el índice del día de la semana (0-6)
    const dayIndex = (dateObj.getUTCDay() + 7) % 7; // Usar getUTCDay para evitar problemas de zona horaria

    // Retornar el nombre del día correspondiente
    return daysOfWeek[dayIndex];
}



$(function () {
   //Date range as a button
$('#daterange-btn').daterangepicker(
    {
      ranges   : {
        'Today'       : [moment(), moment()],
        'Yesterday'   : [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
        'Last 7 Days' : [moment().subtract(6, 'days'), moment()],
        'Last 30 Days': [moment().subtract(29, 'days'), moment()],
        'This Month'  : [moment().startOf('month'), moment().endOf('month')],
        'Last Month'  : [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
      },
      startDate: moment().subtract(29, 'days'),
      endDate  : moment()
    },
    function (start, end) {
      $('#reportrange span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'))
      selectedStartDate = start;
  selectedEndDate = end;

  // Puedes hacer algo con los valores aquí, por ejemplo:
  console.log('Fecha de inicio:', selectedStartDate.format('YYYY-MM-DD'));
  console.log('Fecha de fin:', selectedEndDate.format('YYYY-MM-DD'));
  daterangeSellProfits(selectedStartDate,selectedEndDate);
    
    }
    
  )
  });