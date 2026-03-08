from typing import TextIO

from .iv_shaders import get_shader_params
from ..utils import jump_to, convert_str, to_float, to_none


def gta_iv_odr_to_dict(filepath) -> dict:
    with open(filepath, "r") as reader:
        line = jump_to("Version", reader)
        if line == "":
            raise ValueError(f"Version header not found! File: {filepath}")
        elif line.strip().split(maxsplit=1)[1] != "110 12":
            raise ValueError(f"Version mismatch. File: {filepath}")
        # print(f"Got GTA IV Drawable at {filepath}")

        data = {"Version": "110 12"}

        data.update(parse_drawable_data(reader))

        return data


def parse_drawable_data(reader: TextIO) -> dict:
    drawable_data = dict()
    line = reader.readline()

    while "}" not in line and line != "":
        key = line.strip().split(maxsplit=1)[0]

        match key:
            case "shadinggroup":
                drawable_data["Shaders"] = parse_shader_data(reader)
            case "skel":
                drawable_data["Skeleton"] = parse_single_line_data("skel", reader)
            case "lodgroup":
                drawable_data["LodGroup"] = parse_lod_data(reader)
            case "light":
                drawable_data["Light"] = parse_single_line_data("light", reader)
        line = reader.readline()

    return drawable_data


def parse_shader_data(reader) -> list:
    shaders = []
    line = reader.readline()

    while "}" not in line:
        if line.split(maxsplit=1)[0].endswith(".sps"):
            shader_type, shader_param_value = (line.strip().split(maxsplit=1) + [None])[:2]
            shader_params = parse_shader_params(shader_type[:-4], shader_param_value)
            shader_params["shader_type"] = shader_type[:-4]
            shaders.append(shader_params)

        line = reader.readline()
    reader.readline()
    return shaders


def parse_shader_params(shader_type: str, shader_value: list | str) -> dict:
    shader_params = dict()
    for key, value in zip(get_shader_params(shader_type), convert_str(shader_value.split())):
        if "Vector4" in key:
            shader_params[key] = convert_str(value.split(";"))
        else:
            shader_params[key] = value
    return shader_params


def parse_single_line_data(token: str, reader: TextIO) -> str | None:
    line = reader.readline()

    while "}" not in line:
        if line.lstrip().startswith(token):
            reader.readline()
            return line.split()[1]
        line = reader.readline()


def parse_lod_data(reader: TextIO) -> dict:
    lod_data = dict()
    reader.readline()
    line = reader.readline()

    while "}" not in line:
        key, value = (line.strip().split(maxsplit=1) + [None])[:2]
        value = value.split() if " " in value else value
        if key in ["high", "med", "low", "vlow"]:
            no_of_meshes = to_none(value[0])
            if no_of_meshes is None:
                lod_data.update({key.capitalize(): {"Distance": float(value[1])}})
            else:
                meshes = []
                for i in range(no_of_meshes):
                    meshes.append(value[i + 1])
                    value.pop(i + 2)
                lod_data.update({key.capitalize(): {"Mesh": meshes, "Distance": float(value[-1])}})
        elif key[0] != "r":
            lod_data[key] = to_float(value)
        else:
            lod_data[key] = float(value)

        line = reader.readline()
    return lod_data
