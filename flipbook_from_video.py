#!/usr/bin/env python

import argparse
import os
import sys
import cv2


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

parser = argparse.ArgumentParser()
parser.add_argument("video", help="Input video for the flipbook", type=lambda x: is_valid_file(parser, x))
parser.add_argument("--fps", help="How many frames (images) per second of video", default=20)


args = parser.parse_args()
cap = cv2.VideoCapture(args.video)
fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)

print "FPS (video={}, flipbook={})".format(fps, args.fps)

# Now loop over the all images in the video and collect the flipbook frames
flipbook_frames = []
while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        print "Failed to read frame from video file capture!"
        sys.exit(1)

    cv2.imshow('video', frame)
    cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()
