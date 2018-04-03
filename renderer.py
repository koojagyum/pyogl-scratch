import cv2
import numpy as np

from cvutils import Webcam, FPSChecker
from framework import *
from OpenGL.GL import *


class Renderer:

    def __init__(self, vs_path, fs_path, name=''):
        self.name = name
        self._vs_path = vs_path
        self._fs_path = fs_path

    def prepare(self):
        with open(self._vs_path) as f:
            vs_code = f.read()
        with open(self._fs_path) as f:
            fs_code = f.read()

        self._program = Program(vs_code=vs_code, fs_code=fs_code)

    def reshape(self, w, h):
        glViewport(0, 0, w, h)

    def render(self):
        pass

    def dispose(self):
        self._program = None


class TriangleRenderer(Renderer):

    default_vs_path = './shader/basic_color.vs'
    default_fs_path = './shader/basic_color.fs'

    def __init__(self, name=''):
        super().__init__(
            vs_path=self.__class__.default_vs_path,
            fs_path=self.__class__.default_fs_path,
            name=name
        )

    def prepare(self):
        super().prepare()

        v = np.array(
            [-0.5, -0.5, +0.0, 1.0, 0.0, 0.0,
             +0.5, -0.5, +0.0, 0.0, 1.0, 0.0,
             +0.0, +0.5, +0.0, 0.0, 0.0, 1.0],
            dtype='float32'
        )
        self._vertex_object = VertexObject(v, [3, 3])

    def render(self):
        with self._program:
            with self._vertex_object as vo:
                glDrawArrays(GL_TRIANGLES, 0, vo.count)

    def dispose(self):
        super().dispose()
        self._vertex_object = None


class RectangleRenderer(Renderer):

    default_vs_path = './shader/basic_color.vs'
    default_fs_path = './shader/basic_color.fs'

    def __init__(self, name=''):
        super().__init__(
            vs_path=self.default_vs_path,
            fs_path=self.default_fs_path,
            name=name
        )

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
        self._vertex_object = VertexObject(v, [3, 3], e)

    def render(self):
        with self._program:
            with self._vertex_object as vo:
                glDrawElements(
                    GL_TRIANGLES,
                    vo.count,
                    GL_UNSIGNED_BYTE,
                    None
                )

    def dispose(self):
        super().dispose()
        self._vertex_object = None


class TextureRenderer(Renderer):

    default_vs_path = './shader/basic_tex.vs'
    default_fs_path = './shader/basic_tex.fs'

    def __init__(self, name='', image=None):
        super().__init__(
            vs_path=self.default_vs_path,
            fs_path=self.default_fs_path,
            name=name
        )

        self._image = None
        self._next_image = None

        self.image = image

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._next_image = value

    def prepare(self):
        super().prepare()
        v = np.array(
            [-1.0, -1.0, +0.0, 0.0, 0.0,
             +1.0, -1.0, +0.0, 1.0, 0.0,
             -1.0, +1.0, +0.0, 0.0, 1.0,
             +1.0, +1.0, +0.0, 1.0, 1.0],
            dtype='float32'
        )
        e = np.array(
            [0, 1, 2,
             1, 3, 2],
            dtype='uint8'
        )
        self._vertex_object = VertexObject(v, [3, 2], e)
        self._texture = Texture()

    def render(self):
        if self._next_image is not None:
            self._image = self._next_image
            self._texture.update(image=self._image)

            self._next_image = None

        with self._program as program:
            with self._vertex_object as vo:
                with self._texture as tex:
                    program.setInt('inputTexture', tex.unit_number)
                    glDrawElements(
                        GL_TRIANGLES,
                        vo.count,
                        GL_UNSIGNED_BYTE,
                        None
                    )

    def dispose(self):
        super().dispose()
        self._vertex_object = None
        self._texture = None


class VideoRenderer(TextureRenderer):

    def __init__(self,
                 name='',
                 image=None,
                 video_source=None,
                 frame_block=None):
        super().__init__(name=name, image=image)

        self.video_source = video_source
        self.fps_checker = FPSChecker()
        self.frame_block = frame_block

    def render(self):
        image = self.video_source.frame
        if image is not None:
            if self.frame_block:
                image = self.frame_block(image)
            self.fps_checker.lab(image)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = image[::-1, ...]
            self.image = image

        super().render()
