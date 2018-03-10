import cv2
import cyglfw3 as glfw
import numpy as np
import os
import time

from renderer import *
from cvutils import *


DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_TITLE = 'vc sample'


def test_vcgl():
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
        DEFAULT_WIDTH,
        DEFAULT_HEIGHT,
        DEFAULT_TITLE
    )

    # make context current
    glfw.MakeContextCurrent(win)

    glClearColor(0.5, 0.5, 0.5, 1.0)

    renderer = TextureRenderer()
    renderer.prepare()

    webcam = Webcam()
    webcam.start()

    fps_checker = FPSChecker()
    while not glfw.WindowShouldClose(win):
        frame = webcam.frame
        fps_checker.lab(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = frame[::-1, ...]
        renderer.update(frame)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        renderer.render()

        glfw.SwapBuffers(win)

        # Poll for and process events
        glfw.PollEvents()

    webcam.stop()
    glfw.Terminate()


def test_vc():
    webcam = Webcam()
    webcam.start()

    fps_checker = FPSChecker()
    while True:
        frame = webcam.frame
        fps_checker.lab(frame)

        cv2.imshow(DEFAULT_TITLE, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    webcam.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # test_vc()
    test_vcgl()
