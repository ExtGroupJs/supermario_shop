// Listar eventos
function listEvents() {
    $.ajax({
        url: '/events/',
        type: 'GET',
        success: function (data) {
            console.log(data);
        },
        error: function (xhr, status, error) {
            console.error(error);
        }
    });
}

function resetEventForm() {
    document.getElementById('add-event-form').reset();
}

// Agregar un evento que se dispare al cerrar la ventana modal
$('#modal-add-event').on('hidden.bs.modal', function (e) {
    resetEventForm();
});

// Agregar una función para enviar el formulario
function submitEventForm() {
    var form = document.getElementById('add-event-form');
    if (form.checkValidity()) {
        var formData = new FormData(form);

        $.ajax({
            url: '../business-gestion/events/create/',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
                console.log(data);
                Swal.fire({
                    icon: "success",
                    title: "Evento creado con éxito",
                    showConfirmButton: false,
                    timer: 1500
                });
                // Limpiar los campos del formulario
                resetEventForm();
                // Recargar la página después de 0.5 segundos
                setTimeout(function () {
                    location.reload();
                }, 500);

            },
            error: function (xhr, status, error) {
                console.error(error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Hubo un problema al guardar el evento. Por favor, inténtalo de nuevo.',
                    timer: 1500
                });
                resetEventForm();
            }
        });

        // Cerrar la ventana modal después de enviar el formulario
        $('#modal-add-event').modal('hide');
        resetEventForm();
    } else {
        // Mostrar un mensaje de error personalizado
        var errorMessage = 'Por favor completa todos los campos obligatorios.';
        var invalidFields = form.querySelectorAll(':invalid');
        if (invalidFields.length > 0) {
            errorMessage += '\nCampos faltantes:';
            invalidFields.forEach(function (field) {
                errorMessage += '\n- ' + field.name;
            });
        }
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: errorMessage,
            timer: 1500
        });
    }
}


// Editar evento
function editEvent(event_id, event_name, event_icon) {
    var formData = new FormData();
    formData.append('event_name', event_name);
    formData.append('event_icon', $('#modal-edit-event #event-icon')[0].files[0]);
    $.ajax({
        url: '../business-gestion/events/edit/' + event_id + '/',
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function (data) {
            console.log(data);
            $('#modal-edit-event').modal('hide'); // Ocultar la ventana modal después de la edición
            Swal.fire({
                icon: "success",
                title: "Evento editado con éxito",
                showConfirmButton: false,
                timer: 1500
            });
            setTimeout(function () {
                location.reload();
            }, 500);
        },
        error: function (xhr, status, error) {
            console.error(error);
        }
    });
}
$(document).ready(function() {
  // Botón de editar en la lista de eventos
  $('.btn-edit').click(function() {
    // Obtener los datos del evento seleccionado
    var event_id = $(this).data('event-id');
    var event_name = $(this).data('event-name');
    var event_icon = $(this).data('event-icon');
    // Mostrar el nombre del evento
    $('#modal-edit-event #event-name').val(event_name);
    // Mostrar la imagen previamente cargada del icono del evento
    $('#modal-edit-event #event-icon-preview').attr('src', '/media/'+ event_icon);
    // Almacenar la URL del icono en un campo oculto para enviarlo al editar el evento
    $('#modal-edit-event #event-icon-url').val(event_icon);
    // Mostrar la ventana modal
    $('#modal-edit-event').modal('show');
  });

  // Enviar formulario al hacer click en el botón Enviar
  $('#btn-edit-event').click(function() {
    var event_id = $(this).data('event-id');
    var event_name = $('#modal-edit-event #event-name').val();
    var event_icon = $('#modal-edit-event #event-icon')[0].files[0];  // Obtener el archivo de imagen
    // Realizar la solicitud AJAX para editar el evento
    editEvent(event_id, event_name, event_icon);
  });
});


// Eliminar evento
function deleteEvent(event_id) {
    $.ajax({
        url: `../business-gestion/events/delete/${event_id}/`,
        type: 'POST',
        success: function (data) {
            console.log(data);
            $('#modal-delete-event').modal('hide'); // Ocultar la ventana modal después de la elminacion
            Swal.fire({
                    icon: "success",
                    title: "Evento eliminado con éxito",
                    showConfirmButton: false,
                    timer: 1500
                });
             setTimeout(function () {
                    location.reload();
                }, 500);

        },
        error: function (xhr, status, error) {
            console.error(error);
        }
    });
    $('#modal-delete-event').modal('hide');
}