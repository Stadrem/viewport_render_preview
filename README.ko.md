🌐 [English](README.md) | 🇰🇷 [한국어](README.ko.md)

# 📸 Viewport Render & Preview 사용자 가이드

뷰포트 렌더링 워크플로우를 혁신적으로 간소화해 주는 고성능 블렌더(Blender) 애드온입니다. 단 한 번의 클릭으로 활성화된 오브젝트 이름을 가진 투명하고 격자/오버레이가 없는 아름다운 뷰포트 스크린샷을 자동으로 저장합니다.

<p align="center">
  <img src="https://img.shields.io/badge/Blender-5.1+-306EE8?logo=blender&logoColor=white&style=for-the-badge" alt="Blender Version">
  <img src="https://img.shields.io/badge/Format-PNG%20%2F%20RGBA-4CAF50?style=for-the-badge" alt="Format support">
  <img src="https://img.shields.io/badge/License-GPL--3.0-blue?style=for-the-badge" alt="License">
</p>

---

## 🌟 주요 기능 (Key Features)

* ⚡ **자동 이름 지정 뷰포트 렌더**: 현재 선택된 활성 오브젝트 이름과 날짜/시간 타임스탬프를 조합하여 고화질 뷰포트 렌더 이미지(`오브젝트이름_YYYYMMDD_HHMMSS.png`)로 자동 저장합니다.
* 🙈 **스마트 그리드 & 오버레이 숨김**: 렌더링 캡처 순간에만 뷰포트의 오버레이(그리드, 기즈모, 3D 커서, 아머쳐 뼈 등)를 일시적으로 끄고, 캡처가 완료되면 기존의 오버레이 구성을 원상복구합니다.
* 👻 **원클릭 투명 배경 지원**: PNG 형식, RGBA 모드 및 Eevee Film 투명도 옵션을 렌더링 시에만 다이내믹하게 적용하여, 프로젝트의 원래 렌더링 설정을 전혀 건드리지 않고 투명한 스프라이트를 렌더링합니다.
* 🎨 **사용자 지정 뷰포트 배경색**: 투명 배경 옵션을 끌 경우 단색 배경 컬러 피커가 활성화되어 원하는 평면 배경 위에 스프라이트를 렌더링할 수 있습니다.
* 📁 **원클릭 출력 폴더 열기**: 폴더 바로가기 버튼(↪)을 눌러 탐색기(Windows) 또는 파인더(macOS)에서 저장된 경로를 즉시 열어볼 수 있습니다.
* 📐 **활성 화면 종횡비 가이드**: 3D 뷰포트 내에 카메라 영역 바깥을 어둡게 투명 마스크로 덮고 노란색 테두리선을 그려 최종 카메라 앵글에 담길 영역을 확실하게 가이드해 줍니다.

---

## ⚠️ 엔진 지원 및 Cycles 대비책 (Cycles Fallback)

기본 블렌더 뷰포트 렌더링 연산자(`bpy.ops.render.opengl`)는 Cycles 렌더 뷰포트의 비동기 드로우 루프 특성상Progressive 렌더링을 잡아내지 못하고 투명한 알파나 빈 검은색 화면을 캡처하는 제약이 있습니다.

이를 해결하고 즉각적인 캡처를 보장하기 위해 애드온은 다음과 같이 자동 대응합니다:
* **Cycles 렌더 모드 자동 감지**: 활성 3D 뷰포트가 `Rendered(렌더)` 모드이면서 엔진이 `Cycles`로 설정되어 있다면, 스크린샷을 찍는 0.1초의 순간에만 임시로 Eevee 엔진으로 전환하여 깨끗한 화면을 캡처한 뒤 다시 Cycles 모드로 즉시 복구합니다.
* *참고*: Solid(솔리드), Material Preview(재질 미리보기), Wireframe(와이어프레임) 모드에서는 현재 활성화된 렌더 엔진에 관계없이 즉시 안정적으로 화면을 캡처합니다.

---

## 🛠️ 패널 인터페이스 개요 (Panel Interface)

3D Viewport > Sidebar (N-패널) > **K-Quick Tools** 탭의 **Viewport Render** 패널에 위치해 있습니다.

```
┌──────────────────────────────────────────┐
│ ▼ 📺 Viewport Render                     │
├──────────────────────────────────────────┤
│ [ Show Render Guide ]                    │
│                                          │
│ ┌─ Render Options ───────────────────┐   │
│ │ [x] Hide Overlays on Render        │   │
│ │ [ ] Transparent BG (PNG)           │   │
│ │   Background Color [🎨 Pick]       │   │
│ └────────────────────────────────────┘   │
│                                          │
│ Folder: [ Rendering        ] ↪           │
│                                          │
│ ┌────────────────────────────────────┐   │
│ │     [ 📷 Rendering ]               │   │
│ └────────────────────────────────────┘   │
└──────────────────────────────────────────┘
```

* **Show / Hide Render Guide**: GPU 셰이더로 그려지는 종횡비 가이드 라인과 외곽 마스크를 켜고 끕니다.
* **Hide Overlays on Render**: 체크 시 오버레이들을 렌더링 중에만 자동으로 숨깁니다.
* **Transparent BG (PNG)**: 프로젝트 설정 변경 없이 즉석에서 알파 채널을 가진 투명 배경 PNG 이미지를 뽑아냅니다.
* **Background Color**: 투명 배경이 꺼져 있을 때 렌더링 배경색을 직접 지정합니다.
* **Folder**: 이미지가 저장될 디렉토리 이름입니다 (블렌더 `.blend` 파일이 위치한 폴더의 하위 경로로 생성되며 기본값은 `Rendering` 입니다).
* **열기 버튼 (↪)**: 지정된 폴더가 없으면 자동 생성하고 운영체제 파일 탐색기로 엽니다.

---

## 🚀 설치 방법

1. 저장소를 `.zip` 파일로 다운로드합니다.
2. 블렌더를 실행하고 `Edit > Preferences > Addons`로 이동합니다.
3. 우측 상단의 `Install...` 버튼을 누르고 다운로드한 `.zip` 파일을 선택합니다.
4. 검색창에 "Viewport Render & Preview"를 입력하고 체크박스를 켜서 애드온을 활성화합니다.

---

## 📖 사용 순서

1. 진행 중인 `.blend` 파일을 먼저 저장합니다 (렌더 이미지가 이 상대 경로에 생성됩니다).
2. 뷰포트에서 캡처의 주인공이 될 오브젝트를 클릭하여 선택(Select)합니다.
3. 3D 뷰포트 오른편 N패널에서 **K-Quick Tools** 탭을 클릭합니다.
4. 투명 배경 여부 및 오버레이 자동 숨김 옵션을 구성합니다.
5. 큰 **Rendering** 버튼을 누릅니다.
6. 이미지가 즉시 저장됩니다: `<blend_파일_디렉토리>/Rendering/오브젝트이름_YYYYMMDD_HHMMSS.png`
7. 폴더 바로가기 버튼(↪)을 눌러 결과물을 바로 확인합니다!

---

## 📁 파일 구조

* `__init__.py`: 애드온 메타데이터 정의, 등록(Register) 및 모듈 리로딩을 제어합니다.
* `viewport_render_preview.py`: GPU 가이드 드로잉, 렌더링 캡처용 임시 엔진 스위처, 투명 배경 스위처 및 UI 구성을 담고 있는 메인 엔진 코드입니다.

---

## 📄 라이선스 (License)
이 애드온은 블렌더 Python API(`bpy`)를 임포트하여 통합 실행되는 블렌더의 2차 저작물로서 **GNU GPL v3.0** 라이선스 하에 배포됩니다. 자세한 내용은 프로젝트 폴더의 [LICENSE](file:///c:/Users/user/AppData/Roaming/Blender%20Foundation/Blender/5.1/scripts/addons/viewport_render_preview/LICENSE) 파일을 참고하십시오.
