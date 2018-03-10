import ctypes
import numpy as np

from OpenGL.GL import *
from PIL import Image

from glutils import *


class Program:

    def __init__(self, vs_code, fs_code):
        shaders = []
        shaders.append(create_shader(GL_VERTEX_SHADER, vs_code))
        shaders.append(create_shader(GL_FRAGMENT_SHADER, fs_code))

        self._program = create_program(shaders)

        for shader in shaders:
            glDeleteShader(shader)

    def __del__(self):
        if self._program > 0:
            glDeleteProgram(self._program)

    def __enter__(self):
        glUseProgram(self._program)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        glUseProgram(0)

    def setInt(self, name, value):
        glUniform1i(glGetUniformLocation(self._program, name), value)

    def setFloat(self, name, value):
        glUniform1f(glGetUniformLocation(self._program, name), value)


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


class VertexObject:

    # vertices: float numpy array (1d)
    # alignment: int Python array
    # indices: uint8 numpy array
    def __init__(self, vertices, alignment, indices=None):
        total = 0
        for part in alignment:
            total = total + part

        # Checking alignment
        remain = vertices.size % total
        if remain is not 0:
            raise ValueError

        self._stride = total
        self._attribute_count = len(alignment)

        self._vao = glGenVertexArrays(1)
        glBindVertexArray(self._vao)

        self._ebo = None
        if indices is not None and indices.size > 0:
            self.count = indices.size
            self._ebo = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._ebo)
            glBufferData(
                GL_ELEMENT_ARRAY_BUFFER,
                indices,
                GL_STATIC_DRAW
            )
        else:
            self.count = int(vertices.size / self._stride)

        self._vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(
            GL_ARRAY_BUFFER,
            vertices,
            GL_STATIC_DRAW
        )

        for i in range(self._attribute_count):
            glVertexAttribPointer(
                i,
                alignment[i],
                GL_FLOAT,
                False,
                self._stride * ctypes.sizeof(ctypes.c_float),
                ctypes.c_void_p(
                    offsetof(i, alignment) * ctypes.sizeof(ctypes.c_float))
            )
            glEnableVertexAttribArray(i)  # Unordered layout would not work!

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def __del__(self):
        if self._vbo is not None:
            glDeleteBuffers(1, np.array([self._vbo]))
        if self._ebo is not None:
            glDeleteBuffers(1, np.array([self._ebo]))
        if self._vao is not None:
            glDeleteVertexArrays(1, np.array([self._vao]))

    def __enter__(self):
        glBindVertexArray(self._vao)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        glBindVertexArray(0)


class Texture:

    def __init__(self, **kwargs):
        self._tex_id = glGenTextures(1)
        self.update(**kwargs)

    def __del__(self):
        glDeleteTextures(np.array([self._tex_id], dtype='int32'))

    def __enter__(self):
        glActiveTexture(self._unit)
        glBindTexture(self._target, self._tex_id)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        glActiveTexture(self._unit)
        glBindTexture(self._target, 0)

    # image is numpy uint8 array
    def update(self, **kwargs):
        self._target = kwargs.pop('target', GL_TEXTURE_2D)
        self._unit = kwargs.pop('unit', GL_TEXTURE0)
        self.unit_number = self._unit - GL_TEXTURE0

        image = kwargs.pop('image', None)
        if image is not None:
            glBindTexture(self._target, self._tex_id)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexImage2D(
                self._target,
                0,
                GL_RGB,
                image.shape[1], image.shape[0],
                0,
                GL_RGB,  # BGR
                GL_UNSIGNED_BYTE,
                image
            )
            glBindTexture(self._target, 0)
