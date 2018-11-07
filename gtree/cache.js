var Cache = function() {
    this.c = {};    
}
Cache.prototype.check = function(k) {
    if ((k == null) || !k.length) k = '__root';
    if (this.c.hasOwnProperty(k)) {
        console.log('found',k);
        return this.c[k];
    }
    return null;
}
Cache.prototype.add = function(k,v) {
    if ((k == null) || !k.length) k = '__root';
    this.c[k] = v;
}
Cache.prototype.clear = function() {
    this.c = {};
}
