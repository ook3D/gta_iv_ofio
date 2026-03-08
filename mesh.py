from pathlib import Path
from time import time

import bpy
import orjson
from bpy.props import StringProperty, CollectionProperty
from bpy.types import Operator, PropertyGroup
from bpy_extras.io_utils import ImportHelper

from .blender_utils import create_empty_obj, parent_objs, try_unregister_class
from .openformats2json.gta_iv_mesh import gta_iv_mesh_to_dict
from .skinned_mesh import import_skinned_mesh


def import_mesh_handler(self, filepath: Path) -> int:
    filename = filepath.name
    file_extension = filepath.suffix

    if file_extension == ".mesh":
        mesh_data = gta_iv_mesh_to_dict(filepath.resolve())
    elif file_extension == ".json":
        with open(filepath, "r") as mesh_json:
            mesh_data = orjson.loads(mesh_json.read())
    # logger.info(f"Importing Mesh.json: {filename} | version: {mesh_data['Version']}")
    with open(filepath.with_suffix(".json"), "wb") as f:
        f.write(orjson.dumps(mesh_data))
    empty = create_empty_obj(filename)
    mesh_objs = import_mesh(self, filename, empty, mesh_data, apply_skel=False)
    parent_objs(mesh_objs, empty)

    return len(mesh_objs)


def import_mesh(self, name: str, armature, data: dict, apply_skel=True) -> list:
    if data["Version"] != "11 13":
        raise ValueError(f'Expected .mesh file version: 11 13. Got {data["Version"]}')
    mesh_objs = []
    for mesh_data in data["Geometries"]:
        mesh_objs.append(create_mesh(self, name, armature, mesh_data, data["Skinned"] and apply_skel))
    return mesh_objs


def create_mesh(self, name, armature, geometry_data: dict, is_skinned: bool):
    """Creates a mesh object in Blender."""
    mesh = bpy.data.meshes.new(f"{name}")
    obj = bpy.data.objects.new(f"{name}", mesh)

    bpy.context.collection.objects.link(obj)

    faces, verts, normals, colors, uv_coords = (
        geometry_data["Indices"],
        geometry_data["Vertices"],
        geometry_data["VertxNormals"],
        geometry_data["VertxColors"],
        geometry_data["UVCoords"],
    )

    mesh.from_pydata(verts, [], faces, shade_flat=False)

    bpy.context.view_layer.objects.active = obj

    mesh.mtl.index = geometry_data["Material"]

    # Add a new vertex color layer
    if not mesh.color_attributes:
        mesh.color_attributes.new("Color", "FLOAT_COLOR", "POINT")

    color_layer = mesh.color_attributes.active.data

    for vert_index, vertex in enumerate(mesh.vertices):
        color_layer[vert_index].color = [x / 255.0 for x in colors[vert_index]]  # Assign RGBA color

    for i, uv_coord in enumerate(uv_coords):
        create_uv_map(mesh, f"UVMap_{i}", uv_coord)

    if is_skinned:
        import_skinned_mesh(obj, armature, geometry_data)

    mesh.normals_split_custom_set_from_vertices(normals)

    if mesh.validate(verbose=True):
        self.report({"WARNING"}, "Invalid geometry corrected/removed, check console.")
    mesh.update()

    return obj


def create_uv_map(mesh, name, uv_coord):
    uv_layer = mesh.uv_layers.new(name=name).uv

    for loop in mesh.loops:
        u, v = uv_coord[loop.vertex_index]
        uv_layer[loop.index].vector = u, 1 - v  # flip y axis


class ImportGTAIVMesh(Operator, ImportHelper):
    """Imports meshes and lights referenced in the .odr file"""

    bl_idname = "gta4_ofio.import_mesh"
    bl_label = "Import .mesh(IV)"

    filename_ext = ".mesh"

    filter_glob: StringProperty(default="*.mesh;*.mesh.json", options={"HIDDEN"})

    files: CollectionProperty(type=PropertyGroup)

    def execute(self, context):
        folder = Path(self.filepath)
        meshes = 0
        time_start = time()
        for selection in self.files:
            fp = Path(folder.parent, selection.name)
            meshes += import_mesh_handler(self, fp)
        time_spent = time() - time_start
        self.report({"INFO"}, f"Imported {meshes} mesh(es) in {time_spent:.4f}sec")
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


def register():
    try_unregister_class(ImportGTAIVMesh)
    bpy.utils.register_class(ImportGTAIVMesh)


def unregister():
    bpy.utils.unregister_class(ImportGTAIVMesh)
