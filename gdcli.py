#!/usr/bin/env python3

import mygoogle as google
import json
import os
import sys
import re


config = {
    'google': {
        'refresh_period': 3600,                                                 
        'credentials_file': 'creds.json',                          
        'credentials_dir': os.path.expanduser('~') + '/.gdcli',
        'client_secrets': 'client_secrets.json',                                
        'scopes': ['https://www.googleapis.com/auth/drive'],                    
        'max_credentials': 1,                                                   
    },  
    'command_names': {
        'put':      'upload',
        'upload':   'upload',
        'up':       'upload',
        'push':     'upload',
        'put':      'upload',
        'get':      'download',
        'download': 'download',
        'down':     'download',
        'pull':     'download',
        'list':     'list',
        'ls':       'list',
        'dir':      'list',
        'del':      'unlink',
        'remove':   'unlink',
        'rm':       'unlink',
        'unlink':   'unlink',
        'mkdir':    'mkdir',
        'info':     'info',
        'share':    'share',
        'help':     'help',
        'rename':   'rename',
        'addparent':'addp',
        'delparent':'rmp',
        'rmparent': 'tmp',
    },
}


def saveJS(fn,d):
    with open(fn,'w') as fh:
        fh.write(json.dumps(d,indent=2,sort_keys=True))

def loadJS(fn):
    d = None
    with open(fn,'r') as fh:
        d = json.loads(fh.read())
    return d

def showJS(d):
    print(json.dumps(d,indent=2,sort_keys=True))

def getArgs():
    args = {
        'action': None,
        'naked': [],
        'errors': [],
    }

    inargs = sys.argv
    my_name = inargs.pop(0)

    act_arg = None
    if len(inargs):
        act_arg = inargs.pop(0)

    for command in config['command_names']:
        if act_arg == command:
            args['action'] = config['command_names'][command]
            break

    if args['action'] is None:
        args['errors'].append('No action specified.')

    while len(inargs):
        next_arg = inargs.pop(0)
        print('next_arg',next_arg)
        dack = re.match(r'^--(\w+)$',next_arg)
        if dack:
            key = dack.group(1)
            value = None
            if not len(inargs):
                value = True
            elif re.match(r'^--(\w+)$',inargs[0]):
                value = True
            else:
                value = inargs.pop(0)
            args[key] = value
        else:
            args['naked'].append(next_arg)

    if not len(args['errors']):
        del args['errors']

    return args


def assignFromNaked(args,index,name):
    naked_args = args.get('naked',[])
    if len(naked_args) > index:
        args[name] = naked_args[index]
        return True
    return False

def setCheckFileId(args):
    if args.get('fileId',None) is not None:
        return True
    else:
        naked_args = args.get('naked',[])
        if len(naked_args):
            args['fileId'] = naked_args[0]
            return True
    return False


def showUsage(full_monty = False):

    short_str = '''
gdcli.py <action> [ args... ] 

Synposis:

    Simple command line access to Google Drive.

Examples:

    gdcli help

    gdcli list 
    gdcli list  <fileId> 
    gdcli list  <fileId> --match "string to match" 

    gdcli get   <fileId>
    gdcli get   <fileId> local_file_name

    gdcli put   local_file_path
    gdcli put   local_file_path --parent <fileId>

    gdcli rm    <fileId>

    gdcli mkdir newdirname
    gdcli mkdir newdirname --parent <fileId> 

    gdcli share <fileId> <user_email>
    gdcli share <fileId> <user_email> --readonly

    gdcli rename <fileId> <newname>

    gdcli info  <fileId>
    '''

    long_str = '''

    Sometimes it is convenient to access Google Drive from the command 
    line. This is great for uploading a large file or for putting some
    Drive activity into a simple shell script. This program enables that.

    First run & login
    -----------------

    The first time you run gdcli, it will prompt you with an URL to copy/
    paste into your browser to login to a Google account. Once you have done
    so, paste the resulting token string back into this window. gdcli will
    then save the appropriate token in your home directory, ~/.gdcli.

    The file contained therein will provide access to your Google Drive, so
    consider making it readable only by you: chmod 700 ~/.gdcli/creds.json

    About Google Drive
    ------------------

    Google Drive is an object store and does not follow many file system
    conventions. Objects in Google Drive may have names but they *always 
    have "fileIds" and these are the primary identifier used to manage 
    such files. 
    
    fileIds are also the ONLY unique identifier for an object. Names, 
    on the other hand, are not unique. You can have multiple files of the 
    same name, even in the same folder.

    THIS TOOL WORKS PRIMARILY WITH FILEIDs. The only time it uses a name
    is when you are uploading a file to Drive or creating a folder and 
    want to name it.

    Folders in Google Drive are just special files, and they also have 
    fileIds. For a file to be "in" a folder, that folder will be listed 
    as one of the "parents" of that file. A file can be in more than one
    folder at once.

    Specifying the folder to work in
    --------------------------------

    If you do not specify a "parent" folder, gdcli will assume you want
    to work in the top level folder of your Google Drive. This is usually
    not what you want.

    You can specify a parent folder with the --parent flag. When listing
    files, do not need to include the flag, as the only argument the tool
    is expecting is that parent folder.

About: 

    Author  : Dave Jacobowitz (dgj@lbl.gov)
    Version : 0.0.2 9.Oct.2018

    '''

    if (full_monty):
        return ''.join([short_str,long_str])
    return short_str


def doInfo(g, args):
    if not setCheckFileId(args):
        return { 'error': 'missing fileId' }
    return g.fileInfo(args)

def doUnlink(g,args):
    if not setCheckFileId(args):
        return { 'error': 'missing fileId' }

    return g.deleteFile(args)

def doRename(g,args):
    if not setCheckFileId(args):
        return { 'error': 'missing fileId' }
    if not args.get('name',None):
        assignFromNaked(args,1,'name')

    return g.renameFile(args)

def doAddParent(g,args):
    if not setCheckFileId(args):
        return { 'error': 'missing fileId' }
    if not args.get('parent',None):
        assignFromNaked(args,1,'parent')
    return g.addParent(args)

def doRemoveParent (g,args):
    if not setCheckFileId(args):
        return { 'error': 'missing fileId' }
    if not args.get('parent',None):
        assignFromNaked(args,1,'parent')
    return g.rmParent(args)

def doShare(g,args):
    if not setCheckFileId(args):
        return { 'error': 'missing fileId' }
    if not assignFromNaked(args,1,'user'):
        return { 'error': 'missing user to share' }

    return g.createPermissions(args)

def doMkdir(g,args):
    if not assignFromNaked(args,0,'name'):
        return { 'error': 'No name provided' }

    return g.createFolder(args)

def doUpload(g,args):
    if not assignFromNaked(args,0,'src_path'):
        return {'error': 'no source path provided'}
    if not assignFromNaked(args,1,'name'):
        (prepath, args['name']) = os.path.split(args['src_path'])

    return g.uploadFile(args)


def doDownload(g, args):
    if not setCheckFileId(args):
        return { 'error': 'missing fileId' }

    assignFromNaked(args,1,'dst_path')

    return g.downloadFile(args)


def doList(g, args):
    def bytesToStr(b):

        try:
            b = int(b)
        except Exception as e:
            return b

        sizes = [
            { 's': (1024 * 1024 * 1024),
              'n': 'GiB', },
            { 's': (1024 * 1024),
              'n': 'MiB', },
            { 's': (1024),
              'n': 'KiB', },
            { 's': (1),
              'n': 'B', },
        ]
        n = 'B'
        for size in sizes:
            if b > size['s']:
                b /= size['s']
                n = size['n']
                break

        b = round(b)
        return str(b) + ' ' + n


    def shortenTime(t):
        return re.sub(r'\.\d+Z','Z',re.sub(r'-','',t))

    def mTypeToStr(mt):
        rv = re.sub('application\/vnd\.google-apps','g',mt)
        if rv == 'g.folder':
            rv = 'folder'
        elif rv == 'g.spreadsheet':
            rv = 'g.sheet'
        return '(' + rv + ')'

    def showList(l):
        print('\nFile List:\n')

        formats = [
            '{:5} : "{}" {} {}',
            '      : {} {} {}',
            '-------------------------------------------------------------',
        ]

        count = 0
        for f in l:
            vals = [
                [ 
                  count,
                  l[f].get('name',''),
                  mTypeToStr(l[f].get('mimeType','')),
                  'trashed' if l[f].get('trashed',False) else ''
                ],
                [ 

                  l[f].get('id',''),
                  #shortenTime(l[f].get('modifiedTime','')),
                  l[f].get('modifiedTime',''),
                  bytesToStr(l[f].get('size','')),
                ],
                [],
            ]
            strings = [formats[i].format(*vals[i]) for i in range(len(formats))]
            print('\n'.join(strings))
            count += 1

    if not args.get('parent',None):
        naked_args = args.get('naked',[])
        if len(naked_args):
            args['parent'] = naked_args[0]

    result = g.listFiles(args)
    showList(result)
    result['already_shown'] = True
    return result


config['commands'] = {
    'upload':   doUpload,
    'download': doDownload,
    'list':     doList,
    'info':     doInfo,
    'unlink':   doUnlink,
    'mkdir':    doMkdir,
    'share':    doShare,
    'rename':   doRename,
    'addp':     doAddParent,
    'rmp':      doRemoveParent,
}

if __name__ == '__main__':

    args = getArgs()

    if args.get('action',None) == 'help':
        print(showUsage(True))
        sys.exit(0)

    if args.get('errors',None):
        print('Error:')
        print('\n'.join(args['errors']))
        print(showUsage())
        sys.exit(-1)

    fn_to_call = config['commands'].get(args['action'],None)
    if not fn_to_call:
        print('Error: unknown command.')
        print(showUsage())
        sys.exit(-2)

    g = google.Google(config)
    g.get_credentials()
    drive = g.get_drive()['v3']

    res = fn_to_call(g, args)

    if res and not res.get('already_shown',False):
        print('\nResult:\n')
        print(json.dumps(res,indent=2,sort_keys=True))

    if res.get('error',None) is not None:
        sys.exit(-3)
    else:
        sys.exit(0)




