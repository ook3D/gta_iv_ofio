def gta_iv_dict_to_mesh(data: dict) -> str:
    version = data["Version"]

    if version != "11 13":
        raise ValueError("Unsupported Mesh")

    output = "Version 11 13\n" + "{\n"

    if data.get("Skinned") is not None:
        output += f"\tSkinned {int(data['Skinned'])}\n"
    if data.get("Bounds") is not None and version == "11 13":
        output += f"\tBounds {len(data['Bounds'])}\n"
        output += parse_bounds(data["Bounds"])
    if data.get("Geometries") is not None:
        output += parse_meshes(data["Geometries"], is_skinned=data["Skinned"])
    output += "}"

    return output


def parse_bounds(data: list) -> str:
    output = "\t{\n"
    for bound in data:
        output += "\t\t" + " ".join(format(x, ".8g") for x in bound) + "\n"
    output += "\t}\n"
    return output


def parse_meshes(data: list, is_skinned: bool) -> str:
    output = ""
    for mesh in data:
        output += f"\tMtl {mesh['Material']}\n" + "\t{\n" + "\t\tPrim 0\n\t\t{\n"

        idx = mesh["Indices"]
        output += f"\t\t\tIdx {len(idx) * 3}\n" + "\t\t\t{\n"
        for i in range(0, len(idx), 5):
            chunk = idx[i : i + 5]  # Get the next 5 elements or fewer if idx is smaller
            output += "\t\t\t\t" + " ".join(" ".join(str(x) for x in sublist) for sublist in chunk) + "\n"
        output += "\t\t\t}\n"
        output += f"\t\t\tVerts {len(mesh['Vertices'])}\n" + "\t\t\t{\n"
        output += parse_skinned_vertx(mesh) if is_skinned else parse_vertx(mesh)
        output += "\t\t}\n\t}\n"

    return output


def parse_vertx(data: dict) -> str:
    output = ""
    i = 0
    vertices = data["Vertices"]
    vertex_count = len(vertices)

    normals = data["VertxNormals"]
    color = data["VertxColors"]
    tangents = data["Tangents"] or None
    uv0 = data["UVCoords"][0] or None
    uv1 = data["UVCoords"][1] or None
    uv2 = data["UVCoords"][2] or None
    uv3 = data["UVCoords"][3] or None
    uv4 = data["UVCoords"][4] or None
    uv5 = data["UVCoords"][5] or None

    empty_tangent = "0.0 0.0 0.0 0.0"
    empty_uv = "0.0 0.0"

    while i < vertex_count:
        vcolor = color[i]
        vcolor[0], vcolor[2] = vcolor[2], vcolor[0]
        output += (
            "\t\t\t\t"
            + " ".join(format(x, ".8g") for x in vertices[i])
            + " / "
            + " ".join(format(x, ".8g") for x in normals[i])
            + " / "
            + " ".join(str(x) for x in vcolor)
            + " / "
            + (" ".join(format(x, ".8g") for x in tangents[i]) if tangents is not None else empty_tangent)
            + " / "
            + (" ".join(format(x, ".8g") for x in uv0[i]) if uv0 is not None else empty_uv)
            + " / "
            + (" ".join(format(x, ".8g") for x in uv1[i])if uv1 is not None else empty_uv)
            + " / "
            + (" ".join(format(x, ".8g") for x in uv2[i])if uv2 is not None else empty_uv)
            + " / "
            + (" ".join(format(x, ".8g") for x in uv3[i])if uv3 is not None else empty_uv)
            + " / "
            + (" ".join(format(x, ".8g") for x in uv4[i])if uv4 is not None else empty_uv)
            + " / "
            + (" ".join(format(x, ".8g") for x in uv5[i])if uv5 is not None else empty_uv)
            + "\n"
        )

        i+=1
    output += "\t\t\t}\n"
    return output


def parse_skinned_vertx(data: dict) -> str:
    output = ""

    i = 0
    vertices = data["Vertices"]
    vertex_count = len(vertices)

    normals = data["VertxNormals"]
    weights = data["BlendWeight"]
    bone_indices = data["BlendIndices"]
    color = data["VertxColors"]
    tangents = data["Tangents"] or None
    uv0 = data["UVCoords"][0] or None
    uv1 = data["UVCoords"][1] or None

    empty_tangent = "0.0 0.0 0.0 0.0"
    empty_uv = "0.0 0.0"

    while i < vertex_count:
        vcolor = color[i]
        vcolor[0], vcolor[2] = vcolor[2], vcolor[0]
        output += (
            "\t\t\t\t"
            + " ".join(format(x, ".8g") for x in vertices[i])
            + " / "
            + " ".join(format(x, ".8g") for x in normals[i])
            + " / "
            + " ".join(format(x, ".8g") for x in weights[i])
            + " / "
            + " ".join(str(x) for x in bone_indices[i])
            + " / "
            + " ".join(str(x) for x in vcolor)
            + " / "
            + (" ".join(format(x, ".8g") for x in tangents[i]) if tangents is not None else empty_tangent)
            + " / "
            + (" ".join(format(x, ".8g") for x in uv0[i]) if uv0 is not None else empty_uv)
            + " / "
            + (" ".join(format(x, ".8g") for x in uv1[i])if uv1 is not None else empty_uv)
            + "\n"
        )
        i+=1
    output += "\t\t\t}\n"
    return output
