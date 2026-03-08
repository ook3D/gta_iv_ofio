import bpy


def import_skinned_mesh(mesh_obj, armature, data: dict) -> None:
    mesh_obj.modifiers.new(name="Armature", type="ARMATURE")
    mesh_obj.modifiers["Armature"].object = armature

    blend_indices = data["BlendIndices"]
    blend_weights = data["BlendWeight"]

    apply_blend_indices_and_weights(mesh_obj, armature, blend_indices, blend_weights)


def add_weight_to_vertex_group(mesh_obj, vertex_idx, bone_name, weight):
    """Adds a weight to a specific vertex group (bone) for a given vertex."""
    if bone_name not in mesh_obj.vertex_groups:
        mesh_obj.vertex_groups.new(name=bone_name)

    vertex_group = mesh_obj.vertex_groups[bone_name]
    # Add the vertex to the vertex group with the given weight
    vertex_group.add([vertex_idx], weight, "REPLACE")


def get_bone_name(armature_obj, bone_index):
    """Retrieves the bone name from the armature based on the bone index."""
    bone_names = armature_obj.data.bones.keys()

    if bone_index < len(bone_names):
        return bone_names[bone_index]

    return None


def apply_weights_to_vertex(mesh_obj, armature_obj, vertex_idx, indices, weights):
    """Applies weights to a single vertex based on blend indices and weights."""
    for bone_index, weight in zip(indices, weights):
        if weight > 0.0:
            bone_name = get_bone_name(armature_obj, bone_index)
            if bone_name:
                add_weight_to_vertex_group(mesh_obj, vertex_idx, bone_name, weight)


def apply_blend_indices_and_weights(mesh_obj, armature_obj, blend_indices, blend_weights):
    """
    Applies blend indices and weights to a mesh object based on an armature.

    :param mesh_obj: The mesh object to apply the weights to.
    :param armature_obj: The armature object that influences the mesh.
    :param blend_indices: List of blend indices for each vertex, e.g., [[77, 77, 77, 77], ...]
    :param blend_weights: List of blend weights for each vertex, e.g., [[0.0, 0.0, 1.0, 0.0], ...]
    """
    # Switch to object mode for adding weights to vertex groups
    bpy.context.view_layer.objects.active = mesh_obj

    # Iterate through vertices and apply weights
    for vertex_idx, (indices, weights) in enumerate(zip(blend_indices, blend_weights)):
        apply_weights_to_vertex(mesh_obj, armature_obj, vertex_idx, indices, weights)
