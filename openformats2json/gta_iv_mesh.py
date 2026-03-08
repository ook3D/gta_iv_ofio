from pathlib import Path
from typing import TextIO

from .common import parse_indices
from ..utils import jump_to, to_float, to_int


def gta_iv_mesh_to_dict(filepath: Path | str) -> dict:
    with open(filepath, "r", encoding="utf-8") as reader:
        line = jump_to("Version", reader)
        if line == "":
            raise ValueError(f"Version header not found! File: {filepath}")
        elif line.strip().split(maxsplit=1)[1] != "11 13":
            raise ValueError(f"Version mismatch. File: {filepath}")
        # print(f"Got GTA IV Mesh at {filepath}")

        data = {"Version": "11 13"}

        data.update(read_mesh_file(reader))

    return data


def read_mesh_file(reader) -> dict:
    data = {}
    line = jump_to("Skinned", reader).strip()
    if line == "":
        raise ValueError("Skinned header not found")
    elif line.split()[1].isnumeric():
        data["Skinned"] = bool(int(line.split()[1]))
    else:
        raise ValueError("Invalid Skinned value")

    if not data["Skinned"]:
        jump_to("Bounds", reader)
        reader.readline()
        line = reader.readline().strip()
        bounds = []
        while "}" not in line and line != "":
            bounds.append(to_float(line.split()))
            line = reader.readline()
        data["Bounds"] = bounds
    data["Geometries"] = read_geometry_data(data["Skinned"], reader)
    return data


def read_geometry_data(is_skinned: bool, reader) -> list:
    meshes = []
    line = reader.readline()

    while "}" not in line and line != "":
        if "Mtl" in line:
            mesh = {"Material": int(line.split()[1])}
            mesh.update(read_mesh_data(is_skinned, reader))
            meshes.append(mesh)
        line = reader.readline()

    return meshes


def read_mesh_data(is_skinned: bool, reader: TextIO) -> dict:
    line = reader.readline()
    mesh = dict()

    while "}" not in line:
        if "Idx" in line:
            mesh["Indices"] = parse_indices(reader)
        elif "Verts" in line:
            if is_skinned:
                (
                    mesh["Vertices"],
                    mesh["VertxNormals"],
                    mesh["BlendWeight"],
                    mesh["BlendIndices"],
                    mesh["VertxColors"],
                    mesh["UVCoords"],
                ) = parse_vertices_skinned(reader)
            else:
                (
                    mesh["Vertices"],
                    mesh["VertxNormals"],
                    mesh["VertxColors"],
                    mesh["UVCoords"],
                ) = parse_vertices(reader)
            reader.readline()  # skip the '}' of "Prim'
        line = reader.readline()
    return mesh


def parse_vertices(reader: TextIO) -> list:
    line = jump_to("/", reader)

    vertx, normals, colors, uv_coords = [], [], [], []
    uv_coord_0, uv_coord_1, uv_coord_2, uv_coord_3, uv_coord_4, uv_coord_5 = [], [], [], [], [], []

    while "}" not in line:
        dataline = line.split("/")

        vertx.append(to_float(dataline[0].split()))
        normals.append(to_float(dataline[1].split()))

        color_bgra = dataline[2].split()
        color_rgba = color_bgra[:-1][::-1] + [color_bgra[-1]]  # BGRA to RGBA, thanks BrynnaDaRosa(midsummerlibertycity)
        colors.append(to_int(color_rgba))

        uv_coord_0.append(to_float(dataline[4].split()))
        uv_coord_1.append(to_float(dataline[5].split()))
        uv_coord_2.append(to_float(dataline[6].split()))
        uv_coord_3.append(to_float(dataline[7].split()))
        uv_coord_4.append(to_float(dataline[8].split()))
        uv_coord_5.append(to_float(dataline[9].split()))

        line = reader.readline()
    uv_coords = [uv_coord_0, uv_coord_1, uv_coord_2, uv_coord_3, uv_coord_4, uv_coord_5]

    return [vertx, normals, colors, uv_coords]


def parse_vertices_skinned(reader: TextIO) -> list:
    line = jump_to("/", reader)

    vertx, normals, blend_weight, blend_indices, colors, uv_coords = ([] for _ in range(6))  # fuck you, black formatter
    uv_coord_0, uv_coord_1 = [], []

    while "}" not in line:
        dataline = line.split("/")

        vertx.append(to_float(dataline[0].split()))
        normals.append(to_float(dataline[1].split()))
        blend_weight.append(to_float(dataline[2].split()))
        blend_indices.append(to_int(dataline[3].split()))

        color_bgra = dataline[4].split()
        color_rgba = color_bgra[:-1][::-1] + [color_bgra[-1]]  # BGRA to RGBA, thanks BrynnaDaRosa(midsummerlibertycity)
        colors.append(to_int(color_rgba))

        uv_coord_0.append(to_float(dataline[6].split()))
        uv_coord_1.append(to_float(dataline[7].split()))

        line = reader.readline()
    uv_coords = [uv_coord_0, uv_coord_1]

    return [vertx, normals, blend_weight, blend_indices, colors, uv_coords]
