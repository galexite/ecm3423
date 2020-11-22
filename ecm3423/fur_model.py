from typing import Any

from OpenGL.GL import *
import numpy as np

from ecm3423.mesh import Mesh
from ecm3423.shaders import Shaders
from ecm3423.util import build_pose_matrix, build_rotation_matrix_xy, unhomogenise

NOISE_SIZE = 512


class FurModel:
    def __init__(self, mesh: Mesh, shaders: Shaders, M: np.array = build_pose_matrix(), layers: int = 50,
                 density: float = 5.0, length: float = 0.05, gravity: np.array = np.array([0., -1., 0.])):
        self.M = M
        self.vao = glGenVertexArrays(1)
        self.vbos = {}
        self.attributes = {}
        self.index_buffer = None

        self.primitive = None
        self.n_vertices = 0
        self.n_elements = 0

        self.layers = layers
        self.density = density
        self.length = length
        self.gravity = gravity

        self.texture = glGenTextures(1)
        self.texture_data = np.random.randint(2, size=(NOISE_SIZE, NOISE_SIZE))

        self.set_mesh(mesh)
        self.set_shaders(shaders)

    def _add_vbo(self, name: str, value: Any, n: int = 3):
        self.attributes[name] = attrib = len(self.vbos)

        self.vbos[name] = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbos[name])

        glEnableVertexAttribArray(attrib)
        glVertexAttribPointer(attrib, n, GL_FLOAT, False, 0, None)
        glBufferData(GL_ARRAY_BUFFER, value, GL_STATIC_DRAW)

    def _bind(self):
        glBindVertexArray(self.vao)

        self._add_vbo("position", self.fur_mesh.vertices)
        self._add_vbo("normal", self.fur_mesh.normals)
        self._add_vbo("layer", self.layer_data, n=1)

        if self.fur_mesh.faces is None:
            if self.index_buffer is not None:
                glDeleteBuffers(1, self.index_buffer)
                self.index_buffer = None
            self.n_elements = None
        else:
            if self.fur_mesh.faces.shape[1] == 4:
                self.primitive = GL_QUADS
            if self.index_buffer is None:
                self.index_buffer = glGenBuffers(1)
            self.n_elements = self.fur_mesh.faces.flatten().shape[0]

        if self.index_buffer is not None:
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.fur_mesh.faces, GL_STATIC_DRAW)

        glBindVertexArray(0)

    def build_fur_mesh(self):
        self.fur_mesh = Mesh(np.tile(self.mesh.vertices, (self.layers, 1)),
                             np.tile(self.mesh.faces, (self.layers, 1)),
                             np.tile(self.mesh.normals, (self.layers, 1)))

        orig_n_vertices = self.mesh.vertices.shape[0]
        self.layer_data = np.zeros(orig_n_vertices * self.layers, 'f')
        orig_n_faces = self.mesh.faces.shape[0]
        for i in range(self.layers):
            layer = i / self.layers

            # Select all the vertices in this layer using this slice. Extrude each successive layer out from the
            # original model.
            vertices_slice = slice(i * orig_n_vertices, (i + 1) * orig_n_vertices)
            self.layer_data[vertices_slice] = layer
            self.fur_mesh.vertices[vertices_slice] += self.fur_mesh.normals[vertices_slice] * self.length * layer

            # Select all the faces in this layer, and make sure they point to the new vertices!
            self.fur_mesh.faces[i * orig_n_faces:(i + 1) * orig_n_faces] += orig_n_vertices * i

    def set_mesh(self, mesh: Mesh):
        self.mesh = mesh
        self.primitive = GL_TRIANGLES
        self.build_fur_mesh()

        self.n_vertices = self.fur_mesh.vertices.shape[0]
        self._bind()

    def set_shaders(self, shaders: Shaders):
        self.shaders = shaders
        self.shaders.add_uniform("density", self.density)
        self.shaders.add_uniform("gravity", self.gravity)
        self.shaders.link(self.attributes)

        glBindTexture(GL_TEXTURE_2D, self.texture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, NOISE_SIZE, NOISE_SIZE, 0, GL_RED, GL_FLOAT, self.texture_data)

    def set_density(self, density: float):
        if density > 0.0:
            self.density = density

    def set_length(self, length: float):
        if length > 0.0:
            self.length = length

    def set_direction(self, psi: float, phi: float):
        self.gravity = unhomogenise(np.matmul(np.array([1.0, 1.0, 1.0, 1.0], "f"), build_rotation_matrix_xy(psi, phi)))

    def draw(self, P: np.array, V: np.array):
        """
        Draw the mesh to the scene.
        """
        glBindVertexArray(self.vao)
        self.shaders.use(P, V, self.M)

        self.shaders.set_uniform("density", self.density)
        self.shaders.set_uniform("gravity", self.gravity * self.length)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        if self.n_elements is not None:
            glDrawElements(self.primitive, self.n_elements, GL_UNSIGNED_INT, None)
        else:
            glDrawArrays(self.primitive, 0, self.n_vertices)

        glBindVertexArray(0)

    def __del__(self):
        vbos_values = list(self.vbos.values())
        glDeleteBuffers(len(vbos_values), np.array(vbos_values))
        glDeleteVertexArrays(1, np.array([self.vao]))
