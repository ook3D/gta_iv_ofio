from typing import Optional

import bpy


def create_empty_obj(name: str) -> bpy.types.Object:
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_size = 0
    bpy.context.collection.objects.link(empty)

    return empty


def parent_objs(children: list, parent):
    for child in children:
        child.parent = parent


def try_unregister_class(target_class):
    try:
        bpy.utils.unregister_class(target_class)
    except RuntimeError:
        pass


def calculate_spot_blend(inner_cone_angle, outer_cone_angle):
    """inner_cone_angle and outer_cone_angle should be of same type (degrees or radians)"""
    if outer_cone_angle == 0:
        return 1
    spot_blend = 1 - (inner_cone_angle / outer_cone_angle)
    return max(0, min(spot_blend, 1))  # Clamp the result between 0 and 1


def find_bone_by_name_return_id(bone_name, bones) -> int:
    for bone in bones:
        if bone.name == bone_name:
            return bone.attr.id
    return -1


def apply_child_of_constraint(child, parent_obj, subtarget, flags):
    child_of_constraint = child.constraints.new(type="CHILD_OF")
    child_of_constraint.target = parent_obj
    child_of_constraint.subtarget = subtarget
    child_of_constraint.use_rotation_x = False if "LockRotX" in flags else True
    child_of_constraint.use_rotation_y = False if "LockRotY" in flags else True
    child_of_constraint.use_rotation_z = False if "LockRotZ" in flags else True
    child_of_constraint.use_location_x = False if "LockTransX" in flags else True
    child_of_constraint.use_location_y = False if "LockTransY" in flags else True
    child_of_constraint.use_location_z = False if "LockTransZ" in flags else True
    bpy.context.view_layer.objects.active = child
    bpy.ops.constraint.childof_clear_inverse(constraint="Child Of", owner="OBJECT")


def apply_copy_transforms(child, parent_obj, subtarget):
    copy_transforms_constraints = child.constraints.new(type="COPY_TRANSFORMS")
    copy_transforms_constraints.target = parent_obj
    copy_transforms_constraints.subtarget = subtarget


def find_bone_by_id(bone_id: int, bones: dict) -> Optional[str]:
    for bone in bones:
        if bones[bone]["Id"] == bone_id:
            return bone
    return None


def find_bone_by_index(bone_index: int, bones: dict) -> tuple[Optional[str], Optional[list[str]]]:
    for bone in bones:
        if bones[bone]["Index"] == bone_index:
            return bone
    return None, []


def find_bone_by_name(bone_name: str, bones: dict) -> tuple[Optional[int], Optional[list[str]]]:
    for bone in bones:
        if bone == bone_name:
            return bones[bone]["Id"], bones[bone]["Flags"]
    return None, []
