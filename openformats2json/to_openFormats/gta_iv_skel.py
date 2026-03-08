def gta_iv_dict_to_skel(data: dict) -> str:
    version = data["Version"]

    if version != "107 11":
        raise Exception("Unsupported Skel")

    output = "Version 107 11\n" + f"NumBones {data['NumBones']}\n" + f"Flags {' '.join(data['Flags'])}\n"
    output += parse_bones(data["Bones"])

    return output


class IndexCounter:

    def __init__(self):
        self.index = 0

    def increment(self):
        self.index += 1


def parse_bones(bones: dict, indent=0, index_counter=IndexCounter()) -> str:
    output = ""
    for bone, value in bones.items():
        output += "\t" * indent + f"bone {bone}\n" + "\t" * indent + "{\n"
        indent += 1
        output += "\t" * indent + f"Flags {' '.join(value['Flags'])}\n"
        output += "\t" * indent + f"Index {value['Index'] if value.get('Index') is not None else index_counter.index}\n"
        output += "\t" * indent + f"Id {value['Id']}\n"
        output += "\t" * indent + f"Mirror {value['Mirror']}\n"
        index_counter.increment()
        output += "\t" * indent + f"LocalOffset {' '.join(f'{x:.8f}' for x in value['LocalOffset'])}\n"
        output += "\t" * indent + f"RotationEuler {' '.join(f'{x:.8f}' for x in value['RotationEuler'])}\n"
        output += "\t" * indent + f"RotationQuaternion {' '.join(f'{x:.8f}' for x in value['RotationQuaternion'])}\n"
        output += "\t" * indent + f"Scale {' '.join(f'{x:.8f}' for x in value['Scale'])}\n"
        output += "\t" * indent + f"WorldOffset {' '.join(f'{x:.8f}' for x in value['WorldOffset'])}\n"
        output += "\t" * indent + f"Orient {' '.join(f'{x:.8f}' for x in value['Orient'])}\n"
        output += "\t" * indent + f"Sorient {' '.join(f'{x:.8f}' for x in value['Sorient'])}\n"
        output += "\t" * indent + f"TransMin {' '.join(f'{x:.8f}' for x in value['TransMin'])}\n"
        output += "\t" * indent + f"TransMax {' '.join(f'{x:.8f}' for x in value['TransMax'])}\n"
        output += "\t" * indent + f"RotMin {' '.join(f'{x:.8f}' for x in value['RotMin'])}\n"
        output += "\t" * indent + f"RotMax {' '.join(f'{x:.8f}' for x in value['RotMax'])}\n"
        if value.get("Children") is not None:
            output += "\t" * indent + f"Children {len(value['Children'])}\n" + "\t" * indent + "{\n"
            indent += 1
            output += parse_bones(value["Children"], indent=indent, index_counter=index_counter)
            indent -= 1
            output += "\t" * indent + "}\n"
        indent -= 1
        output += "\t" * indent + "}\n"
    return output
