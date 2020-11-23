import numpy as np
from ecm3423.util import build_translation_matrix, build_rotation_matrix_xy


class Camera:
    """
    A simple camera implementation which permits rotation and x/y translations.
    """

    center = [0.0, 0.0, 0.0]
    psi = 0.0
    phi = 0.0
    distance = 7.0

    def __init__(self):
        self.V = np.identity(4)
        self.V[2, 3] = -self.distance

        self.D = build_translation_matrix(self.center)
        self.R = build_rotation_matrix_xy(self.psi, self.phi)
        self.T = build_translation_matrix([0.0, 0.0, -self.distance])

    def update(self):
        """
        Apply changes in camera position and rotation to the view matrix.
        """
        self.V = np.matmul(np.matmul(self.T, self.R), self.D)

    def rotate(self, psi: float, phi: float):
        """
        Rotate the camera by given deltas in x and y direction.

        :param psi:
        :param phi:
        """
        self.phi += phi
        self.psi += psi
        self.R = build_rotation_matrix_xy(self.psi, self.phi)

        self.update()

    def translate(self, dx: float, dy: float):
        """
        Move the camera by the given delta x/y coordinates.

        :param dx: change in the camera's x coordinate
        :param dy: change in the camera's y coordinate
        """
        self.center[0] += dx
        self.center[1] -= dy
        self.D = build_translation_matrix(self.center)

        self.update()
