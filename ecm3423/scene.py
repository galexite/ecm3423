from OpenGL.GL import *
from ecm3423.camera import Camera
import glfw


class Scene:
    last_x = 0.
    last_y = 0.

    mouse_button_pressed = False

    def __init__(self):
        self.camera = Camera()

    def setup(self):
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)

    def draw(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

    def cursor_position_callback(self, window: glfw._GLFWwindow, x: float, y: float):
        if self.mouse_button_pressed:
            self.camera.translate(x, y)

    def key_callback(self, window: glfw._GLFWwindow, key: int, scancode: int, action: int, modifiers: int):
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


    def mouse_button_callback(self, window: glfw._GLFWwindow, button: int, action: int, modifiers: int):
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                self.mouse_button_pressed = True
            if action == glfw.RELEASE:
                self.mouse_button_pressed = False
