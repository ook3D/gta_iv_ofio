from bpy.types import Panel
from bpy.utils import register_class, unregister_class

from .blender_utils import try_unregister_class


class GTAIV_PT_material(Panel):
    bl_label = "GTA IV Material"
    bl_idname = "GTAIV_PT_material"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == "MESH"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(context.object.data.mtl, "index")


class GTAIV_PT_shader(Panel):
    bl_label = "Shader"
    bl_idname = "GTAIV_PT_shader"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_parent_id = GTAIV_PT_material.bl_idname

    @classmethod
    def poll(cls, context):
        return context.material is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(context.material.shader, "type")


class GTAIV_PT_light_attributes(Panel):
    bl_label = "GTA IV Light Attributes"
    bl_idname = "GTAIV_PT_light_attributes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.light is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        light = context.light
        attributes = light.attributes

        if context.object.constraints.find("Child Of") != -1:
            child_of_constraint = context.object.constraints["Child Of"]
        else:
            child_of_constraint = None

        layout.prop(attributes, "range")
        layout.prop(attributes, "intensity")
        if light.type == "SPOT":
            layout.prop(attributes, "inner_cone_angle", slider=True)
            layout.prop(light, "spot_size", text="OuterConeAngle", slider=True)
        layout.prop(attributes, "vol_size", slider=True)
        layout.prop(attributes, "vol_intensity", slider=True)
        layout.prop(attributes, "vol_softness")
        layout.prop(attributes, "light_fade_dist")
        layout.prop(attributes, "corona_hash")
        layout.prop(attributes, "corona_size", slider=True)
        layout.prop(attributes, "corona_intensity", slider=True)
        layout.prop(attributes, "luminescence_hash")
        layout.prop(attributes, "f5C")
        if child_of_constraint is not None:
            layout.prop_search(
                child_of_constraint,
                "subtarget",
                child_of_constraint.target.data,
                "bones",
                text="Bone",
            )
        else:
            layout.prop(attributes, "bone_id")
        layout.prop(attributes, "f66")


class GTAIV_PT_light_flags(Panel):
    bl_label = "GTA IV Light Flags"
    bl_idname = "GTAIV_PT_light_flags"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.light is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        light = context.light
        flags = light.flags

        layout.prop(flags, "flag")
        layout.prop(flags, "time_flag")

        row = layout.row(align=True)
        row.prop(flags, "weak_light")
        row.prop(flags, "static_shadows")

        row = layout.row(align=True)
        row.prop(flags, "dynamic_shadows")
        row.prop(flags, "use_sun_color")

        row = layout.row(align=True)
        row.prop(flags, "buzzing")
        row.prop(flags, "volumetric_lights")

        layout.prop(flags, "no_corona_reflection")

        layout.separator()

        layout.prop(flags, "flashiness_flags")
        layout.prop(flags, "misc_flags")

        layout.separator()

        layout.label(text="Unknown Flags")
        row = layout.row(align=True)
        row.prop(flags, "unk18")
        row.prop(flags, "unk22")

        row = layout.row(align=True)
        row.prop(flags, "unk23")
        row.prop(flags, "unk24")


_classes = [
    GTAIV_PT_material,
    GTAIV_PT_shader,
    GTAIV_PT_light_attributes,
    GTAIV_PT_light_flags,
]


def register():
    for cls in _classes:
        try_unregister_class(cls)
        register_class(cls)


def unregister():
    for cls in reversed(_classes):
        unregister_class(cls)
