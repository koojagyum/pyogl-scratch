import cyglfw3 as glfw
import numpy as np
import os

from OpenGL.GL import *
from PIL import Image
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

        self._key_callback = None
        self._mbtn_callback = None
        self._mpos_callback = None
        self._close_callback = None

        debug('GLView is being created: {}'.format(self))

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

    @property
    def key_callback(self):
        return self._key_callback

    @key_callback.setter
    def key_callback(self, value):
        self._key_callback = value
        if self._win:
            glfw.SetKeyCallback(self._win, self._key_callback)

    @property
    def mbtn_callback(self):
        return self._mbtn_callback

    @mbtn_callback.setter
    def mbtn_callback(self, value):
        self._mbtn_callback = value
        if self._win:
            glfw.SetMouseButtonCallback(self._win, self._mbtn_callback)

    @property
    def mpos_callback(self):
        return self._mpos_callback

    @mpos_callback.setter
    def mpos_callback(self, value):
        self._mpos_callback = value
        if self._win:
            glfw.SetCursorPosCallback(self._win, self._mpos_callback)

    @property
    def close_callback(self):
        return self._close_callback

    @close_callback.setter
    def close_callback(self, value):
        self._close_callback = value
        if self._win:
            glfw.SetWindowCloseCallback(self._win, self._close_callback)

    @property
    def width(self):
        if self._win:
            return glfw.GetWindowSize(self._win)[0]
        return 0.0

    @property
    def height(self):
        if self._win:
            return glfw.GetWindowSize(self._win)[1]
        return 0.0

    @property
    def snapshot(self, mode='RGB'):
        _modes = {
            'rgb': GL_RGB,
            'rgba': GL_RGBA,
        }

        if not self._win:
            return None

        glfw.MakeContextCurrent(self._win)
        _, _, w, h = glGetIntegerv(GL_VIEWPORT)
        data = glReadPixels(0, 0, w, h, _modes[mode.lower()], GL_UNSIGNED_BYTE)
        data = Image.frombytes(mode=mode, size=(w, h), data=data)

        return np.asarray(data, dtype='uint8')

    def run_loop(self):
        glfw.MakeContextCurrent(self._win)

        glfw.SetWindowShouldClose(self._win, False)
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

        if self._renderer:
            self._renderer.dispose()
        if self._next_renderer is None:
            self._next_renderer = self._renderer

    def __del__(self):
        glfw.MakeContextCurrent(self._win)
        if self._renderer:
            self._renderer.dispose()
        glfw.Terminate()
        debug('GLView is being deleted: {}'.format(self))


class EventListener:

    def __init__(self):
        self._xpos = 0.0
        self._ypos = 0.0
        self._glview = None

    def lbtn_down(self):
        pass

    def rbtn_down(self):
        pass

    def esc_key(self):
        pass

    def mouse_move(self, xpos, ypos):
        self._xpos = min(max(0.0, xpos), self.width)
        self._ypos = min(max(0.0, ypos), self.height)
        debug('xpos/ypos: {}/{}'.format(self._xpos, self._ypos))

    @property
    def glview(self):
        return self._glview

    @glview.setter
    def glview(self, value):
        self._glview = value

    @property
    def width(self):
        if self.glview:
            return self.glview.width
        return 0.0

    @property
    def height(self):
        if self.glview:
            return self.glview.height
        return 0.0


class EventDispatcher:

    def __init__(self, listener=None):
        debug('EventDispatcher is being created: {}'.format(self))
        self._listener = listener
        self._glview = None

    def __del__(self):
        debug('EventDispatcher is being deleted: {}'.format(self))

    def register(self, glview):
        self._glview = glview
        self._listener.glview = self._glview

        if self._glview:
            self._glview.key_callback = self._key_cb
            self._glview.mbtn_callback = self._mbtn_cb
            self._glview.mpos_callback = self._mpos_cb
            self._glview.close_callback = self._close_cb

    def unregister(self):
        if self._glview:
            self._glview.key_callback = None
            self._glview.mbtn_callback = None
            self._glview.mpos_callback = None
            self._glview.close_callback = None

            self._listener.glview = None
            self._glview = None

    def _key_cb(self, window, key, scancode, action, mods):
        if self._listener and \
           key == glfw.KEY_ESCAPE and \
           action == glfw.PRESS:
            self._listener.esc_key()

    def _mbtn_cb(self, window, button, action, mods):
        if self._listener and \
           action == glfw.PRESS:
            if button == glfw.MOUSE_BUTTON_RIGHT:
                self._listener.rbtn_down()
            elif button == glfw.MOUSE_BUTTON_LEFT:
                self._listener.lbtn_down()

    def _mpos_cb(self, window, xpos, ypos):
        if self._listener:
            self._listener.mouse_move(xpos, ypos)

    def _close_cb(self, window):
        self.unregister()

    @property
    def glview(self):
        return self._glview

    @glview.setter
    def glview(self, value):
        self.unregister()
        self.register(value)

    @property
    def listener(self):
        return self._listener

    @listener.setter
    def listener(self, value):
        self._listener = value
        if self._glview:
            self._listener.glview = self._glview
