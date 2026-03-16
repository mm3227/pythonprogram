let grupos = []
let pagina = 1
const limite = 10
let textoBusqueda = ""

let total = 0

function volver(){
    window.location.href="/users.html"
}

function cerrarSesion(){
    window.location.href="/index.html"
}

async function cargarGrupos(){

    const respuesta = await fetch(
        `/listar_grupos_usuario?pagina=${pagina}&limite=${limite}&buscar=${textoBusqueda}`
    )

    const resultado = await respuesta.json()

    grupos = resultado.datos
    total = resultado.total

    mostrarGrupos(grupos)
    actualizarPaginacion()
}

function mostrarGrupos(lista){

const tabla=document.querySelector("#tablaGrupos tbody")

tabla.innerHTML=""

lista.forEach(g=>{

tabla.insertAdjacentHTML("beforeend",`

<tr>
<td>${g.semestre}</td>
<td>${g.grupo}</td>
<td>${g.tipo}</td>
<td>${g.alumnos}</td>
<td>${g.materias}</td>

<td>
    <button onclick="abrirModalEditar(${g.id})">✏️</button>
    <button onclick="eliminarGrupo(${g.id})">🗑</button>
</td>

</tr>
`)
})

}

async function guardarGrupo() {

    const id = document.getElementById("grupoId").value

    const datos = {
        semestre: document.getElementById("semestre").value,
        grupo: document.getElementById("grupo").value,
        tipo: document.getElementById("tipo").value,
        alumnos: document.getElementById("alumnos").value,
        materias: document.getElementById("materias").value
    }

    let url = "/agregar_grupo_usuario"

    if (id) {
        datos.id = id
        url = "/editar_grupo_usuario"
    }

    const respuesta = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos)
    })

    alert(await respuesta.text())

    // limpiar
    document.getElementById("semestre").value = ""
    document.getElementById("grupo").value = ""
    document.getElementById("tipo").value = ""
    document.getElementById("alumnos").value = ""
    document.getElementById("materias").value = ""
    document.getElementById("grupoId").value = ""   
    document.getElementById("btnGuardar").textContent = "Guardar"

    cargarGrupos()
}

async function importarExcel(){

    const archivo = document.getElementById("archivoExcel").files[0]

    if(!archivo){
        alert("Seleccione archivo")
        return
    }

    const formData = new FormData()
    formData.append("archivo", archivo)

    const respuesta = await fetch("/importar_grupos_usuario",{
        method:"POST",
        body:formData
    })

    alert(await respuesta.text())
    cargarGrupos()
}

function buscarGrupo(){

    textoBusqueda = document
        .getElementById("buscadorgrupos")
        .value

    pagina = 1  //reiniciar página
    cargarGrupos()
}

  

document.addEventListener("DOMContentLoaded",function(){
    cargarGrupos()

    document
    .getElementById("buscadorgrupos")
    .addEventListener("input",buscarGrupo)
})

function abrirModalEditar(id) {

    const grupo = grupos.find(g => g.id === id)
    if (!grupo) return

    document.getElementById("editarSemestre").value = grupo.semestre
    document.getElementById("editarGrupo").value = grupo.grupo
    document.getElementById("editarTipo").value = grupo.tipo
    document.getElementById("editarAlumnos").value = grupo.alumnos
    document.getElementById("editarMaterias").value = grupo.materias

    document.getElementById("grupoId").value = id

    document.getElementById("modalEditarGrupo").style.display = "block"
}

function cerrarModal() {

    document.getElementById("modalEditarGrupo").style.display = "none"

    document.getElementById("editarSemestre").value = ""
    document.getElementById("editarGrupo").value = ""
    document.getElementById("editarTipo").value = ""
    document.getElementById("editarAlumnos").value = ""
    document.getElementById("editarMaterias").value = ""
    document.getElementById("grupoId").value = ""
    
}

async function eliminarGrupo(id){

    if(!confirm("¿Eliminar grupo?")) return

    const respuesta = await fetch("/eliminar_grupo_usuario",{
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body: JSON.stringify({ id })
    })

    alert(await respuesta.text())
    cargarGrupos()
}

async function guardarEdicion() {

    const id = document.getElementById("grupoId").value
    if (!id) return

    const datos = {
        id: id,
        semestre: document.getElementById("editarSemestre").value,
        grupo: document.getElementById("editarGrupo").value,
        tipo: document.getElementById("editarTipo").value,
        alumnos: document.getElementById("editarAlumnos").value,
        materias: document.getElementById("editarMaterias").value
    }

    const respuesta = await fetch("/editar_grupo_usuario", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos)
    })

    alert(await respuesta.text())

    cerrarModal()
    cargarGrupos()
}

function actualizarPaginacion(){

    const totalPaginas = Math.ceil(total / limite)

    document.getElementById("infoPagina").textContent =
    `Página ${pagina} de ${totalPaginas}`
}

function siguiente(){
    if(pagina * limite < total){
        pagina++
        cargarGrupos()
    }
}

function anterior(){
    if(pagina > 1){
        pagina--
        cargarGrupos()
    }
}