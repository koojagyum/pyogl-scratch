import cv2
import numpy as np
import time

from threading import Thread
# Sync using Condition causes critical performance down
# from threading import Condition


class WebCam:

    def __init__(self):
        self.__cap = cv2.VideoCapture(0)
        _, self.__frame = self.__cap.read()

    # Create thread for capturing image
    def start(self):
        self.__run = True
        Thread(target=self._update_frame, args=()).start()

    def stop(self):
        self.__run = False

    def _update_frame(self):
        while self.__run:
            _, self.__frame = self.__cap.read()

    @property
    def frame(self):
        # Copy may cause some problems about performance
        # return self.__frame
        return np.copy(self.__frame)

    def __del__(self):
        self.__cap.release()


class FPSChecker:
    font = cv2.FONT_HERSHEY_SIMPLEX
    pos = (0, 30)
    interval = 1.0

    def __init__(self):
        self.fps = 0
        self.color = (0, 0, 255)
        self.__timeToCheck = time.time()
        self.__frameCount = 0

    def draw(self, frame):
        fpsStr = '{:5.2f} fps'.format(self.fps)
        if len(frame.shape) < 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        cv2.putText(
            frame,
            fpsStr,
            self.pos,
            self.font,
            1,
            self.color,
            1,
            cv2.LINE_AA
        )

        return frame

    def lab(self, frame):
        now = time.time()
        dt = now - self.__timeToCheck
        self.__frameCount += 1
        if dt > self.interval:
            self.fps = float(self.__frameCount) / dt
            self.__frameCount = 0
            self.__timeToCheck = now

        if frame is not None:
            self.draw(frame)

        return self.fps
