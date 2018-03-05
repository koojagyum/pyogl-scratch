from OpenGL.GL import *
from renderer import TriangleRenderer, RectangleRenderer

import cyglfw3 as glfw
import os


def main():
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
    win = glfw.CreateWindow(512, 512,
                            b'simpleglfw')

    # make context current
    glfw.MakeContextCurrent(win)

    glClearColor(0.5, 0.5, 0.5,1.0)

    # renderer = TriangleRenderer('./scene/triangle.vs', './scene/triangle.fs')
    renderer = RectangleRenderer('./scene/triangle.vs', './scene/triangle.fs')
    renderer.prepare()

    while not glfw.WindowShouldClose(win):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        renderer.render()
        glfw.SwapBuffers(win)

        # Poll for and process events
        glfw.PollEvents()

    glfw.Terminate()


if __name__ == '__main__':
    main()
