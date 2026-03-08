def gta_iv_dict_to_light(data: dict) -> str:
    version = data["Version"]

    if version != "1 10":
        raise ValueError("Unsupported Light")

    output = "Version 1 10\n" + "{\n"
    output += parse_lights(data["Lights"])
    output += "}\n"
    return output


def parse_lights(attributes: list[dict]) -> str:
    output = str()
    for index, attribute in enumerate(attributes):
        output += f"\tAttribute {index}\n" + "\t{\n"
        output += parse_attributes(attribute)
        output += "\t}\n"
    return output


def parse_attributes(data: dict) -> str:
    output = str()
    output += "\t\tPosition " + " ".join(f"{x:.8f}" for x in data["Position"]) + "\n"
    output += "\t\tDirection " + " ".join(f"{x:.8f}" for x in data["Direction"]) + "\n"
    output += "\t\tOrigin " + " ".join(f"{x:.8f}" for x in data["Tangent"]) + "\n"
    output += "\t\tColor " + " ".join(map(str, data["Color"])) + "\n"
    output += f"\t\t_f28 {data['VolumeSoftness']}\n"
    output += f"\t\t_f2C {data['VolumeIntensity']}\n"
    output += f"\t\t_f30 {data['VolumeSize']}\n"
    output += f"\t\tDistance {data['Range']}\n"
    output += f"\t\tRange {data['Intensity']}\n"
    output += f"\t\tCoronaSize {data['CoronaSize']}\n"
    output += f"\t\tHotSpot {data['InnerConeAngle']}\n"
    output += f"\t\tFalloff {data['OuterConeAngle']}\n"
    output += f"\t\tFlags {data['Flags']}\n"
    output += f"\t\tCoronaHash {data['CoronaHash']}\n"
    output += f"\t\tLuminescenceHash {data['LuminescenceHash']}\n"
    output += f"\t\tTypeFlags {data['Flags2']}\n"
    output += f"\t\tType {data['Type']}\n"
    output += f"\t\t_f58 {data['CoronaIntensity']}\n"
    output += f"\t\t_f5C {data['f5C']}\n"
    output += f"\t\t_f60 {data['LightFadeDistance']}\n"
    output += f"\t\tBoneID {data['BoneID']}\n"
    output += f"\t\t_f66 {data['f66']}\n"
    return output
