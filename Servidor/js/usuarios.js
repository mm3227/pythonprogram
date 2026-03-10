function volver(){
window.location.href="/admin.html"
}

function cerrarSesion(){
window.location.href="/index.html"
}

async function cargarUsuarios(){

const respuesta = await fetch("/listar_usuarios")
const datos = await respuesta.json()

const tabla = document.querySelector("#tablaUsuarios tbody")

tabla.innerHTML=""

datos.forEach(u=>{

tabla.innerHTML += `
<tr>
<td>${u.id}</td>
<td>${u.usuario}</td>
<td>${u.programa}</td>
<td>${u.tipo_usuario}</td>
<td>
<button class="btn-reset" onclick="resetPassword(${u.id})">🔑 Reset</button>
<button class="btn-eliminar" onclick="eliminarUsuario(${u.id})">🗑 Eliminar</button>
</td>
</tr>
`

})

}

async function resetPassword(id){

const respuesta = await fetch("/reset_password",{
method:"POST",
headers:{ "Content-Type":"application/json" },
body:JSON.stringify({ id:id })
})

const datos = await respuesta.json()

alert("Nueva contraseña: " + datos.password)

}

async function eliminarUsuario(id){

if(!confirm("¿Eliminar este usuario?")){
return
}

const respuesta = await fetch("/eliminar_usuario",{
method:"POST",
headers:{ "Content-Type":"application/json" },
body:JSON.stringify({ id:id })
})

const texto = await respuesta.text()

alert(texto)

cargarUsuarios()

}

document.getElementById("formUsuario").addEventListener("submit", async function(e){

e.preventDefault()

const usuario = document.getElementById("usuario").value
const programa = document.getElementById("programa").value
const password = document.getElementById("password").value

const respuesta = await fetch("/agregar_usuario",{
method:"POST",
headers:{ "Content-Type":"application/json" },
body:JSON.stringify({
usuario:usuario,
programa:programa,
password:password
})
})

const texto = await respuesta.text()

document.getElementById("resultado").innerText = texto

this.reset()

cargarUsuarios()

})

async function importarExcel(){

const archivo = document.getElementById("archivoExcel").files[0]

if(!archivo){
alert("Selecciona un archivo")
return
}

const formData = new FormData()
formData.append("archivo", archivo)

const respuesta = await fetch("/importar_usuarios",{
method:"POST",
body:formData
})

const texto = await respuesta.text()

document.getElementById("resultado").innerText = texto

cargarUsuarios()

}

document.addEventListener("DOMContentLoaded", function(){
cargarUsuarios()
})