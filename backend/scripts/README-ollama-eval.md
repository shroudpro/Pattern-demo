# 外接 LLM 单字分析评测脚本说明

## 用途

该脚本用于评测外接 LLM 是否满足“纹生万象”项目第一阶段单字文化分析的最低结构与质量要求。

当前默认评测对象：

- 单字：`山`
- 模型：`qwen3.6-35b-a3b`

脚本会把模型输出与项目 mock 基准进行对比，并给出：

- `pass`
- `borderline`
- `fail`

## 运行前提

请确认：

1. 根目录 `.env` 已配置 `DASHSCOPE_API_KEY`
2. DashScope 兼容接口可访问
3. 项目根目录下存在：
   - `src/lib/mock/character-analysis.json`

## 运行命令

在项目根目录执行：

```powershell
$env:PYTHONPATH='backend'
python backend/scripts/eval_character_analysis_ollama.py
```

可选参数：

```powershell
$env:PYTHONPATH='backend'
python backend/scripts/eval_character_analysis_ollama.py --character 山 --model qwen3.6-35b-a3b --base-url https://dashscope.aliyuncs.com/api/v2/apps/protocols/compatible-mode/v1
```

## 输出文件

详细结果会写入：

- `outputs/llm-evals/shan-qwen3.6-35b-a3b-eval.json`

## 判定含义

- `pass`
  - 结构完整，且满足当前第一阶段最低质量线

- `borderline`
  - JSON 结构合格，但内容质量仍有明显短板

- `fail`
  - JSON 无法解析，或缺字段，或关键列表数量不足，或字符不匹配
