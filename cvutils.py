import cv2
import numpy as np
import time


class FPSChecker:
    font = cv2.FONT_HERSHEY_SIMPLEX
    color = (0, 0, 255)
    pos = (0, 30)

    def __init__(self):
        self.recent = time.time()

    def draw(self, frame):
        fps_str = '{:5.2f} fps'.format(self.fps)
        if len(frame.shape) < 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        cv2.putText(frame, fps_str, self.pos, self.font, 1, self.color, 1, cv2.LINE_AA)

        return frame

    def lab(self, frame):
        start = self.recent
        self.recent = time.time()
        d = self.recent - start
        self.fps = 1.0 / d

        if frame is not None:
            self.draw(frame)

        return self.fps
