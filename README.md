# 杂志交换记录 MVP

前后端分离的全栈 MVP：管理杂志/书籍交换记录（书名、对方昵称、寄出/收到日期、完成状态、备注说明）。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + TypeScript + Naive UI，端口 **5101** |
| 后端 | FastAPI + SQLAlchemy + SQLite（`backend/data/zine.db`），端口 **5000** |

## 目录结构

```
├── backend/          # FastAPI 后端
├── frontend/         # Vue 3 前端
└── README.md
```

## 启动方式

### 1. 后端（一条命令）

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
uvicorn main:app --reload --port 5000
```

首次启动会自动创建 SQLite 数据库并写入 **5 条** seed 数据。

API 文档：http://127.0.0.1:5000/docs

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器访问：http://localhost:5101

> 前端通过 Vite 代理将 `/api` 请求转发到后端 `5000` 端口，请先启动后端。

## 功能

- **页面 1 · 数据概览**（首页 `/`）：三张卡片展示「总记录数」「已完成数」「进行中数」三项核心指标，已完成记录附带百分比统计
- **页面 2 · 交换记录列表**（`/list`）：列表页顶部增加轻量统计条，用 `n-tag` 展示「总记录数」「已完成数」「进行中数」三项数字，与数据概览页核心指标保持一致；`n-data-table` 展示全部记录，表格首列为多选列（支持全选/取消全选），包含书名、对方昵称、寄出/收到日期、状态、备注列（内容过长自动省略，悬浮显示完整内容），状态列用 `n-tag` 区分「已完成 / 进行中」，支持查看、编辑、单条删除；选中任意行后顶部显示红色「批量删除 (N)」按钮，点击弹出确认对话框，确认后一次性删除所有选中记录，删除成功后自动刷新列表、清空选中项并更新统计数字；列表页顶部提供搜索框与状态下拉筛选：在搜索框输入关键词（书名或对方昵称）后按回车自动筛选，点击搜索框右侧清除按钮或手动清空内容后自动恢复完整列表；状态下拉可选「全部状态 / 已完成 / 进行中」，切换后立即刷新表格；列表底部提供 `n-pagination` 分页组件，支持翻页与切换每页条数（10 / 20 / 50），翻页时携带 `page` 与 `page_size` 参数重新拉取数据，搜索或筛选变更时自动回到第一页；删除记录后统计数字自动同步更新，从新增/编辑页返回列表时统计数字自动重新拉取
- **页面 3 · 交换记录详情**（`/detail/:id`）：`n-descriptions` 描述列表只读展示单条记录，字段包括书名、对方昵称、寄出日期、收到日期、完成状态（带 `n-tag` 状态标签）
- **页面 4 · 新增/编辑交换记录**（`/new`、`/edit/:id`）：`n-form` 表单，字段包括书名、对方昵称、寄出日期、收到日期、是否完成、备注说明（多行文本，选填，最长 500 字）。其中「收到日期」与「是否完成」存在如下联动规则：
  - 用户填写「收到日期」时，若「是否完成」当前为关闭，则自动将其开关切换为开启（标记为自动完成）
  - 用户清空「收到日期」时，若此前「是否完成」是由填写日期自动触发开启的，则恢复为关闭；若用户曾手动操作过「是否完成」开关，则清空日期不再自动回退状态
  - 用户手动点击「是否完成」开关后，日期与完成状态的联动关系解除，后续日期变更不再自动驱动该开关
- **页面 5 · 通讯录列表**（`/contacts`）：`n-data-table` 展示全部交换对象，字段包括昵称、联系方式、备注说明，支持查看、编辑、删除；列表底部提供 `n-pagination` 分页组件，支持翻页与切换每页条数（10 / 20 / 50），翻页时携带 `page` 与 `page_size` 参数重新拉取数据
- **页面 6 · 联系人详情**（`/contacts/detail/:id`）：`n-descriptions` 描述列表只读展示单条联系人，字段包括昵称、联系方式、备注说明
- **页面 7 · 新增/编辑联系人**（`/contacts/new`、`/contacts/edit/:id`）：`n-form` 表单，字段包括昵称、联系方式、备注说明

> 顶部导航栏可在各页面之间自由切换，「数据概览」为默认首页。

## API 概览

### 交换记录

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/statistics` | 统计概览（总记录数、已完成数、进行中数） |
| GET | `/api/exchanges` | 分页列表，返回 `{ items: [...], total: number }`；支持可选查询参数：`keyword`（关键词，模糊匹配书名或对方昵称）、`status`（状态筛选，`completed` 已完成 / `in_progress` 进行中）、`page`（页码，默认 1，≥1）、`page_size`（每页条数，默认 10，1~100） |
| GET | `/api/exchanges/export` | 导出全部交换记录为 CSV 文件（带表头） |
| GET | `/api/exchanges/{id}` | 详情 |
| POST | `/api/exchanges` | 新增 |
| PUT | `/api/exchanges/{id}` | 更新 |
| DELETE | `/api/exchanges/{id}` | 删除单条记录 |
| POST | `/api/exchanges/batch-delete` | 批量删除，请求体：`{ ids: number[] }`，返回 204 |

### 通讯录

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/contacts` | 分页列表，返回 `{ items: [...], total: number }`；支持可选查询参数：`page`（页码，默认 1，≥1）、`page_size`（每页条数，默认 10，1~100） |
| GET | `/api/contacts/{id}` | 详情 |
| POST | `/api/contacts` | 新增 |
| PUT | `/api/contacts/{id}` | 更新 |
| DELETE | `/api/contacts/{id}` | 删除 |

## 依赖说明

所有依赖均在项目目录内安装（Python venv + 前端 `node_modules`），无需全局 pnpm/yarn。

## 持续集成（CI）

本项目通过 GitHub Actions 实现自动化持续集成，工作流配置位于 [.github/workflows/ci.yml](.github/workflows/ci.yml)。

### 触发条件

- **推送触发**：向 `main` 或 `master` 分支推送代码时自动执行
- **PR 触发**：向 `main` 或 `master` 分支提交 Pull Request 时自动执行

### CI 工作流说明

CI 包含两个并行任务：`backend`（后端）和 `frontend`（前端），均在 Ubuntu 最新版环境下运行。

#### 后端任务（Backend - Install Dependencies & Test）

| 步骤 | 说明 |
|------|------|
| Checkout code | 检出仓库代码（使用 `actions/checkout@v4`） |
| Set up Python | 配置 Python 3.11 环境，启用 pip 缓存（使用 `actions/setup-python@v5`） |
| Install dependencies | 升级 pip 并安装 `backend/requirements.txt` 中的全部依赖 |
| Run pytest | 在 `backend/` 目录下执行 `pytest -v` 运行全部测试用例 |

#### 前端任务（Frontend - Install Dependencies & Type Check）

| 步骤 | 说明 |
|------|------|
| Checkout code | 检出仓库代码（使用 `actions/checkout@v4`） |
| Set up Node.js | 配置 Node.js 20 环境，启用 npm 缓存（使用 `actions/setup-node@v4`） |
| Install dependencies | 执行 `npm ci` 按照 `package-lock.json` 锁定版本安装依赖 |
| Run TypeScript type check | 执行 `npx vue-tsc --noEmit` 进行 TypeScript 类型检查，不输出编译产物 |

### 本地复现 CI 检查

在提交代码前，可在本地手动执行以下命令复现 CI 检查，确保所有检查通过后再推送。

#### 后端：安装依赖并运行 pytest

```bash
cd backend

# 1. 创建并激活虚拟环境（如尚未创建）
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行测试（等同于 CI 中的 pytest -v）
python -m pytest -v
```

测试通过后，将输出全部用例的 `PASSED` 结果以及汇总信息。

#### 前端：安装依赖并运行 TypeScript 类型检查

```bash
cd frontend

# 1. 安装依赖（CI 使用 npm ci，本地使用 npm install 亦可）
npm ci   # 或 npm install

# 2. 执行 TypeScript 类型检查（等同于 CI 中的 vue-tsc --noEmit）
npx vue-tsc --noEmit
```

若无类型错误，命令将正常退出且无额外输出；若存在类型问题，会打印具体的错误位置和信息。

也可以直接运行完整的构建命令（包含类型检查 + Vite 打包）：

```bash
npm run build
```

### 后端：运行交换记录列表接口专项集成测试

`backend/tests/` 目录下提供了交换记录列表接口（`GET /api/exchanges`）的专项集成测试，使用独立临时 SQLite 数据库，每个测试前后自动建表与清理数据。

```bash
cd backend

# 运行 tests 目录下的全部专项集成测试
python -m pytest tests/ -v

# 仅运行交换记录列表接口测试文件
python -m pytest tests/test_exchange_list.py -v

# 运行全部后端测试（根目录下的原有测试 + tests 目录下的专项测试）
python -m pytest -v
```
