from pathlib import Path
from typing import TextIO

from ..utils import to_int


def parse_indices(reader: TextIO) -> list:
    reader.readline()
    line = reader.readline()
    indices = []

    while "}" not in line:
        datalines = line.strip().split()
        while datalines:
            indices.append(to_int(datalines[:3]))
            del datalines[:3]
        line = reader.readline()
    return indices


def collect_meshes(data: dict) -> list[Path]:
    list_meshes = []
    if data.get("Drawable") is not None:
        list_meshes = iter_meshes(data["Drawable"]["LodGroup"])
    elif data.get("LodGroup") is not None:
        list_meshes = iter_meshes(data["LodGroup"])
    if any(["High", "Med", "Low", "Vlow"]) in data:
        list_meshes = iter_meshes(data)
    return list_meshes


def iter_meshes(data: dict) -> list[Path]:
    list_meshes = []
    for lod in [x for x in data if x in ["High", "Med", "Low", "Vlow"]]:
        if data[lod].get("Mesh") is not None:
            list_meshes.extend([Path(x) for x in data[lod]["Mesh"]])
    return list_meshes


def collect_children(data: dict) -> dict[Path, str]:
    children_dict = dict()
    for group in data:
        if data.get(group).get("Children") is not None:
            for child in data[group]["Children"]:
                children_dict[Path(child["Path"])] = group
        if data.get(group).get("Groups") is not None:
            children = collect_children(data[group]["Groups"])
            if len(children):
                children_dict.update(children)

    return children_dict
