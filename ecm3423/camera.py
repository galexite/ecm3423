import numpy as np
from ecm3423.util import build_translation_matrix, build_rotation_matrix_xy


class Camera:
    V = np.identity(4)

    center = [0., 0., 0.]
    psi = 0.
    phi = 0.
    distance = 5.

    rot_speed = 0.5

    def __init__(self):
        self.V[2, 3] = -5.

        self.D = -build_translation_matrix(self.center)
        self.R = build_rotation_matrix_xy(self.psi, self.phi)
        self.T = build_translation_matrix([0., 0., -self.distance])

    def update(self):
        self.V = np.matmul(np.matmul(T, R), D)

    def rotate(self, psi: int, phi: int):
        self.phi += phi * rot_speed
        self.psi += psi * rot_speed
        self.R = build_rotation_matrix_xy(self.psi, self.phi)

        self.update()

    def translate(self, dx: int, dy: int):
        self.center[0] += dx
        self.center[1] += dy
        self.D = -build_translation_matrix(self.center)
        
        self.update()
    