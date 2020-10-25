import glfw
from ecm3423.scene import Scene


def present_scene(scene: Scene, width: int = 800, height: int = 600, title: str = "Scene"):
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.RESIZABLE, False)

    window = glfw.create_window(width, height, title, None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    glfw.set_cursor_pos_callback(window, scene.cursor_position_callback)
    glfw.set_key_callback(window, scene.key_callback)
    glfw.set_mouse_button_callback(window, scene.mouse_button_callback)

    scene.setup()

    while not glfw.window_should_close(window):
        scene.draw()

        glfw.swap_buffers(window)
        glfw.poll_events()


def main():
    if not glfw.init():
        return

    scene = Scene()
    present_scene(scene, title="Fur Effect")

    glfw.terminate()


if __name__ == "__main__":
    main()
