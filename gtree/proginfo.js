
var ProgInfo = function()  {
    this.pe = gebi('folders_scanned');
    this.ce = gebi('currently_scanning');
    this.fe = gebi('total_files');
    this.ee = gebi('errors');
    this.we = gebi('warnings');
    this.reset();
}
ProgInfo.prototype.listToLI = function(target, ary) {
   removeChildren(target);
   var ol = cr('ol')
   ary.forEach((item) => {
       var li = cr('li');
       li.innerText = jss(item)
       ol.appendChild(li)
   }); 
  target.appendChild(ol)
}
ProgInfo.prototype.reset = function() {
    this.folder_count = 0;
    this.file_count = 0;
    this.last_item = null;
    this.errors = [];
    this.warnings = [];
    this.pe.innerText = this.folder_count;
    this.ce.innerText = '__ready to start__';
    this.fe.innerText = this.file_count;;
    this.listToLI(this.ee,this.errors)
    this.listToLI(this.we,this.warnings)
}
ProgInfo.prototype.done = function() {
    this.last_item = '__complete__';
    this.ce.innerText = this.last_item;
}
ProgInfo.prototype.error = function(es) {
    this.errors.push(es);
    this.listToLI(this.ee,this.errors)
}
ProgInfo.prototype.warn= function(es) {
    this.warnings.push(es);
    this.listToLI(this.we,this.warnings)
}
ProgInfo.prototype.showFolder = function(item) {
    this.folder_count += 1;
    this.last_item = item.name + ' (' + item.id + ')';
    if (item.hasOwnProperty('webViewLink')) {
        removeChildren(this.ce);
        var a = cr('a');
        a.innerText = this.last_item;
        a.href = item.webViewLink
        a.target = '_blank';
        this.ce.appendChild(a);
    } else {
        this.ce.innerText = this.last_item;
    }
    this.pe.innerText = this.folder_count;
}
ProgInfo.prototype.addFile = function() {
    this.file_count += 1;
    this.fe.innerText = this.file_count;;
}
