import pygame
from ecm3423.scene import Scene


def present_scene(
    scene: Scene, width: int = 800, height: int = 600, title: str = "Scene"
):
    """
    Present a given Scene object by creating a new window of the given width and height, with a title.

    :param scene: a scene to draw
    :param width: the new window's width
    :param height: the new window's height
    :param title: title for the new window
    :return:
    """

    # Set up Pygame to explicitly request an OpenGL 3.2 core profile context.
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 2)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    screen = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF, 24)

    scene.setup(width, height)

    # Our main draw loop.
    running = True
    while running:
        scene.draw()

        pygame.display.flip()
        running = scene.process_events()


def main():
    pygame.init()

    scene = Scene()
    present_scene(scene, title="Fur Effect")


if __name__ == "__main__":
    main()
