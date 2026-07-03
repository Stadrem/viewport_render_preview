🌐 [English](README.md) | 🇰🇷 [한국어](README.ko.md)

# 📸 Viewport Render & Preview

A professional, high-performance Blender addon designed to streamline your viewport rendering workflow. Automatically save beautiful, transparent, and overlay-free viewport screenshots named after your active object with a single click.

<p align="center">
  <img src="https://img.shields.io/badge/Blender-5.1+-306EE8?logo=blender&logoColor=white&style=for-the-badge" alt="Blender Version">
  <img src="https://img.shields.io/badge/Format-PNG%20%2F%20RGBA-4CAF50?style=for-the-badge" alt="Format support">
  <img src="https://img.shields.io/badge/License-GPL--3.0-blue?style=for-the-badge" alt="License">
</p>

---

## 🌟 Key Features

- ⚡ Auto-Named Viewport Rendering: Saves high-quality viewport preview images named automatically after the currently selected active object with a clean date-time timestamp (`Object_YYYYMMDD_HHMMSS.png`).
- 🙈 Smart Grid & Overlay Hiding: Temporarily disables all viewport overlays (Grid, Gizmos, 3D Cursor, Bones) only *during* the render operation, restoring your viewport configuration perfectly immediately afterward.
- 👻 One-Click Transparent Backgrounds: Render high-quality sprites with transparency! Dynamically applies PNG, RGBA, and Eevee Film Transparent settings just for the render, preserving your scene's original settings completely.
- 🎨 Custom Viewport Background Color: When transparency is toggled off, a customizable background color picker becomes visible, allowing you to render sprites on a clean, custom flat color.
- 📁 One-Click Open Directory: Easily open your output directory directly in your operating system's file explorer using the folder shortcut button.
- 📐 Active Aspect Ratio Render Guides: Expose a customizable dark mask and yellow aspect-ratio outline that shows you exactly how your final scene camera boundaries crop the active 3D Viewport.

---

## ⚠️ Engine Support & Cycles Fallback

The standard viewport rendering operator (`bpy.ops.render.opengl`) cannot synchronously capture progressive viewport renders in Cycles Rendered Mode due to Cycles' decoupled, asynchronous draw loop (resulting in completely blank or empty alpha frames). 

To guarantee perfect and instant previews:
- Cycles Rendered Mode Fallback: If your active viewport is in `Rendered` shading mode and your engine is set to `Cycles`, the addon automatically swaps the viewport engine to Eevee for the split second it takes to capture the screenshot, then instantly reverts your engine settings back to `Cycles` without disrupting your workflow.
- *Note:* Using Material Preview, Solid, or Wireframe shading modes will capture instantly using Eevee/Workbench regardless of your active render engine.

---

## 🛠️ Panel Interface Overview

Located in the 3D Viewport > Sidebar (N-Panel) > K-Quick Tools tab under the Viewport Render section:

```
┌──────────────────────────────────────────┐
│ ▼ 📺 Viewport Render           │
├──────────────────────────────────────────┤
│ [ Show Render Guide ]          │
│                     │
│ ┌─ Render Options ───────────────────┐ │
│ │ [x] Hide Overlays on Render    │ │
│ │ [ ] Transparent BG (PNG)      │ │
│ │   Background Color [🎨 Pick]   │ │
│ └────────────────────────────────────┘ │
│                     │
│ Folder: [ Rendering        ] ↪ │
│                     │
│ ┌────────────────────────────────────┐ │
│ │     [ 📷 Rendering ]      │ │
│ └────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

- Show / Hide Render Guide: Toggles the custom aspect-ratio boundary guide drawn natively using the GPU shader.
- Hide Overlays on Render: When checked, hides all overlays (grids, paths, axes, bones) during render only, so you don't have to manually hide them.
- Transparent BG (PNG): Automatically handles rendering transparency (PNG format, RGBA mode, Film transparent) without changing your main project's permanent render settings.
- Background Color: Visible only when *Transparent BG* is off. Lets you specify a flat colored background for the viewport preview render.
- Folder: Specify the directory name (relative to the active `.blend` file) where preview images are saved. Defaults to `Rendering`.
- Open Directory Button (↪ / FOLDER_REDIRECT): Automatically creates the specified folder (if it doesn't exist yet) and opens it in Windows Explorer / Finder.

---

## 🚀 Installation

1. Download the repository as a `.zip` file.
2. Open Blender, go to Edit > Preferences > Addons.
3. Click Install... at the top right and select the downloaded `.zip` file.
4. Search for "Viewport Render & Preview" in the list and check the checkbox to activate it.

---

## 📖 How to Use

1. Save your `.blend` file (renders will be saved relative to this file).
2. Select the object you want to render in the viewport (the saved file name will match the active object's name + date-time).
3. Open the N-Panel (Sidebar) in the 3D viewport, click the K-Quick Tools tab.
4. Configure your Render Options (Hide Overlays, Transparent BG, or Background Color).
5. Click the big Rendering button.
6. The image will render instantly and save to the `<your_blend_file_directory>/Rendering/Active_Object_Name_YYYYMMDD_HHMMSS.png`!
7. Click the folder shortcut button (↪) next to the folder path to open and verify the rendered files immediately!

---

## 📁 File Structure

- `__init__.py`: Handles addon metadata definition, registration, and module reloading.
- `viewport_render_preview.py`: Main engine including the custom GPU viewport aspect-ratio guides, key render operators, dynamic transparent overlays, and N-Panel UI elements.

---

## 📄 License

This project is licensed under the GNU GPL v3.0 License. See the [LICENSE](file:///c:/Users/user/AppData/Roaming/Blender%20Foundation/Blender/5.1/scripts/addons/viewport_render_preview/LICENSE) file for details.

