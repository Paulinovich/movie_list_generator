// ----- MOVIESELECTOR ----- //
// writing and updating name of choosing person
var indexNames=0;
var names = {{names|tojson}};
var name = names[indexNames];
document.getElementById("who_picks").innerHTML = name;

function nextName(){
    if (indexNames < names.length-1){
        indexNames++;
        name = names[indexNames];
    }
}

function updateName(){
    nextName();
    document.getElementById("who_picks").innerHTML = name;
}

// movie information display and hiding
// converting 'information' into json representation with proper escaping of special characters for html
var movie_information = JSON.parse('{{information | tojson | safe}}');

function popup(id){
    var el = document.getElementById("\""+id+"\"");
    el.classList.toggle("show");
}

function eliminate(id){
    var el = document.getElementById("\""+id+"\"");
    el.classList.add("eliminated");
}