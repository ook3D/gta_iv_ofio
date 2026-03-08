def gta_iv_dict_to_odr(data: dict) -> str:
    version = data["Version"]

    if version != "110 12":
        raise Exception("Unsupported ODR")

    output = "Version 110 12\n"

    # if data.get('Shaders') is not None:
    #     ...
    # skip it for now

    if data.get("Skeleton") is not None:
        output += "skel\n{\n\tskel " + data["Skeleton"] + "\n}\n"
    if data.get("LodGroup") is not None:
        output += "lodgroup\n{\n"
        output += parse_lodgroup(data["LodGroup"])
    if data.get("Light") is not None:
        output += "light\n{\n\tlight " + data["Light"] + "\n}\n"

    return output


def parse_lodgroup(data: dict) -> str:
    output = ""
    for key in data:
        value = data[key]
        if key in ["High", "Med", "Low", "Vlow"]:
            if value.get("Mesh") is None:
                output += f"\t{key.lower()} none {value['Distance']}\n"
            else:
                output += f"\t{key.lower()} 1 {value['Mesh']} {value['Pointer']} {value['Distance']}\n"
        elif key in ["Center", "AABBMin", "AABBMax"]:
            output += f"\t{key.lower() if key == 'Center' else key} {' '.join(str(elem) for elem in value)}\n"
        elif key == "Radius":
            output += f"\tradius {value}\n"
    output += "}\n"

    return output
