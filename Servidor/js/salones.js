let salones = []

function volver(){
window.location.href="/admin.html"
}

function cerrarSesion(){
window.location.href="/index.html"
}

async function cargarSalones(){

try{

const respuesta = await fetch("/listar_salones")

if(!respuesta.ok) throw new Error("Error cargando salones")

salones = await respuesta.json()

mostrarSalones(salones)

}catch(e){

console.error(e)
alert("No se pudieron cargar los salones")

}

}

function mostrarSalones(lista){

const tabla = document.querySelector("#tablaSalones tbody")

if(!tabla) return

tabla.innerHTML=""

lista.forEach(s=>{

tabla.insertAdjacentHTML("beforeend",`

<tr>

<td>${s.programa || ""}</td>
<td>${s.edificio || ""}</td>
<td>${s.salon || ""}</td>
<td>${s.capacidad || 0}</td>

<td>

<button onclick="editarSalon(${s.id})">✏️</button> <button onclick="eliminarSalon(${s.id})">🗑</button>

</td>

</tr>

`)

})

}

async function guardarSalon(){

const form = document.getElementById("formSalon")

const id = form.dataset.id

const datos = {

programa: document.getElementById("programa").value.trim(),
edificio: document.getElementById("edificio").value.trim(),
salon: document.getElementById("salon").value.trim(),
capacidad: document.getElementById("capacidad").value

}

if(!datos.programa || !datos.salon){

alert("Programa y salón son obligatorios")
return

}

if(id){
datos.id = id
}

const url = id ? "/editar_salon" : "/agregar_salon"

try{

const respuesta = await fetch(url,{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify(datos)
})

alert(await respuesta.text())

form.reset()
form.dataset.id=""

cargarSalones()

}catch(e){

console.error(e)
alert("Error guardando salón")

}

}

async function eliminarSalon(id){

if(!confirm("Eliminar salón")) return

try{

const respuesta = await fetch("/eliminar_salon",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({id:id})
})

alert(await respuesta.text())

cargarSalones()

}catch(e){

console.error(e)
alert("Error eliminando salón")

}

}

function editarSalon(id){

const s = salones.find(x => x.id == id)

if(!s) return

document.getElementById("programa").value = s.programa || ""
document.getElementById("edificio").value = s.edificio || ""
document.getElementById("salon").value = s.salon || ""
document.getElementById("capacidad").value = s.capacidad || ""

document.getElementById("formSalon").dataset.id = id

window.scrollTo({top:0,behavior:"smooth"})

}

function buscarSalon(){

const input = document.getElementById("buscadorSalones")

if(!input) return

const texto = input.value.toLowerCase()

const filtrados = salones.filter(s =>

(s.programa || "").toLowerCase().includes(texto) ||
(s.edificio || "").toLowerCase().includes(texto) ||
(s.salon || "").toLowerCase().includes(texto) ||
String(s.capacidad || "").includes(texto)

)

mostrarSalones(filtrados)

}

async function cargarProgramas(){

try{

const respuesta = await fetch("/listar_programas")

if(!respuesta.ok) return

const programas = await respuesta.json()

const lista = document.getElementById("listaProgramas")

if(!lista) return

lista.innerHTML=""

programas.forEach(p=>{

lista.insertAdjacentHTML("beforeend",
`<option value="${p}">`
)

})

}catch(e){

console.error(e)

}

}

async function importarExcel(){
    const inputFile = document.getElementById("archivoExcel");
    if (!inputFile || inputFile.files.length === 0) {
        alert("Seleccione un archivo Excel");
        return;
    }
    const archivo = inputFile.files[0];
    const formData = new FormData();
    formData.append("archivo", archivo);

    try {
        const respuesta = await fetch("/importar_salones", {
            method: "POST",
            body: formData
        });
        const texto = await respuesta.text();
        alert(texto);
        inputFile.value = ""; // Limpiar el input
        cargarSalones(); // Recargar la tabla
    } catch(e) {
        console.error(e);
        alert("Error importando Excel");
    }
}

document.addEventListener("DOMContentLoaded",function(){

cargarSalones()

cargarProgramas()

const buscador = document.getElementById("buscadorSalones")

if(buscador){
buscador.addEventListener("input",buscarSalon)
}

})
