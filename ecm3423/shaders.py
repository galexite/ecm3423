from typing import TypeVar, Dict, Any, Optional
from os.path import join

import numpy as np
from OpenGL.GL import *

from ecm3423.util import homogenise, unhomogenise


class Uniform:
    """
    Represents a single shader uniform.
    """

    T = TypeVar("T")

    def __init__(self, name: str, value: T = None):
        self.name = name
        self.location = -1
        self.value = value

    def bind(self, value: T = None):
        """
        Bind the uniform given an optional value, otherwise use the value
        already set for this uniform.

        :param value:
        """
        if value is not None:
            self.value = value

        if isinstance(self.value, int):
            glUniform1i(self.location, self.value)
        elif isinstance(self.value, float):
            glUniform1f(self.location, self.value)
        elif isinstance(self.value, np.ndarray):
            if self.value.ndim == 1:
                if self.value.shape[0] == 3:
                    glUniform3fv(self.location, 1, self.value)
                else:
                    raise RuntimeError(f"Unable to bind uniform `{self.name}': only 3D vectors are supported")
            elif self.value.ndim == 2:
                if self.value.shape[0] == 3 and self.value.shape[1] == 3:
                    glUniformMatrix3fv(self.location, 1, True, self.value)
                elif self.value.shape[0] == 4 and self.value.shape[1] == 4:
                    glUniformMatrix4fv(self.location, 1, True, self.value)
                else:
                    raise RuntimeError(
                        f"Unable to bind uniform `{self.name}': matrix must be 4x4"
                    )
            else:
                raise RuntimeError(f"Unable to bind uniform `{self.name}': unsupported matrix/vector size")
        else:
            raise RuntimeError(
                f"Unable to bind uniform `{self.name}': unsupported type `{type(self.value)}'"
            )


class Shaders:
    """
    Represents a GL shader program with a Gouraud or Phong lighting model.
    """

    light = np.array([-3.0, -3.0, 0.0], "f")
    Ia = np.array([0.9, 0.9, 0.9], "f")
    Id = np.array([1.0, 1.0, 1.0], "f")
    Is = np.array([0.1, 0.1, 0.1], "f")
    Ka = np.array([1.0, 1.0, 1.0], "f")
    Kd = np.array([1.0, 1.0, 1.0], "f")
    Ks = np.array([0.5, 0.5, 0.5], "f")
    color = np.array([150 / 255, 128 / 255, 124 / 255], "f")
    Ns = 0.5

    def __init__(self, name: str, vertex_shader_path: str, fragment_shader_path: str):
        self.name = name
        self.vertex_shader = None
        self.fragment_shader = None
        self.geometry_shader = None
        self.geometry_shader_source = None
        self.program = None

        self.uniforms = {
            "PVM": Uniform("PVM"),
            "VM": Uniform("VM"),
            "VMiT": Uniform("VMiT"),
            "color": Uniform("color", self.color),
            "light": Uniform("light"),
            "Ia": Uniform("Ia", self.Ia),
            "Id": Uniform("Id", self.Id),
            "Is": Uniform("Is", self.Is),
            "Ka": Uniform("Ka", self.Ka),
            "Kd": Uniform("Kd", self.Kd),
            "Ks": Uniform("Ks", self.Ks),
            "Ns": Uniform("Ns", self.Ns),
        }

        with open(vertex_shader_path, "r") as vsh:
            self.vertex_shader_source = vsh.read()

        with open(fragment_shader_path, "r") as fsh:
            self.fragment_shader_source = fsh.read()

    def bind_attributes(self, attributes: Dict[str, int]):
        """
        Bind the given attributes (as a dictionary of name-location pairings) to this shader.

        :param attributes:
        """
        for name, location in attributes.items():
            glBindAttribLocation(self.program, location, name)

    def compile(self):
        """
        Compile shader source code.
        """
        self.vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(self.vertex_shader, self.vertex_shader_source)
        glCompileShader(self.vertex_shader)

        if glGetShaderiv(self.vertex_shader, GL_COMPILE_STATUS) == GL_FALSE:
            raise RuntimeError("Failed to compile vertex shader:\n" + glGetShaderInfoLog(self.vertex_shader).decode("utf-8"))

        self.fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(self.fragment_shader, self.fragment_shader_source)
        glCompileShader(self.fragment_shader)

        if glGetShaderiv(self.fragment_shader, GL_COMPILE_STATUS) == GL_FALSE:
            raise RuntimeError("Failed to compile fragment shader:\n" + glGetShaderInfoLog(self.fragment_shader).decode("utf-8"))

        self.program = glCreateProgram()
        glAttachShader(self.program, self.vertex_shader)
        glAttachShader(self.program, self.fragment_shader)

    def add_uniform(self, name: str, value: Optional[Any] = None):
        """
        Add a new uniform to the shader. Must be declared within the shader.

        :param name: name of the new uniform
        :param value: its value
        """
        self.uniforms[name] = Uniform(name, value)

    def set_uniform(self, name: str, value: Any):
        """
        Set the value of the given uniform. If the given uniform does not
        exist, KeyError will be raised.

        :param name:
        :param value:
        """
        self.uniforms[name].value = value

    def link(self, attributes: Dict[str, int]):
        """
        Link this program.

        :param attributes: A list of attribute name-location pairs to bind to
        the shader.
        """
        self.bind_attributes(attributes)

        glLinkProgram(self.program)

        if glGetProgramiv(self.program, GL_LINK_STATUS) == GL_FALSE:
            raise RuntimeError(f"Failed to link shader program `{self.name}':\n" + glGetProgramInfoLog(self.program).decode("utf-8"))

        glUseProgram(self.program)

        for uname in self.uniforms:
            location = glGetUniformLocation(self.program, uname)
            if location == -1:
                raise RuntimeError(
                    f"Failed to link shader program `{self.name}': no such uniform `{uname}'"
                )

            self.uniforms[uname].location = location

    def use(self, P: np.array, V: np.array, M: np.array):
        """
        Start using this program during rendering.

        :param P: projection matrix
        :param V: view matrix
        :param M: model matrix
        """
        if self.program == None:
            raise RuntimeError("cannot use program which has not been compiled yet")

        VM = np.matmul(V, M)

        glUseProgram(self.program)

        self.set_uniform("PVM", np.matmul(P, VM))
        self.set_uniform("VM", VM)
        self.set_uniform("VMiT", np.linalg.inv(VM[:3, :3].T))
        self.set_uniform("light", unhomogenise(np.dot(V, homogenise(self.light))))

        for uniform in self.uniforms.values():
            uniform.bind()

    def remove(self):
        """
        Stop using the program.
        """
        glUseProgram(0)


class ShaderStore:
    def __init__(self, path: str):
        self.shaders = {
            "fur": Shaders("fur",
                vertex_shader_path=join(path, "fur/vertex.glsl"),
                fragment_shader_path=join(path, "fur/fragment.glsl")
            )
        }

    def compile(self):
        """
        Compile all the shaders in the store.
        """
        for name in self.shaders:
            self.shaders[name].compile()

    def get(self, shader_name: str) -> Shaders:
        """
        Retrieve a shader from the store by its name.
        :param shader_name: name for the shader within the store
        """
        return self.shaders[shader_name]
