window.onload=function(){
cargarProfesores()
}

function volver(){
window.location.href="/users.html"
}

function cerrarSesion(){
window.location.href="/index.html"
}

function cargarProfesores(){

fetch("/listar_profesores_usuario")

.then(res=>res.json())

.then(datos=>{

let tabla=document.getElementById("tabla")

tabla.innerHTML=""

datos.forEach(p=>{

let fila=`

<tr>

<td>${p.nombre}</td>
<td>${p.contratacion}</td>
<td>${p.telefono}</td>
<td>${p.email}</td>

<td>

<button onclick="editarProfesor(${p.id},'${p.nombre}','${p.contratacion}','${p.telefono}','${p.email}')">

✏️ Editar

</button>

<button onclick="eliminarProfesor(${p.id})">

🗑 Eliminar

</button>

</td>

</tr>
`

tabla.innerHTML+=fila

})

})

}

function agregarProfesor(){

let nombre=document.getElementById("nombre").value
let contratacion=document.getElementById("contratacion").value
let telefono=document.getElementById("telefono").value
let email=document.getElementById("email").value

fetch("/agregar_profesor_usuario",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({

nombre:nombre,
contratacion:contratacion,
telefono:telefono,
email:email

})

})

.then(res=>res.text())
.then(res=>{

alert(res)

cargarProfesores()

})

}

function eliminarProfesor(id){

fetch("/eliminar_profesor_usuario",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({id:id})

})

.then(res=>res.text())
.then(res=>{

alert(res)

cargarProfesores()

})

}

function editarProfesor(id,nombre,contratacion,telefono,email){

let nuevoNombre=prompt("Nombre:",nombre)
if(nuevoNombre==null) return

let nuevaContratacion=prompt("Contratación:",contratacion)
if(nuevaContratacion==null) return

let nuevoTelefono=prompt("Telefono:",telefono)
if(nuevoTelefono==null) return

let nuevoEmail=prompt("Email:",email)
if(nuevoEmail==null) return

fetch("/editar_profesor_usuario",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({

id:id,
nombre:nuevoNombre,
contratacion:nuevaContratacion,
telefono:nuevoTelefono,
email:nuevoEmail

})

})

.then(res=>res.text())
.then(res=>{

alert(res)

cargarProfesores()

})

}

function importarExcel(){

let archivo=document.getElementById("archivoExcel").files[0]

let formData=new FormData()

formData.append("archivo",archivo)

fetch("/importar_profesores_usuario",{

method:"POST",
body:formData

})

.then(res=>res.text())
.then(res=>{

alert(res)

cargarProfesores()

})

}

function buscarProfesor(){

let filtro=document.getElementById("buscadorProfesores").value.toLowerCase()

let filas=document.querySelectorAll("#tabla tr")

filas.forEach(fila=>{

let texto=fila.innerText.toLowerCase()

fila.style.display = texto.includes(filtro) ? "" : "none"

})

}