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
            raise RuntimeError(
                f"Unable to bind uniform `{self.name}': unsupported type `{type(self.value)}'"
            )


class Shaders:
    """
    Represents a GL shader program.
    """

    light = np.array([2.0, 2.0, 0.0], "f")
    Ia = np.array([0.2, 0.2, 0.2], "f")
    Id = np.array([0.9, 0.9, 0.9], "f")
    Is = np.array([1.0, 1.0, 1.0], "f")
    Ka = np.array([1.0, 1.0, 1.0], "f")
    Kd = np.array([1.0, 1.0, 1.0], "f")
    Ks = np.array([1.0, 1.0, 1.0], "f")
    Ns = 10.0

    def __init__(self, vertex_shader_path: str, fragment_shader_path: str, geometry_shader_path: Optional[str] = None):
        self.vertex_shader = None
        self.fragment_shader = None
        self.geometry_shader = None
        self.geometry_shader_source = None
        self.program = None

        self.uniforms = {
            "PVM": Uniform("PVM"),
            # "VM": Uniform("VM"),
            "VMiT": Uniform("VMiT"),
            # We already know what model we're using, so hard-code these.
            # "light": Uniform("light", np.array([0.0, 0.0, 0.0], "f")),
            # "Ia": Uniform("Ia", self.Ia),
            # "Id": Uniform("Id", self.Id),
            # "Is": Uniform("Is", self.Is),
            # "Ka": Uniform("Ka", self.Ka),
            # "Kd": Uniform("Kd", self.Kd),
            # "Ks": Uniform("Ks", self.Ks),
            # "Ns": Uniform("Ns", self.Ns),
        }

        with open(vertex_shader_path, "r") as vsh:
            self.vertex_shader_source = vsh.read()

        with open(fragment_shader_path, "r") as fsh:
            self.fragment_shader_source = fsh.read()

        if geometry_shader_path is not None:
            with open(geometry_shader_path, "r") as gsh:
                self.geometry_shader_source = gsh.read()

    def bind_attributes(self, attributes: Dict[str, int]):
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

        if self.geometry_shader_source is not None:
            self.geometry_shader = glCreateShader(GL_GEOMETRY_SHADER)
            glShaderSource(self.geometry_shader, self.geometry_shader_source)
            glCompileShader(self.geometry_shader)

            if glGetShaderiv(self.geometry_shader, GL_COMPILE_STATUS) == GL_FALSE:
                raise RuntimeError(
                    "Failed to compile geometry shader:\n" + glGetShaderInfoLog(self.geometry_shader).decode("utf-8"))

        self.program = glCreateProgram()
        glAttachShader(self.program, self.vertex_shader)
        glAttachShader(self.program, self.fragment_shader)

        if self.geometry_shader is not None:
            glAttachShader(self.program, self.geometry_shader)

    def add_uniform(self, name: str, value: Any):
        self.uniforms[name] = Uniform(name, value)

    def link(self, attributes: Dict[str, int]):
        """
        Link this program.
        """
        self.bind_attributes(attributes)

        glLinkProgram(self.program)

        if glGetProgramiv(self.program, GL_LINK_STATUS) == GL_FALSE:
            raise RuntimeError(f"Failed to link shader program:\n" + glGetProgramInfoLog(self.program).decode("utf-8"))

        glValidateProgram(self.program)

        # if glGetProgramiv(self.program, GL_VALIDATE_STATUS) == GL_FALSE:
        #     raise RuntimeError(f"Failed to validate shader program\n" + glGetProgramInfoLog(self.program).decode("utf-8"))

        glUseProgram(self.program)

        for name in self.uniforms:
            location = glGetUniformLocation(self.program, name)
            if location == -1:
                raise RuntimeError(
                    f"Failed to link shader program: no such uniform `{name}'"
                )

            self.uniforms[name].location = location

    def use(self, P: np.array, V: np.array, M: np.array):
        """
        Start using this program during rendering.
        """
        if self.program == None:
            raise RuntimeError("cannot use program which has not been compiled yet")

        VM = np.matmul(V, M)

        glUseProgram(self.program)

        self.uniforms["PVM"].bind(np.matmul(P, VM))
        # self.uniforms["VM"].bind(VM)
        self.uniforms["VMiT"].bind(np.linalg.inv(VM[:3, :3].T))
        # self.uniforms["light"].bind(unhomogenise(np.dot(V, homogenise(self.light))))

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
            "fur": Shaders(
                vertex_shader_path=join(path, "fur/vertex.glsl"),
                fragment_shader_path=join(path, "fur/fragment.glsl"),
                geometry_shader_path=join(path, "fur/geometry.glsl")
            ),
            "normals": Shaders(
                vertex_shader_path=join(path, "normals/vertex.glsl"),
                fragment_shader_path=join(path, "normals/fragment.glsl"),
            ),
            "phong": Shaders(
                vertex_shader_path=join(path, "phong/vertex_shader.glsl"),
                fragment_shader_path=join(path, "phong/fragment_shader.glsl")
            )
        }

    def compile(self):
        for name in self.shaders:
            self.shaders[name].compile()

    def get(self, shader_name: str) -> Shaders:
        return self.shaders[shader_name]
