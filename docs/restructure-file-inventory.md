# 重构文件清单

## 删除

### 前端旧正式路由

- `src/app/entry/[id]/page.tsx`
- `src/app/workbench/[id]/page.tsx`
- `src/app/scene/[id]/page.tsx`
- `src/app/export/[id]/page.tsx`
- `src/app/debug/gallery/page.tsx`
- `src/app/debug/image-generation/page.tsx`
- `src/app/api/render-plan/route.ts`

### 前端旧产品组件

- `src/components/home/EntryWall.tsx`
- `src/components/entry/EntrySummary.tsx`
- `src/components/workbench/WorkbenchLayout.tsx`
- `src/components/workbench/WorkbenchCompareView.tsx`
- `src/components/scene/SceneLayout.tsx`
- `src/components/export/ExportButton.tsx`
- `src/components/export/ExportCard.tsx`
- `src/components/export/ExportSnapshotRoot.tsx`
- `src/components/insights/ExplanationDebugPanel.tsx`
- `src/components/insights/RenderPlanExplainPanel.tsx`
- `src/components/debug/ImageGenerationPanel.tsx`
- `src/components/gallery/GalleryFilters.tsx`
- `src/components/shared/PreviewCanvas.tsx`

### 前端旧规则与数据层

- `src/lib/data/runtime.ts`
- `src/lib/engine/*`
- `src/lib/config/loaders.ts`
- `src/lib/config/validators.ts`
- `src/lib/utils/query-state.ts`
- `src/lib/utils/canvas-layout.ts`
- `src/types/content.ts`
- `scripts/check-config.ts`
- `scripts/render-plan-cli.ts`
- `scripts/smoke-all-entries.ts`

### 后端旧正式链路

- `backend/app/api/routes/content.py`
- `backend/app/api/routes/llm.py`
- `backend/app/api/routes/render_plan.py`
- `backend/app/service/config_service.py`
- `backend/app/service/export_service.py`
- `backend/app/service/render_plan_service.py`
- `backend/app/service/text_enhancement_service.py`
- `backend/app/schema/content.py`

### 后端旧测试

- `backend/tests/test_api.py`
- `backend/tests/test_render_plan_service.py`
- `backend/tests/test_image_flow.py`
- `backend/tests/test_smoke.py`

## 保留

- `backend/app/providers/*`
- `backend/app/core/*`
- `backend/app/repository/records.py`
- `backend/app/model/records.py`
- `backend/app/service/image_generation_service.py`
- `backend/app/service/texture_prompt_service.py`
- `public/generated/textures`
- `public/assets/*`

## 新增

### 前端

- `src/app/create/page.tsx`
- `src/app/analyze/[sessionId]/page.tsx`
- `src/app/generate/[sessionId]/page.tsx`
- `src/app/editor/[projectId]/page.tsx`
- `src/features/create/CreateEntryForm.tsx`
- `src/features/generate/GenerateWorkbench.tsx`
- `src/lib/api/client.ts`
- `src/lib/constants/characters.ts`
- `src/types/analysis.ts`
- `src/types/generation.ts`
- `src/types/project.ts`

### 后端

- `backend/app/api/routes/analysis.py`
- `backend/app/api/routes/project.py`
- `backend/app/schema/analysis.py`
- `backend/app/schema/generation.py`
- `backend/app/schema/project.py`
- `backend/app/service/character_validation_service.py`
- `backend/app/service/character_analysis_service.py`
- `backend/app/service/prompt_composer_service.py`
- `backend/tests/test_character_services.py`
- `backend/tests/test_new_api_skeleton.py`
