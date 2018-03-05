import numpy as np

from OpenGL.GL import *
from framework import *


class TriangleRenderer(Renderer):

    def __init__(self, vsPath, fsPath, name=''):
        super().__init__(vsPath, fsPath, name)

    def prepare(self):
        super().prepare()

        v = np.array(
            [-0.5, -0.5, +0.0, 1.0, 0.0, 0.0,
             +0.5, -0.5, +0.0, 0.0, 1.0, 0.0,
             +0.0, +0.5, +0.0, 0.0, 0.0, 1.0],
            dtype='float32'
        )
        self.vertexObject = VertexObject(v, [3, 3])

    def reshape(self, w, h):
        super().reshape(w, h)

    def render(self):
        with self.program as program:
            with self.vertexObject as vertexObject:
                glDrawArrays(GL_TRIANGLES, 0, vertexObject.count)

    def dispose(self):
        super().dispose()
        self.vertexObject = None


class RectangleRenderer(Renderer):

    def __init__(self, vsPath, fsPath, name=''):
        super().__init__(vsPath, fsPath, name)

    def prepare(self):
        super().prepare()

        v = np.array(
            [-0.5, -0.5, +0.0, 1.0, 0.0, 0.0,
             +0.5, -0.5, +0.0, 0.0, 1.0, 0.0,
             -0.5, +0.5, +0.0, 0.0, 0.0, 1.0,
             +0.5, +0.5, +0.0, 1.0, 1.0, 1.0],
            dtype='float32'
        )
        e = np.array(
            [0, 1, 2,
             1, 3, 2],
            dtype='uint8'
        )
        self.vertexObject = VertexObject(v, [3, 3], e)

    def reshape(self, w, h):
        super().reshape(w, h)

    def render(self):
        with self.program as program:
            with self.vertexObject as vertexObject:
                glDrawElements(
                    GL_TRIANGLES,
                    vertexObject.count,
                    GL_UNSIGNED_BYTE,
                    None
                )

    def dispose(self):
        super().dispose()
        self.vertexObject = None
