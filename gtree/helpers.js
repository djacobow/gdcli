function cr(what,clsn = null, it = null) {
    var x = document.createElement(what);
    if (clsn) {
        x.className = clsn;
    }
    if (it) {
        x.innerText = it;
    }
    return x;
}

function gebi(en) {
    return document.getElementById(en);
}

function appendChildren(elem, elems, splitText = null) {
    for (var i=0;i<elems.length;i++) {
        elem.appendChild(elems[i]);
        if ((splitText !== null) && (i < (elems.length-1))) {
            elem.appendChild(cr('span',null,splitText));
        }
    }
};

//Returns true if it is a DOM node
function isNode(o){
  return (
    typeof Node === "object" ? o instanceof Node : 
    o && typeof o === "object" && typeof o.nodeType === "number" && typeof o.nodeName==="string"
  );
}

//Returns true if it is a DOM element    
function isElement(o){
  return (
    typeof HTMLElement === "object" ? o instanceof HTMLElement : //DOM2
    o && typeof o === "object" && o !== null && o.nodeType === 1 && typeof o.nodeName==="string"
);
}

var addRemoveClasses = function(elem, to_add, to_remove) {
    if (Array.isArray(to_add)) {
        to_add.forEach((c) => { elem.classList.add(c); });
    } else if (to_add) {
        elem.classList.add(to_add);
    }
    if (Array.isArray(to_remove)) {
        to_remove.forEach((c) => { elem.classList.remove(c); });
    } else if (to_remove) {
        elem.classList.remove(to_remove);
    }
    return elem;
};

var SymplDateToFriendly = function(sd) {
    if (typeof sd != 'string') sd = sd.toString();
    var m = sd.match(/^(\d{4})(\d{2})(\d{2})$/);
    var fd = null;
    if (m) {
        var year = parseInt(m[1]);
        var mo   = parseInt(m[2]);
        var day  = parseInt(m[3]);
        if ((mo == 1) && (day == 1)) {
            // probably not reall 1/1 but just unknown date
            fd = year.toString();
        } else {
            var months = [
                'January',
                'February',
                'March',
                'April',
                'May',
                'June',
                'July',
                'August',
                'September',
                'Octoboer',
                'November',
                'December',
            ];
            fd = months[mo-1] + ' ' + day.toString() + ', ' + year.toString();
        }
    }
    return fd || sd;
};


// a very minimalist asyncSeries type of fn.
var doAsyncThings = function(things, action, final_cb) {
    var outputs = [];
    things.forEach((thing) => {
        action(thing,(err,res) => {
            outputs.push([thing,err,res]);
            if (outputs.length == things.length) {
                final_cb(outputs);
            }
        });
    });
};


// a very minimalist syncSeries type of fn                                     
var doSyncThings = function(things, action, final_cb) {                        
    var outputs = [];                                                          
    var things_c = things.slice(0);
    var doNext = function() {                                                  
        var current_thing = things_c.pop();                                      
        if (current_thing) {                                                   
            action(current_thing,(err,res) => {                                
                outputs.push([current_thing,err,res]);                         
                doNext();                                                      
            });                                                                
        } else {                                                               
            return final_cb(outputs);                                          
        }                                                                      
    };                                                                         
                                                                               
    doNext();                                                                  
};


var jss = function(x) {
    return JSON.stringify(x,null,2);
}

function removeChildren(e) {
    if (typeof e === 'string') {
        e = document.getElementById(e);
    }
    while (e.firstChild) e.removeChild(e.firstChild);
    return e;
}

