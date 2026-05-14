# 纹生万象答辩演示与验证清单

## 核心演示链路

```text
山 → Analyze → Generate traditional + 16:9 → Editor → 导出 PNG
```

## 手动演示步骤

1. 打开 `/create`。
2. 输入 `山`，提交生成文化解析。
3. 在 Analyze 页确认：
   - 有字海背景。
   - 中心汉字有光场。
   - 说文解字、现代释义、意象分析、诗词关联均可读。
4. 进入 Generate 页。
5. 选择 `传统` 和 `16:9 横屏解析图`。
6. 点击 `生成文化解析图`。
7. 任务完成后进入 Editor。
8. 确认画布底图是上一步生成的最终文化阐释效果图。
9. 如需补充说明，添加少量注释层。
10. 点击 `导出 PNG`。

## 降级策略

文本模型：

- S 级精品字直接使用本地数据。
- 本地未命中字且未配置文本模型时，Create 页提示切换精品演示字。

图片模型：

- 图片任务异常时，后端自动使用本地解析图模板降级。
- `山 + 16:9` 使用 `/img/F1.png`。
- 其他 `traditional` 使用 `/img/D1.png`。
- `modern` 使用 `/img/D2.png`。
- 前端会显示本地模板降级提示，但仍允许进入 Editor。

Editor 导出：

- PNG 导出失败时显示错误提示。
- 项目图层保存不依赖导出流程，用户仍可保留当前画布状态。

## 验证命令

前端：

```powershell
E:\anaconda\envs\wen-sheng-mvp\npm.cmd run typecheck
E:\anaconda\envs\wen-sheng-mvp\npm.cmd run build
```

后端：

```powershell
cd backend
python -m unittest discover tests
```

文案扫描：

```powershell
rg "包装|海报|纹理图|通用设计|自由设计" src\app src\features -n
```

期望：无命中。

## 答辩表达重点

- 系统不是普通图片生成器。
- 汉字文化内容先结构化，再驱动视觉生成。
- Generate 阶段直接让图片 API 输出最终文化阐释效果图，Editor 在成品图上做轻量标注和导出。
- Editor 不是通用设计平台，而是解析图微调工具。
- 本地 S 级字库保证现场演示稳定。
