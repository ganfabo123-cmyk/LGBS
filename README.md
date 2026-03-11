# LangGraph Builder (LGBS)

LangGraph Builder 是一个可视化 LangGraph 项目生成平台，帮助开发者通过图形化界面快速创建和部署 LangGraph 智能体应用。

## 项目简介

LangGraph Builder (LGBS) 是一个基于 Web 的可视化工具，用于：

- **可视化设计**：通过拖拽式界面设计 LangGraph 工作流
- **自动生成代码**：根据可视化配置自动生成完整的 LangGraph 项目代码
- **模块化管理**：支持将复杂任务拆分为多个模块，每个模块包含独立的节点和工作流
- **快速测试**：为每个模块提供独立的测试入口，方便单独调试

## 技术栈

### 前端

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Zustand (状态管理)

### 后端

- Python 3.10+
- FastAPI
- LangGraph
- LangChain

## 项目结构

```
LGBS/
├── backend/                 # 后端服务
│   ├── src/
│   │   ├── api/
│   │   │   └── endpoints/   # API 端点
│   │   │       ├── codegen.py      # 代码生成逻辑
│   │   │       ├── project.py      # 项目管理
│   │   │       └── templates.py    # 代码生成模板
│   │   └── main.py         # FastAPI 应用入口
│   └── requirements.txt    # Python 依赖
│
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/     # React 组件
│   │   ├── store/          # 状态管理
│   │   ├── types/          # TypeScript 类型定义
│   │   └── lib/            # 工具函数
│   └── package.json        # Node 依赖
│
└── generated_projects/     # 生成的项目存放目录
```

## 快速开始

### 前置要求

- Node.js 18+
- Python 3.10+
- pnpm (推荐)

### 安装

1. 克隆项目

```bash
git clone <repository-url>
cd LGBS
```

2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

3. 安装前端依赖

```bash
cd frontend
pnpm install
```

### 启动

1. 启动后端服务

```bash
cd backend
python src/main.py
# 或
uvicorn src.main:app --reload
```

后端服务将在 http://localhost:8000 运行

2. 启动前端开发服务器

```bash
cd frontend
pnpm dev
```

前端应用将在 http://localhost:5173 运行

## 使用指南

### 1. 定义项目基本信息

在第一步中，填写项目名称、描述等信息。

### 2. 设计模块和工作流

- 添加模块：每个模块代表一个独立的功能单元
- 添加节点：每个模块可以包含多个节点（LLM 节点、工具节点等）
- 配置连接：定义节点之间的连接关系

### 3. 定义状态管理

- 全局状态：定义整个应用共享的状态变量
- 模块状态：每个模块可以有自己的子状态

### 4. 配置映射

- 定义输入输出映射关系
- 配置状态变量的传递方式

### 5. 生成项目

点击生成按钮，系统将自动创建完整的 LangGraph 项目代码。

## 生成的项目结构

生成的 LangGraph 项目包含以下结构：

```
project_name/
├── main.py                 # 项目入口
├── state.py               # 状态定义
├── config.py              # 配置管理
├── requirements.txt       # 依赖列表
├── modules/               # 模块目录
│   ├── module1/
│   │   ├── __init__.py
│   │   ├── build.py       # 模块图构建
│   │   ├── test_input.py  # 模块测试入口
│   │   └── nodes/
│   │       ├── prompts.py # 提示词定义
│   │       ├── models.py  # 数据模型
│   │       ├── tools.py   # 工具定义
│   │       └── *.py       # 节点实现
│   └── module2/
│       └── ...
└── README.md              # 项目说明文档
```

## 模块测试

每个生成的模块都包含一个 `test_input.py` 文件，用户可以通过修改测试输入来单独测试模块功能：

```bash
cd modules/<module_name>
python test_input.py
```

## 开发指南

### 添加新的代码模板

模板文件位于 `backend/src/api/endpoints/templates.py`。每个模板使用 `string.Template` 格式，支持变量替换。

### 自定义节点类型

在 `codegen.py` 中的 `generate_node_file` 函数添加新的节点类型处理逻辑。

### API 端点

- `POST /api/project/generate` - 生成项目代码
- `POST /api/project/download` - 下载生成的项目压缩包
- `GET /api/project/list` - 列出已生成的项目

## 示例项目

参考 `DeepResearchAgent.json` 了解项目配置的完整格式。

## 许可证

MIT License
