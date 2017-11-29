#!/usr/bin/env python

import argparse
import os
import sys
import cv2
import Image
from fpdf import FPDF


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def get_flipbook_frames(flipbook_fps, video_file_path):
    cap = cv2.VideoCapture(video_file_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    video_dt = 1./fps
    flipbook_dt = 1./args.fps

    video_t = 0
    flipbook_t = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            if video_t >= flipbook_t: 
                yield frame
                flipbook_t += flipbook_dt

            video_t += video_dt
        else:
            break


parser = argparse.ArgumentParser()
parser.add_argument("video", help="Input video for the flipbook", type=lambda x: is_valid_file(parser, x))
parser.add_argument("--fps", type=float, help="How many frames (images) per second of video", default=20)


args = parser.parse_args()

for i, frame in enumerate(get_flipbook_frames(args.fps, args.video)):
    tmp_frame_path = '/tmp/tmp_{}.jpeg'.format(i)
    print "Writing image to tmp path {}".format(tmp_frame_path)
    cv2.imwrite(tmp_frame_path, frame)
