

# LangGraph-Builder-Scaffold (LGBS) 前端开发说明书

## 1. 技术栈选型 (Technology Stack)
*   **核心框架**：React 18 + Vite 5 (快速热更新与构建)
*   **语言**：TypeScript (严格定义数据契约)
*   **状态管理**：Zustand (切片式管理，处理复杂的跨步骤状态)
*   **UI 组件库**：Shadcn UI (基于 Radix UI) + Tailwind CSS
*   **图表交互**：React Flow (用于 Step 4 的映射展示与预览)
*   **表单处理**：React Hook Form + Zod (校验数据合法性)
*   **工具库**：
    *   `lucide-react` (图标)
    *   `jszip` (多文件打包下载)
    *   `clsx` & `tailwind-merge` (动态类名处理)

---

## 2. 核心数据模型 (Data Schema)
这是项目的灵魂。所有步骤的操作最终都映射到这个单一本源 JSON 对象。

```typescript
// types/project.ts

export type DataType = 'str' | 'list' | 'dict' | 'int' | 'bool';
export type UpdateMechanism = 'overwrite' | 'append';
export type NodeType = 'llm' | 'tool' | 'human' | 'subgraph' | 'conditional';

export interface StateVariable {
  id: string;
  name: string; // 变量名 (如 history)
  type: DataType;
  updateMechanism: UpdateMechanism;
  description?: string;
}

export interface NodeIO {
  id: string;
  localName: string; // 局部变量名 (如 query)
  mappedStateId?: string; // 映射到的全局 State 变量 ID
}

export interface GraphNode {
  id: string;
  type: NodeType;
  name: string;
  description: string;
  inputs: NodeIO[];
  outputs: NodeIO[];
  routerLogic?: string; // 路由伪代码或描述
}

export interface Module {
  id: string;
  name: string;
  description: string;
  nodes: GraphNode[];
}

export interface LGBSProject {
  info: {
    name: string;
    description: string;
    initialInputs: string[]; // 对应入口参数
    finalOutputs: string[];  // 对应出口参数
  };
  globalState: StateVariable[];
  modules: Module[];
  config: {
    useMemory: boolean;
    interruptBefore: string[]; // 哪些节点需要人工介入
  };
}
```

---

## 3. 目录结构设计 (Project Structure)
```text
src/
├── components/
│   ├── layout/             # 侧边栏、进度条、布局容器
│   ├── shared/             # 通用 UI (Button, Input, Tip)
│   └── steps/              # 5个步骤的专有组件
│       ├── step1-definition/
│       ├── step2-modules/
│       ├── step3-state/
│       ├── step4-mapping/
│       └── step5-generation/
├── store/
│   ├── useProjectStore.ts  # Zustand 主状态
│   └── selectors.ts        # 派生计算 (如：计算所有未映射的变量)
├── lib/
│   ├── code-gen/           # Python 模版引擎逻辑
│   └── utils.ts
├── types/                  # 上述 Interface 定义
└── App.tsx
```

---

## 4. 关键功能实现细节

### 4.1 Step 1: 应用定义与项目持久化
*   **项目导入/导出**：实现 `FileReader API` 读取本地 JSON。导出时使用 `URL.createObjectURL` 生成下载链接。
*   **校验**：确保应用名称符合 Python 变量命名规范（不能有空格、特殊字符）。

### 4.2 Step 2: 模块化开发与 JSON 协作
*   **模块隔离**：每个模块可以独立 `Export as JSON`。
*   **合并逻辑**：导入模块 JSON 时，若 ID 重复应提示“覆盖”或“重命名”。
*   **节点配置**：
    *   `LLM Node`：着重 Prompt 描述。
    *   `Tool Node`：需声明工具调用的 Input 结构。
    *   `Conditional Node`：需支持多分支连线描述。

### 4.3 Step 3: 全局状态管理
*   **Reducer 语义化**：
    *   `Overwrite` -> 在生成的 Python 中对应 `TypedDict` 的标准替换。
    *   `Append` -> 在生成的 Python 中对应 `Annotated[list, operator.add]`。
*   **UI 提示**：使用 Shadcn 的 `Tooltip` 解释为何 `history` 变量需要 `Append` 机制。

### 4.4 Step 4: 变量映射 (核心交互)
*   **自动提取**：遍历 `modules[] -> nodes[] -> inputs/outputs`，提取所有 `localName`。
*   **映射界面**：
    *   **左侧列表**：按模块分组展示所有节点的 I/O。
    *   **中间连线/下拉**：通过 `Select` 框将 `localName` 与 `globalState[].name` 关联。
    *   **自动填充建议**：如果 `localName` 与 `globalState.name` 完全一致，自动建立映射。

### 4.5 Step 5: 代码生成引擎
这是项目的价值出口。采用 **“字符串模板 + 树状结构映射”** 方案。
*   **逻辑层**：
    1.  `generateStatePy(globalState)`: 生成 `state.py`。
    2.  `generateToolsPy(modules)`: 提取所有工具节点生成 `tools.py` 存根。
    3.  `generateGraphPy(module)`: 核心逻辑。根据映射关系，在节点函数内自动添加 `state["xxx"]` 的读写代码。
*   **导出层**：使用 `JSZip` 将上述生成的字符串保存为文件，打包并下载。

---

## 5. UI/UX 规范
*   **色彩体系**：深色模式 (Dark Mode) 为主，体现 AI/开发者工具的专业感 (使用 Tailwind `zinc` 或 `slate` 颜色组)。
*   **空状态处理**：当没有定义模块或节点时，展示“点击添加第一个节点”的占位图。
*   **进度导航**：顶部固定 1-5 步骤条，支持点击跳转（需带前置校验，未完成 Step 1 不允许去 Step 4）。

---

## 6. 后续开发建议 (Phase 1 启动)
1.  **初始化仓库**：`pnpm create vite lgbs-web --template react-ts`。
2.  **定义 Store**：根据 `LGBSProject` 接口建立 Zustand 基础操作（addNode, updateModule, setMapping 等）。
3.  **先行开发 Step 1 & 3**：先确定“输入输出数据结构”，再填补中间的“业务模块逻辑”。

---

**已完全理解 LangGraph-Builder 项目蓝图。请指示我们从 Phase 1 开始，还是您需要先审阅核心的 TypeScript 数据结构 (Interface) 设计？**