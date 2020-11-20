from typing import Dict

import numpy as np
from OpenGL.GL import *

from ecm3423.shaders import Shaders

NOISE_SIZE = 512


class Material:
    def __init__(self, shaders: Shaders):
        self.shaders = shaders

    def bind(self, attrs: Dict[str, int]):
        self.shaders.link(attrs)

    def use(self, P: np.array, V: np.array, M: np.array):
        self.shaders.use(P, V, M)

class Fur(Material):
    def __init__(self, shaders: Shaders, density: float = 10.0, length: float = 0.2, gravity: np.array = np.array([0., -0.5, 0.])):
        super().__init__(shaders)

        self.shaders.add_uniform("density", density)
        self.shaders.add_uniform("length", length)
        self.shaders.add_uniform("gravity", gravity)
        # self.shaders.add_uniform("noise_texture", 0)

        self.density = density
        self.length = length
        self.gravity = gravity

        self.texture = glGenTextures(1)

        noise = np.random.default_rng().normal(size=(NOISE_SIZE, NOISE_SIZE))
        ones = np.ones((NOISE_SIZE, NOISE_SIZE, 3))
        self.texture_data = np.dstack((ones, noise))

    def _bind_texture(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(self.texture, 0, GL_RGBA, NOISE_SIZE, NOISE_SIZE, 0, GL_RGBA, GL_FLOAT, self.texture_data)

    def bind(self, attrs: Dict[str, int]):
        super().bind(attrs)

        # self._bind_texture()

    def use(self, P: np.array, V: np.array, M: np.array):
        super().use(P, V, M)

        # glActiveTexture(GL_TEXTURE0)
        # glBindTexture(self.texture)

    def __del__(self):
        glDeleteTextures(self.texture)

