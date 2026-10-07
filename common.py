import bpy
import os
import sys
import subprocess

# ═══════════════════════════════════════════════════════════
# 공통 출력 설정 — 뷰포트 캡처 / 카메라 배치 렌더가 함께 사용
# ═══════════════════════════════════════════════════════════

class K_RENDER_Settings(bpy.types.PropertyGroup):
    output_dir: bpy.props.StringProperty(
        name="Folder",
        description="Output folder. Relative paths are resolved next to the .blend file",
        default="Rendering",
        subtype='DIR_PATH'
    )
    file_format: bpy.props.EnumProperty(
        name="File Format",
        items=[
            ('PNG', "PNG", "Save as PNG image"),
            ('JPEG', "JPG", "Save as JPG image"),
        ],
        default='PNG'
    )
    use_transparent: bpy.props.BoolProperty(
        name="Transparent Background",
        description="Render with a transparent background (Film Transparent & RGBA). PNG only",
        default=False
    )
    hide_overlays: bpy.props.BoolProperty(
        name="Hide Overlays",
        description="Temporarily disable viewport overlays (grid, gizmos, etc.) during viewport captures",
        default=True
    )
    bg_color: bpy.props.FloatVectorProperty(
        name="Background Color",
        description="Viewport background color for captures when transparency is off",
        subtype='COLOR',
        min=0.0, max=1.0,
        default=(0.1, 0.1, 0.1),
        size=3
    )
    camera_names: bpy.props.StringProperty(
        name="Camera Names",
        description="Comma-separated list of camera names to render",
        default=""
    )
    camera_method: bpy.props.EnumProperty(
        name="Method",
        items=[
            ('RENDER', "Render", "Full render (F12) with the scene render engine"),
            ('VIEWPORT', "Viewport", "Fast viewport capture through each camera"),
        ],
        default='RENDER'
    )

    def get_camera_list(self):
        return [name.strip() for name in self.camera_names.split(",") if name.strip()]

    @property
    def is_transparent(self):
        return self.use_transparent and self.file_format == 'PNG'


def get_settings(context):
    return context.scene.k_render


def resolve_output_dir(raw_path):
    """Return (absolute_dir, error_message)."""
    raw_path = raw_path.strip() or "Rendering"
    if raw_path.startswith("//") or not os.path.isabs(raw_path):
        if not bpy.data.is_saved:
            return None, "Save the .blend file first, or use an absolute folder path."
        if not raw_path.startswith("//"):
            raw_path = "//" + raw_path
        raw_path = bpy.path.abspath(raw_path)
    return os.path.normpath(raw_path), None


def prepare_output_dir(operator, settings):
    """Resolve and create the output folder. Reports and returns None on failure."""
    out_dir, error = resolve_output_dir(settings.output_dir)
    if error:
        operator.report({'ERROR'}, error)
        return None
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as e:
        operator.report({'ERROR'}, f"Failed to create directory: {e}")
        return None
    return out_dir


_INVALID_FILENAME_CHARS = '/\\:*?"<>|'

def safe_filename(name):
    for ch in _INVALID_FILENAME_CHARS:
        name = name.replace(ch, "_")
    return name


class SceneRenderState:
    """Save scene render settings on enter and restore them on exit."""

    def __init__(self, scene):
        self.scene = scene

    def __enter__(self):
        render = self.scene.render
        image = render.image_settings
        self.camera = self.scene.camera
        self.filepath = render.filepath
        self.engine = render.engine
        self.film_transparent = render.film_transparent
        self.res_x = render.resolution_x
        self.res_y = render.resolution_y
        self.media_type = getattr(image, "media_type", None)
        self.file_format = image.file_format
        self.color_mode = image.color_mode
        return self

    def __exit__(self, exc_type, exc, tb):
        render = self.scene.render
        image = render.image_settings
        self.scene.camera = self.camera
        render.filepath = self.filepath
        if render.engine != self.engine:
            render.engine = self.engine
        render.film_transparent = self.film_transparent
        render.resolution_x = self.res_x
        render.resolution_y = self.res_y
        # media_type 가 먼저 복구되어야 file_format 값이 유효해짐
        for attr in ("media_type", "file_format", "color_mode"):
            value = getattr(self, attr)
            if value is None:
                continue
            try:
                setattr(image, attr, value)
            except Exception:
                pass
        return False


def apply_output_format(scene, settings):
    """Apply shared file format / transparency to the scene. Call inside SceneRenderState."""
    image = scene.render.image_settings
    if hasattr(image, "media_type"):
        image.media_type = 'IMAGE'
    image.file_format = settings.file_format
    transparent = settings.is_transparent
    image.color_mode = 'RGBA' if transparent else 'RGB'
    scene.render.film_transparent = transparent
    return transparent


class K_RENDER_OT_open_folder(bpy.types.Operator):
    bl_idname = "k_render.open_folder"
    bl_label = "Open Folder"
    bl_description = "Open the output folder"

    def execute(self, context):
        target_dir = prepare_output_dir(self, get_settings(context))
        if not target_dir:
            return {'CANCELLED'}
        try:
            if sys.platform == 'win32':
                os.startfile(target_dir)
            elif sys.platform == 'darwin':
                subprocess.call(["open", target_dir])
            else:
                subprocess.call(["xdg-open", target_dir])
        except Exception as e:
            self.report({'ERROR'}, f"Failed to open folder: {e}")
            return {'CANCELLED'}
        return {'FINISHED'}


classes = (
    K_RENDER_Settings,
    K_RENDER_OT_open_folder,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.k_render = bpy.props.PointerProperty(type=K_RENDER_Settings)

def unregister():
    del bpy.types.Scene.k_render
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
