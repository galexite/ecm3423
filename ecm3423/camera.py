import numpy as np
from ecm3423.util import build_translation_matrix, build_rotation_matrix_xy


class Camera:
    """
    A simple camera implementation which permits rotation and x/y translations.
    """

    center = [0.0, 0.0, 0.0]
    psi = 0.0
    phi = 0.0
    distance = 5.0

    rot_speed = 0.2
    translate_speed = 0.01

    def __init__(self):
        self.V = np.identity(4)
        self.V[2, 3] = -5.0

        self.D = build_translation_matrix(self.center)
        self.R = build_rotation_matrix_xy(self.psi, self.phi)
        self.T = build_translation_matrix([0.0, 0.0, -self.distance])

    def update(self):
        """
        Apply changes in camera position and rotation to the view matrix.
        """
        self.V = np.matmul(np.matmul(self.T, self.R), self.D)

    def rotate(self, psi: int, phi: int):
        """
        Rotate the camera by given deltas in x and y direction.
        """
        self.phi += phi * self.rot_speed
        self.psi += psi * self.rot_speed
        self.R = build_rotation_matrix_xy(self.psi, self.phi)

        self.update()

    def translate(self, dx: int, dy: int):
        """
        Move the camera by the given delta x/y coordinates.
        """
        self.center[0] += dx * self.translate_speed
        self.center[1] += dy * self.translate_speed
        self.D = build_translation_matrix(self.center)

        self.update()
