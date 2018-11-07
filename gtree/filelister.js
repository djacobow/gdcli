var FileLister = function(cache) {
    this.cache = cache;
};

var STARTING_TRIES = 3;

FileLister.prototype.addTeamDriveKeys = function(args, teamDriveId = null, doing_list = false) {
    if (teamDriveId) {
        args.supportsTeamDrives = true;
        if (doing_list) {
            args.teamDriveId = teamDriveId;
            args.corpora     = 'teamDrive';
            args.includeTeamDriveItems = true;
        }
    }
}

FileLister.prototype.run = function(parentFileId, cb) {
    this.parent_fileId = parentFileId;
    this.teamDriveId = gebi('teamdriveid').value;
    this.show_trash = false;
    this.matching = null;
    this.all_files = [];
    this.pageWrapper(null, (err,olist) => {
        if (err) pi.error(err);
        return cb(err,olist);
    });
};


FileLister.prototype.safe_run = function(parentFileId, cb, tries=STARTING_TRIES) {
    var cv = this.cache.check(parentFileId);
    if (cv != null) {
        // setTimeout is to deal with call stack issues when most
        // calls short circuit any io
        return setTimeout(() => {
            return cb(null,cv);
        }, 0);
    } else if (tries) {
        this.run(parentFileId,(err,res) => {
            if (err) {
                pi.warn('(warning) query failed retrying');
                this.safe_run(parentFileId,cb,tries-1);
            } else {
               this.cache.add(parentFileId,res);
               return cb(null,res);
            }
        });
    } else {
        pi.error('retries exhaused');
        return cb('attempts_exhausted');
    }
}



FileLister.prototype.onePageRaw = function(npt, cb) {
    if (!this.teamDriveId.length) teamDriveId = null;
    args = {
        pageSize: 100,
        fields: 'nextPageToken, files(id,name,mimeType,modifiedTime,size,trashed,webViewLink,owners,parents)',
    };
    qs = [];
    if (this.parent_fileId) {
        qs.push("'" + this.parent_fileId + "' in parents");
    } else if (this.teamDriveId) {
        qs.push("'" + this.teamDriveId + "' in parents");
    } else {
        qs.push("'root' in parents");
    }
    if (this.matching) {
        qs.push("name contains '" + matching + "'");
    }
    if (!this.show_trash) {
        qs.push("trashed != true");
    }
    qs = qs.map((e) => { return '( ' + e + ' )'; });
    args.q = qs.join(' and ');
    this.addTeamDriveKeys(args, this.teamDriveId, true)
    if (npt) {
        args.pageToken = npt;
    }

    try {
        gapi.client.drive.files.list(args).then((res) => {
            if (res.status != 200) {
                console.log('res.status',res.status);
                return(res.status,res);
            }
            return cb(null,res);
        }).catch((err) => {
            if (err && err.result && err.result.error) {
                pi.error(JSON.stringify(err.result.error,null,2));
            }
        });
    } catch (ex) {
        pi.error(ex);
        cb(ex);
    }
} 

FileLister.prototype.pageWrapper = function(npt, cb) {
    this.onePageRaw(npt, (err,res) => {
        if (err) {
            pi.error(err);
            return cb(err,res);
        }

        this.all_files.push(...res.result.files);
        if (res.result.nextPageToken) {
            this.pageWrapper(res.result.nextPageToken, cb);
        } else {
            return cb(null,this.all_files);
        }
    });
}
