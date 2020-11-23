from typing import Any

from OpenGL.GL import *
import numpy as np

from ecm3423.mesh import Mesh
from ecm3423.shaders import Shaders
from ecm3423.util import build_pose_matrix, build_rotation_matrix_xy, unhomogenise

NOISE_SIZE = 512


class FurModel:
    def __init__(self, mesh: Mesh, shaders: Shaders, M: np.array = build_pose_matrix(), n_layers: int = 25,
                 density: float = 5.0, length: float = 0.1, gravity: np.array = np.array([-0.5, -1., 0.])):
        """
        Initialise a new FurModel.

        :param mesh: this new model's mesh
        :param shaders: this model's shaders
        :param M: a model pose matrix to position and scale the object within the scene
        :param n_layers: the number of fur layers that are to be rendered to show fur
        :param density: how dense the fur appears - the larger the number, the more clumps of fur
        :param length: how long the fur hairs appear as
        :param gravity: normalised direction for the individual fur hairs to point in away from the model's faces
        """
        self.M = M
        self.vao = glGenVertexArrays(1)
        self.vbos = {}
        self.attributes = {}
        self.index_buffer = None

        # Populated within set_mesh, information required for OpenGL to draw our mesh.
        self.primitive = None
        self.n_vertices = 0
        self.n_elements = 0
        self.layer_data = None

        # Fur properties.
        self.n_layers = n_layers
        self.density = density
        self.length = length
        self.gravity = gravity

        # Fur texture. Repeated over each layer to give the illusion of fur.
        self.texture = glGenTextures(1)
        self.texture_data = np.random.randint(2, size=(NOISE_SIZE, NOISE_SIZE))

        self.set_mesh(mesh)
        self.set_shaders(shaders)

    def _add_vbo(self, name: str, value: Any, n: int = 3):
        """
        Add a new vertex buffer object with the given value to the shader.

        :param name: the object's name - must match the name of the input to the vertex shader
        :param value: array of data which this object will point to
        :param n: size of each element in the array
        """
        self.attributes[name] = attrib = len(self.vbos)

        self.vbos[name] = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbos[name])

        glEnableVertexAttribArray(attrib)
        glVertexAttribPointer(attrib, n, GL_FLOAT, False, 0, None)
        glBufferData(GL_ARRAY_BUFFER, value, GL_STATIC_DRAW)

    def _bind(self):
        """
        Bind the the model to the shader's inputs.
        """
        glBindVertexArray(self.vao)

        self._add_vbo("position", self.fur_mesh.vertices)
        self._add_vbo("normal", self.fur_mesh.normals)
        self._add_vbo("layer", self.layer_data, n=1)

        # Determine whether we are drawing using indexed vertices, and the type of primitives we will be drawing.
        if self.fur_mesh.faces is None:
            if self.index_buffer is not None:
                glDeleteBuffers(1, self.index_buffer)
                self.index_buffer = None
            self.n_elements = None
        else:
            if self.fur_mesh.faces.shape[1] == 4:
                self.primitive = GL_TRIANGLE_STRIP
            if self.index_buffer is None:
                self.index_buffer = glGenBuffers(1)
            self.n_elements = self.fur_mesh.faces.flatten().shape[0]

            # If we're drawing indexed vertices, we need to bind an index buffer.
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.fur_mesh.faces, GL_STATIC_DRAW)

        glBindVertexArray(0)

    def build_fur_mesh(self):
        """
        Generate the additional extruded layers required for showing fur on the rendered model.
        """
        self.fur_mesh = Mesh(np.tile(self.mesh.vertices, (self.n_layers, 1)),
                             np.tile(self.mesh.faces, (self.n_layers, 1)),
                             np.tile(self.mesh.normals, (self.n_layers, 1)))

        orig_n_vertices = self.mesh.vertices.shape[0]
        self.layer_data = np.zeros(orig_n_vertices * self.n_layers, 'f')
        orig_n_faces = self.mesh.faces.shape[0]
        for i in range(self.n_layers):
            layer = i / self.n_layers

            # Select all the vertices in this layer using this slice. Extrude
            # each successive layer out from the original model.
            vertices_slice = slice(i * orig_n_vertices, (i + 1) * orig_n_vertices)
            self.layer_data[vertices_slice] = layer
            self.fur_mesh.vertices[vertices_slice] += self.fur_mesh.normals[vertices_slice] * self.length * layer

            # Select all the faces in this layer, and make sure they point to
            # the new vertices!
            self.fur_mesh.faces[i * orig_n_faces:(i + 1) * orig_n_faces] += orig_n_vertices * i

    def set_mesh(self, mesh: Mesh):
        """
        Set this model's mesh.

        :param mesh: the model's new mesh
        """
        self.mesh = mesh
        self.primitive = GL_TRIANGLES
        self.build_fur_mesh()

        self.n_vertices = self.fur_mesh.vertices.shape[0]
        self._bind()

    def set_shaders(self, shaders: Shaders):
        """
        Set this model's shaders and passes the texture to OpenGL for use within the shader.

        :param shaders: the model's new shaders
        """
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
        """
        Set the fur's density to that of the given density or 0.0, whichever is greater.

        :param density: new value of density for the fur
        """
        if density > 0.0:
            self.density = density

    def set_length(self, length: float):
        """
        Set the fur's length to the given length or 0.0, whichever is greater.

        :param length: new value of fur length
        """
        if length > 0.0:
            self.length = length

    def set_direction(self, psi: float, phi: float):
        """
        Change the direction of the fur.

        :param psi:
        :param phi:
        """
        self.gravity = unhomogenise(np.matmul(np.array([1.0, 1.0, 1.0, 1.0], "f"), build_rotation_matrix_xy(psi, phi)))

    def draw(self, P: np.array, V: np.array):
        """
        Draw the mesh to the scene.

        :param P: projection matrix
        :param V: view matrix
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
