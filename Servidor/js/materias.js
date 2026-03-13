let materias=[]

function volver(){
    window.location.href="/admin.html"
}

function cerrarSesion(){
    window.location.href="/index.html"
}


async function cargarMaterias(){

const respuesta = await fetch("/listar_materias")

materias = await respuesta.json()

mostrarMaterias(materias)

}

function mostrarMaterias(lista){

const tabla=document.querySelector("#tablaMaterias tbody")

tabla.innerHTML=""

lista.forEach(m=>{

tabla.insertAdjacentHTML("beforeend",`

<tr>
<td>${m.programa}</td>
<td>${m.materia}</td>
<td>${m.continuidad}</td>
<td>${m.creditos}</td>

<td>
<button onclick="editarMateria(${m.id})">✏️</button>
<button onclick="eliminarMateria(${m.id})">🗑</button>
</td>

</tr>

`)

})

}

async function guardarMateria(){

const datos={

programa:document.getElementById("programa").value,
materia:document.getElementById("materia").value,
continuidad:document.getElementById("continuidad").value,
creditos:document.getElementById("creditos").value

}

const respuesta = await fetch("/agregar_materia",{

method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify(datos)

})

alert(await respuesta.text())

cargarMaterias()

}

async function eliminarMateria(id){

if(!confirm("Eliminar materia")) return

const respuesta=await fetch("/eliminar_materia",{

method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({id:id})

})

alert(await respuesta.text())

cargarMaterias()

}

async function cargarProgramas(){

const respuesta = await fetch("/listar_programas")

if(!respuesta.ok) return

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
alert("Seleccione un archivo Excel")
return
}

const formData = new FormData()

formData.append("archivo",archivo)

const respuesta = await fetch("/importar_materias",{

method:"POST",
body:formData

})

const texto = await respuesta.text()

alert(texto)

cargarMaterias()

}

function buscarMateria(){

const texto = document
.getElementById("buscadormaterias")
.value
.toLowerCase()

const filtradas = materias.filter(m=>
m.materia.toLowerCase().includes(texto) ||
m.programa.toLowerCase().includes(texto)
)

mostrarMaterias(filtradas)

}

document.addEventListener("DOMContentLoaded",function(){

cargarMaterias()
cargarProgramas()

document
.getElementById("buscadormaterias")
.addEventListener("input",buscarMateria)

})