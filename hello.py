import cyglfw3 as glfw
import os

from OpenGL.GL import *
from PIL import Image
from threading import Timer

from glview import GLView
from renderer import *


def glview_test():
    glview = GLView(512, 512, title='GLView Test')

    def _change_renderer(glview, renderer):
        glview.renderer = renderer

    t1 = Timer(3.0, _change_renderer, (glview, TriangleRenderer()))
    t2 = Timer(6.0, _change_renderer, (glview, RectangleRenderer()))
    t1.start()
    t2.start()

    with Image.open('./image/psh.jpg') as img:
        data = np.asarray(img, dtype='uint8')
        data = data[::-1, ...]
        t3 = Timer(9.0, _change_renderer,
                   (glview, TextureRenderer(image=data)))
        t3.start()

    glview.run_loop()


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

    glClearColor(0.5, 0.5, 0.5, 1.0)

    # renderer = TriangleRenderer()
    # renderer = RectangleRenderer()
    with Image.open('./image/psh.jpg') as img:
        data = np.asarray(img, dtype='uint8')
        data = data[::-1, ...]
        renderer = TextureRenderer(image=data)

    renderer.prepare()
    while not glfw.WindowShouldClose(win):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        renderer.render()
        glfw.SwapBuffers(win)

        # Poll for and process events
        glfw.PollEvents()

    glfw.Terminate()


if __name__ == '__main__':
    # main()
    glview_test()
