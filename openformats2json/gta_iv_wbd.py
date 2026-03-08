from typing import TextIO

from ..utils import jump_to, to_bool, to_float, to_int


def gta_iv_obd_to_dict(filepath) -> dict:
    with open(filepath, "r") as reader:
        line = jump_to("Version", reader)
        if line == "":
            raise ValueError
        elif line.strip().split(maxsplit=1)[1] != "32 11":
            raise ValueError("Incorrect Version")

        data = {"Version": "32 11", "Bounds": read_obd_file(reader)}

    return data


def read_obd_file(reader) -> dict:
    line = reader.readline()

    bounds = {}

    while "}" not in line and line != "":
        if "phBound" in line:
            bound_name = line.strip().split()[1]
            reader.readline()
            bounds[bound_name] = parse_bound_data(reader)
        line = reader.readline()
    return bounds


def parse_bound_data(reader: TextIO) -> dict:
    bound_data = {}

    line = reader.readline()
    while "}" not in line:
        if line == "":
            break
        key, value = (line.strip().split(maxsplit=1) + [None])[:2]

        match key:
            case "Type":
                bound_data["Type"] = value
            case "CentroidPresent":
                bound_data["CentroidPresent"] = to_bool(value)
            case "CGPresent":
                bound_data["CGPresent"] = to_bool(value)
            case "Radius":
                bound_data["Radius"] = float(value)
            case "WorldRadius":
                bound_data["WorldRadius"] = float(value)
            case "AABBMax":
                bound_data["AABBMax"] = to_float(value.split())
            case "AABBMin":
                bound_data["AABBMin"] = to_float(value.split())
            case "Centroid":
                bound_data["Centroid"] = to_float(value.split())
            case "CenterOfMass":
                bound_data["CenterOfMass"] = to_float(value.split())
            case "Margin":
                bound_data["Margin"] = to_float(value.split())
            case "Shrunk":
                bound_data["Shrunk"] = parse_vertices(reader)
            case "Polygons":
                bound_data["Polygons"] = parse_polygons(reader)
            case "VertexScale":
                bound_data["VertexScale"] = to_float(value.split())
            case "VertexOffset":
                bound_data["VertexOffset"] = to_float(value.split())
            case "Vertices":
                bound_data["Vertices"] = parse_vertices(reader)
            case "Materials":
                bound_data["Materials"] = parse_vertices(reader)  # same structure
            case "CurvedEdges":
                bound_data["CurvedEdges"] = parse_curved_edges(reader)  # same structure
            case "Children":
                bound_data["Children"] = list(read_obd_file(reader).values())
            case "ChildTransforms":
                bound_data["ChildTransforms"] = parse_matrix(reader)

        line = reader.readline()

    return bound_data


def parse_polygons(reader: TextIO) -> list[dict]:
    polygons = []

    line = reader.readline()
    while "}" not in line:
        if "Polygon" not in line:
            line = reader.readline()
            continue
        poly = {}
        while "}" not in line:
            key, value = (line.strip().split(maxsplit=1) + [None])[:2]

            match key:
                case "Material":
                    poly["Material"] = int(value)  # material index, defined in Materials
                case "Vertices":
                    poly["Vertices"] = to_int(value.split())
                case "Siblings":
                    poly["Siblings"] = to_int(value.split())
            line = reader.readline()
        polygons.append(poly)
        line = reader.readline()
    return polygons


def parse_vertices(reader: TextIO) -> list[list[float]]:
    vertices = []
    reader.readline()
    line = reader.readline()

    while "}" not in line:
        vertices.append(to_int(line.split()))
        line = reader.readline()

    return vertices


def parse_matrix(reader) -> list:
    line = reader.readline()
    matrix = []

    while "}" not in line:
        if "Matrix" in line:
            matrix.append(parse_vertices(reader))

        line = reader.readline()

    return matrix


def parse_curved_edges(reader: TextIO) -> list:
    line = reader.readline()
    edges = []

    while "}" not in line:
        if "edge" in line:
            edge = {}
            while "}" not in line:
                key, value = (line.strip().split(maxsplit=1) + [None])[:2]

                match key:
                    case "unk_V":
                        edge["unk_V"] = to_float(value.split())
                    case "unk_V2":
                        edge["unk_V2"] = to_float(value.split())
                    case "unk_F":
                        edge["unk_F"] = float(value)
                    case "Vertices":
                        edge["Vertices"] = to_int(value.split())
                line = reader.readline()
            edges.append(edge)
        line = reader.readline()
    return edges
