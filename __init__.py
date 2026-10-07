bl_info = {
    "name": "Viewport Render & Batch Camera",
    "author": "Kim Dongsu",
    "version": (2, 0, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > K-Quick Tools",
    "description": "Viewport capture and per-camera batch rendering with shared output settings.",
    "category": "Render",
}

if "common" in locals():
    import importlib
    importlib.reload(common)
    importlib.reload(render_guide)
    importlib.reload(viewport_render)
    importlib.reload(batch_camera)
    importlib.reload(ui)
else:
    from . import common, render_guide, viewport_render, batch_camera, ui

modules = (common, render_guide, viewport_render, batch_camera, ui)

def register():
    for mod in modules:
        mod.register()

def unregister():
    for mod in reversed(modules):
        mod.unregister()

if __name__ == "__main__":
    register()
