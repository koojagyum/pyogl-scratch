import ctypes
import numpy as np

from OpenGL.GL import *
from PIL import Image

from glutils import *


class Program:

    def __init__(self, vsSource, fsSource):
        shaderList = []
        shaderList.append(create_shader(GL_VERTEX_SHADER, vsSource))
        shaderList.append(create_shader(GL_FRAGMENT_SHADER, fsSource))

        self.program = create_program(shaderList)

        for shader in shaderList:
            glDeleteShader(shader)

    def __del__(self):
        if self.program > 0:
            glDeleteProgram(self.program)

    def __enter__(self):
        glUseProgram(self.program)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        glUseProgram(0)

    def setInt(self, name, value):
        glUniform1i(glGetUniformLocation(self.program, name), value)

    def setFloat(self, name, value):
        glUniform1f(glGetUniformLocation(self.program, name), value)


class Renderer:

    def __init__(self, vsPath, fsPath, name):
        self.name = name
        self.vsPath = vsPath
        self.fsPath = fsPath

    def prepare(self):
        with open(self.vsPath) as f:
            vsSource = f.read()
        with open(self.fsPath) as f:
            fsSource = f.read()

        self.program = Program(vsSource=vsSource, fsSource=fsSource)

    def reshape(self, w, h):
        glViewport(0, 0, w, h)

    def render(self):
        pass

    def dispose(self):
        self.program = None


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

        self.stride = total
        self.attributeCount = len(alignment)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.ebo = None
        if indices is not None and indices.size > 0:
            self.count = indices.size
            self.ebo = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
            glBufferData(
                GL_ELEMENT_ARRAY_BUFFER,
                indices,
                GL_STATIC_DRAW
            )
        else:
            self.count = int(vertices.size / self.stride)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(
            GL_ARRAY_BUFFER,
            vertices,
            GL_STATIC_DRAW
        )

        for i in range(self.attributeCount):
            glVertexAttribPointer(
                i,
                alignment[i],
                GL_FLOAT,
                False,
                self.stride * ctypes.sizeof(ctypes.c_float),
                ctypes.c_void_p(
                    offsetof(i, alignment) * ctypes.sizeof(ctypes.c_float))
            )
            glEnableVertexAttribArray(i) # Unordered layout would not work!

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def __del__(self):
        if self.vbo is not None:
            glDeleteBuffers(1, np.array([self.vbo]))
        if self.ebo is not None:
            glDeleteBuffers(1, np.array([self.ebo]))
        if self.vao is not None:
            glDeleteVertexArrays(1, np.array([self.vao]))

    def __enter__(self):
        glBindVertexArray(self.vao)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        glBindVertexArray(0)


class Texture:

    def __init__(self, **kwargs):
        self.texture = glGenTextures(1)
        self.update(**kwargs)

    def __del__(self):
        glDeleteTextures(np.array([self.texture], dtype='int32'))

    def __enter__(self):
        glActiveTexture(self.unit)
        glBindTexture(self.target, self.texture)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        glActiveTexture(self.unit)
        glBindTexture(self.target, 0)

    # image is numpy uint8 array
    def update(self, **kwargs):
        self.target = kwargs.pop('target', GL_TEXTURE_2D)
        self.unit = kwargs.pop('unit', GL_TEXTURE0)
        self.unitNumber = self.unit - GL_TEXTURE0

        image = kwargs.pop('image', None)
        if image is not None:
            glBindTexture(self.target, self.texture)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexImage2D(
                self.target,
                0,
                GL_RGB,
                image.shape[1], image.shape[0],
                0,
                GL_RGB, # BGR
                GL_UNSIGNED_BYTE,
                image
            )
            glBindTexture(self.target, 0)
