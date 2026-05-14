# 字象万千静态演示前端说明

当前前端主流程已精简为 Netlify 静态演示版：

- `/create`
- `/analyze/山`
- `/analyze/月`
- `/generate/山`
- `/generate/月`
- `/editor/山`
- `/editor/月`

核心闭环：

```text
输入山/月
→ 读取前端静态文化数据
→ 展示汉字文化星图
→ 固定 4 秒生成过程
→ 展示固定成品图
→ 成品图微调与导出
```

## 当前目录重点

- `src/lib/demo/static-demo-data.ts`
  - 山、月两组静态演示数据和固定产出图路径。
- `src/app/create`
  - 单字输入与静态演示字提示入口。
- `src/app/analyze/[sessionId]`
  - 汉字文化星图页，路由参数实际为 `山` 或 `月`。
- `src/app/generate/[sessionId]`
  - 固定 4 秒生成流程和静态成品图展示页。
- `src/app/editor/[projectId]`
  - Fabric.js 静态成品图微调与 PNG 导出页，路由参数实际为 `山` 或 `月`。

## 固定演示素材

```text
山 -> /img/山.png
月 -> /img/月.png
```

## 运行

```powershell
npm run dev
```

## 静态构建

```powershell
npm run typecheck
npm run build
```

构建后静态产物输出到：

```text
out/
```
