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
- **页面 2 · 交换记录列表**（`/list`）：`n-data-table` 展示全部记录，包含书名、对方昵称、寄出/收到日期、状态、备注列（内容过长自动省略，悬浮显示完整内容），状态列用 `n-tag` 区分「已完成 / 进行中」，支持查看、编辑、删除；列表页顶部提供搜索框与状态下拉筛选：在搜索框输入关键词（书名或对方昵称）后按回车自动筛选，点击搜索框右侧清除按钮或手动清空内容后自动恢复完整列表；状态下拉可选「全部状态 / 已完成 / 进行中」，切换后立即刷新表格；列表底部提供 `n-pagination` 分页组件，支持翻页与切换每页条数（10 / 20 / 50），翻页时携带 `page` 与 `page_size` 参数重新拉取数据，搜索或筛选变更时自动回到第一页
- **页面 3 · 交换记录详情**（`/detail/:id`）：`n-descriptions` 描述列表只读展示单条记录，字段包括书名、对方昵称、寄出日期、收到日期、完成状态（带 `n-tag` 状态标签）
- **页面 4 · 新增/编辑交换记录**（`/new`、`/edit/:id`）：`n-form` 表单，字段包括书名、对方昵称、寄出日期、收到日期、是否完成、备注说明（多行文本，选填，最长 500 字）
- **页面 5 · 通讯录列表**（`/contacts`）：`n-data-table` 展示全部交换对象，字段包括昵称、联系方式、备注说明，支持编辑、删除；列表底部提供 `n-pagination` 分页组件，支持翻页与切换每页条数（10 / 20 / 50），翻页时携带 `page` 与 `page_size` 参数重新拉取数据
- **页面 6 · 新增/编辑联系人**（`/contacts/new`、`/contacts/edit/:id`）：`n-form` 表单，字段包括昵称、联系方式、备注说明

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
| DELETE | `/api/exchanges/{id}` | 删除 |

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
