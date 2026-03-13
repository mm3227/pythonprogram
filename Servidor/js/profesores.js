let profesores = []

function volver(){
    window.location.href="/admin.html"
}

function cerrarSesion(){
    window.location.href="/index.html"
}

async function cargarProfesores(){

    try{

        const respuesta = await fetch("/listar_profesores")

        if(!respuesta.ok){
            console.error("Error al cargar profesores")
            return
        }

        profesores = await respuesta.json()

        mostrarProfesores(profesores)

    }catch(error){
        console.error("Error:", error)
    }
}

async function cargarProgramas(){

    try{

        const respuesta = await fetch("/listar_programas")

        if(!respuesta.ok){
            console.error("Error al cargar programas")
            return
        }

        const programas = await respuesta.json()

        const lista = document.getElementById("listaProgramas")

        lista.innerHTML=""

        programas.forEach(p=>{
            lista.insertAdjacentHTML("beforeend", `<option value="${p}">`)
        })

    }catch(error){
        console.error("Error:", error)
    }
}

document.addEventListener("DOMContentLoaded", function(){

    cargarProfesores()
    cargarProgramas()

    document
    .getElementById("buscadorProfesores")
    .addEventListener("input", buscarProfesor)

})

function mostrarProfesores(lista){

    const tabla = document.querySelector("#tablaProfesores tbody")

    tabla.innerHTML=""

    lista.forEach(p=>{

        tabla.insertAdjacentHTML("beforeend",`
        <tr>
        <td style="display:none;">${p.id}</td>
        <td>${p.programa}</td>
        <td>${p.nombre}</td>
        <td>${p.contratacion}</td>
        <td>${p.telefono}</td>
        <td>${p.email}</td>
        <td>
        <button onclick="editarProfesor(${p.id})">✏️</button>
        <button onclick="eliminarProfesor(${p.id})">🗑</button>
        </td>
        </tr>
        `)

    })
}

function buscarProfesor(){

const texto = document
.getElementById("buscadorProfesores")
.value
.toLowerCase()
.trim()

if(texto === ""){
    mostrarProfesores(profesores)
    return
}

const filtrados = profesores.filter(p => {

const nombre = (p.nombre || "").toLowerCase()
const programa = (p.programa || "").toLowerCase()
const email = (p.email || "").toLowerCase()
const telefono = (p.telefono || "").toLowerCase()

return nombre.includes(texto) ||
       programa.includes(texto) ||
       email.includes(texto) ||
       telefono.includes(texto)
})

mostrarProfesores(filtrados)

}

async function guardarProfesor(){

    const form = document.getElementById("formProfesor")
    const id = form.dataset.id || null

    const datos = {
        programa: document.getElementById("programa").value.trim(),
        nombre: document.getElementById("nombre").value.trim(),
        contratacion: document.getElementById("contratacion").value.trim(),
        telefono: document.getElementById("telefono").value.trim(),
        email: document.getElementById("email").value.trim()
    }

    if(!datos.programa || !datos.nombre){
        alert("Programa y nombre son obligatorios")
        return
    }

    if(id){
        datos.id = parseInt(id)
    }

    const url = id ? "/editar_profesor" : "/agregar_profesor"

    try{

        const respuesta = await fetch(url,{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body: JSON.stringify(datos)
        })

        const texto = await respuesta.text()

        alert(texto)

        limpiarFormulario()
        cargarProfesores()

    }catch(error){
        console.error(error)
        alert("Error al guardar profesor")
    }

}

function limpiarFormulario(){

    document.getElementById("programa").value=""
    document.getElementById("nombre").value=""
    document.getElementById("contratacion").value=""
    document.getElementById("telefono").value=""
    document.getElementById("email").value=""

    delete document.getElementById("formProfesor").dataset.id

}

async function eliminarProfesor(id){

    if(!confirm("¿Eliminar este profesor?")) return

    const respuesta = await fetch("/eliminar_profesor",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({id:id})
    })

    const texto = await respuesta.text()

    alert(texto)

    cargarProfesores()

}

function editarProfesor(id){

    const profesor = profesores.find(p => p.id === id)

    if(!profesor) return

    document.getElementById("programa").value = profesor.programa
    document.getElementById("nombre").value = profesor.nombre
    document.getElementById("contratacion").value = profesor.contratacion
    document.getElementById("telefono").value = profesor.telefono
    document.getElementById("email").value = profesor.email

    document.getElementById("formProfesor").dataset.id = id

}

async function importarExcel(){

    const archivo = document.getElementById("archivoExcel").files[0]

    if(!archivo){
        alert("Seleccione un archivo")
        return
    }

    const formData = new FormData()

    formData.append("archivo",archivo)

    const respuesta = await fetch("/importar_profesores",{
        method:"POST",
        body:formData
    })

    const texto = await respuesta.text()

    alert(texto)

    cargarProfesores()

}