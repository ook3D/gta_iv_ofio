from .gta_iv_wdr import parse_drawable_data
from ..utils import jump_to


def gta_iv_odd_to_dict(filepath) -> dict:
    with open(filepath, "r") as reader:
        line = jump_to("Version", reader)
        if line == "":
            raise ValueError("Version header not found")
        elif line.strip().split(maxsplit=1)[1] != "110 12":
            raise ValueError("Version mismatch")

        data = {"Version": "110 12", "Drawables": {}}

        line = reader.readline()
        while "}" not in line and line != "":
            line = jump_to("gtaDrawable", reader)  # ? Investigate, can backfire
            if line == "":
                break
            drawable_name = line.strip().split()[1]
            reader.readline()
            drawable_data = parse_drawable_data(reader)
            data["Drawables"][drawable_name] = drawable_data

    return data
