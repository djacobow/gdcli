
var FileRecurser = function(fl) {
    this.fl = fl;
    this.keep_going = true;
}
FileRecurser.prototype.stop = function() {
    this.keep_going = false;
}
FileRecurser.prototype.recurseList = function(topl, curr_depth, cb) {
   // console.log('topl_start',jss(topl));
   if (!this.keep_going) {
       return cb('user_stopped','user_stopped');
   }
   if (curr_depth >= this.max_depth) {
       return cb(null,[]);
   }
   doSyncThings(topl,(item,icb) => {
       // console.log('item',jss(item));
       if (!this.keep_going) {
           icb('user_stopped','user_stopped');
       } else if (item.mimeType == 'application/vnd.google-apps.folder') {
           this.fl.safe_run(item.id, (err, pllist) => {
               if (err) pi.error(err);
               pi.showFolder(item);
               // console.log('item_w_children',jss(item));
               this.recurseList(pllist, curr_depth + 1, (res) => {
                   item.children = res;
                   icb(null, item);
               });
           });
       } else {
           pi.addFile();
           icb(null,item);
       }
   }, (allres) => {
       var just_results = allres.map((i) => { return i[2]; });
       // console.log('just_results',jss(just_results));
       cb(just_results);
   });
};
FileRecurser.prototype.run = function(parent_fileId = null, max_depth = 1000, cb) {
    this.max_depth = max_depth;
    this.keep_going = true;
    if (!parent_fileId.length) parent_fileId = null;
    
    this.fl.safe_run(parent_fileId, (err, toplist) => {
        if (err) pi.error(err);
        this.recurseList(toplist, 0, (mlres) => {
            return cb(mlres);
        });
    });
};
