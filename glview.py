import cyglfw3 as glfw
import numpy as np
import os

from OpenGL.GL import *
from threading import Thread

from renderer import *


class GLView:

    def __init__(self, width, height, title='', renderer=None):
        self._width = width
        self._height = height
        self._title = title
        self._renderer = None
        self._next_renderer = None

        self._initialize()

        self.renderer = renderer

    def _initialize(self):
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
        glfw.WindowHint(
            glfw.OPENGL_PROFILE,
            glfw.OPENGL_CORE_PROFILE
        )

        # make a window
        self._win = glfw.CreateWindow(
            self._width,
            self._height,
            self._title
        )

    @property
    def renderer(self):
        return self._renderer

    @renderer.setter
    def renderer(self, value):
        self._next_renderer = value

    def run_loop(self):
        glfw.MakeContextCurrent(self._win)

        while not glfw.WindowShouldClose(self._win):
            if self._next_renderer:
                if self._renderer:
                    self._renderer.dispose()

                self._renderer = self._next_renderer
                self._renderer.prepare()

                self._next_renderer = None

            glClearColor(0.5, 0.5, 0.5, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            if self._renderer:
                self._renderer.render()

            glfw.SwapBuffers(self._win)

            # Poll for and process events
            glfw.PollEvents()

        glfw.Terminate()
