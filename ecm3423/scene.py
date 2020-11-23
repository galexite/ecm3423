from os.path import realpath, join, dirname

import numpy as np
from OpenGL.GL import *
import pygame

from ecm3423.camera import Camera
from ecm3423.shaders import ShaderStore
from ecm3423.mesh import Mesh
from ecm3423.fur_model import FurModel
from ecm3423.util import build_frustum_matrix, build_rotation_matrix_z, build_rotation_matrix_y, \
    build_rotation_matrix_x, build_translation_matrix

RESOURCE_PATH = join(dirname(realpath(__file__)), "..")


class Scene:
    """
    The application's main scene, which manages the entire rendering pipeline, from model to screen.
    """

    def __init__(self):
        self.models = []
        self.rot_speed = 0.2
        self.translation_speed = 2.0
        self.camera = Camera()
        self.shader_store = ShaderStore(join(RESOURCE_PATH, "shaders"))
        self.mouse_rel_pos = None

        near = 1.5
        far = 50
        left = -1.0
        right = 1.0
        top = -1.0
        bottom = 1.0

        self.width = 0
        self.height = 0

        self.P = build_frustum_matrix(left, right, bottom, top, near, far)

    def setup(self, width: int, height: int):
        """
        Configure OpenGL before we start drawing.
        """
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.width = width
        self.height = height

        self.shader_store.compile()

        M_bunny = np.matmul(build_translation_matrix([-2.0, 0.0, 0.0]), build_rotation_matrix_y(np.pi / 2.))
        bunny_mesh = Mesh.from_obj_file(join(RESOURCE_PATH, "models/bunny_world.obj"))
        self.models.append(FurModel(bunny_mesh, self.shader_store.get("fur"), M=M_bunny))

        M_torus = np.matmul(build_translation_matrix([2.0, 0.0, 0.0]), build_rotation_matrix_x(np.pi / 2.))
        torus_mesh = Mesh.from_obj_file(join(RESOURCE_PATH, "models/torus.obj"))
        self.models.append(FurModel(torus_mesh, self.shader_store.get("fur"), M=M_torus))

    def draw(self):
        """
        Draw our scene's objects to the screen.
        """
        glClearColor(0.52, 0.8, 0.92, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.camera.update()

        for model in self.models:
            model.draw(self.P, self.camera.V)

    def cursor_position_callback(self, x: int, y: int):
        """
        Handle updates to the mouse cursor's position.

        :param x: mouse x position
        :param y: mouse y position
        """
        self.camera.translate((x / self.width) * self.translation_speed, (y / self.height) * self.translation_speed)

    def key_callback(self, key: int):
        """
        Handle keyboard presses.

        :param key: key involved in the event
        """
        if key == pygame.K_l:
            # increase fur length
            for model in self.models:
                model.set_length(model.length + 0.01)
        elif key == pygame.K_k:
            # decrease fur length
            for model in self.models:
                model.set_length(model.length - 0.01)
        elif key == pygame.K_m:
            # increase fur density
            for model in self.models:
                model.set_density(model.density + 0.5)
        elif key == pygame.K_n:
            # decrease fur density
            for model in self.models:
                model.set_density(model.density - 0.5)
        elif key == pygame.K_b:
            # move fur in random direction
            psi = np.random.default_rng().normal()
            phi = np.random.default_rng().normal()
            for model in self.models:
                model.set_direction(psi, phi)
        elif key == pygame.K_UP:
            # rotate the bunny upwards
            self.camera.rotate(-self.rot_speed, 0)
        elif key == pygame.K_DOWN:
            # rotate the bunny downwards
            self.camera.rotate(self.rot_speed, 0)
        elif key == pygame.K_LEFT:
            # rotate the bunny left
            self.camera.rotate(0, -self.rot_speed)
        elif key == pygame.K_RIGHT:
            # rotate the bunny right
            self.camera.rotate(0, self.rot_speed)

    def process_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                self.key_callback(event.key)
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed(3)[0]:
                    if self.mouse_rel_pos is not None:
                        self.mouse_rel_pos = pygame.mouse.get_rel()
                        self.cursor_position_callback(*self.mouse_rel_pos)
                    else:
                        self.mouse_rel_pos = pygame.mouse.get_rel()
                else:
                    self.mouse_rel_pos = None

        return True
