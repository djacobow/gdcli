# gdcli.py

Yet Another Google Drive CLI client

## What

A simple command line client allows basic operations (list, get, put) with
Google Drive.

 * can list files and show sizes, types, and fileIds
 * can put a file from local drive onto Google Drive, with same name
   or different name, at the top level or in a parent folder with 
   --parent <fileId>
 * can get files from Google Drive by fileId
 * supports TeamDrive with the option --teamDriveId <xxxx>
 * large file uploads will be chunked for better reliability

It can do a few others things, but that's the basic gist.

I just want to be able to do simple operations with Google Drive from
the command line. There are other tools for this, but this one is mine.

## What else?

A companion program `gtree.py` can make a tree list in csv format
of a Google Drive or a folder in Google Drive. The only options 
it understands are 

    * --teamDriveId <teamDriveId>
    * --parent <starting folder fileId>

## Testing

Very little, but for my purposes so far it works.

### Author: Dave Jacobowitz (dgj@lbl.gov)
### Version: 0.1
### Date: October 2018
 



