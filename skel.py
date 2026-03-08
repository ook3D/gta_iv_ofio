from pathlib import Path

import bpy
import orjson
from mathutils import Euler, Matrix

from .openformats2json.gta_iv_skel import gta_iv_skel_to_dict


def import_skel(filepath: Path, name=None, skel_json=None) -> list:
    if skel_json is None:
        if filepath.suffix == ".skel" and skel_json:
            skel_json = gta_iv_skel_to_dict(filepath.resolve())
        elif "".join(filepath.suffixes) == ".skel.json":
            skel_json = orjson.loads(filepath.resolve().read_text())
        else:
            raise ValueError

    if skel_json["Version"] != "107 11":
        raise ValueError(f'Expected .skel version: 107 11. Got {skel_json["Version"]}')

    armature_obj = create_armature(filepath.name if name is None else name)
    # ! Edit Mode
    for bone in skel_json["Bones"]:
        create_bone(bone, skel_json["Bones"][bone], armature_obj.data)

    # ! Pose Mode
    bpy.ops.object.mode_set(mode="POSE")
    for bone in skel_json["Bones"]:
        apply_rotation_constrain(bone, skel_json["Bones"][bone])

    # ! Object Mode
    bpy.ops.object.mode_set(mode="OBJECT")
    for bone in skel_json["Bones"]:
        armature_obj.data.bones[bone].attr.id = skel_json["Bones"][bone]["Id"]
        armature_obj.data.bones[bone].attr.index = skel_json["Bones"][bone]["Index"]

    return [armature_obj, skel_json["NumBones"]]


# Create an armature and bones
def create_armature(name: str) -> bpy.types.Object:
    bpy.ops.object.armature_add(enter_editmode=True, align="WORLD", location=(0, 0, 0))

    # Reference to the armature object
    armature_object = bpy.context.object
    armature = bpy.context.object.data
    armature_object.name = name
    armature.name = name.split(".", maxsplit=1)[0]

    armature.show_axes = True

    # remove default bone
    armature.edit_bones.remove(armature.edit_bones[0])

    return armature_object


def create_bone(bone_name: str, bone_data: dict, armature: bpy.types.Armature):
    edit_bones = armature.edit_bones
    edit_bone = edit_bones.new(bone_name)

    if bone_data.get("ParentIndex") is not None:
        edit_bone.parent = edit_bones[bone_data["ParentIndex"]]

    # https://github.com/Sollumz/Sollumz/blob/50efa04fb4b983c90ed31eba27ca4cea04722ff0/ydr/ydrimport.py#L394
    mat_rot = Euler(bone_data["RotationEuler"]).to_matrix().to_4x4()
    mat_loc = Matrix.Translation(bone_data["LocalOffset"])  # ! IDK!
    mat_sca = Matrix.Scale(1, 4, (1, 1, 1))

    edit_bone.head = (0, 0, 0)
    edit_bone.tail = (0, 0.05, 0)
    edit_bone.matrix = mat_loc @ mat_rot @ mat_sca

    if edit_bone.parent is not None:
        edit_bone.matrix = edit_bone.parent.matrix @ edit_bone.matrix


def apply_rotation_constrain(bone: str, bone_data: dict):
    armature_obj = bpy.context.object

    pose_bone = armature_obj.pose.bones[bone]
    pose_bone.constraints.new(type="LIMIT_ROTATION")

    # apply_locks(pose_bone, bone_data['Flags'])

    rot_constrain = pose_bone.constraints["Limit Rotation"]
    rot_constrain.use_limit_x = True
    rot_constrain.min_x = bone_data["RotMin"][0]
    rot_constrain.max_x = bone_data["RotMax"][0]
    rot_constrain.use_limit_y = True
    rot_constrain.min_y = bone_data["RotMin"][1]
    rot_constrain.max_y = bone_data["RotMax"][1]
    rot_constrain.use_limit_z = True
    rot_constrain.min_z = bone_data["RotMin"][2]
    rot_constrain.max_z = bone_data["RotMax"][2]


def apply_locks(pose_bone: bpy.types.PoseBone, flags: list[str]):
    rot_locks = [False, False, False]
    trans_locks = [False, False, False]
    pose_bone.rotation_mode = "XYZ"

    if "LockRotXYZ" in flags:
        rot_locks = [True, True, True]
    else:
        if "LockRotX" in flags:
            rot_locks[0] = True
        if "LockRotY" in flags:
            rot_locks[1] = True
        if "LockRotZ" in flags:
            rot_locks[2] = True

    if "LimitRotXYZ" in flags:
        trans_locks = [True, True, True]
    else:
        if "LimitRotX" in flags:
            trans_locks[0] = True
        if "LimitRotY" in flags:
            trans_locks[1] = True
        if "LimitRotZ" in flags:
            trans_locks[2] = True

    pose_bone.lock_rotation = rot_locks
    pose_bone.lock_location = trans_locks


if __name__ == "__main__":
    import_skel(Path(r"../test/hand_000_r/hand.skel.json"))
