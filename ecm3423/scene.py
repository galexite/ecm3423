from OpenGL.GL import *
import glfw

from ecm3423.camera import Camera


class Scene:
    """
    The application's main scene, which manages the entire rendering pipeline, from model to screen.
    """

    last_x = 0.0
    last_y = 0.0

    mouse_button_pressed = False

    def __init__(self):
        self.camera = Camera()

    def setup(self):
        """
        Configure OpenGL before we start drawing.
        """
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)

    def draw(self):
        """
        Draw our scene's objects to the screen.
        """
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

    def cursor_position_callback(self, _window: glfw._GLFWwindow, x: float, y: float):
        """
        Handle updates to the mouse cursor's position.
        """
        if self.mouse_button_pressed:
            self.camera.translate(x, y)

    def key_callback(
        self,
        _window: glfw._GLFWwindow,
        key: int,
        _scancode: int,
        _action: int,
        _modifiers: int,
    ):
        """
        Handle keyboard presses.
        """
        if key == glfw.KEY_L:
            # increase fur length
            pass
        elif key == glfw.KEY_K:
            # decrease fur length
            pass
        elif key == glfw.KEY_M:
            # increase fur density
            pass
        elif key == glfw.KEY_N:
            # decrease fur density
            pass
        elif key == glfw.KEY_B:
            # move fur in random direction
            pass

    def mouse_button_callback(
        self, window: glfw._GLFWwindow, button: int, action: int, _modifiers: int
    ):
        """
        Handle mouse button state changes.
        """
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                self.mouse_button_pressed = True
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_HIDDEN)
            if action == glfw.RELEASE:
                self.mouse_button_pressed = False
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
