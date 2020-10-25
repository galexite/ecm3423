from enum import Enum
from typing import Optional
import numpy as np


class Mesh:
    def __init__(
        self, vertices: np.array, faces: np.array, normals: Optional[np.array] = None
    ):
        self.vertices = vertices
        self.faces = faces

        if normals == None:
            self._calculate_normals()
        else:
            self.normals = normals

    def _calculate_normals(self):
        """
        Based on https://www.khronos.org/opengl/wiki/Calculating_a_Surface_Normal
        """
        self.normals = np.zeros((self.vertices.shape[0], 3), dtype="f")

        for i, f in enumerate(self.faces):
            u = self.vertices[f[1]] - self.vertices[f[0]]
            v = self.vertices[f[3]] - self.vertices[f[0]]

            self.normals[i, 0] = (u[1] * v[2]) - (u[2] * v[1])
            self.normals[i, 1] = (u[2] * v[0]) - (u[0] * v[2])
            self.normals[i, 2] = (u[0] * v[1]) - (u[1] - v[0])

    @staticmethod
    def from_obj_file(path: str) -> Mesh:
        vertices = []
        faces = []

        with open(path, "r") as fp:
            for line, num in enumerate(fp):
                spl = line.split()

                if spl[0] == "#":
                    continue
                elif spl[0] == "v":
                    if len(spl) != 4:
                        raise ValueError(
                            f"{path}, line {num}: v must by accompanied by 3 float components"
                        )

                    vertices.append(map(float, spl[1:]))
                    continue
                elif spl[0] == "f":
                    if len(spl) != 4 and len(spl) != 5:
                        raise ValueError(
                            f"{path}, line {num}: f must be accompanied either 3 or 4 components"
                        )

                    faces.append(
                        [[np.uint32(i) - 1 for j in i.split()] for i in spl[1:]]
                    )
                    continue

        return Mesh(np.array(vertices, dtype="f"), np.array(faces, dtype="uint32"))
