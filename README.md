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
- **页面 2 · 交换记录列表**（`/list`）：`n-data-table` 展示全部记录，包含书名、对方昵称、寄出/收到日期、状态、备注列（内容过长自动省略，悬浮显示完整内容），状态列用 `n-tag` 区分「已完成 / 进行中」，支持编辑、删除
- **页面 3 · 新增/编辑交换记录**（`/new`、`/edit/:id`）：`n-form` 表单，字段包括书名、对方昵称、寄出日期、收到日期、是否完成、备注说明（多行文本，选填，最长 500 字）
- **页面 4 · 通讯录列表**（`/contacts`）：`n-data-table` 展示全部交换对象，字段包括昵称、联系方式、备注说明，支持编辑、删除
- **页面 5 · 新增/编辑联系人**（`/contacts/new`、`/contacts/edit/:id`）：`n-form` 表单，字段包括昵称、联系方式、备注说明

> 顶部导航栏可在各页面之间自由切换，「数据概览」为默认首页。

## API 概览

### 交换记录

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/statistics` | 统计概览（总记录数、已完成数、进行中数） |
| GET | `/api/exchanges` | 列表 |
| GET | `/api/exchanges/{id}` | 详情 |
| POST | `/api/exchanges` | 新增 |
| PUT | `/api/exchanges/{id}` | 更新 |
| DELETE | `/api/exchanges/{id}` | 删除 |

### 通讯录

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/contacts` | 列表 |
| GET | `/api/contacts/{id}` | 详情 |
| POST | `/api/contacts` | 新增 |
| PUT | `/api/contacts/{id}` | 更新 |
| DELETE | `/api/contacts/{id}` | 删除 |

## 依赖说明

所有依赖均在项目目录内安装（Python venv + 前端 `node_modules`），无需全局 pnpm/yarn。
