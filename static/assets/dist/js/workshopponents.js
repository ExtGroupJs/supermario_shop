const clearform = document.getElementById("form-workshop-ponents");
var createWorkshopOnents = function () {

    // event.preventDefault();

    const csrfToken = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')[1];
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    let data = new FormData();

    // data.append("system_user", localStorage.getItem('id'));
    data.append("workshop", document.getElementById("workshop").value);
    data.append("work_english_summary", document.getElementById("work_english_summary").value);
    data.append("work_english_title", document.getElementById("work_english_title").value);
    data.append("work_spanish_keywords", document.getElementById("work_spanish_keywords").value);
    data.append("work_spanish_summary", document.getElementById("work_spanish_summary").value);
    data.append("work_spanish_title", document.getElementById("work_spanish_title").value);
    data.append("author_list", document.getElementById("author_list").value);

    if (document.getElementById('DocumentCustomFile').files[0] != null) {
        data.append('uploaded_work', document.getElementById('DocumentCustomFile').files[0]);
    }

    const url = '../event-gestion/workshop-ponents/';
    if (editWork) {
        axios
            .patch(url + editWorkid + '/', data)
            .then((response) => {
                if (response.status === 200) {
                    Swal.fire({
                        icon: "success",
                        title: "trabajo actualizado con éxito",
                        showConfirmButton: false,
                        timer: 1500
                    });

                    clearforms(clearform)
                    var head_timeline = document.getElementById("head-timeline");
                    var head_work = document.getElementById("head-work");
                    var tabwork = document.getElementById("work");
                    var tabwork = document.getElementById("work");
                    var tabtimeline = document.getElementById("timeline");
                    tabtimeline.classList.add("show", "active");
                    head_timeline.classList.add("show", "active");
                    tabwork.classList.remove("active");
                    head_work.classList.remove("active");
                }

            })
            .catch((error) => {

                let dict = error.response.data;
                let textError = "Revise los siguientes campos: ";
                for (const key in dict) {
                    textError = textError + ":" + key;
                }

                if (error.response.status === 406) {

                    Swal.fire({
                        icon: "error",
                        title: "error ",
                        text: "error ",
                        showConfirmButton: false,
                        timer: 5000
                    });
                } else {

                    Swal.fire({
                        icon: "error",
                        title: "Error al editar el trabajo",
                        text: textError,
                        showConfirmButton: false,
                        timer: 1500
                    });
                }
            });

    } else {
        axios
            .post(url, data)
            .then((response) => {
                if (response.status === 201) {
                    Swal.fire({
                        icon: "success",
                        title: "trabajo subido con éxito",
                        showConfirmButton: false,
                        timer: 1500
                    });
                    // let clearform = document.getElementById("form-workshop-ponents");

                    clearforms(clearform)
                    var head_timeline = document.getElementById("head-timeline");
                    var head_work = document.getElementById("head-work");
                    var tabwork = document.getElementById("work");
                    var tabwork = document.getElementById("work");
                    var tabtimeline = document.getElementById("timeline");
                    tabtimeline.classList.add("show", "active");
                    head_timeline.classList.add("show", "active");
                    tabwork.classList.remove("active");
                    head_work.classList.remove("active");
                }
            })
            .catch((error) => {

                let dict = error.response.data;
                let textError = "Revise los siguientes campos: ";
                for (const key in dict) {
                    textError = textError + ":" + key;
                }

                if (error.response.status === 406) {

                    Swal.fire({
                        icon: "error",
                        title: "error ",
                        text: "error ",
                        showConfirmButton: false,
                        timer: 5000
                    });
                } else {

                    Swal.fire({
                        icon: "error",
                        title: "Error al crear usuario",
                        text: textError,
                        showConfirmButton: false,
                        timer: 1500
                    });
                }
            });
    }
    poblarListasWorkShopPonents();
    clearListasWorkShopPonents();


}

$(function () {
    bsCustomFileInput.init();
    $('.select2').select2({ theme: 'bootstrap4' })
    poblarListas();
    poblarListasWorkShopPonents();

});

$(function () {
    $.validator.setDefaults({
        language: 'es',
        submitHandler: function () {
            // alert("Form successful submitted!");
        }
    });

    $('#form-workshop-ponents').validate({

        rules: {

            work_spanish_title: {
                required: true,

            },
            work_spanish_summary: {
                required: true,

            },
            work_english_title: {
                required: true,

            },
            work_english_summary: {
                required: true,

            },
            customFile: {
                required: true,

            },

        },
        submitHandler: function (form) {
            createWorkshopOnents();
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


function poblarListas() {
    var $workshop = document.getElementById("workshop");
    axios.get("../../event-gestion/workshops/").then(function (response) {
        response.data.results.forEach(function (element) {
            var option = new Option(element.title, element.id);
            $workshop.add(option);
        });
    });

}


function clearforms(form) {
    editWork = false;
    editWorkid = null;
    form.reset();
    const elements = [...form.elements];
    elements.forEach(elem => elem.classList.remove('is-invalid'));

}


function clearListasWorkShopPonents() {
    // Obtener todos los elementos div con la clase "saco"
    var divsEliminar = document.getElementsByClassName("saco");
    // Convertir la lista de elementos en un array para poder recorrerlos
    var divsArray = Array.from(divsEliminar);
    // Recorrer el array y eliminar cada elemento div
    divsArray.forEach(function (div) {
        div.remove();
    });
}

function poblarListasWorkShopPonents() {

    var url = "../event-gestion/workshop-ponents/?system_user=" + localStorage.getItem('id');
    var div2 = document.getElementById("timelinecont");
    var divclock = document.getElementById("clock");

    //div2.innerHTML = "";

    axios
        .get(url)
        .then(function (response) {
            if (response.status === 200) {



                response.data.results.forEach(element => {
                    // Crea el elemento i con la clase "fas fa-user bg-primary"
                    var icono = document.createElement("i");
                    icono.classList.add("fas", "fa-user", "bg-primary");

                    // Crea el elemento timeline-item
                    var timelineItem = document.createElement("div");
                    timelineItem.classList.add("timeline-item");

                    // Crea el elemento de tiempo con el ícono del reloj
                    var tiempo = document.createElement("span");
                    tiempo.classList.add("time");
                    var reloj = document.createElement("i");
                    reloj.classList.add("far", "fa-clock");
                    tiempo.appendChild(reloj);
                    var fechaFormateada = new Date(element['uploaded_datetime']).toLocaleDateString();
                    tiempo.appendChild(document.createTextNode(fechaFormateada));

                    // Crea el encabezado de la línea de tiempo
                    var encabezado = document.createElement("h3");
                    encabezado.classList.add("timeline-header");
                    var enlace = document.createElement("a");
                    enlace.setAttribute("href", "#");
                    enlace.appendChild(document.createTextNode("Título: "));
                    encabezado.appendChild(enlace);
                    encabezado.appendChild(document.createTextNode(element['work_spanish_title']));

                    // Crea el cuerpo de la línea de tiempo
                    var cuerpo = document.createElement("div");
                    cuerpo.classList.add("timeline-body");
                    cuerpo.appendChild(document.createTextNode("Título en español:  "));
                    cuerpo.appendChild(document.createTextNode(element['work_spanish_summary']));
                    cuerpo.appendChild(document.createElement("br")); // Agrega un salto de línea
                    cuerpo.appendChild(document.createTextNode("Título en ingles: "));
                    cuerpo.appendChild(document.createTextNode(element['work_english_title']));
                    cuerpo.appendChild(document.createElement("br")); // Agrega un salto de línea
                    cuerpo.appendChild(document.createTextNode("Resumen en ingles: "));
                    cuerpo.appendChild(document.createTextNode(element['work_english_summary']));
                    cuerpo.appendChild(document.createElement("br")); // Agrega un salto de línea
                    cuerpo.appendChild(document.createTextNode("Palabras claves: "));
                    cuerpo.appendChild(document.createTextNode(element['work_spanish_keywords']));
                    cuerpo.appendChild(document.createElement("br")); // Agrega un salto de línea
                    cuerpo.appendChild(document.createTextNode("Autores: "));
                    cuerpo.appendChild(document.createTextNode(element['author_list']));

                    // Crea el pie de la línea de tiempo
                    var pie = document.createElement("div");
                    pie.classList.add("timeline-footer");
                    var enlaceLeerMas = document.createElement("a");
                    enlaceLeerMas.addEventListener("click", function (event) {
                        event.preventDefault(); // Evita que el enlace siga su enlace predeterminado
                        // Llamar a la función deseada aquí
                        editWorkshopPonente(element)

                    })
                    enlaceLeerMas.classList.add("btn", "btn-danger", "btn-sm");
                    enlaceLeerMas.appendChild(document.createTextNode("Editar"));
                    pie.appendChild(enlaceLeerMas);
                    var saco = document.createElement("div");
                    // Agrega todos los elementos creados al div principal
                    timelineItem.appendChild(tiempo);
                    timelineItem.appendChild(encabezado);
                    timelineItem.appendChild(cuerpo);
                    timelineItem.appendChild(pie);
                    saco.appendChild(icono);
                    saco.appendChild(timelineItem);
                    saco.classList.add("saco");
                    div2.insertBefore(saco, divclock);


                });


                // loadUser();
            }
        })
        .catch((error) => {

        });
}

let editWork = false;
let editWorkid = null;
var seccionx = document.getElementById("work");
function editWorkshopPonente(element) {
    clearform.elements.work_english_summary.value = element['work_english_summary'];
    clearform.elements.work_english_title.value = element['work_english_title'];
    clearform.elements.work_spanish_keywords.value = element['work_spanish_keywords'];
    clearform.elements.work_spanish_summary.value = element['work_spanish_summary'];
    clearform.elements.work_spanish_title.value = element['work_spanish_title'];
    clearform.elements.author_list.value = element['author_list'];
    $('#workshop').val(element['workshop']).trigger('change.select2');
    editWork = true;
    editWorkid = element['id'];
    var head_timeline = document.getElementById("head-timeline");
    var head_work = document.getElementById("head-work");
    var tabwork = document.getElementById("work");
    var tabwork = document.getElementById("work");
    var tabtimeline = document.getElementById("timeline");
    tabtimeline.classList.remove("active")
    head_timeline.classList.remove("active")
    tabwork.classList.add("show", "active");
    head_work.classList.add("show", "active");
}







