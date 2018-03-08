import cv2
import cyglfw3 as glfw
import numpy as np
import os
import time

from renderer import *
from threading import Thread


DEFAULT_WIDTH=1280
DEFAULT_HEIGHT=720
DEFAULT_TITLE='vc sample'


# class WebCam:

#     def __init__(self, consumer):
#         self.video_capture = cv2.VideoCapture(0)
#         self.current_frame = None
#         self.consumer = consumer
#         # _, self.current_frame = self.video_capture.read()

#     # create thread for capturing image
#     def start(self):
#         Thread(target=self._update_frame, args=()).start()

#     def _update_frame(self):
#         while True:
#             _, self.current_frame = self.video_capture.read()
#             self.consumer.update(self.current_frame)


def process_frame(frame, fps):
    font = cv2.FONT_HERSHEY_SIMPLEX
    color = (0, 0, 255)
    pos = (0, 30)
    fps_str = '{:5.2f} fps'.format(fps)

    if len(frame.shape) < 3:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

    cv2.putText(frame, fps_str, pos, font, 1, color, 1, cv2.LINE_AA)

    return frame


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

    cap = cv2.VideoCapture(0)

    start = recent = time.time()
    while not glfw.WindowShouldClose(win):
        _, frame = cap.read()

        # Calc fps
        start = recent
        recent = time.time()
        diff = recent - start
        fps = 1.0 / diff
        frame = process_frame(frame, fps)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        renderer.update(frame)
        renderer.render()
        glfw.SwapBuffers(win)

        # Poll for and process events
        glfw.PollEvents()

    cap.release()
    glfw.Terminate()


def test_vc():
    cap = cv2.VideoCapture(0)

    while True:
        _, frame = cap.read()

        cv2.imshow(DEFAULT_TITLE, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # test_vc()
    test_vcgl()
