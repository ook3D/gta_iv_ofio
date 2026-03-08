from .gta_iv_wbd import parse_bound_data
from ..utils import jump_to


def gta_iv_obd_to_dict(filepath) -> dict:
    with open(filepath, "r") as reader:
        line = jump_to("Version", reader)
        if line == "":
            raise ValueError
        elif line.strip().split(maxsplit=1)[1] != "32 11":
            raise ValueError("Incorrect Version")

        data = {"Version": "32 11"}

        line = jump_to("phBound", reader)
        if line == "":
            raise ValueError("No Bound Data Found")
        while "}" not in line and line != "":
            data.update(parse_bound_data(reader))
            line = reader.readline()
        data.update(parse_bound_data(reader))

    return data
