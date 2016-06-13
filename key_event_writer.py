# import the needed packages
from pyimagesearch.keyclipwriter import KeyClipWriter
from pyimagesearch.tempimage import TempImage
from pyimagesearch.peddetect import PedDetect
from pyimagesearch.dbupload import DBUpload
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import json
import time
import cv2
import os

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
                help="path to the JSON configuration file")
args = vars(ap.parse_args())

#filter warnings, load the confic, initialize Dropbox client
conf = json.load(open(args["conf"]))
client = None
avg = None

#if dropbox is enabled initialize DB
if conf["use_dropbox"]:
    uploader = DBUpload(conf["dropbox_key"], conf["dropbox_secret"])

#initialize the video stream and let the camera warmup
print("[INFO] warming up camera...")
vs = VideoStream(usePiCamera=conf["picamera"]>0).start()
time.sleep(conf["camera_warmup_time"])


#initialize the key clip writer and the motionFrames
# and consecFrames to track frames without motion
kcw = KeyClipWriter(bufSize=conf["buffer_size"])
pDet = PedDetect()
consecFrames = 0
motionFrames = 0
pedFrames = 0
p = ""

while True:
    #grab the current frame, resize, add status Text and timestamp
    frame = vs.read()
    frame = imutils.resize(frame, width=conf["resize_width"])
    timestamp = datetime.datetime.now()
    text = "Standby"
    consecFrames += 1

    #blur, grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    #if the average frame is None, initialize it
    if avg is None:
        print("[INFO] starting background model...")
        avg = gray.copy().astype("float")
        #rawCapture.truncate(0)
        continue

    # accumulate the weighted average between the current frame and
    # previous frames, then compute the difference between the current
    # frame and running average
    cv2.accumulateWeighted(gray, avg, 0.5)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    # threshold the delta image, dilate the thresholded image to fill
    # in holes, then find contours on thresholded image
    thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,
            cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    (im2, cnts, heirarchy) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)

    # loop over the motion contours, draw boxes
    for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < conf["min_area"]:
                    continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Detected"
            consecFrames = 0

    # draw the text and timestamp on the frame
    ts = timestamp.strftime("%A %d %B %Y %H:%M:%S%p")
    cv2.putText(frame, "Status: {}".format(text), (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (0, 0, 255), 1)

    # check to see if motion is detected
    if text == "Detected":
        motionFrames += 1

        # check to see if the number of frames with consistent motion is
        # a multiple of the ped_frame_rate config parameter
        if (motionFrames % conf["ped_frame_rate"] == 0 and pedFrames < conf["ped_min_detections"]):

            #look for pedestrians
            print("Saw Motion, Checking for Peds")
            pedRet = pDet.count_peds(frame)
            peds = pedRet[0]
            if peds > 0:
                pedFrames += 1
                print("Found {} Pedestrians, {} times".format(peds, pedFrames))

        if pedFrames >= conf["ped_min_detections"]:

            if not kcw.recording:
                #p = TempImage(ext= conf["filetype"])
                timestamp = datetime.datetime.now()
                p = "./{}.{}".format(timestamp.strftime("%Y%m%d-%H%M%S"),conf["filetype"])
                print("Path of Temp file = {}".format(p))
                kcw.start(p, cv2.VideoWriter_fourcc(*conf["codec"]),conf["fps"])

    # motion was not detectec, increment the still counter, decrement the motion counter
    else:
        consecFrames += 1
        motionFrames -= 1

    #if we are recording and the motion has stopped for long enough
    #or we've reached the buffer length, stop recording
    if kcw.recording and consecFrames >= conf["buffer_size"]:
        print("Reached max buffer, closing the file")
        kcw.finish()
        consecFrames = 0
        pedFrames = 0

        #if Dropbox is turned on, upload the file
        if conf["use_dropbox"]:
            path = "{base_path}/{timestamp}.{extension}".format(
                            base_path=conf["dropbox_base_path"], timestamp=ts,
                            extension=conf["filetype"])
            uploader.upload_file(p, path, ts)

    # put this frame into the video buffer
    cv2.putText(frame, "{} Humans".format(peds), (frame.shape[1] - 40, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    kcw.update(frame)

    #show the frame
    cv2.imshow("Security Feed", frame)
    key  = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

#if we are in the middle of recording, cleanup
if kcw.recording:
    kcw.finish()

#do some cleanup
cv2.destroyAllWindows()
vs.stop()
