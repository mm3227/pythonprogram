window.onload=function(){
cargarMaterias()
}

function volver(){
window.location.href="/users.html"
}

function cerrarSesion(){
window.location.href="/index.html"
}

function cargarMaterias(){

fetch("/listar_materias_usuario")

.then(res=>res.json())

.then(datos=>{

let tabla=document.getElementById("tabla")

tabla.innerHTML=""

datos.forEach(m=>{

let fila=`

<tr>

<td>${m.materia}</td>
<td>${m.continuidad}</td>
<td>${m.creditos}</td>

<td>

<button onclick="editarMateria(${m.id},'${m.materia}','${m.continuidad}',${m.creditos})">
✏️ Editar
</button>

<button onclick="eliminarMateria(${m.id})">
🗑 Eliminar
</button>

</td>

</tr>
`

tabla.innerHTML+=fila

})

})

}

function agregarMateria(){

let materia=document.getElementById("materia").value
let continuidad=document.getElementById("continuidad").value
let creditos=document.getElementById("creditos").value

fetch("/agregar_materia_usuario",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({

materia:materia,
continuidad:continuidad,
creditos:creditos

})

})

.then(res=>res.text())
.then(res=>{

alert(res)

cargarMaterias()

})

}

function eliminarMateria(id){

fetch("/eliminar_materia_usuario",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({id:id})

})

.then(res=>res.text())
.then(res=>{

alert(res)

cargarMaterias()

})

}

function editarMateria(id,materia,continuidad,creditos){

let nuevaMateria=prompt("Materia:",materia)
if(nuevaMateria==null) return

let nuevaContinuidad=prompt("Continuidad:",continuidad)
if(nuevaContinuidad==null) return

let nuevosCreditos=prompt("Creditos:",creditos)
if(nuevosCreditos==null) return

fetch("/editar_materia_usuario",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({

id:id,
materia:nuevaMateria,
continuidad:nuevaContinuidad,
creditos:nuevosCreditos

})

})

.then(res=>res.text())
.then(res=>{

alert(res)

cargarMaterias()

})

}

function importarExcel(){

let archivo=document.getElementById("archivoExcel").files[0]

if(!archivo){
alert("Selecciona un archivo")
return
}

let formData=new FormData()

formData.append("archivo",archivo)

fetch("/importar_materias_usuario",{

method:"POST",
body:formData

})
.then(res=>res.text())
.then(res=>{

alert(res)

cargarMaterias()

})

}

function buscarMateria(){

let filtro=document.getElementById("buscadorMaterias").value.toLowerCase()

let filas=document.querySelectorAll("#tabla tr")

filas.forEach(fila=>{

let texto=fila.innerText.toLowerCase()

fila.style.display = texto.includes(filtro) ? "" : "none"

})

}