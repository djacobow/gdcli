/* jshint esversion:6 */

var Exporter = function(config) {
    this.config = config;
};

Exporter.prototype.init = function(data, target) {
    this.data = data;
    var btn = cr('button',
                 this.config.button.classname || 'export_button',
                 this.config.button.label || 'Export Data');
    btn.id = this.config.button.id || 'export_button';
    var info = cr('div')
    this.infodiv = info;
    btn.addEventListener('click',(ev) => {
        btn.disabled = true;
        btn.innerText = 'Please wait';
        info.innerText = 'working...';
        try {
            this.download();
        } catch (ex) {
            this.infodiv.innerText += ex.toString();
        }
        info.innerText += 'done.'
        btn.disabled = false;
        btn.innerText = this.config.button.label || 'Export Data';
    });
    target.appendChild(btn);
    target.appendChild(info)
};

Exporter.prototype.date = function() {
    var now = new Date();
    var year = now.getFullYear().toString();
    var month = (now.getMonth() + 1).toString();
    while (month.length < 2) month = '0' + month;
    var day = now.getDate().toString();
    while (day.length < 2) day = '0' + day;
    return year + month + day;
};

Exporter.prototype.arrayOfDictsToCSV = function(ary) {
    var keys = {};
    ary.forEach((row) => {
        Object.keys(row).forEach((kn) => {
            keys[kn] = 1;
        });
    });

    keys = Object.keys(keys);
    keys.sort();

    var escapeVal = function(val) {
        if (val === null) val = '';

        if (Array.isArray(val)) {
            if (val.length && (typeof val[0] == 'object')) {
                try {
                    val = JSON.stringify(val);
                } catch (ex) {
                    val = ex.toString();
                }
            } else {
                val = val.join('/');
            }
        } else if (typeof val == 'object') {
            try {
                val = JSON.stringify(val);
            } catch (ex) {
                val = ex.toString();
            }
        }

        if ((typeof val == 'string') && val.match(/[,"]/)) {
            val = val.replace(/"/g,'""');
            val = '"' + val + '"';
        }
        return val;
    };

    var oary = [];
    oary.push(keys.map((key) => { return escapeVal(key); }).join(','));

    ary.forEach((row) => {
        var rowary = keys.map((key) => { 
            return escapeVal(row.hasOwnProperty(key) ? row[key] : ''); 
        });
        oary.push(rowary.join(','));
    });
    return oary.join('\n');
};

Exporter.prototype.download = function() {
    var a = cr('a');
    var file = new Blob([ this.arrayOfDictsToCSV(this.data) ], {type: 'text/csv'});
    a.href = URL.createObjectURL(file);
    var fname = ['drive_tree_',
                 this.date(),
                 '.csv'].join('_');
    a.setAttribute('download', fname);
    a.click();
};

