import numpy as np
from typing import List


def build_translation_matrix(t: List[float]) -> np.array:
    n = len(t)
    T = np.identity(n + 1, dtype="f")
    T[:n, -1] = t
    print(T)
    return T


def build_scale_matrix(x: float, y: float, z: float) -> np.array:
    return np.array([
        [x, 0, 0, 0],
        [0, y, 0, 0],
        [0, 0, z, 0],
        [0, 0, 0, 1]
    ])


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
    Ry[0:3:2, 0:3:2] = build_elementary_rotation_matrix(phi)

    return Ry


def build_rotation_matrix_z(theta: float) -> np.array:
    Rz = np.identity(4)
    Rz[0:2, 0:2] = build_elementary_rotation_matrix(theta)

    return Rz


def build_rotation_matrix_xy(psi: float, phi: float) -> np.array:
    return np.matmul(build_rotation_matrix_x(psi), build_rotation_matrix_y(phi))


def build_orthographic_projection_matrix(
    left: float, right: float, bottom: float, top: float, near: float, far: float
) -> np.array:
    return np.array(
        [
            [2 / (right - left), 0, 0, (right + left) / (right - left)],
            [0, -2 / (top - bottom), 0, (top + bottom) / (top - bottom)],
            [0, 0, 2 / (far - near), (far + near) / (far - near)],
            [0, 0, 0, 1],
        ]
    )


def build_frustum_matrix(
    left: float, right: float, bottom: float, top: float, near: float, far: float
) -> np.array:
    return np.array(
        [
            [2 * near / (right - left), 0, (right + left) / (right - left), 0],
            [0, -2 * near / (top - bottom), (top + bottom) / (top - bottom), 0],
            [0, 0, -(far + near) / (far - near), -2 * far * near / (far - near)],
            [0, 0, -1, 0],
        ]
    )


def build_pose_matrix(
    position: List[float] = [0, 0, 0],
    orientation: float = 0,
    scale: List[float] = [1, 1, 1],
):
    R = build_rotation_matrix_z(orientation)
    T = build_translation_matrix(position)
    S = build_scale_matrix(scale[0], scale[1], scale[2])

    return np.matmul(np.matmul(T, R), S)


def homogenise(vec):
    return np.hstack([vec, 1.0])


def unhomogenise(vec):
    return vec[:-1] / vec[-1]
