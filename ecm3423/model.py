from typing import Any

from OpenGL.GL import *
import numpy as np

from ecm3423.mesh import Mesh
from ecm3423.shaders import Shaders
from ecm3423.util import build_pose_matrix


class Model:
    def __init__(self, mesh: Mesh, shaders: Shaders, M: np.array = build_pose_matrix()):
        self.M = M
        self.vao = glGenVertexArrays(1)
        self.vbo = {}
        self.attributes = {}
        self.index_buffer = None

        self.primitive = None
        self.n_vertices = 0
        self.n_elements = 0

        self.set_mesh(mesh)
        self.set_shaders(shaders)

    def _add_vbo(self, name: str, value: Any):
        self.attributes[name] = attrib = len(self.vbo)

        self.vbo[name] = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo[name])
        
        glEnableVertexAttribArray(attrib)
        glVertexAttribPointer(attrib, value.shape[1], GL_FLOAT, False, 0, None)
        glBufferData(GL_ARRAY_BUFFER, value, GL_STATIC_DRAW)

    def _bind(self):
        glBindVertexArray(self.vao)

        self._add_vbo("position", self.mesh.vertices)
        self._add_vbo("normal", self.mesh.normals)

        if self.mesh.faces is None:
            if self.index_buffer is not None:
                glDeleteBuffers(1, self.index_buffer)
                self.index_buffer = None
            self.n_elements = None
        else:
            if self.mesh.faces.shape[1] == 4:
                self.primitive = GL_QUADS
            if self.index_buffer is None:
                self.index_buffer = glGenBuffers(1)
            self.n_elements = self.mesh.faces.flatten().shape[0]

        if self.index_buffer is not None:
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.mesh.faces, GL_STATIC_DRAW)
        
        glBindVertexArray(0)

    def set_mesh(self, mesh: Mesh):
        self.mesh = mesh
        self.primitive = GL_TRIANGLES
        self.n_vertices = self.mesh.vertices.shape[0]

        self._bind()

    def set_shaders(self, shaders: Shaders):
        self.shaders = shaders
        self.shaders.compile_and_link(self.attributes)

    def draw(self, V: np.array, P: np.array):
        """
        Draw the mesh to the scene.
        """
        glBindVertexArray(self.vao)

        self.shaders.use(P, V, self.M)

        if self.index_buffer is None:
            glDrawArrays(self.primitive, 0, self.n_vertices)
        else:
            glDrawElements(self.primitive, self.n_elements, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)
        self.shaders.remove()

    def __del__(self):
        for vbo in self.vbo.items():
            glDeleteBuffers(1, vbo)
        glDeleteVertexArrays(self.vao)
