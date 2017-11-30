#!/usr/bin/env python

import argparse
import os
import cv2
import math
from reportlab.pdfgen import canvas
import datetime


A4_INCH_WIDTH = 8.27
DEFAULT_FILENAME = datetime.datetime.now().strftime("out_%Y-%m-%d_%H-%M-%S.pdf")


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg


def get_flipbook_frames(flipbook_fps, video_file_path):
    cap = cv2.VideoCapture(video_file_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    video_dt = 1./fps
    flipbook_dt = 1./flipbook_fps

    video_t = 0
    flipbook_t = 0
    while cap.isOpened():
        ret, video_frame = cap.read()
        if ret:
            if video_t >= flipbook_t: 
                yield video_frame
                flipbook_t += flipbook_dt

            video_t += video_dt
        else:
            break


parser = argparse.ArgumentParser()
parser.add_argument("video", help="Input video for the flipbook", type=lambda x: is_valid_file(parser, x))
parser.add_argument("--fps", type=float, help="How many frames (images) per second of video", default=20)
parser.add_argument("--dpi", type=int, help="How many pixels per inch", default=75)
parser.add_argument("--num-cols", type=int, help="How many columns", default=2)
parser.add_argument("--output", type=str, help="Output PDF filename", default=DEFAULT_FILENAME)


args = parser.parse_args()

a4_width = 8.27 * args.dpi
a4_height = a4_width * math.sqrt(2)

c = canvas.Canvas(args.output)
c.setPageSize((a4_width, a4_height))

for i, frame in enumerate(get_flipbook_frames(args.fps, args.video)):
    tmp_frame_path = '/tmp/tmp_{}.jpeg'.format(i)

    # print "Writing image to tmp path {}".format(tmp_frame_path)
    cv2.imwrite(tmp_frame_path, frame)
    ratio = float(frame.shape[0]) / frame.shape[1]

    width = a4_width / args.num_cols
    height = width * ratio
    num_rows = int(a4_height / height)
    per_page = num_rows * args.num_cols

    offset_x = (i % args.num_cols) * width
    offset_y = int((i % per_page) / args.num_cols) * height

    # print "idx={}\t offset_x:{}\t offset_y={}".format(i, offset_x, offset_y)
    c.drawImage(tmp_frame_path, offset_x, offset_y, width, height)

    if (i + 1) % per_page == 0:
        c.showPage()

c.save()
print "Saved file to {}".format(args.output)
