import bpy
from bpy.types import Panel


class GTAIV_PT_TOOL_PANEL(Panel):
    bl_label = "General"
    bl_idname = "GTAIV_PT_TOOL_PANEL"
    bl_category = "GTA IV Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 0

    def draw_header(self, context):
        self.layout.label(text="", icon="MODIFIER_DATA")

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.menu("GTA4_MT_Import_Menu", text="Import", icon="IMPORT")
        row.menu("GTA4_MT_Export_Menu", text="Export", icon="EXPORT")


class GTA4ToolChildPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = GTAIV_PT_TOOL_PANEL.bl_idname
    bl_category = GTAIV_PT_TOOL_PANEL.bl_category


class GTAIV_PT_SELECTED_OBJECT_PANEL(GTA4ToolChildPanel, Panel):
    bl_label = "Selected Object"
    bl_idname = "GTAIV_PT_SELECTED_OBJECT_PANEL"
    bl_options = set()
    bl_order = 0

    def draw_header(self, context):
        self.layout.label(text="", icon="OBJECT_DATA")

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        if obj is None:
            layout.label(text="No object selected")
            return

        if obj.type == "MESH":
            layout.label(text=f"Mesh: {obj.name}", icon="MESH_DATA")
            layout.prop(obj.data.mtl, "index")
            if obj.active_material and hasattr(obj.active_material, "shader"):
                layout.prop(obj.active_material.shader, "type", text="Shader")
        elif obj.type == "LIGHT":
            layout.label(text=f"Light: {obj.name}", icon="LIGHT")
            layout.prop(obj.data.attributes, "range")
            layout.prop(obj.data.attributes, "intensity")
        elif obj.type == "ARMATURE":
            layout.label(text=f"Skeleton: {obj.name}", icon="ARMATURE_DATA")
            layout.label(text=f"Bones: {len(obj.data.bones)}")
        elif obj.type == "EMPTY":
            layout.label(text=f"Empty: {obj.name}", icon="EMPTY_DATA")
            if "filepath" in obj:
                layout.label(text=f"Source: {obj['filepath']}")
        else:
            layout.label(text=f"{obj.type}: {obj.name}")


def register():
    bpy.utils.register_class(GTAIV_PT_TOOL_PANEL)
    bpy.utils.register_class(GTAIV_PT_SELECTED_OBJECT_PANEL)


def unregister():
    bpy.utils.unregister_class(GTAIV_PT_SELECTED_OBJECT_PANEL)
    bpy.utils.unregister_class(GTAIV_PT_TOOL_PANEL)
