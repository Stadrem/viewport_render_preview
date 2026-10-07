🌐 [English](README.md) | 🇰🇷 [한국어](README.ko.md)

# 📸 Viewport Render & Batch Camera 사용자 가이드

결과 이미지를 바로 폴더에 저장해 주는 블렌더 애드온입니다. 활성 오브젝트 이름으로 뷰포트를 빠르게 캡처하거나, 여러 카메라를 카메라별 해상도로 순차 렌더링할 수 있으며 두 기능이 하나의 출력 설정을 공유합니다.

<p align="center">
  <img src="https://img.shields.io/badge/Blender-5.1+-306EE8?logo=blender&logoColor=white&style=for-the-badge" alt="Blender Version">
  <img src="https://img.shields.io/badge/Format-PNG%20%2F%20JPG-4CAF50?style=for-the-badge" alt="Format support">
  <img src="https://img.shields.io/badge/License-GPL--3.0-blue?style=for-the-badge" alt="License">
</p>

> 2.0 버전부터 기존 **Batch Camera Renderer** 애드온이 이 애드온에 통합되었습니다. 기존 애드온을 사용 중이었다면 `batch_camera_renderer.py`를 비활성화/삭제한 뒤 활성화하세요. `.blend` 파일에 저장된 카메라별 해상도는 그대로 유지됩니다.

---

## 🌟 주요 기능 (Key Features)

* ⚡ **자동 이름 지정 뷰포트 캡처**: 활성 오브젝트 이름과 타임스탬프로 `오브젝트이름_YYYYMMDD_HHMMSS.png`를 저장합니다. 같은 초에 여러 번 캡처하면 덮어쓰지 않고 `_2`, `_3`… 을 붙입니다.
* 🎥 **카메라 배치 렌더링**: 목록의 카메라를 순서대로 `<카메라이름>.png/.jpg`로 저장합니다. 풀 렌더(F12) 또는 카메라 시점 뷰포트 캡처 중 선택할 수 있습니다.
* 📏 **카메라별 해상도**: 카메라마다 해상도를 따로 저장합니다. 해당 카메라를 선택하면 씬 해상도에 적용되고 Render Guide가 켜집니다.
* 🙈 **오버레이 자동 숨김**: 뷰포트 캡처 순간에만 그리드, 기즈모, 3D 커서, 본 등 오버레이를 끄고 복구합니다.
* 👻 **투명 배경**: PNG / RGBA / Film Transparent 를 렌더링 시에만 적용하고 원래 씬 설정을 복구합니다.
* 🎨 **뷰포트 배경색 지정**: 투명 배경을 끄면 뷰포트 캡처에 원하는 단색 배경을 사용합니다.
* 📁 **출력 폴더 열기**: 버튼(↪) 하나로 탐색기/파인더에서 출력 폴더를 엽니다.
* 📐 **Render Guide**: 렌더 해상도 바깥 영역을 어둡게 덮고 노란 테두리로 최종 프레임 영역을 표시합니다.

---

## ⚠️ 엔진 지원 및 Cycles 대비책 (Cycles Fallback)

뷰포트 렌더 연산자(`bpy.ops.render.opengl`)는 Cycles 렌더 뷰포트의 Progressive 렌더를 캡처하지 못하고 빈 화면을 저장합니다. 뷰포트가 `Rendered` 모드이고 엔진이 `Cycles`이면 캡처하는 순간에만 Eevee로 전환했다가 Cycles로 복구합니다. Solid / Material Preview / Wireframe 은 엔진과 관계없이 정상 캡처됩니다.

카메라 배치의 **Render** 모드는 실제 씬 엔진(Cycles 포함)으로 렌더링합니다.

---

## 🛠️ 패널 인터페이스 개요 (Panel Interface)

3D Viewport > Sidebar (N-패널) > **K-Quick Tools** > **Render**:

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

* **Folder**: 출력 폴더입니다. 상대 경로는 `.blend` 파일 옆에 생성되며(파일 저장 필요), 절대 경로는 어디서나 동작합니다. 기본값은 `Rendering` 입니다.
* **PNG / JPG**: 뷰포트 캡처와 카메라 렌더 공통 파일 형식입니다.
* **Transparent Background**: PNG 전용. 렌더 시에만 RGBA + Film Transparent 를 적용합니다.
* **Hide Overlays / Background Color**: 뷰포트 캡처(카메라 배치의 Viewport 모드 포함)에 적용됩니다.
* **Cameras › Render | Viewport**: *Render* 는 카메라마다 F12 풀 렌더, *Viewport* 는 각 카메라 시점으로 뷰포트를 캡처합니다(빠른 미리보기, 뷰포트 셰이딩 사용).

---

## 🚀 설치 방법

1. 저장소를 `.zip` 파일로 다운로드합니다.
2. 블렌더에서 `Edit > Preferences > Add-ons`로 이동합니다.
3. `Install...` 버튼을 누르고 다운로드한 `.zip` 파일을 선택합니다.
4. "Viewport Render & Batch Camera"를 검색해 활성화합니다.

---

## 📖 사용 순서

**뷰포트 캡처**
1. `.blend` 파일을 먼저 저장합니다.
2. 이미지 이름으로 쓸 오브젝트를 선택합니다.
3. **Capture Viewport** 클릭 → `<blend_디렉토리>/Rendering/오브젝트이름_YYYYMMDD_HHMMSS.png`

**카메라 배치**
1. 카메라들을 선택하고 **Get Selected Cameras** 를 누릅니다.
2. (선택) 카메라를 하나씩 선택해 **Use Custom Resolution** 을 설정합니다.
3. **Render** 또는 **Viewport** 를 고른 뒤 **Render Cameras** 클릭 → `<blend_디렉토리>/Rendering/<카메라이름>.png`

---

## 📁 파일 구조

* `__init__.py`: 애드온 메타데이터, 등록 및 모듈 리로딩.
* `common.py`: 공통 출력 설정, 출력 경로 처리, 씬 렌더 설정 저장/복구.
* `render_guide.py`: GPU 렌더 해상도 가이드 오버레이.
* `viewport_render.py`: 뷰포트 캡처 헬퍼와 Capture Viewport 연산자.
* `batch_camera.py`: 카메라별 해상도 속성과 카메라 배치 연산자.
* `ui.py`: N-패널 UI.

---

## 📄 라이선스 (License)
이 애드온은 블렌더 Python API(`bpy`)를 임포트하여 통합 실행되는 블렌더의 2차 저작물로서 **GNU GPL v3.0** 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하십시오.
