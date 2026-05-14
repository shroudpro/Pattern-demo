# 项目环境配置保姆级教程

这份文档用于指导同事在一台全新的电脑上，从 GitHub 拉取并运行当前项目。

适用项目目录：`Patterns`

项目结构说明：

- 前端：`Next.js 15 + React 19`
- 后端：`FastAPI`
- 前端默认地址：`http://localhost:3000`
- 后端默认地址：`http://127.0.0.1:8000`

如果你严格按本文操作，最终应该可以做到两件事：

1. 前端页面能正常打开
2. 后端健康检查接口能正常返回

---

## 1. 先准备好这些软件

请先在你的电脑上安装以下工具。

### 1.1 Git

用途：从 GitHub 拉取项目代码。

下载地址：

- `https://git-scm.com/downloads`

安装完成后，在终端执行：

```powershell
git --version
```

如果能看到版本号，说明安装成功。

### 1.2 Node.js

用途：运行前端项目。

建议版本：

- `Node.js 20.x` 或更高版本

下载地址：

- `https://nodejs.org/`

安装完成后，在终端执行：

```powershell
node -v
npm -v
```

如果都能输出版本号，说明安装成功。

### 1.3 Python

用途：运行后端项目。

建议版本：

- `Python 3.10` 或更高版本

下载地址：

- `https://www.python.org/downloads/`

安装时请勾选：

- `Add Python to PATH`

安装完成后，在终端执行：

```powershell
python --version
pip --version
```

如果都能输出版本号，说明安装成功。

### 1.4 推荐编辑器

建议使用：

- `VS Code`

下载地址：

- `https://code.visualstudio.com/`

---

## 2. 从 GitHub 拉取项目

### 2.1 选择你想存放项目的目录

例如：

```powershell
cd E:\
mkdir Vibe-coding
cd Vibe-coding
```

### 2.2 克隆项目

把下面的仓库地址替换成你们真实的 GitHub 地址：

```powershell
git clone <你的 GitHub 仓库地址>
```

示例：

```powershell
git clone https://github.com/your-org/Patterns.git
```

### 2.3 进入项目目录

```powershell
cd Patterns
```

### 2.4 确认代码已经拉下来

执行：

```powershell
git status
```

如果看到类似下面的信息，说明仓库正常：

```powershell
On branch main
nothing to commit, working tree clean
```

---

## 3. 配置前端环境变量 `.env`

这个项目的 `.env` 文件不会提交到 GitHub，所以你拉代码后通常是没有这个文件的，需要手动创建。

### 3.1 在项目根目录新建 `.env`

也就是在 `Patterns` 根目录创建一个文件：

```text
.env
```

### 3.2 把下面内容复制进去

注意：

- 不要把真实密钥提交到 GitHub
- `DASHSCOPE_API_KEY` 请向项目负责人索取

```env
NEXT_PUBLIC_WENSHENG_BACKEND_BASE_URL='http://127.0.0.1:8000'
DASHSCOPE_API_KEY='请替换成你自己的密钥'
DASHSCOPE_BASE_URL='https://dashscope.aliyuncs.com/api/v2/apps/protocols/compatible-mode/v1'
DASHSCOPE_MODEL_NAME='qwen3.6-35b-a3b'
DASHSCOPE_TIMEOUT_SECONDS='60'
WENSHENG_TEXT_PROVIDER='dashscope'
```

### 3.3 特别提醒

请注意不要写成这种格式：

```env
DASHSCOPE_API_KEY ='xxx'
```

虽然某些脚本会兼容这种写法，但标准写法应该是不在 key 后面留空格：

```env
DASHSCOPE_API_KEY='xxx'
```

---

## 4. 安装前端依赖

你现在应该还在项目根目录 `Patterns` 下。

执行：

```powershell
npm install
```

等待安装完成。

### 4.1 如果安装成功，你会看到什么

通常会看到大量安装日志，这是正常的。

### 4.2 如果安装失败，先检查这几项

1. `node -v` 是否太低
2. 网络是否能访问 `npm`
3. 是否误用了公司内网代理
4. 是否没有在项目根目录执行命令

---

## 5. 创建并激活 Python 虚拟环境

后端建议使用虚拟环境，避免污染你电脑上的全局 Python 包。

### 5.1 进入项目根目录

```powershell
cd 项目根目录
```

如果你已经在 `Patterns` 下，可以跳过这一步。

### 5.2 创建虚拟环境

```powershell
python -m venv .venv
```

### 5.3 激活虚拟环境

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

激活成功后，终端前面通常会出现：

```powershell
(.venv)
```

### 5.4 如果提示脚本执行被禁止

先执行：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

然后输入：

```powershell
Y
```

再重新执行：

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 6. 安装后端依赖

### 6.1 进入后端目录

```powershell
cd backend
```

### 6.2 安装依赖

确保虚拟环境已经激活，然后执行：

```powershell
pip install -r requirements.txt
```

当前后端依赖主要包括：

- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `pydantic`
- `httpx`

### 6.3 安装完成后验证

执行：

```powershell
python -c "import fastapi, uvicorn, sqlalchemy, pydantic, httpx; print('backend dependencies ok')"
```

如果输出：

```powershell
backend dependencies ok
```

说明后端依赖安装成功。

---

## 7. 启动后端服务

后端启动前，请确认你当前所在目录是：

```text
Patterns\backend
```

然后执行：

```powershell
python -m uvicorn app.main:app --reload
```

启动成功后，终端通常会看到类似信息：

```powershell
Uvicorn running on http://127.0.0.1:8000
```

### 7.1 验证后端是否正常

不要关闭后端窗口，新开一个终端窗口执行：

```powershell
curl http://127.0.0.1:8000/health
```

如果返回：

```json
{"status":"ok"}
```

说明后端启动成功。

---

## 8. 启动前端服务

前端建议在另一个终端窗口中启动。

### 8.1 进入项目根目录

```powershell
cd 项目根目录\Patterns
```

### 8.2 启动前端

```powershell
npm run dev
```

启动成功后，终端通常会显示：

```powershell
Local: http://localhost:3000
```

### 8.3 在浏览器打开

打开：

- `http://localhost:3000`

如果页面能打开，说明前端启动成功。

---

## 9. 正确的启动顺序

为了避免前端请求后端时报错，建议每次都按这个顺序启动：

1. 打开终端 A
2. 激活 Python 虚拟环境
3. 启动后端
4. 打开终端 B
5. 进入项目根目录
6. 启动前端
7. 浏览器访问前端页面

---

## 10. 建议你直接照着敲一遍

如果你是第一次配置，可以直接按下面这一整套命令执行。

### 10.1 终端 A：后端

```powershell
cd E:\Vibe-coding\Patterns
python -m venv .venv
.\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### 10.2 终端 B：前端

```powershell
cd E:\Vibe-coding\Patterns
npm install
npm run dev
```

### 10.3 终端 C：健康检查

```powershell
curl http://127.0.0.1:8000/health
```

---

## 11. 这个项目目前的已知关键点

### 11.1 前端读取哪个后端地址

前端通过根目录 `.env` 中的这个变量访问后端：

```env
NEXT_PUBLIC_WENSHENG_BACKEND_BASE_URL='http://127.0.0.1:8000'
```

如果你的后端不是运行在 `8000` 端口，就必须同步修改这个值。

### 11.2 后端允许哪些前端地址访问

当前后端已放行：

- `http://127.0.0.1:3000`
- `http://localhost:3000`

所以前端默认跑在 `3000` 端口是可以直接联通的。

### 11.3 数据库文件

项目后端会使用 SQLite。

当前仓库里已经存在类似这种数据库文件：

```text
backend\wen-sheng-v2.sqlite3
```

如果你的同事拉到的是完整仓库，通常不需要额外安装数据库软件。

---

## 12. 常见报错与解决方法

### 12.1 报错：`npm` 不是内部或外部命令

原因：

- Node.js 没装好
- 没有重开终端

解决：

1. 重新安装 Node.js
2. 关闭终端再打开
3. 再执行 `node -v` 和 `npm -v`

### 12.2 报错：`python` 不是内部或外部命令

原因：

- Python 未加入 PATH

解决：

1. 重新安装 Python
2. 勾选 `Add Python to PATH`
3. 关闭终端再打开

### 12.3 报错：无法激活 `.venv`

原因：

- PowerShell 执行策略限制

解决：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

然后重新激活虚拟环境。

### 12.4 报错：前端页面打开了，但接口请求失败

优先检查：

1. 后端是否真的启动了
2. `http://127.0.0.1:8000/health` 能否访问
3. `.env` 里的 `NEXT_PUBLIC_WENSHENG_BACKEND_BASE_URL` 是否正确
4. 前端是否在修改 `.env` 后重启过

### 12.5 报错：图片或文本模型接口失败

优先检查：

1. `.env` 中的 `DASHSCOPE_API_KEY` 是否正确
2. API Key 是否有调用额度
3. 当前网络是否允许访问阿里云 DashScope
4. 是否把 key 写错成了带空格的格式

正确写法：

```env
DASHSCOPE_API_KEY='你的真实密钥'
```

### 12.6 报错：`ModuleNotFoundError`

原因通常是：

- 没激活虚拟环境
- 依赖没有安装完成

解决：

1. 确认终端前面有 `(.venv)`
2. 重新执行 `pip install -r requirements.txt`

---

## 13. 如何判断你已经配置成功

满足下面 4 条，基本就说明配置完成了：

1. `npm install` 能成功
2. `pip install -r requirements.txt` 能成功
3. 打开 `http://127.0.0.1:8000/health` 能返回 `{"status":"ok"}`
4. 打开 `http://localhost:3000` 能看到前端页面

---

## 14. 每天开发时的最短流程

以后如果已经配好环境，通常不需要重复安装，只需要这样启动：

### 14.1 启动后端

```powershell
cd E:\Vibe-coding\Patterns
.\.venv\Scripts\Activate.ps1
cd backend
python -m uvicorn app.main:app --reload
```

### 14.2 启动前端

```powershell
cd E:\Vibe-coding\Patterns
npm run dev
```

---

## 15. 如果你要更新代码

在项目根目录执行：

```powershell
git pull
```

如果本次更新涉及依赖变更，再执行：

```powershell
npm install
```

如果后端依赖有变化，再执行：

```powershell
cd backend
pip install -r requirements.txt
```

---

## 16. 建议发给同事的注意事项

你可以把下面这段话直接发给同事：

```text
先按《项目环境配置保姆级教程》一步一步来，不要跳步骤。
先装 Git、Node.js、Python。
然后 clone 仓库，创建根目录 .env。
再装前端依赖和后端依赖。
最后先启后端，再启前端。
如果报错，先看教程第 12 节的常见问题。
```

---

## 17. 需要项目负责人额外提供的内容

你的同事自己无法从 GitHub 获得下面这些信息，必须由项目负责人提供：

1. GitHub 仓库真实地址
2. 根目录 `.env` 的正确内容
3. `DASHSCOPE_API_KEY`
4. 是否需要额外的图片模型或文本模型权限
5. 是否有固定分支要求，比如 `main`、`develop` 或其他开发分支

---

## 18. 最后检查清单

请逐项确认：

- 已安装 Git
- 已安装 Node.js
- 已安装 Python 3.10+
- 已从 GitHub clone 项目
- 已在根目录创建 `.env`
- 已执行 `npm install`
- 已创建 `.venv`
- 已执行 `pip install -r requirements.txt`
- 后端 `http://127.0.0.1:8000/health` 可访问
- 前端 `http://localhost:3000` 可访问

如果上面全部完成，这个项目就已经能在你的电脑上运行起来了。
