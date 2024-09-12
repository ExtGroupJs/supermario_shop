// variable para gestionar los elementos seleccionados
let selected_id;

// Variable con el token 
const csrfToken = document.cookie.split(';')
    .find(c => c.trim().startsWith('csrftoken='))
    ?.split('=')[1];
// url del endpoint principal 
const url = '../product-gestion/production/'



$(document).ready(function () {

    $('table')
        .addClass('table table-hover')
        .DataTable({
            responsive: true,
            dom: '<"top"l>Bfrtip',
            buttons: [
                {
                    text: ' Agregar',
                    className: ' btn btn-primary btn-info',
                    action: function (e, dt, node, config) {
                        $('#modal-crear-elemento').modal('show');
                    },

                }, {
                    extend: 'excel',
                    text: 'Excel'
                },
                {
                    extend: 'pdf',
                    text: 'PDF'
                },
                {
                    extend: 'print',
                    text: 'Imprimir'
                }
            ],
            //Adding server-side processing
            serverSide: true,
            search: {
                return: true,
            },
            processing: true,
            ajax: function (data, callback, settings) {
                dir = "";
                if (data.order[0].dir == "desc") {
                    dir = "-"
                }
                axios.get(url, {
                    params: {
                        page_size: data.length,
                        page: (data.start / data.length) + 1,
                        search: data.search.value,
                        ordering: dir + data.columns[data.order[0].column].data,
                    }

                }).then(res => {
                    callback({

                        recordsTotal: res.data.count,
                        recordsFiltered: res.data.count,
                        data: res.data.results

                    });
                }).catch(error => {
                    alert(error)
                })
                console.log(data)
            },
            columns: [

                { data: "name", "title": "Nombre" },
                { data: "product_name", "title": "Producto" },
                { data: "distribution_format_name", "title": "Formato" },
                { data: "wholesale_price", "title": "Precio" },
                { data: "destination_name", "title": "Destino" },
                { data: "entity_name", "title": "UEB" },
                { data: "quantity", "title": "Cantidad" },
                { data: "cost", "title": "Costo" },
                {
                    data: 'description', "title": "Estado", render: (data, type, row) => {
                        if (row.active) {
                            return `<span title="Activo" class="badge badge-success"><i class="nav-icon fas fa-toggle-on"></i></span> `;
                        } else {
                            return `<span title="Inactivo" class="badge badge-danger"><i class="nav-icon fas fa-toggle-off"></i></span> `;
                        }
                    }
                },

                {
                    data: 'description', "title": "Acciones", "className": 'text-center',
                    render: (data, type, row) => {

                        if (row.deletion_timestamp == null) {
                            return `<div class="btn-group">
                                        <button type="button" title="edit" class="btn bg-olive active" data-toggle="modal" data-target="#modal-crear-elemento" data-id="${row.id}" data-type="edit" data-name="${row.name}" id="${row.id}"  >
                                             <i class="fas fa-edit"></i>
                                         </button>
                                        <button type="button" title="Detalles" class="btn bg-olive " data-toggle="modal" data-target="#modal-crear-elemento" data-id="${row.id}" data-type="detail" data-name="${row.name}" id="${row.id}"  >
                                             <i class="fas fa-file-alt"></i>
                                         </button>
                                         <button type="button" title="Archivar" class="btn bg-olive" data-toggle="modal" data-target="#modal-eliminar-elemento" data-id="${row.id}" data-name="${row.name}" id="${row.id}">
                                              <i class="fas fa-archive"></i>
                                         </button>
                                     </div>`;
                        } else {
                            return `<div class="btn-group">
                            <button type="button" title="edit" class="btn bg-olive active" data-toggle="modal" data-target="#modal-crear-elemento" data-id="${row.id}" data-type="edit" data-name="${row.name}" id="${row.id}"  >
                                 <i class="fas fa-edit"></i>
                             </button>
                             <button type="button" title="Detalles" class="btn bg-olive " data-toggle="modal" data-target="#modal-crear-elemento" data-id="${row.id}" data-type="detail" data-name="${row.name}" id="${row.id}"  >
                                <i class="fas fa-file-alt"></i>
                             </button>
                             <button type="button" title="Restaurar" class="btn bg-olive" data-toggle="modal" data-id="${row.id}" data-name="${row.name}" id="${row.id}" onclick="function_des_archivar(${row.id})">
                                  <i class="fas fa-box-open"></i>
                             </button>
                         </div>`;
                        }

                    }
                },

            ],
            //  esto es para truncar el texto de las celdas
            "columnDefs": [


            ]
        });
    console.log("lista");
    poblarListas();
});



$('#modal-eliminar-elemento').on('hide.bs.modal', (event) => {
    document.getElementById("cause").value = ""

});


$('#modal-eliminar-elemento').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) // Button that triggered the modal
    var dataName = button.data('name') // Extract info from data-* attributes
    selected_id = button.data('id') // Extract info from data-* attributes
    var modal = $(this)
    modal.find('.mytext').text('¿Desea archivar a ' + dataName + '?')
})

// funcion para archivar 
function function_archivar(selected_id) {
    const table = $('#tabla-de-Datos').DataTable();
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    let data = new FormData();
    data.append("deletion_cause", document.getElementById("cause").value);
    axios.post(`${url}${selected_id}/archive/`, data)
        .then((response) => {
            Toast.fire({
                icon: 'success',
                title: 'El elemento se archivó correctamente'
            })
            table.ajax.reload();

        })
        .catch((error) => {
            Toast.fire({
                icon: 'error',
                title: 'El elemento no se archivó'
            })
        });
}
// funcion para des archivar 
function function_des_archivar(selected_id) {
    const table = $('#tabla-de-Datos').DataTable();
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    let data = new FormData();
    data.append("deletion_cause", document.getElementById("cause").value);
    axios.post(`${url}${selected_id}/des_archive/`, data)
        .then((response) => {
            Toast.fire({
                icon: 'success',
                title: 'El elemento se restauró correctamente'
            })
            table.ajax.reload();
        })
        .catch((error) => {
            Toast.fire({
                icon: 'error',
                title: 'El elemento no se restauró'
            })
        });
}



$('#modal-crear-elemento').on('hide.bs.modal', (event) => {
    // The form element is selected from the event trigger and its value is reset.
    const form = event.currentTarget.querySelector('form');
    form.reset();
    // The 'edit_elemento' flag is set to false.
    edit_elemento = false;
    // An array 'elements' is created containing all the HTML elements found inside the form element.
    const elements = [...form.elements];
    // A forEach loop is used to iterate through each element in the array.
    elements.forEach(elem => {
        elem.classList.remove('is-invalid');
        elem.disabled = false;
        elem.classList.remove('is-warning');
        if (elem.textContent == 'Enviar') {
            elem.style.display = 'unset';
        }
        var ribbon = document.querySelector('.ribbon-wrapper.ribbon-xl');
        ribbon.hidden = true;
    });

});


let edit_elemento = false;
$('#modal-crear-elemento').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) // Button that triggered the modal
    var modal = $(this)
    if (button.data('type') == "edit") {
        var dataName = button.data('name') // Extract info from data-* attributes
        selected_id = button.data('id') // Extract info from data-* attributes
        edit_elemento = true
        modal.find('.modal-title').text('Editar ' + dataName)
        // Realizar la petición con Axios
        axios.get(`${url}${selected_id}/`)
            .then(function (response) {
                // Recibir la respuesta
                const elemento = response.data;
                form.elements.name.value = elemento.name;
                // form.elements.product.value = elemento.product;
                $('#product').select2({ dropdownParent: $('#modal-crear-elemento'), theme: 'bootstrap4' });
                $('#product').val(elemento.product).trigger('change.select2');
                // form.elements.distribution_format.value = elemento.distribution_format;
                $('#distribution_format').select2({ dropdownParent: $('#modal-crear-elemento'), theme: 'bootstrap4' });
                $('#distribution_format').val(elemento.distribution_format).trigger('change.select2');
                form.elements.wholesale_price.value = elemento.wholesale_price;
                form.elements.quantity.value = elemento.quantity;
                form.elements.cost.value = elemento.cost;
                $('#entity').select2({ dropdownParent: $('#modal-crear-elemento'), theme: 'bootstrap4' });
                $('#entity').val(elemento.entity).trigger('change.select2');
                $('#destination').select2({ dropdownParent: $('#modal-crear-elemento'), theme: 'bootstrap4' });
                $('#destination').val(elemento.destination).trigger('change.select2');
                form.elements.description.value = elemento.description;
                form.elements.myenabled.value = elemento.active;
                if (elemento.active) {
                    form.elements.myenabled.checked = true;
                } else { form.elements.myenabled.checked = false; }


            })
            .catch(function (error) {

            });

    } else {
        if (button.data('type') == "detail") {
            var dataName = button.data('name') // Extract info from data-* attributes
            selected_id = button.data('id') // Extract info from data-* attributes
            edit_elemento = true
            modal.find('.modal-title').text('Detalles de ' + dataName)
            var ribbon = document.querySelector('.ribbon-wrapper.ribbon-xl');
            // Realizar la petición con Axios
            axios.get(`${url}${selected_id}/`)
                .then(function (response) {
                    // Recibir la respuesta
                    const elemento = response.data;
                    form.elements.name.value = elemento.name;
                    $('#product').select2({ dropdownParent: $('#modal-crear-elemento'), theme: 'bootstrap4' });
                    $('#product').val(elemento.product).trigger('change.select2');
                    // form.elements.distribution_format.value = elemento.distribution_format;
                    $('#distribution_format').select2({ dropdownParent: $('#modal-crear-elemento'), theme: 'bootstrap4' });
                    $('#distribution_format').val(elemento.distribution_format).trigger('change.select2');
                    form.elements.wholesale_price.value = elemento.wholesale_price;
                    form.elements.destination.value = elemento.destination;
                    form.elements.entity.value = elemento.entity;
                    form.elements.quantity.value = elemento.quantity;
                    form.elements.cost.value = elemento.cost;
                    $('#entity').select2({ dropdownParent: $('#modal-crear-elemento'), theme: 'bootstrap4' });
                    $('#entity').val(elemento.entity).trigger('change.select2');
                    $('#destination').select2({ dropdownParent: $('#modal-crear-elemento'), theme: 'bootstrap4' });
                    $('#destination').val(elemento.destination).trigger('change.select2');
                    form.elements.description.value = elemento.description;
                    var elementos = form.elements;
                    form.elements.myenabled.value = elemento.active;
                    console.log(elemento.active);
                    if (elemento.active) {
                        form.elements.myenabled.checked = true;
                    } else { form.elements.myenabled.checked = false; }

                    Array.from(elementos).forEach(function (elemento) {

                        if (elemento.textContent != 'Close') {
                            elemento.disabled = true;
                            elemento.classList.add('is-warning');
                            if (elemento.textContent == 'Enviar') {
                                elemento.style.display = 'none';
                            }
                        }
                    });
                    ribbon.hidden = false;

                })
                .catch(function (error) {

                });
        } else {
            modal.find('.modal-title').text('Crear Producción')
        }
    }

})



$(function () {
    $('.select2').select2({ dropdownParent: $('#modal-crear-elemento'), theme: 'bootstrap4' })

    bsCustomFileInput.init();
});

// form validator
$(function () {
    $.validator.setDefaults({
        language: 'es',
        submitHandler: function () {
            // alert("Form successful submitted!");
        }
    });
    $('#form-create-elemento').validate({
        rules: {
            name: {
                required: true,

            },




        },
        submitHandler: function (form) {

        },

        messages: {
            email: {
                required: "Por favor debe ingresar una dirección de correo",
                email: "Por favor debe ingresar una dirección de correo válida"
            }
        },
        errorElement: 'span',
        errorPlacement: function (error, element) {
            error.addClass('invalid-feedback');
            element.closest('.form-group').append(error);
        },
        highlight: function (element, errorClass, validClass) {
            $(element).addClass('is-invalid');
        },
        unhighlight: function (element, errorClass, validClass) {
            $(element).removeClass('is-invalid');
        }
    });
});



// crear elemento
let form = document.getElementById("form-create-elemento");
form.addEventListener('submit', function (event) {
    event.preventDefault();
    var table = $('#tabla-de-Datos').DataTable();
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    let data = new FormData();
    data.append("name", document.getElementById("name").value);
    data.append("product", document.getElementById("product").value);
    data.append("distribution_format", document.getElementById("distribution_format").value);
    data.append("quantity", document.getElementById("quantity").value);
    data.append("wholesale_price", document.getElementById("wholesale_price").value);
    data.append("cost", document.getElementById("cost").value);
    data.append("destination", document.getElementById("destination").value);
    data.append("entity", document.getElementById("entity").value);
    data.append("description", document.getElementById("description").value);
    data.append("active", document.getElementById("myenabled").value);


    if (edit_elemento) {
        axios
            .put(`${url}${selected_id}/`, data)
            .then((response) => {
                if (response.status === 200) {

                    Swal.fire({
                        icon: "success",
                        title: "Elemento creado con exito",
                        showConfirmButton: false,
                        timer: 1500
                    });

                    table.ajax.reload();
                    $('#modal-crear-elemento').modal('hide');
                    edit_elemento = false;
                }
            })
            .catch((error) => {
                let dict = error.response.data;
                let textError = "Revise los siguientes campos: ";
                for (const key in dict) {
                    textError = textError + ", " + key;
                }

                Swal.fire({
                    icon: "error",
                    title: "Error al crear producción",
                    text: textError,
                    showConfirmButton: false,
                    timer: 1500
                });
            });
    } else {
        axios
            .post(url, data)
            .then((response) => {
                if (response.status === 201) {

                    Swal.fire({
                        icon: "success",
                        title: "Elemento creado con exito",
                        showConfirmButton: false,
                        timer: 1500
                    });

                    table.ajax.reload();
                    $('#modal-crear-elemento').modal('hide');
                }
            })
            .catch((error) => {

                let dict = error.response.data;
                let textError = "Revise los siguientes campos: ";
                for (const key in dict) {
                    textError = textError + ", " + key;
                }

                Swal.fire({
                    icon: "error",
                    title: "Error al crear elemento",
                    text: textError,
                    showConfirmButton: false,
                    timer: 1500
                });
            });
    }
});

function test() {

    axios.get(url).then(function (response) {
        console.log(response.data.results)
    });
}



function poblarListas() {
    var $product = document.getElementById("product");
    axios.get("../../product-gestion/product/").then(function (response) {
        response.data.results.forEach(function (element) {
            var option = new Option(element.name, element.id);
            $product.add(option);
        });
    });
    var $distribution_format = document.getElementById("distribution_format");
    axios.get("../../product-gestion/grouping-packaging/").then(function (response) {
        response.data.results.forEach(function (element) {
            var option = new Option(element.name, element.id);
            $distribution_format.add(option);
        });
    });
    var $entity = document.getElementById("entity");
    axios.get("../../product-gestion/entity/").then(function (response) {
        response.data.results.forEach(function (element) {
            var option = new Option(element.name, element.id);
            $entity.add(option);
        });
    });
    var $destination = document.getElementById("destination");
    axios.get("../../product-gestion/destination/").then(function (response) {
        response.data.results.forEach(function (element) {
            var option = new Option(element.name, element.id);
            $destination.add(option);
        });
    });

}


function changeCheckboxValue(id) {
    // Get the checkbox element by ID
    const checkboxElement = document.getElementById(id);

    if (checkboxElement.checked) {
        // If the checkbox is already checked, set its value to true
        checkboxElement.value = true;
    } else {
        // Otherwise, set its value to false
        checkboxElement.value = false;
    }
}