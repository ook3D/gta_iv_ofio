from typing import TextIO

from .gta_iv_wbd import parse_bound_data
from .gta_iv_wdr import parse_drawable_data
from ..utils import jump_to, to_float


def gta_iv_child_to_dict(filepath) -> dict:
    with open(filepath, "r") as reader:
        line = jump_to("Version", reader)
        if line == "":
            raise ValueError
        elif line.strip().split(maxsplit=1)[1] != "112 2":
            raise ValueError("Incorrect Version")

        data = {"Version": "112 2"}

        line = reader.readline()
        while line.strip() != "":
            key = line.strip().split()[0]
            match key:
                case "drawable":
                    data["Drawable"] = parse_drawable_data(reader)
                case "boundTransform":
                    data["boundTransform"] = parse_bound_transform_data(reader)
                case "bound":
                    data["Bound"] = parse_bound_data(reader)
            line = reader.readline()

        return data


def parse_bound_transform_data(reader: TextIO) -> list:
    bound_transform_data = []
    reader.readline()
    line = reader.readline()

    while "}" not in line:
        bound_transform_data.append(to_float(line.split()))
        line = reader.readline()

    return bound_transform_data
