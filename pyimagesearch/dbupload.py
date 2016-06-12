from dropbox.client import DropboxOAuth2FlowNoRedirect
from dropbox.client import DropboxClient
import os

class DBUpload:
    def __init__(self):
        # connect to dropbox and start the session authorization process
        flow = DropboxOAuth2FlowNoRedirect(conf["dropbox_key"], conf["dropbox_secret"])
        print("[INFO] Authorize this application: {}".format(flow.start()))
        authCode = input("Enter auth code here: ").strip()

        # finish the authorization and grab the Dropbox client
        (accessToken, userID) = flow.finish(authCode)
        self.client = DropboxClient(accessToken)
        print("[SUCCESS] dropbox account linked")

    def upload_file(source, target, timestamp):
        print("[UPLOAD] {}".format(timestamp))
        self.client.put_file(target, open(source, "rb"))
        # remove the file
        os.remove(source)
