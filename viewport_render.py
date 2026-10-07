import bpy
import os
import glob
import datetime

from .common import (
    get_settings, prepare_output_dir, safe_filename,
    SceneRenderState, apply_output_format,
)
from .render_guide import suspend_render_guides, resume_render_guides

# ═══════════════════════════════════════════════════════════
# Viewport capture — bpy.ops.render.opengl 기반 캡처 헬퍼
# ═══════════════════════════════════════════════════════════

def find_view3d_area(context):
    """Prefer the area the operator was called from, otherwise the first 3D viewport."""
    area = context.area
    if area and area.type == 'VIEW_3D':
        return area
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            return area
    return None

def _window_region(area):
    for region in area.regions:
        if region.type == 'WINDOW':
            return region
    return None


class ViewportCaptureState:
    """Temporarily prepare a 3D viewport for clean captures:
    hide overlays, custom background, Cycles→Eevee fallback, render guides off.
    Use inside SceneRenderState so the engine switch is restored."""

    def __init__(self, context, area, settings, transparent):
        self.context = context
        self.space = area.spaces.active
        self.settings = settings
        self.transparent = transparent

    def __enter__(self):
        scene = self.context.scene
        space = self.space
        self.hid_overlays = False
        self.orig_bg = None

        # Cycles 렌더드 뷰는 opengl 캡처 시 빈 화면이 나오므로 Eevee 로 잠시 전환
        if space.shading.type == 'RENDERED' and scene.render.engine == 'CYCLES':
            for engine in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
                try:
                    scene.render.engine = engine
                    break
                except Exception:
                    pass

        if self.settings.hide_overlays and space.overlay.show_overlays:
            space.overlay.show_overlays = False
            self.hid_overlays = True

        if not self.transparent:
            self.orig_bg = (space.shading.background_type, tuple(space.shading.background_color))
            space.shading.background_type = 'VIEWPORT'
            space.shading.background_color = self.settings.bg_color

        self.guide_token = suspend_render_guides(self.context)
        return self

    def __exit__(self, exc_type, exc, tb):
        space = self.space
        if self.hid_overlays:
            try: space.overlay.show_overlays = True
            except Exception: pass
        if self.orig_bg:
            try:
                space.shading.background_type, space.shading.background_color = self.orig_bg
            except Exception: pass
        resume_render_guides(self.context, self.guide_token)
        return False


def capture_viewport(context, area, out_dir, base_name, overwrite=True):
    """Viewport-render the given 3D view and save it as <out_dir>/<base_name><ext>.
    With overwrite=False an existing file gets a _2, _3... suffix instead.
    Returns the saved file path, or None if the rendered file was not found."""
    scene = context.scene
    ext = scene.render.file_extension
    final_path = os.path.join(out_dir, base_name + ext)
    suffix = 2
    while not overwrite and os.path.exists(final_path):
        final_path = os.path.join(out_dir, f"{base_name}_{suffix}{ext}")
        suffix += 1

    # opengl write_still 은 파일명에 프레임 번호를 붙일 수 있으므로 임시 prefix 로 저장 후 이름 변경
    temp_prefix = os.path.join(out_dir, f"_tmp_{base_name}_")
    scene.render.filepath = temp_prefix

    # Rendered/Material Preview 가 샘플을 쌓을 수 있도록 먼저 다시 그림 (빈 화면 방지)
    try:
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=5)
    except Exception:
        pass

    with context.temp_override(area=area, region=_window_region(area)):
        bpy.ops.render.opengl('EXEC_DEFAULT', animation=False, write_still=True, view_context=True)

    rendered_files = glob.glob(f"{glob.escape(temp_prefix)}*{ext}")
    if not rendered_files:
        return None
    rendered_files.sort(key=os.path.getmtime, reverse=True)
    os.replace(rendered_files[0], final_path)
    for leftover in rendered_files[1:]:
        try: os.remove(leftover)
        except OSError: pass
    return final_path


class K_RENDER_OT_viewport_capture(bpy.types.Operator):
    bl_idname = "k_render.viewport_capture"
    bl_label = "Capture Viewport"
    bl_description = "Save the viewport as an image named after the Active Object"

    def execute(self, context):
        scene = context.scene
        settings = get_settings(context)

        area = find_view3d_area(context)
        if not area:
            self.report({'ERROR'}, "No 3D Viewport found.")
            return {'CANCELLED'}

        out_dir = prepare_output_dir(self, settings)
        if not out_dir:
            return {'CANCELLED'}

        obj = context.active_object
        obj_name = safe_filename(obj.name if obj else "Viewport_Preview")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            with SceneRenderState(scene):
                transparent = apply_output_format(scene, settings)
                with ViewportCaptureState(context, area, settings, transparent):
                    saved = capture_viewport(context, area, out_dir, f"{obj_name}_{timestamp}", overwrite=False)
        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {e}")
            return {'CANCELLED'}

        if saved:
            self.report({'INFO'}, f"Saved: {saved}")
        else:
            self.report({'WARNING'}, "Rendered file not found. Ensure render was not cancelled.")
        return {'FINISHED'}


classes = (
    K_RENDER_OT_viewport_capture,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
