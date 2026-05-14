# 纹生万象三阶段产品重构设计

## 背景

当前项目的正式产品链路仍围绕固定词条、`buildRenderPlan()`、场景模板切换与导出卡片展开。这套 MVP 结构已经不再符合目标产品定义，也不适合作为后续生成式设计产品的主骨架。

本次重构采用激进方案：

- 旧正式路由直接下线
- 旧首页 24 词条入口直接删除
- 旧 `entry / workbench / scene / export` 页面和围绕它们的正式导航全部移除
- `buildRenderPlan()` 不再是新产品主脑
- 旧逻辑若仍需参考，只保留极少量底层通用能力，不保留旧产品语义

## 产品目标

新产品的正式主流程重构为三个阶段：

1. 阶段一 `/create`：用户输入单字并完成合法性校验
2. 阶段二 `/analyze/[sessionId]`：展示该字的文化分析结果
3. 阶段三 `/generate/[sessionId]`：根据分析结果、风格和场景组合 prompt 生成纹理图
4. 延伸工作台 `/editor/[projectId]`：加载纹理图背景并进行轻量在线编辑

虽然产品语义是三阶段，但工程上拆分为四个正式页面，便于路由状态明确、异步任务独立和编辑器持久化。

## 范围

本轮只交付“骨架版”，目标是替换正式结构，而不是一次做完所有业务能力。

本轮包含：

- 新目录结构
- 新正式路由骨架
- 旧路由删除
- 字白名单与校验逻辑骨架
- 分析服务类型与 API 骨架
- Prompt 组合服务类型与 API 骨架
- Fabric 编辑器页面骨架
- 项目重构说明文档
- 删除 / 保留 / 迁移文件清单

本轮不包含：

- 外部文本模型真实接入
- 阶段一完整高质量文化文本生产
- 阶段二真实图片生成参数编排完成版
- 编辑器完整持久化和导出实现
- 完整测试覆盖

## 保留能力

以下能力继续复用：

- Next.js + TypeScript + Tailwind 前端底座
- FastAPI + SQLite 后端底座
- provider 抽象层
- 图片异步任务流
- 图片结果落盘
- 前后端通信方式
- 环境变量配置模式
- 可复用的数据访问层
- 导出稳定化经验

## 删除策略

以下内容直接从正式产品中删除：

- 首页 24 词条入口
- `/entry/[id]`
- `/workbench/[id]`
- `/scene/[id]`
- `/export/[id]`
- `buildRenderPlan()` 在正式主流程中的使用
- `RenderPlanExplainPanel`
- 围绕规则解释、模板切换、规则预览的正式展示链路

删除原则：

- 如果文件只服务于旧正式主流程，直接删除
- 如果文件是底层通用工具，但命名带有旧产品语义，可在本轮先保留，后续再净化
- 如果文件同时被新旧能力依赖，优先保留并在文档中标记“待二轮整理”

## 新数据模型

新正式主数据流围绕三类实体：

### AnalysisSession

负责阶段一分析结果的生产与承载。

字段：

- `id`
- `character`
- `validated`
- `status`
- `analysis`
- `createdAt`
- `updatedAt`

### ImageGenerationJob

复用现有 `ImageJob` 底层表和异步处理能力，但任务 payload 语义改为新主流程。

字段要求：

- `id`
- `analysisSessionId`
- `character`
- `stylePreset`
- `scenePreset`
- `positivePrompt`
- `negativePrompt`
- `width`
- `height`
- `status`
- `outputUrl`
- `localPath`
- `errorMessage`
- `createdAt`

### DesignProject

负责编辑器阶段。

字段：

- `id`
- `character`
- `analysisSessionId`
- `imageJobId`
- `backgroundImageUrl`
- `canvasWidth`
- `canvasHeight`
- `elements`
- `createdAt`
- `updatedAt`

## 后端设计

### 服务层

新增：

- `CharacterValidationService`
- `CharacterAnalysisService`
- `PromptComposerService`
- `ProjectService`（本轮先做骨架）

保留并改造：

- `ImageGenerationService`

边界要求：

- `CharacterValidationService` 只负责白名单判断和格式校验
- `CharacterAnalysisService` 只负责生成阶段一正式结构，不与旧 explanation 增强逻辑复用
- `PromptComposerService` 只负责根据分析结果和预设拼装 prompt，不直接执行图片生成
- `ImageGenerationService` 只负责任务创建、状态流推进、provider 调用与结果落盘

### API

新增正式接口：

- `POST /api/v1/analysis-sessions`
- `GET /api/v1/analysis-sessions/{session_id}`
- `POST /api/v1/image-generation-jobs`
- `GET /api/v1/image-generation-jobs/{job_id}`
- `POST /api/v1/projects`
- `GET /api/v1/projects/{project_id}`

本轮只提供接口骨架与返回类型，不接真实模型。

### 数据来源策略

阶段一文本分析先统一走服务接口，服务内部暂时返回稳定占位数据或 mock 结果。

保留后续扩展点：

- 外部文本模型 provider
- 知识库检索
- 本地静态知识源

## 前端设计

### 路由

正式路由：

- `/create`
- `/analyze/[sessionId]`
- `/generate/[sessionId]`
- `/editor/[projectId]`

`/` 直接收口到 `/create`。

### 页面职责

`/create`

- 输入单字
- 触发校验与分析会话创建
- 非白名单给出明确错误

`/analyze/[sessionId]`

- 分段展示分析结构
- 使用 Framer Motion 做固定东方风格动画
- 动画只承担节奏，不承载业务状态

`/generate/[sessionId]`

- 展示阶段一摘要
- 选择 `traditional | modern`
- 选择 `poster | package`
- 创建图片生成任务
- 呈现 `idle / submitting / queued / generating / succeeded / failed`

`/editor/[projectId]`

- Fabric.js 编辑器骨架
- 加载背景纹理图
- 保留文本、图片、删除、导出按钮位

## 目录结构

前端按阶段重组：

- `src/app/create`
- `src/app/analyze/[sessionId]`
- `src/app/generate/[sessionId]`
- `src/app/editor/[projectId]`
- `src/features/create`
- `src/features/analyze`
- `src/features/generate`
- `src/features/editor`
- `src/lib/api`
- `src/lib/constants`
- `src/types`

后端新增：

- `backend/app/api/routes/analysis.py`
- `backend/app/api/routes/project.py`
- `backend/app/schema/analysis.py`
- `backend/app/schema/project.py`
- `backend/app/service/character_validation_service.py`
- `backend/app/service/character_analysis_service.py`
- `backend/app/service/prompt_composer_service.py`

## 错误处理

- 单字输入为空、长度不合法、非白名单，返回明确中文错误
- 会话不存在、任务不存在、项目不存在，返回 `404`
- 图片任务失败时返回 `failed` 与 `errorMessage`
- 所有响应先以骨架稳定为目标，不暴露未实现细节

## 测试策略

本轮以最小 TDD 覆盖核心骨架：

- 字白名单校验
- Prompt 组合尺寸映射
- 新 API 路由返回结构

由于是激进重构，测试只覆盖新骨架，不为旧主流程继续维护测试。

## 风险与约束

- 直接删除旧正式路由会导致当前已有页面不可访问，这是预期行为
- 本轮 API 为占位接口，前端只能完成骨架联调，不代表最终业务质量
- 图片任务流虽然复用，但任务 payload 从旧 `textureType` 切到新 prompt 组合后，需要下一轮补全兼容处理
- Fabric 编辑器本轮只做容器骨架，不承诺完成实际编辑能力

## 结论

本次重构的核心不是“在旧 MVP 上再包一层”，而是明确建立新的正式产品骨架。旧产品语义整体退出，保留的只有可复用底层能力。后续开发以 `analysis session -> image generation job -> design project` 作为唯一主线。
