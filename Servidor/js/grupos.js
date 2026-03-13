let grupos=[]

function volver(){
window.location.href="/admin.html"
}

function cerrarSesion(){
window.location.href="/index.html"
}

async function cargarGrupos(){

const respuesta = await fetch("/listar_grupos")

grupos = await respuesta.json()

mostrarGrupos(grupos)

}

function mostrarGrupos(lista){

const tabla=document.querySelector("#tablaGrupos tbody")

tabla.innerHTML=""

lista.forEach(g=>{

tabla.insertAdjacentHTML("beforeend",`

<tr>
<td>${g.programa}</td>
<td>${g.semestre}</td>
<td>${g.grupo}</td>
<td>${g.tipo}</td>
<td>${g.alumnos}</td>

<td>
    <button onclick="abrirModalEditar(${g.id})">✏️</button>
    <button onclick="eliminarGrupo(${g.id})">🗑</button>
</td>

</tr>
`)
})

}

async function guardarGrupo(){

const datos={

programa:document.getElementById("programa").value,
semestre:document.getElementById("semestre").value,
grupo:document.getElementById("grupo").value,
tipo:document.getElementById("tipo").value,
alumnos:document.getElementById("alumnos").value

}

const respuesta = await fetch("/agregar_grupo",{

method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify(datos)

})

alert(await respuesta.text())

cargarGrupos()

}

async function guardarGrupo() {
    const id = document.getElementById("grupoId").value;

    const datos = {
        programa: document.getElementById("programa").value,
        semestre: document.getElementById("semestre").value,
        grupo: document.getElementById("grupo").value,
        tipo: document.getElementById("tipo").value,
        alumnos: document.getElementById("alumnos").value
    };

    let url = "/agregar_grupo";

    if (id) {
        // Es edición
        datos.id = id;
        url = "/editar_grupo";
    }

    const respuesta = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos)
    });

    alert(await respuesta.text());

    // Limpiar inputs
    document.getElementById("programa").value = "";
    document.getElementById("semestre").value = "";
    document.getElementById("grupo").value = "";
    document.getElementById("tipo").value = "";
    document.getElementById("alumnos").value = "";
    document.getElementById("grupoId").value = "";
    document.getElementById("btnGuardar").textContent = "Guardar";

    cargarGrupos();
}

async function cargarProgramas(){

const respuesta = await fetch("/listar_programas")

const programas = await respuesta.json()

const lista = document.getElementById("listaProgramas")

lista.innerHTML=""

programas.forEach(p=>{

lista.insertAdjacentHTML("beforeend",
`<option value="${p}">`
)

})

}

async function importarExcel(){

const archivo = document.getElementById("archivoExcel").files[0]

if(!archivo){
alert("Seleccione archivo")
return
}

const formData = new FormData()

formData.append("archivo",archivo)

const respuesta = await fetch("/importar_grupos",{

method:"POST",
body:formData

})

alert(await respuesta.text())

cargarGrupos()

}

function buscarGrupo(){

const texto=document
.getElementById("buscadorgrupos")
.value
.toLowerCase()

const filtrados=grupos.filter(g=>

g.grupo.toLowerCase().includes(texto) ||
g.programa.toLowerCase().includes(texto)

)

mostrarGrupos(filtrados)

}

document.addEventListener("DOMContentLoaded",function(){

cargarGrupos()
cargarProgramas()
cargarSalones()

document
.getElementById("buscadorgrupos")
.addEventListener("input",buscarGrupo)

document
.getElementById("edificio")
.addEventListener("change",filtrarSalones)

})

function editarGrupo(id) {
    // Buscar grupo en la lista cargada
    const grupo = grupos.find(g => g.id === id);
    if (!grupo) return;

    // Llenar los inputs
    document.getElementById("programa").value = grupo.programa;
    document.getElementById("semestre").value = grupo.semestre;
    document.getElementById("grupo").value = grupo.grupo;
    document.getElementById("tipo").value = grupo.tipo;
    document.getElementById("alumnos").value = grupo.alumnos;

    // Guardar el id en un input oculto para saber que es edición
    document.getElementById("grupoId").value = id;

    // Cambiar el botón de Guardar a “Actualizar”
    document.getElementById("btnGuardar").textContent = "Actualizar";
}

function abrirModalEditar(id) {
    const grupo = grupos.find(g => g.id === id);
    if (!grupo) return;

    // Llenar inputs del modal
    document.getElementById("editarPrograma").value = grupo.programa;
    document.getElementById("editarSemestre").value = grupo.semestre;
    document.getElementById("editarGrupo").value = grupo.grupo;
    document.getElementById("editarTipo").value = grupo.tipo;
    document.getElementById("editarAlumnos").value = grupo.alumnos;

    // Guardar id del grupo para la edición
    document.getElementById("grupoId").value = id;

    // Mostrar modal
    document.getElementById("modalEditarGrupo").style.display = "block";
}

function cerrarModal() {
    document.getElementById("modalEditarGrupo").style.display = "none";
}

async function guardarEdicion() {
    const id = document.getElementById("grupoId").value;
    if (!id) return;

    const datos = {
        id: id,
        programa: document.getElementById("editarPrograma").value,
        semestre: document.getElementById("editarSemestre").value,
        grupo: document.getElementById("editarGrupo").value,
        tipo: document.getElementById("editarTipo").value,
        alumnos: document.getElementById("editarAlumnos").value
    };

    const respuesta = await fetch("/editar_grupo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos)
    });

    alert(await respuesta.text());

    cerrarModal();
    cargarGrupos();
}