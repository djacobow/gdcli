#!/usr/bin/env python3

import mygoogle as google
import json
import os
import sys
import csv
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
}


def saveJS(fn,d):
    print('saveJS(' + fn + ')')
    with open(fn,'w') as fh:
        fh.write(json.dumps(d,indent=2,sort_keys=True))

def loadJS(fn):
    d = None
    with open(fn,'r') as fh:
        d = json.loads(fh.read())
    return d

def doListRetryer(g,args):
    attempts = 3
    while attempts:
        attempts -= 1
        try:
            return g.listFiles(args)
        except Exception as e:
            print('that did not go well')
    return {}

def getAllRecursed(g,parent = None, teamDriveId = None):
    args = {}
    if parent:
        args['parent'] = parent
    if teamDriveId:
        args['teamDriveId'] = teamDriveId

    starting_list = doListRetryer(g,args)

    def recurseOne(g, l):
        for item in l:
            is_folder = l[item]['mimeType'] == 'application/vnd.google-apps.folder'
            if is_folder:
                print('listing...',item)
                subargs = {
                    'parent': item,
                }
                if teamDriveId:
                    subargs['teamDriveId'] = args['teamDriveId']
                l[item]['contents'] = doListRetryer(g,subargs)
                recurseOne(g,l[item]['contents'])

    recurseOne(g,starting_list)
    return starting_list

def flattenRecursed(flat,hier,path):
    for item in hier:
        print('flattenRecursed','item',item)
        hier[item]['path'] = path
        flat.append(hier[item])
        if hier[item].get('contents',None) is not None:
            flattenRecursed(flat,hier[item]['contents'],path + [hier[item]['name']])
    return flat

def saveCSV(fn,flat):
    print('saveCSV(' + fn + ')')
    with open(fn,'w') as ofh:
        writer = csv.writer(ofh)
        for item in flat:
            row = [ '/'.join(item['path'] + [ item['name'] ]) ]
            row += [ item.get(x,'') for x in ['id','mimeType','modifiedTime','name','size' ] ]
            writer.writerow(row)

def getArgs():
    args = {
        'action': None,
        'naked': [],
        'errors': [],
    }

    inargs = sys.argv
    my_name = inargs.pop(0)

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

if __name__ == '__main__':

    g = google.Google(config)
    g.get_credentials()
    drive = g.get_drive()['v3']

    args = getArgs()
    starting_parent = args.get('parent',None)
    teamDriveId     = args.get('teamDriveId',None)
    hierfname       = args.get('jsDump',None)
    csvfname        = args.get('save','flat.csv')

    hierres = getAllRecursed(g,starting_parent,teamDriveId)
    if hierfname:
        saveJS(hierfname,hierres)

    flatres = []
    flattenRecursed(flatres, hierres, [])
    flatres.sort(key=lambda x: '/'.join(x['path'] + [ x['name']] ))
    #saveJS('flat.json',flatres)
    saveCSV(csvfname,flatres)
    sys.exit(0)




