import bpy
import gpu
from bpy.app.handlers import persistent
from gpu_extras.batch import batch_for_shader

# ═══════════════════════════════════════════════════════════
# Render Guide — 뷰포트에 씬 해상도 가이드 오버레이 표시
# ═══════════════════════════════════════════════════════════

_render_guide_handler = None

def _get_render_resolution(scene):
    res_x = scene.render.resolution_x * (scene.render.resolution_percentage / 100.0)
    res_y = scene.render.resolution_y * (scene.render.resolution_percentage / 100.0)
    return res_x, res_y

def _draw_render_guide_callback():
    context = bpy.context
    area = getattr(context, 'area', None)
    if not area or area.type != 'VIEW_3D':
        return

    scene = context.scene
    region = context.region

    res_x, res_y = _get_render_resolution(scene)
    if res_y <= 0 or res_x <= 0:
        return

    view_aspect = region.width / region.height
    render_aspect = res_x / res_y

    if view_aspect > render_aspect:
        draw_h = region.height
        draw_w = region.height * render_aspect
    else:
        draw_w = region.width
        draw_h = region.width / render_aspect

    x = (region.width - draw_w) / 2
    y = (region.height - draw_h) / 2

    # Outer dark mask
    shader_poly = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')

    rects = []
    if view_aspect > render_aspect:
        rects.append(((0, 0), (x, region.height)))
        rects.append(((x + draw_w, 0), (region.width, region.height)))
    else:
        rects.append(((0, 0), (region.width, y)))
        rects.append(((0, y + draw_h), (region.width, region.height)))

    for r in rects:
        p1, p2 = r
        v = (p1, (p2[0], p1[1]), p2, (p1[0], p2[1]))
        idx = ((0, 1, 2), (0, 2, 3))
        b = batch_for_shader(shader_poly, 'TRIS', {"pos": v}, indices=idx)
        shader_poly.bind()
        shader_poly.uniform_float("color", (0.0, 0.0, 0.0, 0.6))
        b.draw(shader_poly)

    # Yellow outline border
    shader_line = gpu.shader.from_builtin('UNIFORM_COLOR')
    vertices = (
        (x, y), (x + draw_w, y),
        (x + draw_w, y + draw_h), (x, y + draw_h)
    )
    indices = ((0, 1), (1, 2), (2, 3), (3, 0))
    batch_line = batch_for_shader(shader_line, 'LINES', {"pos": vertices}, indices=indices)

    gpu.state.line_width_set(2.0)
    shader_line.bind()
    shader_line.uniform_float("color", (1.0, 0.8, 0.1, 1.0))
    batch_line.draw(shader_line)

    gpu.state.blend_set('NONE')

def enable_render_guide(context=None):
    """Enable the render guide overlay."""
    global _render_guide_handler
    scene = context.scene if context else bpy.context.scene
    if not _render_guide_handler:
        _render_guide_handler = bpy.types.SpaceView3D.draw_handler_add(
            _draw_render_guide_callback, (), 'WINDOW', 'POST_PIXEL'
        )
    scene.viewport_render_guide_enabled = True
    _tag_redraw_viewports(context)

def disable_render_guide(context=None):
    """Disable the render guide overlay."""
    global _render_guide_handler
    scene = context.scene if context else bpy.context.scene
    if _render_guide_handler:
        bpy.types.SpaceView3D.draw_handler_remove(_render_guide_handler, 'WINDOW')
        _render_guide_handler = None
    scene.viewport_render_guide_enabled = False
    _tag_redraw_viewports(context)

def is_render_guide_enabled(scene=None):
    """Check if render guide is currently enabled."""
    if scene is None:
        scene = bpy.context.scene
    return getattr(scene, "viewport_render_guide_enabled", False)

def _tag_redraw_viewports(context=None):
    try:
        screen = context.screen if context else bpy.context.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
    except Exception:
        pass


def suspend_render_guides(context):
    """Turn off the render guide so it doesn't end up in captures.
    Returns a token for resume_render_guides()."""
    was_on = False
    try:
        was_on = is_render_guide_enabled(context.scene)
        if was_on:
            disable_render_guide(context)
    except Exception as e:
        print(f"Error disabling render guide: {e}")
    return was_on

def resume_render_guides(context, was_on):
    if was_on:
        try: enable_render_guide(context)
        except Exception: pass


class K_RENDER_OT_toggle_render_guide(bpy.types.Operator):
    """Toggle Scene Resolution guide overlay on the 3D viewport"""
    bl_idname = "k_render.toggle_render_guide"
    bl_label = "Toggle Render Guide"
    bl_description = "Toggle the Scene Resolution guide on the 3D viewport"

    def execute(self, context):
        if is_render_guide_enabled(context.scene):
            disable_render_guide(context)
        else:
            enable_render_guide(context)
        return {'FINISHED'}


# 파일을 열면 draw handler 는 사라지지만 씬 속성은 남아있으므로 다시 연결
def _restore_render_guide():
    scene = getattr(bpy.context, "scene", None)
    if scene and is_render_guide_enabled(scene):
        enable_render_guide()
    return None

@persistent
def _load_post_handler(dummy):
    bpy.app.timers.register(_restore_render_guide, first_interval=0.1)


classes = (
    K_RENDER_OT_toggle_render_guide,
)

def register():
    bpy.types.Scene.viewport_render_guide_enabled = bpy.props.BoolProperty(default=False)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.load_post.append(_load_post_handler)

def unregister():
    global _render_guide_handler
    if _load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_load_post_handler)
    if _render_guide_handler:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_render_guide_handler, 'WINDOW')
        except Exception:
            pass
        _render_guide_handler = None
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.viewport_render_guide_enabled
