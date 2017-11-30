#!/usr/bin/env python

import argparse
import os
import cv2
import math
import numpy as np
from reportlab.pdfgen import canvas
import datetime


A4_INCH_WIDTH = 8.27
DEFAULT_FILENAME = datetime.datetime.now().strftime("out_%Y-%m-%d_%H-%M-%S.pdf")


def is_valid_file(parser, arg):
    """
    Check whether the specified file path is valid
    :param parser: ref to arg parser
    :param arg: The file path
    :return: The valid file path
    """
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg


def get_flipbook_frames(flipbook_fps, video_file_path, padding):
    """
    Get flipbook frames of a video
    :param flipbook_fps: Frames per second of flipbook
    :param video_file_path: Video file path
    :param padding: Left-padding in pixels
    """
    cap = cv2.VideoCapture(video_file_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    video_dt = 1./fps
    flipbook_dt = 1./flipbook_fps

    video_t = 0
    flipbook_t = 0
    frame_id = 0
    while cap.isOpened():
        frame_id += 1
        ret, video_frame = cap.read()
        if ret:
            if video_t >= flipbook_t:
                h, w = video_frame.shape[:2]
                result_img = np.zeros((h, w + padding, 3), np.uint8)
                result_img[:h, :padding] = (255, 255, 255)
                result_img[:h, padding:padding+w] = video_frame

                cv2.rectangle(result_img, (0, 0), (w + padding - 1, h - 1), (0, 0, 0), 3)
                cv2.rectangle(result_img, (0, 0), (padding, h - 1), (0, 0, 0), 3)
                cv2.putText(result_img, str(frame_id), (padding / 2 - 10, h / 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))

                yield result_img
                flipbook_t += flipbook_dt

            video_t += video_dt
        else:
            break


parser = argparse.ArgumentParser()
parser.add_argument("video", help="Input video for the flipbook", type=lambda x: is_valid_file(parser, x))
parser.add_argument("--fps", type=float, help="How many frames (images) per second of video", default=24)
parser.add_argument("--dpi", type=int, help="How many pixels per inch", default=75)
parser.add_argument("--num-cols", type=int, help="How many columns", default=2)
parser.add_argument("--output", type=str, help="Output PDF filename", default=DEFAULT_FILENAME)
parser.add_argument("--padding-left", type=float, help="Padding in inches from the left", default=2)
parser.add_argument("--margin-x", type=float, help="Margin x around page in inches", default=.3)
parser.add_argument("--margin-y", type=float, help="Margin y around page in inches", default=1)


args = parser.parse_args()

a4_width = 8.27 * args.dpi
a4_height = a4_width * math.sqrt(2)
padding_left_pixels = int(args.padding_left * args.dpi)
margin_x_pixels = int(args.margin_x * args.dpi)
margin_y_pixels = int(args.margin_y * args.dpi)

c = canvas.Canvas(args.output)
c.setPageSize((a4_width, a4_height))

for i, frame in enumerate(get_flipbook_frames(args.fps, args.video, padding_left_pixels)):
    tmp_frame_path = '/tmp/tmp_{}.jpeg'.format(i)

    # print "Writing image to tmp path {}".format(tmp_frame_path)
    cv2.imwrite(tmp_frame_path, frame)

    # #####
    frame_height, frame_width = frame.shape[:2]
    ratio = float(frame_width) / frame_height
    width = (a4_width - 2 * margin_x_pixels) / args.num_cols
    height = width / ratio
    num_rows = math.floor((a4_height - 2 * margin_y_pixels) / height)
    per_page = num_rows * args.num_cols
    # #####

    offset_x = (i % args.num_cols) * width
    offset_y = int((i % per_page) / args.num_cols) * height

    c.drawImage(tmp_frame_path, margin_x_pixels + offset_x, margin_y_pixels + offset_y, width, height)

    if (i + 1) % per_page == 0:
        c.showPage()

c.save()
print "Saved file to {}".format(args.output)
