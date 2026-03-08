from typing import TextIO

from ..utils import jump_to


def gta_iv_otd_to_dict(filepath) -> dict:
    with open(filepath, "r") as reader:
        line = jump_to("Version", reader)
        if line == "":
            raise ValueError("Version Header not found")
        elif line.strip().split(maxsplit=1)[1] != "8 10":
            raise ValueError("Version mismatch")

        data = {"Version": "8 10", "Textures": {}}

        line = jump_to("grcTexture", reader)
        if line == "":
            raise ValueError("No Texture Data Found")
        while "}" not in line and line != "":
            if "grcTexture" in line:
                texture_data = parse_texture_data(reader)
                texture_name = texture_data.pop("Name")
                data["Textures"][texture_name] = texture_data
            line = reader.readline()

    return data


def parse_texture_data(reader: TextIO) -> dict:
    texture_data = {}
    reader.readline()
    line = reader.readline()
    while "}" not in line:
        key, value = (line.strip().split(maxsplit=1) + [None])[:2]

        match key:
            case "Type":
                texture_data["Type"] = value
            case "Name":
                texture_data["Name"] = value
            case "MipMaps":
                texture_data["MipMaps"] = int(value)
            case "PixelFormat":
                texture_data["PixelFormat"] = value
        line = reader.readline()
    return texture_data
