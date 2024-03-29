from typing import Optional
import numpy as np


class Mesh:
    """
    Represents a mesh imported from a Wavefront OBJ file on disk, to render to a scene.
    """

    def __init__(
        self, vertices: np.array, faces: np.array, normals: Optional[np.array] = None
    ):
        self.vertices = vertices
        self.faces = faces

        if normals is None:
            self._calculate_normals()
        else:
            self.normals = normals

    def _calculate_normals(self):
        """
        Based on https://www.khronos.org/opengl/wiki/Calculating_a_Surface_Normal
        """
        self.normals = np.zeros((self.vertices.shape[0], 3), dtype="f")

        for f in self.faces:
            u = self.vertices[f[1]] - self.vertices[f[0]]
            v = self.vertices[f[2]] - self.vertices[f[0]]

            self.normals[f, :] += np.cross(u, v)

        self.normals /= np.linalg.norm(self.normals, axis=1, keepdims=True)

    @staticmethod
    def from_obj_file(path: str) -> "Mesh":
        """
        Create a new Mesh object from a Wavefront OBJ file stored on disk at the given path.

        :param path: path to a Wavefront OBJ file on disk to load as a new Mesh object
        """
        vertices = []
        faces = []

        with open(path, "r") as fp:
            for num, line in enumerate(fp):
                spl = line.split()

                if spl[0] == "#":
                    continue
                elif spl[0] == "v":
                    if len(spl) != 4:
                        raise ValueError(
                            f"{path}, line {num}: v must by accompanied by 3 float components"
                        )

                    vertices.append(spl[1:])  # numpy casts to float for us later
                    continue
                elif spl[0] == "f":
                    if len(spl) != 4 and len(spl) != 5:
                        raise ValueError(
                            f"{path}, line {num}: f must be accompanied either 3 or 4 components"
                        )

                    faces.append(
                        [[np.uint32(j) - 1 for j in i.split("/")][0] for i in spl[1:]]
                    )
                    continue

        faces = np.array(faces, dtype="uint32")
        vertices = np.array(vertices, dtype="f")

        if faces.shape[1] == 4:
            # Convert these quad faces to triangles - GL_QUADS is deprecated in OpenGL 3.2.
            new_faces = np.ndarray((faces.shape[0] * 2, 3), "i")
            new_faces[0::2] = faces[:, :-1]
            new_faces[1::2] = np.hstack((new_faces[::2, ::2], faces[:, 3][:, None]))
            return Mesh(vertices, new_faces)

        return Mesh(vertices, faces)
