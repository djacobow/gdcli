"""wrappers for making life with the google drive api a bit better"""

import os
import re
import sys
import httplib2
import apiclient
import traceback

# this sets up logging from the google code. I'm using a
# different logger for now.
import logging
logging.basicConfig(filename="google.log", level=logging.INFO)

from oauth2client import tools as oaTools
from oauth2client.file import Storage as oaStorage
from oauth2client.client import flow_from_clientsecrets
from oauth2client import service_account as oaServiceAccount
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

import helpers

file_fields = [
  "kind",
  "id",
  "name",
  "mimeType",
  "description",
  "starred",
  "trashed",
  "explicitlyTrashed",
  "trashingUser",
  "trashedTime",
  "parents",
  "properties",
  "appProperties",
  "spaces",
  "version",
  "webContentLink",
  "webViewLink",
  "iconLink",
  "hasThumbnail",
  "thumbnailLink",
  "thumbnailVersion",
  "viewedByMe",
  "viewedByMeTime",
  "createdTime",
  "modifiedTime",
  "modifiedByMeTime",
  "modifiedByMe",
  "sharedWithMeTime",
  "sharingUser",
  "owners",
  "teamDriveId",
  "lastModifyingUser",
  "shared",
  "ownedByMe",
  "capabilities",
  "viewersCanCopyContent",
  "copyRequiresWriterPermission",
  "writersCanShare",
  "permissions",
  "permissionIds",
  "hasAugmentedPermissions",
  "folderColorRgb",
  "originalFilename",
  "fullFileExtension",
  "fileExtension",
  "md5Checksum",
  "size",
  "quotaBytesUsed",
  "headRevisionId",
  "contentHints",
  "imageMediaMetadata",
  "videoMediaMetadata",
  "isAppAuthorized",
]

# helper to cut down on retyping for arguments for google fns
def addTeamDriveKeys(indict, args, doing_list = False):
    teamDriveId = args.get('teamDriveId',None)

    if teamDriveId is not None:
        indict['supportsTeamDrives'] = True
        if doing_list:
            indict['teamDriveId'] = teamDriveId
            indict['corpora']     = 'teamDrive'
            indict['includeTeamDriveItems'] = True


class Google(object):
    """class to wrap google activities"""

    _config = None

    def __init__(self, config):
        """constructor, takes folder cache as param"""
        self._last_cred_refresh = 0
        self._transferred_this_session = 0
        self._drive = None
        self._credentials = None
        self._config = config

    def refresh_credentials(self):
        """refresh googld credentials"""
        now = helpers.get_now()
        if (now > (self._last_cred_refresh +
                   self._config['google']['refresh_period'])):
            print('refreshing Google credentials')
            self.get_credentials(self._config)
            self.get_drive()

    def get_credentials(self):

        if self._credentials and not self._credentials.invalid:
            return self._credentials

        use_delegation = (
          ('service_keyfile' in self._config['google']) and
          ('impersonate' in self._config['google'])
        );

        credentials = None
        if use_delegation:
            credentials = self.get_credentials_delegate()
        else:
            credentials = self.get_credentials_nodelegate()

        self._credentials = credentials
        return credentials

    def get_credentials_delegate(self):
        gconfig = self._config['google']
        service_keyfile = gconfig['service_keyfile']
        user_email = gconfig['impersonate']
        scopes = gconfig['scopes']
        print(scopes)

        sa_credentials = oaServiceAccount.ServiceAccountCredentials.from_json_keyfile_name(
          service_keyfile, scopes=scopes)

        credentials = sa_credentials.create_delegated(user_email)

        return credentials


    def get_credentials_nodelegate(self):
        """load (or obtain) ands return credentials"""

        # might enable some flags at a later time
        class MyFlags(object):
            logging_level = 'ERROR'
            noauth_local_webserver = True
            auth_host_port = [8080, 8090]
            auth_host_name = 'localhost'

            def __init__(self):
                pass

        flags = MyFlags()

        credential_dir = self._config['google']['credentials_dir']
        if not re.match(r'^/', credential_dir):
            credential_dir = os.path.join(os.getcwd(), credential_dir)

        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_file_name = self._config['google']['credentials_file']
        credential_path = os.path.join(credential_dir, credential_file_name)

        store = oaStorage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = flow_from_clientsecrets(
                self._config['google']['client_secrets'],
                self._config['google']['scopes'])
            flow.user_agent = 'Drive Copier'
            if flags:
                credentials = oaTools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = oaTools.run_flow(flow, store)
            print('Storing credentials to: ' + credential_path)

        return credentials

    def get_drive(self):

        if self._drive:
            return self._drive

        """using the credentials we've gotten, create a drive
        instance"""
        if self._credentials:
            self._drive = {}
            for api_version in ['v3']:
                self._drive[api_version] = apiclient.discovery.build(
                    'drive', api_version,
                    http=self._credentials.authorize(httplib2.Http()),
                    cache_discovery=False)
        else:
            print('-err- get_credentials() no Google credentials')
        return self._drive


    def fileInfo(self,args):

        fileId = args.get('fileId',None)
 
        if fileId is None:
            return { 'error': 'Missing fileId', }

        info_args = {
            'fileId': fileId,
            'fields': ','.join(file_fields),
        }
        addTeamDriveKeys(info_args, args, True)

        d = self.get_drive()['v3']
        req = d.files().get(**info_args)
        try:
            res = req.execute()
            return res
        except Exception as e:
            return {
                'error': 'Google API returned an error',
                'exception': repr(e),
            }


    def listFiles(self,args):
        parent = args.get('parent',None)
        matching = args.get('match',None)

        rv = {}
        done = False
        npt = None
        while not done:
            list_args = {
                'pageSize': 100,
                'fields': 'nextPageToken, files(id,name,mimeType,modifiedTime,size)',
            }
            qs = [] 
            if parent:
                qs.append("'" + parent + "' in parents")
            else:
                qs.append("'root' in parents")

            if matching:
                qs.append("name contains '" + matching + "'")

            list_args['q'] = ' and '.join([ '(' + q + ')' for q in qs])
            addTeamDriveKeys(list_args, args, True)

            if npt:
                list_args['pageToken'] = npt

            d = self.get_drive()['v3']
            req = d.files().list(**list_args)
            res = req.execute()

            for f in res['files']:
                rv[f['id']] = f
            npt = res.get('nextPageToken',None)
            if not npt:
                done = True
        return rv

    def deleteFile(self,args):
        d = self.get_drive()['v3']
        fileId = args.get('fileId',None)
        if not fileId:
            return { 'error': 'No file ID provided'}

        del_args = {
            'fileId': fileId,
        }
        addTeamDriveKeys(del_args, args, False)
        req = d.files().delete(del_args)
        res = req.execute()
        return res


    def createPermissions(self,args):
        user = args.get('user',None)
        fileId = args.get('fileId',None)
        readonly = args.get('readonly',False)
        if not fileId:
            return {'error': 'missing fileId'}
        if not user:
            return {'error': 'missing user assignmet'}

 
        perm_args = {
            'fileId': fileId,
            'body': {
                'role': 'reader' if readonly else 'writer',
                'type': 'user',
                'emailAddress': user,

            },
            'transferOwnership': False,
            'sendNotificationEmail': False,
            #'fields': 'id,permissions',
        }
        addTeamDriveKeys(perm_args, args, False)

        try:
            d = self.get_drive()['v3']
            req = d.permissions().create(**perm_args)
            res = req.execute()

        except Exception as e:
            return { 'error': 'Permissions add failed', 'exception': repr(e) }

        return res

    def createFolder(self,args):
        parent = args.get('parent',None)
        name = args.get('name',None)
        if not name:
            return { 'error': 'No name provided' }

        metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        if parent:
            metadata['parents'] = [parent]
        #elif args.get('teamDriveId',None):
        #    metadata['parents'] = [args['teamDriveId']]

        create_args = {
            'body': metadata,
            'fields': 'id,name',
        }
        addTeamDriveKeys(create_args,args,False)

        try:
            d = self.get_drive()['v3']
            req = d.files().create(**create_args)
            res = req.execute()
        except Exception as e:
            return { 'error': 'Google call failed', 'exception': repr(e) }


        return res



    def uploadFile(self,args):
        parent = args.get('parent',None)
        name = args.get('name',None)
        path = args.get('src_path',None)
        if not path:
            return { 'error': 'No source path specified' }

        (head,tail) = os.path.split(path)
        if name is None:
            name = tail

        # TODO: mimetypes for things Google doesn't understnat
        #media_mimetype= 'application/octet-stream'
        media_mimetype = None

        ftimes = helpers.get_file_details(path)

        file_metadata = {
            'name': helpers.quote_names_google(name),
            'createdTime': helpers.epoch_to_iso3339(ftimes['create']),
            'modifiedTime': helpers.epoch_to_iso3339(ftimes['modify']),
            'appProperties': {
                'copied_by': 'LBNL gdcli',
                'copy_time': helpers.epoch_to_iso3339(ftimes['now']),
            }
        }

        if parent is not None:
            file_metadata['parents'] = [parent]



        media = apiclient.http.MediaFileUpload(
            path,
            mimetype=media_mimetype,
            resumable=True,
            chunksize=1048576 * 20
        )

        create_args = {
            'media_body': media,
            'body': file_metadata,
        }
        addTeamDriveKeys(create_args, args, False)

        d = self.get_drive()['v3']
        req = d.files().create(**create_args)
        response = None
        while response is None:
            status, response = req.next_chunk()
            if status:
                sys.stdout.write('.')
                sys.stdout.flush()
        return response


    def downloadFile(self,args):
        fileId = args.get('fileId',None)
        dst_path = args.get('dst_path',None)

        if fileId is None:
            return { 'error': 'Missing fileId', }

        try:
            nres = self.fileInfo(args)
            google_name = nres.get('name',None)
        except Exception as e:
            return { 'error': 'name lookup failed', 'exception': repr(e) }

        if dst_path is None:
            wpath = os.path.join('.',google_name)
        else:
            wpath = dst_path

        try:
            with open(wpath, 'wb') as fh:
                print('Attempting download to ' + wpath)
                d = self.get_drive()['v3']
                request = d.files().get_media(fileId=fileId)
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    sys.stdout.write('.')
                    sys.stdout.flush()
                if done:
                    print('status',status,'done',done)
                    return { 'message': 'success', 'fileId': fileId, 'wpath': wpath }
        except Exception as e:
            return { 'error': 'Download failed.', 'exception': repr(e), } 

