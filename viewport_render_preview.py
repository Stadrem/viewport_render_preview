import bpy
import os
import glob
import gpu
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
    if getattr(scene, "viewport_render_guide_enabled", False):
        return
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
    if not getattr(scene, "viewport_render_guide_enabled", False):
        return
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


class VIEWPORT_PREVIEW_OT_toggle_render_guide(bpy.types.Operator):
    """Toggle Scene Resolution guide overlay on the 3D viewport"""
    bl_idname = "viewport_preview.toggle_render_guide"
    bl_label = "Toggle Render Guide"
    bl_description = "Toggle the Scene Resolution guide on the 3D viewport"

    def execute(self, context):
        if is_render_guide_enabled(context.scene):
            disable_render_guide(context)
        else:
            enable_render_guide(context)
        return {'FINISHED'}


class VIEWPORT_PREVIEW_OT_open_folder(bpy.types.Operator):
    bl_idname = "viewport_preview.open_folder"
    bl_label = "Open Folder"
    bl_description = "Open the current rendering directory"
    
    def execute(self, context):
        import sys
        import subprocess
        
        scene = context.scene
        dir_name = getattr(scene, "viewport_render_dir_name", "Rendering")
        blend_path = bpy.data.filepath
        
        if blend_path:
            base_dir = os.path.dirname(blend_path)
            target_dir = os.path.join(base_dir, dir_name)
        else:
            target_dir = os.path.join(bpy.app.tempdir, dir_name)
            
        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir)
            except Exception as e:
                self.report({'WARNING'}, f"Could not create directory: {e}")
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
            
        return {'FINISHED'}


class VIEWPORT_PREVIEW_OT_render(bpy.types.Operator):
    bl_idname = "render.viewport_preview_image"
    bl_label = "Render Viewport"
    bl_description = "Save viewport preview as PNG using Active Object name"
    
    def execute(self, context):
        scene = context.scene
        
        original_filepath = scene.render.filepath
        original_format = scene.render.image_settings.file_format
        original_color_mode = scene.render.image_settings.color_mode
        original_film_transparent = scene.render.film_transparent
        original_engine = scene.render.engine
        switched_to_eevee = False
        
        # 1. Setup save directory (relative to current blend file)
        dir_name = scene.viewport_render_dir_name
        blend_path = bpy.data.filepath
        if blend_path:
            base_dir = os.path.dirname(blend_path)
            target_dir = os.path.join(base_dir, dir_name)
        else:
            target_dir = os.path.join(bpy.app.tempdir, dir_name)
            
        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir)
            except Exception as e:
                self.report({'ERROR'}, f"Failed to create directory: {e}")
                return {'CANCELLED'}
            
        # 2. Extract Object Name and define File Name
        obj = context.active_object
        obj_name = obj.name if obj else "Viewport_Preview"
        
        # Remove characters that can cause unwanted directory creation
        obj_name = obj_name.replace("/", "_").replace("\\", "_")
        
        # Generate timestamp: YYYYMMDD_HHMMSS
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Assign settings for the native viewport render to consume (using a unique temporary prefix)
        temp_prefix = f"temp_render_{obj_name}_"
        raw_target_filepath = os.path.join(target_dir, temp_prefix)
        scene.render.filepath = raw_target_filepath
        scene.render.image_settings.file_format = 'PNG'
        
        is_transparent = getattr(scene, "viewport_render_transparent", True)
        if is_transparent:
            scene.render.image_settings.color_mode = 'RGBA'
            scene.render.film_transparent = True
        else:
            scene.render.image_settings.color_mode = 'RGB'
            scene.render.film_transparent = False
        
        final_file_path = os.path.join(target_dir, f"{obj_name}_{timestamp}.png")

        # Disable Overlays temporarily and Handle Custom Background
        hidden_overlay_spaces = []
        modified_bg_spaces = []
        
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                if space:
                    # Force Eevee if Cycles + Rendered
                    if hasattr(space, "shading") and space.shading.type == 'RENDERED':
                        if original_engine == 'CYCLES':
                            try:
                                scene.render.engine = 'BLENDER_EEVEE_NEXT'
                            except Exception:
                                scene.render.engine = 'BLENDER_EEVEE'
                            switched_to_eevee = True
                            
                    # Hide Overlays
                    if getattr(scene, "viewport_render_hide_overlays", False):
                        if hasattr(space, "overlay") and getattr(space.overlay, "show_overlays", False):
                            space.overlay.show_overlays = False
                            hidden_overlay_spaces.append(space)
                            
                    # Custom Background (Only if transparent BG is OFF)
                    if not is_transparent:
                        if hasattr(space, "shading"):
                            orig_bg_type = space.shading.background_type
                            orig_bg_color = tuple(space.shading.background_color)
                            
                            space.shading.background_type = 'VIEWPORT'
                            if hasattr(scene, "viewport_render_bg_color"):
                                space.shading.background_color = scene.viewport_render_bg_color[:3]
                                
                            modified_bg_spaces.append((space, orig_bg_type, orig_bg_color))
        
        # Disable Render Guide temporarily so it isn't rendered into the image
        was_local_guide_enabled = False
        try:
            was_local_guide_enabled = is_render_guide_enabled(scene)
            if was_local_guide_enabled:
                disable_render_guide(context)
        except Exception as e:
            print(f"Error disabling local render guide: {e}")

        was_het_guide_enabled = False
        try:
            import hyper_easy_toolkit
            was_het_guide_enabled = hyper_easy_toolkit.is_render_guide_enabled(scene)
            if was_het_guide_enabled:
                hyper_easy_toolkit.disable_render_guide(context)
        except Exception:
            pass
        # 3. Native Render Viewport Execution
        try:
            # Force a viewport redraw so Eevee/Cycles Rendered mode can accumulate samples
            # before taking the snapshot, preventing invisible/blank objects.
            try:
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=5)
            except Exception:
                pass
                
            bpy.ops.render.opengl('EXEC_DEFAULT', animation=False, write_still=True)
            self.report({'INFO'}, "Requested Viewport Render.")
        except Exception as e:
            self.report({'ERROR'}, f"Render failed: {e}")
            scene.render.filepath = original_filepath
            scene.render.image_settings.file_format = original_format
            scene.render.image_settings.color_mode = original_color_mode
            scene.render.film_transparent = original_film_transparent
            if switched_to_eevee:
                scene.render.engine = original_engine
            
            # Restore Overlays and Backgrounds
            for space in hidden_overlay_spaces:
                try: space.overlay.show_overlays = True
                except Exception: pass
            for space, orig_type, orig_color in modified_bg_spaces:
                try:
                    space.shading.background_type = orig_type
                    space.shading.background_color = orig_color
                except Exception: pass

            # Restore Render Guides
            if was_local_guide_enabled:
                try: enable_render_guide(context)
                except Exception: pass
            if was_het_guide_enabled:
                try:
                    import hyper_easy_toolkit
                    hyper_easy_toolkit.enable_render_guide(context)
                except Exception: pass
            return {'CANCELLED'}
            
        # Restore Overlays and Backgrounds
        for space in hidden_overlay_spaces:
            try: space.overlay.show_overlays = True
            except Exception: pass
        for space, orig_type, orig_color in modified_bg_spaces:
            try:
                space.shading.background_type = orig_type
                space.shading.background_color = orig_color
            except Exception: pass

        # Restore Render Guides
        if was_local_guide_enabled:
            try: enable_render_guide(context)
            except Exception: pass
        if was_het_guide_enabled:
            try:
                import hyper_easy_toolkit
                hyper_easy_toolkit.enable_render_guide(context)
            except Exception: pass
            
        # Restore initial settings
        scene.render.filepath = original_filepath
        scene.render.image_settings.file_format = original_format
        scene.render.image_settings.color_mode = original_color_mode
        scene.render.film_transparent = original_film_transparent
        if switched_to_eevee:
            scene.render.engine = original_engine
        
        # 4. Correct the saved filename.
        # Use glob to dynamically find the rendered file, avoiding frame-number mismatches
        escaped_target = glob.escape(raw_target_filepath)
        search_pattern = f"{escaped_target}*.png"
        rendered_files = glob.glob(search_pattern)
        
        if rendered_files:
            # Sort by modification time to get the most recently saved file
            rendered_files.sort(key=os.path.getmtime, reverse=True)
            saved_file_path = rendered_files[0]
            
            try:
                if os.path.exists(final_file_path) and saved_file_path != final_file_path:
                    os.remove(final_file_path)
                    
                if saved_file_path != final_file_path:
                    os.rename(saved_file_path, final_file_path)
                    
                self.report({'INFO'}, f"Saved to {dir_name}: {obj_name}_{timestamp}.png")
            except Exception as e:
                self.report({'WARNING'}, f"Failed to rename file: {e}")
        else:
            self.report({'WARNING'}, f"Rendered file not found. Ensure render was not cancelled.")
            
        return {'FINISHED'}


class VIEWPORT_PREVIEW_PT_panel(bpy.types.Panel):
    bl_label = "Viewport Render"
    bl_idname = "VIEWPORT_PREVIEW_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'K-Quick Tools'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.label(text="", icon='RESTRICT_VIEW_OFF')
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # 1. Viewport Guide Toggle
        is_on = is_render_guide_enabled(scene)
        icon = 'HIDE_OFF' if is_on else 'HIDE_ON'
        text = "Hide Render Guide" if is_on else "Show Render Guide"
        layout.operator("viewport_preview.toggle_render_guide", text=text, icon=icon)
        
        layout.separator()
        
        # 2. Render Settings Box
        box = layout.box()
        
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text="Render Options")
        
        col_box = box.column(align=False)
        if hasattr(scene, "viewport_render_hide_overlays"):
            col_box.prop(scene, "viewport_render_hide_overlays", text="Hide Overlays on Render")
            
        is_transparent = getattr(scene, "viewport_render_transparent", True)
        if hasattr(scene, "viewport_render_transparent"):
            col_box.prop(scene, "viewport_render_transparent", text="Transparent BG (PNG)")
            
        # Custom BG Color (only if Transparent BG is OFF)
        if not is_transparent and hasattr(scene, "viewport_render_bg_color"):
            col_box.prop(scene, "viewport_render_bg_color", text="Background Color")
        
        layout.separator()
        
        # 3. Directory
        if hasattr(scene, "viewport_render_dir_name"):
            row = layout.row(align=True)
            row.prop(scene, "viewport_render_dir_name")
            row.operator("viewport_preview.open_folder", text="", icon='FOLDER_REDIRECT')
            
        layout.separator()
        
        # 4. Rendering Button
        col = layout.column(align=True)
        col.scale_y = 1.5
        col.operator("render.viewport_preview_image", text="Rendering", icon='RENDER_STILL')


classes = (
    VIEWPORT_PREVIEW_OT_toggle_render_guide,
    VIEWPORT_PREVIEW_OT_open_folder,
    VIEWPORT_PREVIEW_OT_render,
    VIEWPORT_PREVIEW_PT_panel,
)

def register():
    bpy.types.Scene.viewport_render_guide_enabled = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.viewport_render_transparent = bpy.props.BoolProperty(
        name="Transparent Background",
        description="Render viewport with a transparent background (PNG, RGBA)",
        default=True
    )
    bpy.types.Scene.viewport_render_bg_color = bpy.props.FloatVectorProperty(
        name="Background Color",
        description="Custom background color for viewport render when transparency is off",
        subtype='COLOR',
        min=0.0, max=1.0,
        default=(0.1, 0.1, 0.1, 1.0),
        size=4
    )
    bpy.types.Scene.viewport_render_hide_overlays = bpy.props.BoolProperty(
        name="Hide Overlays on Render",
        description="Temporarily disable all viewport overlays (Grid, Gizmos, etc.) during rendering",
        default=True
    )
    bpy.types.Scene.viewport_render_dir_name = bpy.props.StringProperty(
        name="Folder",
        description="Directory to save the renders",
        default="Rendering",
        subtype='DIR_PATH'
    )
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    global _render_guide_handler
    if _render_guide_handler:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_render_guide_handler, 'WINDOW')
        except Exception:
            pass
        _render_guide_handler = None

    if hasattr(bpy.types.Scene, "viewport_render_guide_enabled"):
        del bpy.types.Scene.viewport_render_guide_enabled
    if hasattr(bpy.types.Scene, "viewport_render_transparent"):
        del bpy.types.Scene.viewport_render_transparent
    if hasattr(bpy.types.Scene, "viewport_render_bg_color"):
        del bpy.types.Scene.viewport_render_bg_color
    if hasattr(bpy.types.Scene, "viewport_render_hide_overlays"):
        del bpy.types.Scene.viewport_render_hide_overlays
    if hasattr(bpy.types.Scene, "viewport_render_dir_name"):
        del bpy.types.Scene.viewport_render_dir_name
        
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
