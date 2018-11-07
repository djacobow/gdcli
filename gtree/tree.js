var google_config = {
    discoveryDocs: ["https://www.googleapis.com/discovery/v1/apis/drive/v3/rest"],
    // clientId and scope coming from meta tags in page and filled in already by the auth process
};

var pi = new ProgInfo();
var cache = new Cache();
var fl = new FileLister(cache);
var fr = new FileRecurser(fl);

var flattenHierHelper = function(flat, hier, path) {
    hier.forEach((item) => {
        var ipath = path.concat([item.name]);
        item.path = ipath;
        if (item.children && item.children.length) {
            flattenHierHelper(flat, item.children, ipath);
        }
        flat.push(item);
    });
};


var flattenHier = function(hier) {
    var flat = [];
    var path = [];
    flattenHierHelper(flat, hier, path);
    flat.forEach((item) => { delete item.children; });
    flat.sort((a,b) => {
        var ap = a.path.join('/');
        var bp = b.path.join('/');
        return ap.localeCompare(bp);
    });
    return flat;
}

var Resulter = function(target) {
    this.target = target;
}
Resulter.prototype.show = function(flat) {
   
    var table = cr('table');
    table.id = 'result_table';
    var row = cr('tr');
    var nth = cr('th',null,'path');
    var dth = cr('th',null,'modified time');
    var tth = cr('th',null,'type');
    var sth = cr('th',null,'size');
    var oth = cr('th',null,'owner(s)');
    appendChildren(row,[nth,dth,tth,sth,oth]);
    table.appendChild(row);
 
    flat.forEach((f) => {
        row = cr('tr');

        var ntd = cr('td');
        var spans = [];
        for (var i=0;i<f.path.length-1;i++) {
            spans.push(cr('span',null,f.path[i]));
            spans.push(cr('span',null,'/'));
        }
        var na = cr('a');
        na.innerText = f.path[f.path.length-1];
        na.href = f.webViewLink;
        na.target = '_blank';
        spans.push(na);
        if (f.mimeType == 'application/vnd.google-apps.folder') {
            spans.push(cr('span',null,'/'));
        }
        appendChildren(ntd,spans); 
        row.appendChild(ntd);

        var ttd = cr('td');
        var dt = new Date(f.modifiedTime);
        ttd.innerText = dt.toLocaleString();
        row.append(ttd);
 
        var mtd = cr('td');
        mtd.innerText = f.mimeType || '';
        row.append(mtd);

        var std = cr('td');
        std.innerText = f.size || '';
        row.append(std);

        var otd = cr('td');
        if (f.owners && f.owners.length) {
           otd.innerText = f.owners.map((o) => { return o.displayName; }).join(', ');
        }
        row.append(otd);
 
        table.appendChild(row);
    });
    this.target.appendChild(table);
    this.target.appendChild(cr('br'));
    this.target.appendChild(cr('br'));
    this.target.style.display = 'block';
}
Resulter.prototype.unshow = function() {
    ['result_table','save_button'].forEach((n) => {
        var old = document.getElementById(n);
        if (old) {
            old.parentNode.removeChild(old);
        }
    });
    this.target.style.display = 'none';
}

var listFiles = function() {
    var rs = new Resulter(gebi('results'));
    rs.unshow();
    pi.reset();
    sb.setMode('cancel');
    var parent_fileId = gebi('parent').value;
    var max_depth = parseInt(gebi('maxdepth').value);
    fr.run(parent_fileId, max_depth, (files) => {
        var flattened = flattenHier(files);
        pi.done();
        var exp = new Exporter({
            button: {
                id: 'save_button',
                label: 'Save as .csv',
            },
        });
        exp.init(flattened, gebi('results'));
        rs.show(flattened);
        sb.setMode('scan');
    });
};


var ScanButton = function() {
    this.mode = 'scan';
    this.rbutn = gebi('run');
    this.rbutn.value = 'scan';
    this.rbutn.addEventListener('click',(ev) => {
        if (this.mode == 'scan') {
            listFiles();
            gebi('rundiv').style.display = 'block';
        } else {
            fr.stop();
            this.setMode('scan');
        }
    });
};
ScanButton.prototype.setMode = function(m) {
    this.mode = m;
    this.rbutn.value = m == 'scan' ? 'scan' : 'cancel scan';
}


var sb = new ScanButton();

var signOut = function() {
    gapi.auth2.getAuthInstance().signOut();
    gebi('signout_button').style.display = 'none';
    gebi('setupdiv').style.display = 'none';
    gebi('rundiv').style.display = 'none';
};
function onSignOnFailure() {
    signOut();    
}

function onSignIn(gUser) {
    var sob = gebi('signout_button');
    sob.addEventListener('click', signOut);
    sob.style.display = 'block';
    
    if (gUser) {

        var sob = gebi('signout_button');
        sob.style.display = 'block';
  
        gapi.load('client:auth2',() => {
            gapi.client.init(google_config).then(() => {
                var au2 = gapi.auth2.getAuthInstance();
                var si  = au2.isSignedIn.get();
                if (si) {
                    sb.setMode('scan');
                    var cbutn = gebi('clear');
                    cbutn.value = 'reset cache';
                    cbutn.addEventListener('click',(ev) => {
                        cache.clear();
                    });
                    gebi('setupdiv').style.display = 'block';
                }
            });
        });
    } else {
        gebi('setupdiv').style.display = 'none';
        gebi('rundiv').style.display = 'none';
    }
}

