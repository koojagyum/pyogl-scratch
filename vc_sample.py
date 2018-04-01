import cv2
import cyglfw3 as glfw
import dlib
import numpy as np
import os
import time

from face_landmark import FaceDetector

from cvutils import *
from glview import GLView
from renderer import *


WIDTH = 1280
HEIGHT = 720
TITLE = 'Video capture'


def test_vcgl_glview():
    with Webcam() as webcam:
        glview = GLView(WIDTH, HEIGHT, TITLE)
        glview.renderer = VideoRenderer(video_source=webcam)
        glview.run_loop()


def test_vcgl(frame_block=None):
    # save current working directory
    cwd = os.getcwd()

    # initialize glfw - this changes cwd
    glfw.Init()

    # restore cwd
    os.chdir(cwd)

    # version hints
    glfw.WindowHint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.WindowHint(glfw.CONTEXT_VERSION_MINOR, 2)
    glfw.WindowHint(glfw.OPENGL_FORWARD_COMPAT, True)
    glfw.WindowHint(glfw.OPENGL_PROFILE,
                    glfw.OPENGL_CORE_PROFILE)

    # make a window
    win = glfw.CreateWindow(
        WIDTH,
        HEIGHT,
        TITLE
    )

    # make context current
    glfw.MakeContextCurrent(win)

    glClearColor(0.5, 0.5, 0.5, 1.0)

    renderer = TextureRenderer()
    renderer.prepare()

    fps_checker = FPSChecker()

    webcam = Webcam()
    with webcam:
        while not glfw.WindowShouldClose(win):
            frame = webcam.frame
            fps_checker.lab(frame)

            if frame_block:
                frame_block(frame)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = frame[::-1, ...]
            renderer.image = frame

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            renderer.render()

            glfw.SwapBuffers(win)

            # Poll for and process events
            glfw.PollEvents()

    glfw.Terminate()


def draw_bbox(image, bb, color=(0, 255, 0)):
    left = bb.left()
    top = bb.top()
    right = bb.right()
    bottom = bb.bottom()

    cv2.rectangle(
        image,
        (left, top),
        (right, bottom),
        color=color,
        thickness=2
    )


def draw_bboxes(image, bboxes):
    color = (0, 255, 0)

    for bb in bboxes:
        draw_bbox(image, bb, color)


def draw_shape(image, shape, color=(255, 0, 0)):
    radius = 3
    for pt in shape:
        cv2.circle(image, (pt[0], pt[1]), radius, color, -1)


def draw_shapes(image, shapes):
    for shape in shapes:
        draw_shape(image, shape)


def test_vc_bb():
    detector = FaceDetector()

    def _block(frame):
        rects, shapes = detector.detect(frame)
        if len(rects) > 0:
            draw_bboxes(frame, rects)
            draw_shapes(frame, shapes)

    test_vc(frame_block=_block)
    # test_vcgl(frame_block=_block)


def test_vc(frame_block=None):
    fps_checker = FPSChecker()

    webcam = Webcam()
    with webcam:
        while True:
            frame = webcam.frame
            fps_checker.lab(frame)

            if frame_block:
                frame_block(frame)
            cv2.imshow(TITLE, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # When everything done, release the capture
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # test_vc()
    # test_vcgl()
    # test_vcgl_glview()
    test_vc_bb()
