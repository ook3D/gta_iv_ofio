from math import radians
from pathlib import Path
from time import time

import bpy
import orjson
from bpy.props import StringProperty, CollectionProperty
from bpy.types import Operator, PropertyGroup
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector, Matrix

from .blender_utils import create_empty_obj, parent_objs, calculate_spot_blend, try_unregister_class
from .openformats2json.gta_iv_light import gta_iv_light_to_dict


def import_lights_handler(filepath: Path) -> int:
    filename = filepath.name
    file_extension = filepath.suffix

    if file_extension == ".light":
        light_data = gta_iv_light_to_dict(filepath.resolve())
    elif file_extension == ".json":
        with open(filepath, "r") as light_json:
            light_data = orjson.loads(light_json.read())
    # logger.info(f"Importing light.json: {filename} | version: {light_data['Version']}")

    empty = create_empty_obj(filename)
    light_objs = import_lights(filename, light_data)
    lights_empty = create_empty_obj("Lights")
    parent_objs(light_objs, lights_empty)
    parent_objs([lights_empty], empty)

    return len(light_objs)


def import_lights(name: str, data: dict) -> list:
    if data["Version"] != "1 10":
        raise ValueError(f'Expected .light file version: 1 10. Got {data["Version"]}')
    return create_light(name, data["Lights"])


def create_light(light_name: str, data: list[dict]) -> list:
    """
    Creates light objects in Blender.

    Args:
        light_name (str): Base name for the light.
        data (list): List of LightData objects.
    """
    light_objs = []
    for i, light in enumerate(data):
        # logger.debug(f"> Importing light '{light_name}-{i}'")

        light_type = "SPOT" if light["Type"] == "Spot" else "POINT"
        # Create light data block
        light_data = bpy.data.lights.new(name=f"{light_name}.light", type=light_type)
        light_object = bpy.data.objects.new(name=f"{light_name}.light", object_data=light_data)

        # Create new object, pass the light data, link to scene
        bpy.context.collection.objects.link(light_object)
        bpy.context.view_layer.objects.active = light_object

        # TODO: Find that magic num, (ig it's x10, but no texture make it look super bright)
        light_data.energy = light["Intensity"] * 500

        # Change light position and rotation
        light_object.location = light["Position"]

        apply_rotation(light, light_object)

        # Set light color
        light_data.color = [x / 255 for x in light["Color"][:3]]

        if light_type == "SPOT":
            # Set light cutoff distance
            light_data.use_custom_distance = True
            light_data.cutoff_distance = light["Range"]
            light_data.spot_size = radians(light["OuterConeAngle"])  # Convert falloff angle to radians
            light_data.spot_blend = calculate_spot_blend(light["InnerConeAngle"], light["OuterConeAngle"])
            light_data.attributes.inner_cone_angle = radians(light["InnerConeAngle"])
        else:
            light_data.shadow_soft_size = light["Range"]

        # Assign custom properties
        light_data.attributes.vol_softness = light["VolumeSoftness"]
        light_data.attributes.vol_intensity = light["VolumeIntensity"]
        light_data.attributes.vol_size = light["VolumeSize"]
        light_data.flags.flag = str(light["Flags"])
        if light["Flags2"]:
            light_data.flags.misc_flags = " ".join(light["Flags2"])
        light_data.attributes.range = light["Range"]
        light_data.attributes.intensity = light["Intensity"]
        light_data.attributes.corona_size = light["CoronaSize"]
        light_data.attributes.corona_hash = str(light["CoronaHash"]) if light["CoronaHash"] != 3191162493 else "corona"
        light_data.attributes.luminescence_hash = str(light["LuminescenceHash"])
        light_data.attributes.type = light["Type"]
        light_data.attributes.corona_intensity = light["CoronaIntensity"]
        light_data.attributes.f5C = str(light["f5C"])
        light_data.attributes.light_fade_dist = light["LightFadeDistance"]
        light_data.attributes.bone_id = str(light["BoneID"])
        light_data.attributes.f66 = light["f66"]

        light_objs.append(light_object)
    return light_objs


def apply_rotation(data: dict, light_obj):
    direction_vector = Vector(data["Direction"])
    tangent = Vector(data["Tangent"])

    direction_vector.negate()
    direction_vector.normalize()
    tangent.normalize()

    bitangent = direction_vector.cross(tangent)
    bitangent.normalize()

    rotation_matrix = Matrix((tangent, bitangent, direction_vector)).transposed()

    light_obj.rotation_euler = rotation_matrix.to_euler()


class ImportGTAIVLight(Operator, ImportHelper):
    """Imports .light/.light.json file"""

    bl_idname = "gta4_ofio.import_light"
    bl_label = "Import .light(IV)"

    filename_ext = ".light"

    filter_glob: StringProperty(default="*.light;*.light.json", options={"HIDDEN"})

    files: CollectionProperty(type=PropertyGroup)

    def execute(self, context):
        folder = Path(self.filepath)
        lights = 0
        time_start = time()
        for selection in self.files:
            fp = Path(folder.parent, selection.name)
            lights += import_lights_handler(fp)
        time_spent = time() - time_start
        self.report({"INFO"}, f"Imported {lights} light(s) in {time_spent:.4f}sec")
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


def register():
    try_unregister_class(ImportGTAIVLight)
    bpy.utils.register_class(ImportGTAIVLight)


def unregister():
    bpy.utils.unregister_class(ImportGTAIVLight)
