let datos = []

window.onload = function(){
    cargarSalones()
}

function volver(){
    window.location.href="/users.html"
}

function cerrarSesion(){
    window.location.href="/index.html"
}

function cargarSalones(){

fetch("/listar_salones_usuario")
.then(res => res.json())
.then(datos => {

let tabla = document.getElementById("tabla")

tabla.innerHTML=""

datos.forEach(salon=>{

let fila = `
<tr>

<td>${salon.edificio}</td>
<td>${salon.salon}</td>
<td>${salon.capacidad}</td>

<td>

<button onclick="editarSalon(${salon.id},'${salon.edificio}','${salon.salon}',${salon.capacidad})">
✏️ Editar
</button>

<button onclick="eliminarSalon(${salon.id})">
🗑 Eliminar
</button>

</td>

</tr>
`

tabla.innerHTML += fila

})

})

}

function agregarSalon(){

let edificio = document.getElementById("edificio").value
let salon = document.getElementById("salon").value
let capacidad = document.getElementById("capacidad").value

fetch("/agregar_salon_usuario",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({

edificio:edificio,
salon:salon,
capacidad:capacidad

})

})

.then(res=>res.text())
.then(res=>{

alert(res)

cargarSalones()

})

}

function eliminarSalon(id){

fetch("/eliminar_salon_usuario",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({id:id})

})

.then(res=>res.text())
.then(res=>{

alert(res)

cargarSalones()

})

}

function buscarSalon(){

let filtro = document.getElementById("buscadorSalones").value.toLowerCase()

let filas = document.querySelectorAll("#tabla tr")

filas.forEach(fila=>{

let texto = fila.innerText.toLowerCase()

fila.style.display = texto.includes(filtro) ? "" : "none"

})

}

function importarExcel(){

let archivo = document.getElementById("archivoExcel").files[0]

let formData = new FormData()

formData.append("archivo",archivo)

fetch("/importar_salones_usuario",{

method:"POST",
body:formData

})
.then(res=>res.text())
.then(res=>{

alert(res)

cargarSalones()

})

}

function editarSalon(id, edificio, salon, capacidad){

let nuevoEdificio = prompt("Edificio:", edificio)
if(nuevoEdificio==null) return

let nuevoSalon = prompt("Salon:", salon)
if(nuevoSalon==null) return

let nuevaCapacidad = prompt("Capacidad:", capacidad)
if(nuevaCapacidad==null) return

fetch("/editar_salon_usuario",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({

id:id,
edificio:nuevoEdificio,
salon:nuevoSalon,
capacidad:nuevaCapacidad

})

})
.then(res=>res.text())
.then(res=>{

alert(res)

cargarSalones()

})

}