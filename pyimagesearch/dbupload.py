from dropbox.client import DropboxOAuth2FlowNoRedirect
from dropbox.client import DropboxClient
import os
import time
import logging
from queue import Queue
from threading import Thread


class DBUpload:
    def __init__(self, key, secret):
        # connect to dropbox and start the session authorization process
        flow = DropboxOAuth2FlowNoRedirect(key, secret)
        logging.info("Authorize this application: {}".format(flow.start()))
        authCode = input("Enter auth code here: ").strip()

        # finish the authorization and grab the Dropbox client
        (accessToken, userID) = flow.finish(authCode)
        self.client = DropboxClient(accessToken)
        logging.info("dropbox account linked")

        self.Q = Queue()
        self.thread = Thread(target=self.pull_from_queue, args=())
        self.thread.daemon = True
        self.thread.start()

##        # setup the queue
##        q = Queue()
##        number_workers = 4
##
##        for i in range(number_workers):
##            t = Thread(target=pull_from_queue, q)
##            t.daemon = True
##            t.start()
##
##        while True:
##            time.sleep(1)

    def upload_file(self, source, target, timestamp):
        logging.info(" {}".format(timestamp))
        self.client.put_file(target, open(source, "rb"))
        # remove the file
        os.remove(source)

    def queue_file(self, source, target, timestamp):
        self.Q.put((source, target, timestamp))


    def pull_from_queue(self):
        while True:
            if not self.Q.empty():
                (source, target, timestamp) = self.Q.get()
                logging.info ("found item in queue" )
                self.upload_file(source,target, timestamp)

            else:
                time.sleep(1.0)
