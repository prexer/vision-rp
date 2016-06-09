# import the necessary packages
from __future__ import print_function
from imutils.object_detection import non_max_suppression
from imutils import paths
import numpy as np
import imutils
import cv2

class PedDetect:
        def __init__(self):

                # initialize the HOG descriptor/person detector
                self.hog = cv2.HOGDescriptor()
                self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        def count_peds(self, image):
                image = imutils.resize(image, width=min(400, image.shape[1]))
                orig = image.copy()

                # detect people in the image
                (rects, weights) = self.hog.detectMultiScale(image, winStride=(4, 4),
                        padding=(8, 8), scale=1.05)

                # draw the original bounding boxes
                for (x, y, w, h) in rects:
                        cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 0, 255), 2)

                # apply non-maxima suppression to the bounding boxes using a
                # fairly large overlap threshold to try to maintain overlapping
                # boxes that are still people
                rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
                pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

                # draw the final bounding boxes
                for (xA, yA, xB, yB) in pick:
                        cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)
                cv2.putText(image, "Peds:{}".format(len(pick)), (image.shape[1]-40,
                    10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                # return the image with rectangles drawn over the pedestrians
                # as well as a count of pedestrians
                return( len(pick), image)
