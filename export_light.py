from math import degrees
from pathlib import Path
from typing import Iterable

import orjson
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator
from bpy.utils import register_class, unregister_class
from bpy_extras.io_utils import ExportHelper

from .blender_utils import try_unregister_class
from .blender_utils import find_bone_by_name_return_id
from .include.jenkins import ooat_unsigned
from .openformats2json.to_openFormats.gta_iv_light import gta_iv_dict_to_light


def export_lights(light_obj):
    data = dict()
    attr = light_obj.data.attributes

    data["Position"] = light_obj.location.to_tuple(8)
    data["Direction"], data["Tangent"] = calc_direction_n_tangent(light_obj.rotation_euler)
    data["Color"] = [int(x * 255) for x in light_obj.data.color] + [0]  # Alpha
    data["Type"] = "Omni" if light_obj.data.type == "POINT" else "Spot"
    data["Range"] = round(attr.range, 4)
    data["Intensity"] = round(attr.intensity, 4)
    data["Flags"] = light_obj.data.flags.flag
    data["Flags2"] = light_obj.data.flags.misc_flags if light_obj.data.flags.misc_flags != "None" else ""
    data["InnerConeAngle"] = round(degrees(attr.inner_cone_angle), 4)
    data["OuterConeAngle"] = round(degrees(light_obj.data.spot_size), 4) if light_obj.data.type == "SPOT" else 0.0
    data["VolumeSoftness"] = round(attr.vol_softness, 4)
    data["VolumeIntensity"] = round(attr.vol_intensity, 4)
    data["VolumeSize"] = round(attr.vol_size, 4)
    data["CoronaSize"] = round(attr.corona_size, 4)
    data["CoronaHash"] = attr.corona_hash if attr.corona_hash.isnumeric() else ooat_unsigned(attr.corona_hash)
    data["CoronaIntensity"] = round(attr.corona_intensity, 4)
    data["LuminescenceHash"] = (
        attr.luminescence_hash if attr.luminescence_hash.isnumeric() else ooat_unsigned(attr.luminescence_hash)
    )
    data["f5C"] = float(attr.f5C)
    data["LightFadeDistance"] = attr.light_fade_dist

    if light_obj.constraints.get("Child Of") is not None:
        bone_id = find_bone_by_name_return_id(light_obj.constraints["Child Of"].subtarget, light_obj.parent.data.bones)
        if bone_id == -1:
            bone_id = 0
    else:
        bone_id = int(attr.bone_id)
    data["BoneID"] = bone_id

    data["f66"] = attr.f66
    return data


def calc_direction_n_tangent(rotation_euler) -> tuple[tuple, tuple]:
    # Convert Euler angles to a 3x3 rotation matrix
    rotation_matrix = rotation_euler.to_matrix()

    # Extract direction (Z-axis of the matrix) and tangent (X-axis of the matrix)
    direction = rotation_matrix.col[2]  # The third column is the direction vector
    tangent = rotation_matrix.col[0]  # The first column is the tangent vector
    direction.negate()
    return direction.to_tuple(8), tangent.to_tuple(8)


class EXPORT_OT_IV_Lights(Operator, ExportHelper):
    bl_idname = "iv.export_lights"
    bl_label = "Export .light(IV)"

    filepath = StringProperty()
    filename_ext = ".light"

    filter_glob: StringProperty(default="*.light", options={"HIDDEN"})

    type: EnumProperty(
        name="Export to",
        description="What type of file you want to export to",
        items=[
            ("OP1", ".light", "openFormats for importing into IV using OpenIV"),
            ("OP2", ".light.json", "Json for ez manual editing"),
        ],
        default="OP1",
    )

    def execute(self, context):
        obj = context.object
        data = {"Version": "1 10", "Lights": list()}
        if obj.type == "LIGHT":
            data["Lights"].append(export_lights(obj))
        else:
            for child_obj in obj.children:
                if child_obj.type == "LIGHT":
                    data["Lights"].append(export_lights(child_obj))

        with open(self.filepath, "w") as writer:
            if self.type == "OP1":
                writer.write(gta_iv_dict_to_light(data))
            elif self.type == "OP2":
                print(data)
                writer.write(orjson.dumps(data, option=orjson.OPT_INDENT_2).decode())

        return {"FINISHED"}

    def invoke(self, context, event):
        if context.object.type != "LIGHT":
            if not any_light(context.object.children):
                self.report({"ERROR"}, "Selected object is not a light")
                return {"CANCELLED"}

        filepath = None
        if not self.filepath:
            obj_name = context.object.name.split(".", maxsplit=1)[0]
            if context.object.type != "LIGHT" and "filepath" in context.object:
                filepath = (
                    Path(context.object["filepath"]).parent / context.object.name.split(".", maxsplit=1)[0] / obj_name
                )
            elif context.object.type == "LIGHT" and "filepath" in context.object:
                filepath = Path(context.object["filepath"]).parent / obj_name / obj_name

            if filepath is not None:
                self.filepath = str(filepath) + self.filename_ext

        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


def register():
    try_unregister_class(EXPORT_OT_IV_Lights)
    register_class(EXPORT_OT_IV_Lights)


def unregister():
    unregister_class(EXPORT_OT_IV_Lights)


def any_light(__iterator: Iterable) -> bool:
    for x in __iterator:
        if x.type == "LIGHT":
            return True
    return False
