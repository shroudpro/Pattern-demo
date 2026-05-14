# 纹生万象后端重构说明

当前后端正式接口已经切换到三类核心资源：

- `analysis session`
- `image generation job`
- `design project`

旧的 `render-plan`、旧 explanation 增强接口、旧配置接口已经退出正式产品骨架。

## 当前正式接口

- `GET /health`
- `POST /api/v1/analysis-sessions`
- `GET /api/v1/analysis-sessions/{session_id}`
- `POST /api/v1/image-generation-jobs`
- `GET /api/v1/image-generation-jobs/{job_id}`
- `POST /api/v1/projects`
- `GET /api/v1/projects/{project_id}`

## 当前服务分层

- `api`
  - 路由定义与响应返回
- `service`
  - `character_validation_service.py`
  - `character_analysis_service.py`
  - `prompt_composer_service.py`
  - `image_generation_service.py`
- `repository`
  - SQLite 记录读写
- `schema`
  - `analysis.py`
  - `generation.py`
  - `project.py`
- `model`
  - `AnalysisSession`
  - `ImageJob`
  - `DesignProject`

## 当前实现状态

### 阶段一

- 已完成 30 个单字白名单校验
- 已完成分析会话类型与 API 骨架
- 分析内容当前为稳定占位数据
- 后续再接外部文本模型或知识库

### 阶段二

- 已完成 Prompt 组合服务骨架
- 已将图片任务流切换到新任务载荷
- 已保留异步状态推进与结果落盘

### 阶段三

- 已完成 `project` 模型与 API 骨架
- 供前端编辑器页读取背景纹理与画布尺寸

## 环境变量

```powershell
$env:WENSHENG_IMAGE_PROVIDER='mock'
$env:WENSHENG_IMAGE_API_BASE_URL='http://127.0.0.1:8001'
$env:WENSHENG_IMAGE_MODEL_NAME='gpt-image-1'
$env:WENSHENG_IMAGE_TIMEOUT_SECONDS='120'
$env:WENSHENG_IMAGE_API_KEY='your-key'
```

## 启动

```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## 测试

```powershell
$env:PYTHONPATH='backend'
python -m unittest backend.tests.test_character_services backend.tests.test_new_api_skeleton
```
