🌐 [English](README.md) | 🇰🇷 [한국어](README.ko.md)

# 📸 Viewport Render & Batch Camera

A Blender addon that saves clean images straight to a folder — either a quick viewport capture named after your active object, or a batch of cameras rendered one after another, each with its own resolution. Both share a single set of output settings.

<p align="center">
  <img src="https://img.shields.io/badge/Blender-5.1+-306EE8?logo=blender&logoColor=white&style=for-the-badge" alt="Blender Version">
  <img src="https://img.shields.io/badge/Format-PNG%20%2F%20JPG-4CAF50?style=for-the-badge" alt="Format support">
  <img src="https://img.shields.io/badge/License-GPL--3.0-blue?style=for-the-badge" alt="License">
</p>

> Version 2.0 merges the former **Batch Camera Renderer** addon into this one. If you used it, disable/remove `batch_camera_renderer.py` before enabling this version — per-camera resolutions stored in your `.blend` files carry over unchanged.

---

## 🌟 Key Features

- ⚡ Auto-Named Viewport Capture: Saves the viewport as `Object_YYYYMMDD_HHMMSS.png` named after the active object. Captures within the same second get a `_2`, `_3`… suffix instead of overwriting.
- 🎥 Batch Camera Rendering: Renders every camera in a list to `<CameraName>.png/.jpg`, using either a full render (F12) or a fast viewport capture through each camera.
- 📏 Per-Camera Resolution: Each camera can store its own resolution. Selecting the camera applies it to the scene and turns on the Render Guide.
- 🙈 Smart Overlay Hiding: Temporarily disables viewport overlays (grid, gizmos, 3D cursor, bones) only during viewport captures.
- 👻 Transparent Backgrounds: Applies PNG, RGBA and Film Transparent only for the render, then restores your scene's original settings.
- 🎨 Custom Viewport Background Color: With transparency off, viewport captures use a flat color of your choice.
- 📁 One-Click Open Directory: Opens the output folder in Explorer / Finder.
- 📐 Render Guide: A dark mask and yellow outline that show how the render resolution crops the 3D Viewport.

---

## ⚠️ Engine Support & Cycles Fallback

The viewport render operator (`bpy.ops.render.opengl`) cannot capture Cycles' progressive viewport render (it produces blank frames). If the viewport is in `Rendered` shading with `Cycles`, the addon switches to Eevee just for the capture and restores Cycles afterwards. Solid, Material Preview and Wireframe capture normally with any engine.

Batch camera rendering in **Render** mode uses the real scene engine (Cycles included).

---

## 🛠️ Panel Interface Overview

3D Viewport > Sidebar (N-Panel) > **K-Quick Tools** > **Render**:

```
▼ Render
  [ Show Render Guide ]
  ┌ Output ───────────────────────────┐
  │ Folder: [ Rendering ] ↪            │
  │ [ PNG | JPG ]                      │
  │ [ ] Transparent Background         │
  └────────────────────────────────────┘
  ┌ Viewport Capture ─────────────────┐
  │ [x] Hide Overlays                  │
  │ Background Color [🎨]              │
  └────────────────────────────────────┘
  ▼ Viewport
     Name: Cube_<time>
     [ 📷 Capture Viewport ]
  ▼ Cameras
     [ + Get Selected Cameras ]
     [ Cam_A, Cam_B, ... ]
     Active Cam: Cam_A  [x] Use Custom Resolution  X / Y
     [ Render | Viewport ]
     [ 📷 Render Cameras ]
```

- Folder: Output folder. A relative path is resolved next to the `.blend` file (the file must be saved); an absolute path works anywhere. Defaults to `Rendering`.
- PNG / JPG: File format for both viewport captures and camera renders.
- Transparent Background: PNG only. Applies RGBA + Film Transparent for the render.
- Hide Overlays / Background Color: Apply to viewport captures (including camera batch in Viewport mode).
- Cameras › Render | Viewport: *Render* runs a full F12 render per camera; *Viewport* captures the 3D view through each camera (fast preview, uses the viewport's shading).

---

## 🚀 Installation

1. Download the repository as a `.zip` file.
2. Open Blender, go to Edit > Preferences > Add-ons.
3. Click Install... and select the downloaded `.zip` file.
4. Search for "Viewport Render & Batch Camera" and enable it.

---

## 📖 How to Use

**Viewport capture**
1. Save your `.blend` file.
2. Select the object to name the image after.
3. Click **Capture Viewport** → `<blend_dir>/Rendering/Object_YYYYMMDD_HHMMSS.png`

**Camera batch**
1. Select cameras and click **Get Selected Cameras**.
2. (Optional) Select each camera and set **Use Custom Resolution**.
3. Choose **Render** or **Viewport**, then click **Render Cameras** → `<blend_dir>/Rendering/<CameraName>.png`

---

## 📁 File Structure

- `__init__.py`: Addon metadata, registration and module reloading.
- `common.py`: Shared output settings, output-path handling, scene render state save/restore.
- `render_guide.py`: GPU render-resolution guide overlay.
- `viewport_render.py`: Viewport capture helpers and the Capture Viewport operator.
- `batch_camera.py`: Per-camera resolution properties and the camera batch operator.
- `ui.py`: N-Panel UI.

---

## 📄 License

This project is licensed under the GNU GPL v3.0 License. See the [LICENSE](LICENSE) file for details.
