import numpy as np


def build_translation_matrix(t: int) -> np.array:
    n = len(t)
    T = np.identity(n + 1, dtype="f")
    T[:n, -1] = t
    return T


def build_elementary_rotation_matrix(theta: float) -> np.array:
    s, c = np.sin(theta), np.cos(theta)

    return np.array([
        [c, s],
        [-s, c]
    ])


def build_rotation_matrix_x(psi: float) -> np.array:
    Rx = np.identity(4)
    Rx[1:3, 1:3] = build_elementary_rotation_matrix(psi)

    return Rx


def build_rotation_matrix_y(phi: float) -> np.array:
    Ry = np.identity(4)
    Ry[0:2, 0:2] = build_elementary_rotation_matrix(phi)

    return Ry


def build_rotation_matrix_xy(psi: float, phi: float) -> np.array:
    return np.matmul(build_rotation_matrix_x(psi), build_rotation_matrix_y(phi))
