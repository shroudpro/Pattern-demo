# 纹生万象重构骨架 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用激进重构方式删除旧正式产品链路，并建立三阶段新产品的前后端骨架、类型和文档。

**Architecture:** 前端正式入口切换到 `create / analyze / generate / editor` 四个页面；后端围绕 `analysis session / image generation job / design project` 建立新的 schema、service 和 route。旧正式页面、旧首页与旧主流程组件直接删除，不再保留 legacy 兼容层。

**Tech Stack:** Next.js 15、TypeScript、Tailwind、FastAPI、SQLite、SQLAlchemy、Pydantic、Fabric.js、Framer Motion

---

## 文件结构

- 删除：`src/app/entry/[id]/page.tsx`
- 删除：`src/app/workbench/[id]/page.tsx`
- 删除：`src/app/scene/[id]/page.tsx`
- 删除：`src/app/export/[id]/page.tsx`
- 删除：`src/app/api/render-plan/route.ts`
- 删除：旧正式主流程专属组件与旧首页入口组件
- 新增：`src/app/create/page.tsx`
- 新增：`src/app/analyze/[sessionId]/page.tsx`
- 新增：`src/app/generate/[sessionId]/page.tsx`
- 新增：`src/app/editor/[projectId]/page.tsx`
- 新增：`src/features/create/*`
- 新增：`src/features/analyze/*`
- 新增：`src/features/generate/*`
- 新增：`src/features/editor/*`
- 新增：`src/lib/constants/characters.ts`
- 新增：`src/types/analysis.ts`
- 新增：`src/types/generation.ts`
- 新增：`src/types/project.ts`
- 新增：`backend/app/schema/analysis.py`
- 新增：`backend/app/schema/project.py`
- 新增：`backend/app/service/character_validation_service.py`
- 新增：`backend/app/service/character_analysis_service.py`
- 新增：`backend/app/service/prompt_composer_service.py`
- 新增：`backend/app/api/routes/analysis.py`
- 新增：`backend/app/api/routes/project.py`
- 修改：`backend/app/schema/content.py`
- 修改：`backend/app/service/image_generation_service.py`
- 修改：`backend/app/model/records.py`
- 修改：`backend/app/repository/records.py`
- 修改：`backend/app/main.py`
- 修改：`src/app/page.tsx`
- 修改：`src/README.md`
- 修改：`backend/README.md`

### Task 1: 为新骨架写最小后端测试

**Files:**
- Create: `backend/tests/test_character_services.py`
- Create: `backend/tests/test_new_api_skeleton.py`

- [ ] **Step 1: Write the failing character validation test**

```python
from app.service.character_validation_service import validate_character


def test_validate_character_accepts_whitelist_character():
    result = validate_character("山")
    assert result.validated is True
    assert result.character == "山"


def test_validate_character_rejects_non_whitelist_character():
    result = validate_character("火")
    assert result.validated is False
    assert "白名单" in result.message
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest backend/tests/test_character_services.py -q`
Expected: FAIL with `ModuleNotFoundError` or missing function error

- [ ] **Step 3: Write the failing prompt composer test**

```python
from app.service.prompt_composer_service import compose_prompt


def test_compose_prompt_maps_poster_size():
    analysis = {
        "character": "山",
        "summary": "山象征高峻、沉稳、层峦与时间感。",
        "designKeywords": ["layered", "stone texture", "oriental"]
    }
    result = compose_prompt(
        character="山",
        analysis=analysis,
        style_preset="traditional",
        scene_preset="poster",
    )
    assert result.width == 1024
    assert result.height == 1536
    assert result.scenePreset == "poster"
```

- [ ] **Step 4: Run test to verify it fails**

Run: `python -m pytest backend/tests/test_character_services.py -q`
Expected: FAIL with missing module or missing function error

- [ ] **Step 5: Write the failing API skeleton test**

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_analysis_session_returns_expected_shape():
    response = client.post("/api/v1/analysis-sessions", json={"character": "山"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["character"] == "山"
    assert "shuowenOriginal" in payload["analysis"]


def test_get_project_missing_returns_404():
    response = client.get("/api/v1/projects/999999")
    assert response.status_code == 404
```

- [ ] **Step 6: Run test to verify it fails**

Run: `python -m pytest backend/tests/test_new_api_skeleton.py -q`
Expected: FAIL because routes do not exist

### Task 2: 实现后端骨架与数据模型

**Files:**
- Create: `backend/app/schema/analysis.py`
- Create: `backend/app/schema/project.py`
- Create: `backend/app/service/character_validation_service.py`
- Create: `backend/app/service/character_analysis_service.py`
- Create: `backend/app/service/prompt_composer_service.py`
- Create: `backend/app/api/routes/analysis.py`
- Create: `backend/app/api/routes/project.py`
- Modify: `backend/app/model/records.py`
- Modify: `backend/app/repository/records.py`
- Modify: `backend/app/schema/content.py`
- Modify: `backend/app/service/image_generation_service.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Implement minimal schema and service code**

```python
VALID_CHARACTERS = ("山", "月", "云", "风", "花", "莲", "鹤", "凤", "龙", "雪", "水", "竹", "梅", "松", "舟", "灯", "雨", "泉", "柳", "石", "茶", "酒", "霞", "雁", "桥", "琴", "镜", "玉", "楼", "帆")
```

```python
def validate_character(character: str) -> CharacterValidationResult:
    normalized = character.strip()
    if len(normalized) != 1:
        return CharacterValidationResult(character=normalized, validated=False, message="请输入 1 个白名单汉字。")
    if normalized not in VALID_CHARACTERS:
        return CharacterValidationResult(character=normalized, validated=False, message="当前仅支持白名单中的 30 个传统文化单字。")
    return CharacterValidationResult(character=normalized, validated=True, message="ok")
```

```python
def compose_prompt(character: str, analysis: dict, style_preset: str, scene_preset: str) -> PromptComposeResult:
    width, height = (1024, 1536) if scene_preset == "poster" else (1024, 1024)
    positive = f"{character} themed oriental texture background, {style_preset}, {', '.join(analysis.get('designKeywords', []))}"
    negative = "finished poster, finished package, typography, product mockup, readable text, logo"
    return PromptComposeResult(
        positivePrompt=positive,
        negativePrompt=negative,
        width=width,
        height=height,
        stylePreset=style_preset,
        scenePreset=scene_preset,
    )
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `python -m pytest backend/tests/test_character_services.py backend/tests/test_new_api_skeleton.py -q`
Expected: PASS

### Task 3: 删除旧正式前端主流程并建立新页面骨架

**Files:**
- Delete: `src/app/entry/[id]/page.tsx`
- Delete: `src/app/workbench/[id]/page.tsx`
- Delete: `src/app/scene/[id]/page.tsx`
- Delete: `src/app/export/[id]/page.tsx`
- Delete: `src/app/api/render-plan/route.ts`
- Modify: `src/app/page.tsx`
- Create: `src/app/create/page.tsx`
- Create: `src/app/analyze/[sessionId]/page.tsx`
- Create: `src/app/generate/[sessionId]/page.tsx`
- Create: `src/app/editor/[projectId]/page.tsx`
- Create: `src/types/analysis.ts`
- Create: `src/types/generation.ts`
- Create: `src/types/project.ts`
- Create: `src/lib/constants/characters.ts`

- [ ] **Step 1: Write a failing front-end build check expectation**

Run: `npm run build`
Expected: FAIL because deleted routes are still referenced and new routes do not exist

- [ ] **Step 2: Implement minimal page skeletons and shared types**

```tsx
export default function CreatePage() {
  return <main className="page-shell">create</main>;
}
```

```tsx
export default function AnalyzePage() {
  return <main className="page-shell">analyze</main>;
}
```

```tsx
export default function GeneratePage() {
  return <main className="page-shell">generate</main>;
}
```

```tsx
export default function EditorPage() {
  return <main className="page-shell">editor</main>;
}
```

- [ ] **Step 3: Run build to verify it passes**

Run: `npm run build`
Expected: PASS

### Task 4: 清理旧组件并补最小文档

**Files:**
- Delete: 仅服务旧正式主流程的组件、类型与脚本
- Modify: `src/README.md`
- Modify: `backend/README.md`
- Create: `docs/restructure-file-inventory.md`

- [ ] **Step 1: Remove dead files imported only by deleted routes**

Run: `rg "workbench|render-plan|EntryWall|SceneLayout|ExportCard|EntrySummary" src backend`
Expected: identify dead references to remove or rewrite

- [ ] **Step 2: Write minimal README updates**

```md
- 前端正式流程已切换到 `/create -> /analyze -> /generate -> /editor`
- 后端正式接口已切换到 `analysis-sessions / image-generation-jobs / projects`
```

- [ ] **Step 3: Run final verification**

Run: `python -m pytest backend/tests/test_character_services.py backend/tests/test_new_api_skeleton.py -q`
Expected: PASS

Run: `npm run build`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add docs src backend
git commit -m "refactor: replace legacy mvp flow with three-stage product skeleton"
```
