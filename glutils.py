import ctypes

from OpenGL.GL import *


def create_program(shader_list):
    program = glCreateProgram()

    for shader in shader_list:
        glAttachShader(program, shader)

    glLinkProgram(program)

    status = glGetProgramiv(program, GL_LINK_STATUS)
    if status == GL_FALSE:
        # Note that getting the error log is much simpler in Python
        # than in C/C++ and does not require explicit handling
        # of the string buffer
        log = glGetProgramInfoLog(program)
        print('Link failure:\n{}'.format(log))
        return -1

    for shader in shader_list:
        glDetachShader(program, shader)

    return program


def create_shader(shader_type, shader_source):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, shader_source)
    glCompileShader(shader)

    status = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if status == GL_FALSE:
        # Note that getting the error log is much simpler in Python
        # than in C/C++ and does not require explicit handling
        # of the string buffer
        log = glGetShaderInfoLog(shader)
        str_type = ''
        if shader_type is GL_VERTEX_SHADER:
            str_type = 'vertex'
        elif shader_type is GL_GEOMETRY_SHADER:
            str_type = 'geometry'
        elif shader_type is GL_FRAGMENT_SHADER:
            str_type = 'fragment'

        print('Compilation failure for {} shader:\n{}'.format(str_type, log))

    return shader


def offsetof(index, alignment):
    offset = 0
    for i in range(0, index):
        offset = offset + alignment[i]
    return offset
