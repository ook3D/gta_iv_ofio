from typing import TextIO

from .gta_iv_wdr import parse_drawable_data
from ..utils import jump_to, to_bool, to_float


def gta_iv_oft_to_dict(filepath) -> dict:
    with open(filepath, "r") as reader:
        line = jump_to("Version", reader)
        if line == "":
            raise ValueError("Version Header not found")
        elif line.strip().split(maxsplit=1)[1] != "112 2":
            raise ValueError("Incorrect Version")

        data = {"Version": "112 2"}

        line = reader.readline()

        while line.strip() != "":
            key = line.strip().split()[0]
            match key:
                case "fragments":
                    data["Fragments"] = parse_fragments_data(reader)
                case "drawable":
                    data["Drawable"] = parse_drawable_data(reader)
                case "f8":
                    data["f8"] = parse_f8_data(reader)
                case "light":
                    line = jump_to("light", reader)
                    data["Light"] = line.split()[1]
            line = reader.readline()

        return data


def parse_fragments_data(reader: TextIO) -> dict:
    gta_iv_fragment = {}
    groups = {}

    line = reader.readline()

    while "}" not in line and line != "":
        key, value = (line.strip().split(maxsplit=1) + [None])[:2]

        match key:
            case "unbrokenCGOffset":
                gta_iv_fragment["unbrokenCGOffset"] = to_float(value.split())
            case "dampingLinearC":
                gta_iv_fragment["dampingLinearC"] = to_float(value.split())
            case "dampingLinearV":
                gta_iv_fragment["dampingLinearV"] = to_float(value.split())
            case "dampingLinearV2":
                gta_iv_fragment["dampingLinearV2"] = to_float(value.split())
            case "dampingAngularC":
                gta_iv_fragment["dampingAngularC"] = to_float(value.split())
            case "dampingAngularV":
                gta_iv_fragment["dampingAngularV"] = to_float(value.split())
            case "dampingAngularV2":
                gta_iv_fragment["dampingAngularV2"] = to_float(value.split())
            case "estimatedCacheSize":
                gta_iv_fragment["estimatedCacheSize"] = int(value)
            case "estimatedArticulatedCacheSize":
                gta_iv_fragment["estimatedArticulatedCacheSize"] = int(value)
            case "becomeRope":
                gta_iv_fragment["becomeRope"] = to_bool(value)
            case "artAssetID":
                gta_iv_fragment["artAssetID"] = int(value)
            case "attachBottomEnd":
                gta_iv_fragment["attachBottomEnd"] = int(value)
            case "minMoveForce":
                gta_iv_fragment["minMoveForce"] = float(value)
            case "CenterOfMass":
                gta_iv_fragment["CenterOfMass"] = to_float(value.split())
            case "gravityFactor":
                gta_iv_fragment["gravityFactor"] = float(value)
            case "buoyancyFactor":
                gta_iv_fragment["buoyancyFactor"] = float(value)
            case "group":
                groups[value] = parse_group_data(reader)
            case "flags":
                gta_iv_fragment["flags"] = value

        line = reader.readline()

    gta_iv_fragment["Groups"] = groups
    return gta_iv_fragment


def parse_group_data(reader: TextIO) -> dict:
    group_data = {}

    line = reader.readline()

    children = []
    groups = {}
    while "}" not in line and line != "":
        key, value = (line.strip().split(maxsplit=1) + [None])[:2]

        match key:
            case "strength":
                group_data["strength"] = float(value)
            case "forceTransmissionScaleUp":
                group_data["forceTransmissionScaleUp"] = float(value)
            case "forceTransmissionScaleDown":
                group_data["forceTransmissionScaleDown"] = float(value)
            case "jointStiffness":
                group_data["jointStiffness"] = float(value)
            case "minSoftAngle1":
                group_data["minSoftAngle1"] = float(value)
            case "maxSoftAngle1":
                group_data["maxSoftAngle1"] = float(value)
            case "minSoftAngle2":
                group_data["minSoftAngle2"] = float(value)
            case "maxSoftAngle2":
                group_data["maxSoftAngle2"] = float(value)
            case "minSoftAngle3":
                group_data["mixSoftAngle3"] = float(value)
            case "maxSoftAngle3":
                group_data["maxSoftAngle3"] = float(value)
            case "rotationSpeed":
                group_data["rotationSpeed"] = float(value)
            case "rotationStrength":
                group_data["rotationStrength"] = float(value)
            case "restoringStrength":
                group_data["restoringStrength"] = float(value)
            case "restoringMaxTorque":
                group_data["restoringMaxTorque"] = float(value)
            case "latchStrength":
                group_data["latchStrength"] = float(value)
            case "disappearsWhenDead":
                group_data["disappearsWhenDead"] = to_bool(value)
            case "minDamageForce":
                group_data["minDamageForce"] = float(value)
            case "damageHealth":
                group_data["damageHealth"] = float(value)
            case "child":
                child_data = {"Path": value.split()[0]}
                children.append(parse_child_data(child_data, reader))
            case "group":
                groups[value] = parse_group_data(reader)

        line = reader.readline()

    group_data["Children"] = children
    group_data["Groups"] = groups
    return group_data


def parse_child_data(child_data: dict, reader: TextIO) -> dict:
    line = reader.readline()

    while "}" not in line and line != "":
        key = line.strip().split()[0]

        match key:
            case "pristineMass":
                child_data["pristineMass"] = float(line.split()[1])
            case "damagedMass":
                child_data["damagedMass"] = float(line.split()[1])
            case "f50":
                reader.readline()
                line = reader.readline()
                f50 = []
                while "}" not in line:
                    f50.append(to_float(line.strip().split()))
                    line = reader.readline()
                child_data["f50"] = f50

        line = reader.readline()

    return child_data


def parse_f8_data(reader: TextIO) -> list[list[float]]:
    f8_data = []
    line = reader.readline()

    while "}" not in line:
        jump_to("{", reader)
        line = reader.readline()

        f8 = []
        while "}" not in line:
            f8.append(to_float(line.split()))
            line = reader.readline()
        f8_data.append(f8)

        line = reader.readline()

    return f8_data
