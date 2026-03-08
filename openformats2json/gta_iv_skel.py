from typing import TextIO, Optional

from ..utils import jump_to, to_float


def gta_iv_skel_to_dict(filepath):
    with open(filepath, "r") as reader:
        line = jump_to("Version", reader)
        if line == "":
            raise ValueError(f"Version header not found! File: {filepath}")
        elif line.strip().split(maxsplit=1)[1] != "107 11":
            raise ValueError(f"Version mismatch. File: {filepath}")
        # print(f"Got GTA IV Skeleton at {filepath}")

        line = jump_to("NumBones", reader)
        numbones = int(line.split()[1])
        line = jump_to("Flags", reader)
        flags = line.strip().split()[1:]

        data = {
            "Version": "107 11",
            "NumBones": numbones,
            "Flags": flags,
            "Bones": read_skel_file(reader),
        }

        return data


def read_skel_file(reader, parent_index: Optional[int] = None) -> dict:
    line = jump_to("bone", reader).strip()

    bones = {}

    while "}" not in line and line != "":
        if line.split()[0] == "bone":
            bone_name = line.split()[1]
            bones[bone_name] = {}  # reserve a spot for the bone
            bones[bone_name] = read_bone_data(bones, reader, parent_index)

        line = reader.readline().strip()
    return bones


def read_bone_data(bones: dict, reader: TextIO, parent_index: Optional[int] = None) -> dict:
    line = reader.readline().strip()
    bone = {}
    while "}" not in line:
        key, value = (line.strip().split(maxsplit=1) + [None])[:2]
        match key:
            case "Flags":
                bone["Flags"] = value.split()
            case "Index":
                bone["Index"] = int(value)
                if parent_index is not None:
                    bone["ParentIndex"] = parent_index
            case "Id":
                bone["Id"] = int(value)
            case "Mirror":
                bone["Mirror"] = int(value)
            case "LocalOffset":
                bone["LocalOffset"] = to_float(value.split())
            case "RotationEuler":
                bone["RotationEuler"] = to_float(value.split()[:3])
            case "RotationQuaternion":
                bone["RotationQuaternion"] = to_float(value.split())
            case "WorldOffset":
                bone["WorldOffset"] = to_float(value.split())
            case "Scale":
                bone["Scale"] = to_float(value.split())
            case "Orient":
                bone["Orient"] = to_float(value.split())
            case "Sorient":
                bone["Sorient"] = to_float(value.split())
            case "TransMin":
                bone["TransMin"] = to_float(value.split())
            case "TransMax":
                bone["TransMax"] = to_float(value.split())
            case "RotMin":
                bone["RotMin"] = to_float(value.split()[:3])
            case "RotMax":
                bone["RotMax"] = to_float(value.split()[:3])
            case "Children":
                reader.readline()
                children = read_skel_file(reader, bone["Index"])
                bones.update(children)
        line = reader.readline()

    return bone
