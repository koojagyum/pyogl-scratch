import cv2
import cyglfw3 as glfw
import dlib
import numpy as np
import os
import time

import downloader

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


def draw_bbox(image, bb):
    color = (0, 255, 0)

    l = bb.left()
    t = bb.top()
    r = bb.right()
    b = bb.bottom()

    cv2.rectangle(image, (l, t), (r, b), color=color, thickness=2)


def test_vc_bb():
    detector = dlib.get_frontal_face_detector()
    predictor_path = downloader.check_model()
    predictor = dlib.shape_predictor(predictor_path)

    def _block(frame):
        rects = detector(frame, 1)
        if len(rects) > 0:
            draw_bbox(frame, rects[0])

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
