import bpy
import os
from bpy.app.handlers import persistent

from .common import (
    get_settings, prepare_output_dir, safe_filename,
    SceneRenderState, apply_output_format,
)
from .render_guide import enable_render_guide, disable_render_guide
from .viewport_render import find_view3d_area, ViewportCaptureState, capture_viewport

IS_BATCH_RENDERING = False

# ═══════════════════════════════════════════════════════════
# 카메라별 해상도 — bpy.types.Camera 에 저장 (기존 Batch Camera Renderer 와 동일한 속성명 유지)
# ═══════════════════════════════════════════════════════════

def update_camera_resolution(self, context):
    if IS_BATCH_RENDERING:
        return

    # Check if the modified camera data belongs to the active object
    obj = context.view_layer.objects.active
    if obj and obj.type == 'CAMERA' and obj.data == self:
        if self.use_custom_res:
            if self.res_x > 0: context.scene.render.resolution_x = self.res_x
            if self.res_y > 0: context.scene.render.resolution_y = self.res_y
            enable_render_guide(context)
        else:
            disable_render_guide(context)

@persistent
def auto_update_resolution_handler(scene, depsgraph=None):
    if IS_BATCH_RENDERING:
        return

    obj = bpy.context.view_layer.objects.active
    if obj and obj.type == 'CAMERA':
        cam_data = obj.data
        if getattr(cam_data, "use_custom_res", False):
            if cam_data.res_x > 0 and cam_data.res_y > 0:
                if (scene.render.resolution_x != cam_data.res_x or scene.render.resolution_y != cam_data.res_y):
                    scene.render.resolution_x = cam_data.res_x
                    scene.render.resolution_y = cam_data.res_y

def register_camera_props():
    bpy.types.Camera.use_custom_res = bpy.props.BoolProperty(
        name="Use Custom Resolution",
        description="Use specific resolution for this camera",
        default=False,
        update=update_camera_resolution
    )
    bpy.types.Camera.res_x = bpy.props.IntProperty(
        name="Resolution X",
        default=1920,
        min=1,
        update=update_camera_resolution
    )
    bpy.types.Camera.res_y = bpy.props.IntProperty(
        name="Resolution Y",
        default=1080,
        min=1,
        update=update_camera_resolution
    )

def unregister_camera_props():
    del bpy.types.Camera.use_custom_res
    del bpy.types.Camera.res_x
    del bpy.types.Camera.res_y


class CameraViewState:
    """Put a 3D viewport into camera view for capturing, then restore it."""

    def __init__(self, area):
        self.space = area.spaces.active

    def __enter__(self):
        rv3d = self.space.region_3d
        self.view_perspective = rv3d.view_perspective
        self.use_local_camera = self.space.use_local_camera
        self.space.use_local_camera = False
        rv3d.view_perspective = 'CAMERA'
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            self.space.region_3d.view_perspective = self.view_perspective
            self.space.use_local_camera = self.use_local_camera
        except Exception:
            pass
        return False


class K_RENDER_OT_get_selected_cameras(bpy.types.Operator):
    bl_idname = "k_render.get_selected_cameras"
    bl_label = "Get Selected Cameras"
    bl_description = "Add selected cameras to the render list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_cameras = [obj.name for obj in context.selected_objects if obj.type == 'CAMERA']

        if not selected_cameras:
            self.report({'WARNING'}, "No cameras selected. Please select camera objects.")
            return {'CANCELLED'}

        get_settings(context).camera_names = ", ".join(selected_cameras)

        self.report({'INFO'}, f"Added {len(selected_cameras)} cameras to list.")
        return {'FINISHED'}


class K_RENDER_OT_batch_render_cameras(bpy.types.Operator):
    bl_idname = "k_render.batch_render_cameras"
    bl_label = "Render Cameras"
    bl_description = "Render every camera in the list to the output folder"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global IS_BATCH_RENDERING
        scene = context.scene
        settings = get_settings(context)

        cameras = []
        for cam_name in settings.get_camera_list():
            cam_obj = bpy.data.objects.get(cam_name)
            if cam_obj and cam_obj.type == 'CAMERA':
                cameras.append(cam_obj)
            else:
                self.report({'WARNING'}, f"Skipping '{cam_name}': Not a valid camera.")
        if not cameras:
            self.report({'WARNING'}, "Camera list is empty.")
            return {'CANCELLED'}

        area = None
        if settings.camera_method == 'VIEWPORT':
            area = find_view3d_area(context)
            if not area:
                self.report({'ERROR'}, "No 3D Viewport found.")
                return {'CANCELLED'}

        out_dir = prepare_output_dir(self, settings)
        if not out_dir:
            return {'CANCELLED'}

        IS_BATCH_RENDERING = True
        rendered = 0
        try:
            with SceneRenderState(scene) as state:
                transparent = apply_output_format(scene, settings)

                def setup_camera(cam_obj):
                    scene.camera = cam_obj
                    cam_data = cam_obj.data
                    if getattr(cam_data, "use_custom_res", False):
                        scene.render.resolution_x = cam_data.res_x
                        scene.render.resolution_y = cam_data.res_y
                    else:
                        # 커스텀 설정이 없으면 원래 씬 해상도 사용
                        scene.render.resolution_x = state.res_x
                        scene.render.resolution_y = state.res_y

                if area:
                    with ViewportCaptureState(context, area, settings, transparent), CameraViewState(area):
                        for i, cam_obj in enumerate(cameras):
                            self.report({'INFO'}, f"Capturing camera [{i+1}/{len(cameras)}]: {cam_obj.name}")
                            setup_camera(cam_obj)
                            try:
                                if capture_viewport(context, area, out_dir, safe_filename(cam_obj.name)):
                                    rendered += 1
                            except Exception as e:
                                self.report({'ERROR'}, f"Error capturing {cam_obj.name}: {e}")
                else:
                    for i, cam_obj in enumerate(cameras):
                        self.report({'INFO'}, f"Rendering camera [{i+1}/{len(cameras)}]: {cam_obj.name}")
                        setup_camera(cam_obj)
                        scene.render.filepath = os.path.join(out_dir, safe_filename(cam_obj.name))
                        try:
                            bpy.ops.render.render(write_still=True)
                            rendered += 1
                        except Exception as e:
                            self.report({'ERROR'}, f"Error rendering {cam_obj.name}: {e}")
        finally:
            IS_BATCH_RENDERING = False

        self.report({'INFO'}, f"Batch rendering complete: {rendered}/{len(cameras)} → {out_dir}")
        return {'FINISHED'}


classes = (
    K_RENDER_OT_get_selected_cameras,
    K_RENDER_OT_batch_render_cameras,
)

def register():
    register_camera_props()
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.depsgraph_update_post.append(auto_update_resolution_handler)

def unregister():
    if auto_update_resolution_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(auto_update_resolution_handler)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    unregister_camera_props()
