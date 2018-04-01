import cv2
import dlib
import getopt
import numpy as np
import os
import sys

import downloader

from os.path import split
from matplotlib import pyplot as plt
from matplotlib import patches


class FaceDetector:

    def __init__(self, resize_width=512):
        predictor_path = downloader.check_model()
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(predictor_path)
        self.width = int(resize_width)

    def detect(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        self.width = min(self.width, image.shape[1])
        scale = self.width / image.shape[1]
        dsize = (self.width, int(image.shape[0] * scale))
        gray = cv2.resize(gray, dsize=dsize)

        rects = self.detector(gray, 1)

        for (i, rect) in enumerate(rects):
            left = int(rect.left() / scale)
            top = int(rect.top() / scale)
            right = int(rect.right() / scale)
            bottom = int(rect.bottom() / scale)
            rects[i] = dlib.rectangle(left, top, right, bottom)

        self.rects = rects
        return self.rects


def help():
    def filename_from_path(path):
        return split(path)[-1]

    print('Usage: ' + filename_from_path(sys.argv[0]) + ' [options]')
    print('   options:')
    print('   -i, --input    Path for input file')
    print('   -h, --help    Show this help')
    sys.exit(1)


def plot_pts(image, pts):
    plt.figure(1)

    plt.imshow(image)
    plt.plot(pts[:, 0], pts[:, 1], 'ro')

    plt.show()


def plot_bboxes(image, bboxes):
    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(111)
    plt.imshow(image)

    for bb in bboxes:
        x = bb.left()
        y = bb.top()
        w = bb.right() - x
        h = bb.bottom() - y
        ax1.add_patch(
            patches.Rectangle(
                (x, y),
                w, h,
                fill=False,
                edgecolor='#00ff00'
            )
        )

    plt.show()


def test_bbox(image_path):
    detector = FaceDetector()
    image = cv2.imread(image_path)
    rects = detector.detect(image)

    plot_bboxes(image, rects)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hi:', ['input=', 'help'])
    except getopt.GetoptError as err:
        print(str(err))
        help()

    for opt, arg in opts:
        if opt in ('-i', '--input'):
            input_path = arg
        else:
            assert False, 'unhandled option'

    if 'input_path' not in locals():
        help()

    print('input_path: {}'.format(input_path))
    test_bbox(input_path)


if __name__ == '__main__':
    main()
