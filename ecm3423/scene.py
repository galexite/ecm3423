from os.path import realpath, join, dirname

import numpy as np
from OpenGL.GL import *
import glfw

from ecm3423.camera import Camera
from ecm3423.shaders import ShaderStore
from ecm3423.mesh import Mesh
from ecm3423.fur_model import FurModel
from ecm3423.util import build_frustum_matrix, build_rotation_matrix_z, build_rotation_matrix_y, build_rotation_matrix_x

RESOURCE_PATH = join(dirname(realpath(__file__)), "..")


class Scene:
    """
    The application's main scene, which manages the entire rendering pipeline, from model to screen.
    """

    last_x = 0.0
    last_y = 0.0

    mouse_button_pressed = False

    model = None

    def __init__(self):
        self.camera = Camera()
        self.shader_store = ShaderStore(join(RESOURCE_PATH, "shaders"))

        near = 1.5
        far = 50
        left = -1.0
        right = 1.0
        top = -1.0
        bottom = 1.0

        self.P = build_frustum_matrix(left, right, bottom, top, near, far)

    def setup(self):
        """
        Configure OpenGL before we start drawing.
        """
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glEnable(GL_MULTISAMPLE)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.shader_store.compile()

        mesh = Mesh.from_obj_file(join(RESOURCE_PATH, "models/bunny_world.obj"))
        self.model = FurModel(mesh, self.shader_store.get("fur"), M=build_rotation_matrix_y(np.pi / 2.))

        # bunny_2 = Model(mesh, Material(self.shader_store.get("normals")), M=build_rotation_matrix_y(np.pi / 2.))
        # self.models.append(bunny_2)

    def draw(self):
        """
        Draw our scene's objects to the screen.
        """
        glClearColor(0.52, 0.8, 0.92, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.camera.update()

        self.model.draw(self.P, self.camera.V)

    def cursor_position_callback(self, _window: glfw._GLFWwindow, x: int, y: int):
        """
        Handle updates to the mouse cursor's position.
        """
        if self.mouse_button_pressed:
            self.camera.translate(self.last_x - x, y - self.last_y)

        self.last_x = x
        self.last_y = y

    def key_callback(
        self,
        _window: glfw._GLFWwindow,
        key: int,
        _scancode: int,
        action: int,
        _modifiers: int,
    ):
        """
        Handle keyboard presses.

        :param _window: window which triggered this key event (not used)
        :param key: key involved in the event
        :param _scancode: keyboard scancode (not used)
        :param _action: keyboard action type
        :param _modifiers: any modifiers which were in activated at the time (not used)
        """
        if key == glfw.KEY_L:
            # increase fur length
            self.model.set_length(self.model.length + 0.01)
        elif key == glfw.KEY_K:
            # decrease fur length
            self.model.set_length(self.model.length - 0.01)
        elif key == glfw.KEY_M:
            # increase fur density
            self.model.set_density(self.model.density + 0.5)
        elif key == glfw.KEY_N:
            # decrease fur density
            self.model.set_density(self.model.density - 0.5)
        elif key == glfw.KEY_B:
            # move fur in random direction
            self.model.set_direction(np.random.default_rng().normal(), np.random.default_rng().normal())
        elif key == glfw.KEY_UP:
            # rotate the bunny upwards
            self.camera.rotate(-1, 0)
        elif key == glfw.KEY_DOWN:
            # rotate the bunny downwards
            self.camera.rotate(1, 0)
        elif key == glfw.KEY_LEFT:
            # rotate the bunny left
            self.camera.rotate(0, -1)
        elif key == glfw.KEY_RIGHT:
            # rotate the bunny right
            self.camera.rotate(0, 1)

    def mouse_button_callback(
        self, window: glfw._GLFWwindow, button: int, action: int, _modifiers: int
    ):
        """
        Handle mouse button state changes.

        :param window: window which the event was triggered on
        :param action: what action has occurred on the given button (PRESS, RELEASE...)
        :param _modifiers: any modifiers which were in activated at the time (not used)
        """
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                self.mouse_button_pressed = True
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_HIDDEN)
            if action == glfw.RELEASE:
                self.mouse_button_pressed = False
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
