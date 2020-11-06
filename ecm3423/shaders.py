from OpenGL.GL import *
from typing import TypeVar
from enum import Enum
import numpy as np


class Uniform:
    T = TypeVar("T")

    def __init__(self, name: str, value: T):
        self._name = name
        self._location = -1
        self._value = value

    def set_location(self, location: int):
        self._location = location

    def set_value(self, value: T):
        self._value = value

    def bind_float(self):
        pass


class Shaders:
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
        if self.program == None:
            raise Exception("cannot use program which has not been compiled yet")

        glUseProgram(self.program)

        for u in self.uniforms:
            u.bind()

    def bind_pvm(self, P: np.array, V: np.array, M: np.array):
        self.uniforms["PVM"] =

    def remove(self):
        glUseProgram(0)
