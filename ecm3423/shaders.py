from typing import TypeVar

import numpy as np
from OpenGL.GL import *


class Uniform:
    """
    Represents a single shader uniform.
    """

    T = TypeVar("T")

    def __init__(self, name: str, value: T):
        self._name = name
        self._location = -1
        self._value = value

    def set_location(self, location: int):
        """
        Store OpenGL's opaque handle for the uniform.
        """
        self._location = location

    def set_value(self, value: T):
        """
        Change the uniform's value.
        """
        self._value = value

    def bind_float(self):
        """
        Bind this uniform to the current program in use as a float.
        """
        pass


class Shaders:
    """
    Represents a GL shader program.
    """

    def __init__(self, vertex_shader_path: str, fragment_shader_path: str):
        self.vertex_shader = None
        self.fragment_shader = None
        self.program = None
        self.uniforms = {}

        with open(vertex_shader_path, "r") as vsh:
            self.vertex_shader_source = vsh.read()

        with open(fragment_shader_path, "r") as fsh:
            self.fragment_shader_source = fsh.read()

    def compile_and_link(self):
        """
        Compile the shader source and link this program.
        """
        self.vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(self.vertex_shader, self.vertex_shader_source)
        glCompileShader(self.vertex_shader)

        self.fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(self.fragment_shader, self.fragment_shader_source)
        glCompileShader(self.fragment_shader)

        self.program = glCreateProgram()
        glAttachShader(self.program, self.vertex_shader)
        glAttachShader(self.program, self.fragment_shader)

        glLinkProgram(self.program)

    def use(self):
        """
        Start using this program during rendering.
        """
        if self.program == None:
            raise Exception("cannot use program which has not been compiled yet")

        glUseProgram(self.program)

        for u in self.uniforms:
            u.bind()

    def bind_pvm(self, P: np.array, V: np.array, M: np.array):
        """
        Bind the P, V, and M matrices as shader uniforms.
        """
        self.uniforms["PVM"] = Uniform("PVM", np.matmul(P, np.matmul(V, M)))
        self.uniforms["PVM"].bind_pvm()

    def remove(self):
        """
        Stop using the program.
        """
        glUseProgram(0)
