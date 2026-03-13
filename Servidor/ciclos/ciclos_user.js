window.onload = function(){
    cargarCiclos()
}

function volver(){
    window.location.href="/users.html"
}

function cerrarSesion(){
    window.location.href="/index.html"
}

function cargarCiclos(){

fetch("/listar_ciclos")
.then(res=>res.json())
.then(datos=>{

let lista=document.getElementById("listaCiclos")

lista.innerHTML=""

datos.forEach(ciclo=>{

let opcion=document.createElement("option")
opcion.text=ciclo
lista.add(opcion)

})

})

}

function crearCiclo(){

let nombre=prompt("Nombre del ciclo escolar")

if(!nombre) return

fetch("/crear_ciclo",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
ciclo:nombre
})

})
.then(res=>res.text())
.then(res=>{

alert(res)

cargarCiclos()

})

}

function eliminarCiclo(){

let lista=document.getElementById("listaCiclos")
let ciclo=lista.value

if(!ciclo){
alert("Seleccione un ciclo")
return
}

fetch("/eliminar_ciclo",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
ciclo:ciclo
})

})
.then(res=>res.text())
.then(res=>{

alert(res)

cargarCiclos()

})

}

function abrirCiclo(){

let lista=document.getElementById("listaCiclos")
let ciclo=lista.value

if(!ciclo){
alert("Seleccione un ciclo")
return
}

window.location.href="/htmlusers/gestorhorarios_user.html"

}