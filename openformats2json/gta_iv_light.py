from typing import TextIO

from ..utils import jump_to, to_float, to_int


def gta_iv_light_to_dict(filepath) -> dict:
    with open(filepath, "r") as reader:
        line = jump_to("Version", reader)
        if line == "":
            raise ValueError(f"Version header not found! File: {filepath}")
        elif line.strip().split(maxsplit=1)[1] != "1 10":
            raise ValueError(f"Version mismatch. File: {filepath}")
        # print(f"Got GTA IV Light at {filepath}")

        data = {"Version": "1 10", "Lights": read_gta_iv_light_file(reader)}

        return data


def read_gta_iv_light_file(reader: TextIO) -> list:
    lights = []

    line = reader.readline()

    while "}" not in line and line != "":
        line = jump_to("Attribute", reader)
        if line == "":
            break
        line = reader.readline()
        lights.append(read_gta_iv_light_data(reader))

    return lights


def read_gta_iv_light_data(reader):
    light = dict()

    line = reader.readline()
    while "}" not in line:
        key, value = (line.strip().split(maxsplit=1) + [None])[:2]

        match key:
            case "Position":
                light["Position"] = to_float(value.split())
            case "Direction":
                light["Direction"] = to_float(value.split())
            case "Origin":
                light["Tangent"] = to_float(value.split())
            case "Color":
                light["Color"] = to_int(value.split())
            case "_f28":  # Falloff exp
                light["VolumeSoftness"] = float(value)
            case "_f2C":
                light["VolumeIntensity"] = float(value)
            case "_f30":
                light["VolumeSize"] = float(value)
            case "Distance":
                light["Range"] = float(value)
            case "Range":
                light["Intensity"] = float(value)
            case "CoronaSize":
                light["CoronaSize"] = float(value)
            case "HotSpot":
                light["InnerConeAngle"] = float(value)
            case "Falloff":
                light["OuterConeAngle"] = float(value)
            case "Flags":
                light["Flags"] = int(value)
            case "CoronaHash":
                light["CoronaHash"] = int(value)
            case "LuminescenceHash":
                light["LuminescenceHash"] = int(value)
            case "TypeFlags":
                light["Flags2"] = value.split() if value is not None else []
            case "Type":
                light["Type"] = value
            case "_f58":
                light["CoronaIntensity"] = float(value)
            case "_f5C":
                light["f5C"] = float(value)
            case "_f60":  # Shadow Fade distance
                light["LightFadeDistance"] = float(value)
            case "BoneID":
                light["BoneID"] = int(value)
            case "_f66":  # Group ID
                light["f66"] = int(value)
        line = reader.readline()

    return light
