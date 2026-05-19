bl_info = {
    "name": "Viewport Render & Preview",
    "author": "Kim Dongsu",
    "version": (1, 0, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > K-Quick Tools",
    "description": "Render Viewport Preview with Object Name auto-save.",
    "category": "Render",
}

if "viewport_render_preview" in locals():
    import importlib
    importlib.reload(viewport_render_preview)
else:
    from . import viewport_render_preview

def register():
    viewport_render_preview.register()

def unregister():
    viewport_render_preview.unregister()

if __name__ == "__main__":
    register()
