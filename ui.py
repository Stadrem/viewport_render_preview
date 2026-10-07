import bpy

from .common import get_settings
from .render_guide import is_render_guide_enabled


class K_RENDER_PT_main(bpy.types.Panel):
    bl_label = "Render"
    bl_idname = "K_RENDER_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'K-Quick Tools'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.label(text="", icon='RENDER_STILL')

    def draw(self, context):
        layout = self.layout
        settings = get_settings(context)

        # 1. Viewport Guide Toggle
        is_on = is_render_guide_enabled(context.scene)
        icon = 'HIDE_OFF' if is_on else 'HIDE_ON'
        text = "Hide Render Guide" if is_on else "Show Render Guide"
        layout.operator("k_render.toggle_render_guide", text=text, icon=icon)

        # 2. Output (shared by viewport capture and camera batch)
        box = layout.box()
        box.label(text="Output", icon='OUTPUT')
        row = box.row(align=True)
        row.prop(settings, "output_dir")
        row.operator("k_render.open_folder", text="", icon='FOLDER_REDIRECT')
        box.row().prop(settings, "file_format", expand=True)
        if settings.file_format == 'PNG':
            box.prop(settings, "use_transparent")

        # 3. Viewport capture options (viewport capture + camera batch in Viewport mode)
        box = layout.box()
        box.label(text="Viewport Capture", icon='RESTRICT_VIEW_OFF')
        box.prop(settings, "hide_overlays")
        if not settings.is_transparent:
            box.prop(settings, "bg_color")


class K_RENDER_PT_viewport(bpy.types.Panel):
    bl_label = "Viewport"
    bl_idname = "K_RENDER_PT_viewport"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'K-Quick Tools'
    bl_parent_id = "K_RENDER_PT_main"

    def draw_header(self, context):
        self.layout.label(text="", icon='RESTRICT_VIEW_OFF')

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        layout.label(text=f"Name: {obj.name if obj else 'Viewport_Preview'}_<time>", icon='FILE_IMAGE')

        col = layout.column(align=True)
        col.scale_y = 1.5
        col.operator("k_render.viewport_capture", text="Capture Viewport", icon='RENDER_STILL')


class K_RENDER_PT_cameras(bpy.types.Panel):
    bl_label = "Cameras"
    bl_idname = "K_RENDER_PT_cameras"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'K-Quick Tools'
    bl_parent_id = "K_RENDER_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.label(text="", icon='OUTLINER_OB_CAMERA')

    def draw(self, context):
        layout = self.layout
        settings = get_settings(context)

        # Camera List
        box = layout.box()
        box.label(text="Cameras List", icon='OUTLINER_OB_CAMERA')
        box.operator("k_render.get_selected_cameras", icon='ADD', text="Get Selected Cameras")
        box.prop(settings, "camera_names", text="")

        # Active camera resolution
        active_obj = context.active_object
        if active_obj and active_obj.type == 'CAMERA':
            cam_data = active_obj.data

            box_res = layout.box()
            box_res.label(text=f"Active Cam: {active_obj.name}", icon='CAMERA_DATA')
            box_res.prop(cam_data, "use_custom_res")

            col_res = box_res.column(align=True)
            col_res.enabled = cam_data.use_custom_res
            col_res.prop(cam_data, "res_x")
            col_res.prop(cam_data, "res_y")

        layout.row().prop(settings, "camera_method", expand=True)

        col = layout.column(align=True)
        col.scale_y = 1.5
        col.operator("k_render.batch_render_cameras", icon='RENDER_STILL', text="Render Cameras")


classes = (
    K_RENDER_PT_main,
    K_RENDER_PT_viewport,
    K_RENDER_PT_cameras,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
