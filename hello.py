import cyglfw3 as glfw
import os

from OpenGL.GL import *
from PIL import Image

from renderer import *


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

    imgpath = ''
    # renderer = TriangleRenderer()
    # renderer = RectangleRenderer()
    with Image.open('./image/psh.jpg') as img:
        data = np.asarray(img, dtype='uint8')
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
    main()
    # image_test()
    
