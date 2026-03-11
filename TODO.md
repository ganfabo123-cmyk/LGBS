# LGBS 代码生成器部署规范总结

## 一、项目结构规范

### 1.1 标准项目结构

```
generated_project/
├── README.md                    # 项目说明文档（必须）
├── main.py                      # 主入口，构建主图（必须）
├── state.py                     # 全局状态定义（必须）
├── config.py                    # 共享配置（LLM、工具等）（必须）
├── requirements.txt             # 依赖包（必须）
└── modules/
    ├── {module_name}/           # 模块目录
    │   ├── __init__.py          # 模块信息注释（必须）
    │   ├── build.py             # 模块图构建（必须）
    │   └── nodes/
    │       ├── prompts.py       # 【必须】系统提示词定义
    │       ├── tools.py         # 【必须】工具定义（供LLM和Tool节点共用）
    │       ├── {node1}.py     # 节点实现
    │       ├── {node2}.py     # 节点实现
    │       └── ...
    └── ...
```

### 1.2 关键文件说明

| 文件 | 是否必须 | 作用 |
|------|---------|------|
| `README.md` | ✅ 必须 | 项目说明、开发规范 |
| `main.py` | ✅ 必须 | 主入口，构建主图 |
| `state.py` | ✅ 必须 | 全局状态定义（TypedDict） |
| `config.py` | ✅ 必须 | 共享配置（get_llm, get_tool等） |
| `requirements.txt` | ✅ 必须 | 依赖包列表 |
| `modules/{module}/__init__.py` | ✅ 必须 | 模块信息注释 |
| `modules/{module}/build.py` | ✅ 必须 | 模块图构建 |
| `modules/{module}/nodes/prompts.py` | ✅ 必须 | 系统提示词定义 |
| `modules/{module}/nodes/tools.py` | ✅ 必须 | 工具定义（供LLM和Tool节点共用） |
| `modules/{module}/nodes/{node}.py` | ✅ 必须 | 节点实现 |

---

## 二、节点开发规范

### 2.1 节点文件头部注释（必须）

每个节点文件必须包含以下注释：

```python
"""
{节点名称} 节点定义

节点类型: LLM / Tool / Router
描述: 节点功能描述

输入绑定:
    - {局部变量名} (局部变量) -> {全局状态字段} (state['{字段名}'])
    
输出绑定:
    - {局部变量名} (局部变量) -> {全局状态字段} (state['{字段名}'])

消息管理:
    - 读取: state['messages'] (获取对话历史)
    - 写入: state['messages'] (追加消息)

【重要】系统提示词使用规范:
    每个 LLM 节点必须有独立的系统提示词！
    原因：
    1. messages 列表会累积所有对话历史
    2. 如果不设置系统提示词，节点会继承之前节点的上下文
    3. 每个节点有特定任务，需要明确的角色定义
    
    正确做法：
        messages = [
            SystemMessage(content=prompts.NODE_NAME_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]

【重要】工具调用规范:
    本节点从 .tools 导入工具定义，确保与 Tool 节点使用的工具一致。
    
    工具 vs 工具节点:
    - 工具 (Tool): 实际执行功能的函数或类（定义在 tools.py）
    - 工具节点 (Tool Node): LangGraph 中的节点，负责调用工具并处理结果

工具来源:
    from .tools import {tool_name}, TOOLS
"""
```

### 2.2 节点函数签名（必须）

```python
def node_name(state: AgentState) -> AgentState:
    """
    节点功能描述
    
    处理流程:
        1. 步骤1
        2. 步骤2
        ...
    """
    # 节点类型: llm / tool / router
    
    # 【输入绑定】从全局状态读取输入
    input_value = state.get("global_field")
    
    # 处理逻辑...
    
    # 【输出绑定】更新全局状态
    state["output_field"] = output_value
    
    # 【返回值规范】返回完整状态字典
    return state
```

---

## 三、系统提示词规范（非常重要）

### 3.1 prompts.py 文件结构

每个模块的 `nodes/prompts.py` 必须包含：

```python
"""
{模块名称} 模块 - 系统提示词定义

【重要说明】
每个 LLM 节点必须有独立的系统提示词！
原因：
1. messages 列表会累积所有对话历史
2. 如果不设置系统提示词，节点会继承之前节点的上下文
3. 每个节点有特定任务，需要明确的角色定义
4. 系统提示词确保节点专注于当前任务，不受其他节点干扰

使用方式:
    from . import prompts
    from langchain_core.messages import SystemMessage, HumanMessage
    
    messages = [
        SystemMessage(content=prompts.NODE_NAME_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ]
"""

# ==================== {节点名} 节点系统提示词 ====================
NODE_NAME_SYSTEM_PROMPT = """你是一位专业的{角色}。

你的专属任务：
{任务描述}

工作要求：
1. 要求1
2. 要求2
...

输出格式：
{格式说明}"""
```

### 3.2 LLM 节点必须使用系统提示词

**错误做法 ❌**：
```python
def node_function(state):
    messages = state.get("messages", [])
    response = llm.invoke(messages)  # 没有系统提示词
    return state
```

**正确做法 ✅**：
```python
from langchain_core.messages import SystemMessage, HumanMessage
from . import prompts

def node_function(state):
    # 构造独立的消息列表（不要直接使用 state['messages']）
    llm_messages = [
        SystemMessage(content=prompts.NODE_NAME_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ]
    
    llm = get_llm()
    response = llm.invoke(llm_messages)
    
    # 记录到消息历史
    messages_history = state.get("messages", [])
    messages_history.append(SystemMessage(content=f"[节点名系统提示] ..."))
    messages_history.append(HumanMessage(content=f"[节点名用户提示] ..."))
    messages_history.append(AIMessage(content=response.content))
    state["messages"] = messages_history
    
    return state
```

---

## 四、工具定义与调用规范

### 4.1 tools.py 文件结构（必须）

每个模块的 `nodes/tools.py` 必须包含：

```python
"""
{模块名称} 模块 - 工具定义

说明:
    本文件定义模块级别的工具，供 LLM 节点和 Tool 节点共同使用。
    
    工具 vs 工具节点:
    - 工具 (Tool): 实际执行功能的函数或类（如搜索引擎、API调用）
    - 工具节点 (Tool Node): LangGraph 中的节点，负责调用工具并处理结果
    
    使用场景:
    1. LLM 节点通过 bind_tools 绑定工具，让 LLM 决定何时调用
    2. Tool 节点直接执行工具，获取结果并更新状态
    
    两种场景使用同一个工具定义，确保一致性。

工具列表:
    - {tool_name}: 工具描述
"""

from langchain_community.tools import {ToolClass}
from langchain_core.tools import tool


# ==================== 工具定义 ====================
# 方式1：使用现有的工具类
tool_instance = ToolClass()

# 方式2：使用 @tool 装饰器定义自定义工具
@tool
def custom_tool(param: str) -> str:
    """
    工具功能描述。
    
    参数:
        param: 参数说明
        
    返回:
        返回值说明
    """
    # 实现逻辑
    return result


# ==================== 工具列表 ====================
# 供 LLM 节点 bind_tools 使用
TOOLS = [tool_instance, custom_tool]

# 默认工具（最常用的）
DEFAULT_TOOL = tool_instance
```

### 4.2 工具调用规范

**原则**：
1. **统一工具定义**：所有工具必须在 `tools.py` 中定义
2. **统一导入**：LLM 节点和 Tool 节点都从 `.tools` 导入工具
3. **避免重复定义**：不要在多个地方创建相同的工具实例
4. **文档注释**：工具必须有完整的 docstring

**LLM 节点调用工具**：
```python
from .tools import tool_instance, TOOLS

def llm_node(state):
    llm = get_llm()
    llm_with_tools = llm.bind_tools(TOOLS)  # 绑定所有可用工具
    
    response = llm_with_tools.invoke(messages)
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for tool_call in response.tool_calls:
            result = tool_instance.run(tool_call['args'])
            # 处理工具结果...
```

**Tool 节点调用工具**：
```python
from .tools import tool_instance

def tool_node(state):
    input_value = state.get("input_field")
    result = tool_instance.run(input_value)
    state["output_field"] = result
    return state
```

---

## 五、消息管理规范

### 5.1 使用 state['messages'] 管理消息

**必须使用**：
```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

def node_function(state):
    # 读取当前消息历史
    messages_history = state.get("messages", [])
    
    # 构造 LLM 调用消息列表（独立）
    llm_messages = [
        SystemMessage(content=prompts.SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ]
    
    # 调用 LLM
    response = llm.invoke(llm_messages)
    
    # 记录到消息历史
    messages_history.append(SystemMessage(content=f"[系统提示] ..."))
    messages_history.append(HumanMessage(content=f"[用户提示] ..."))
    messages_history.append(AIMessage(content=response.content))
    
    state["messages"] = messages_history
    return state
```

**禁止**：
- ❌ 不要直接使用 `state['messages']` 作为 LLM 调用的消息列表
- ❌ 不要在节点内部创建新的 `messages` 列表而不更新到 state

---

## 六、输入输出绑定规范

### 6.1 节点必须明确声明输入输出绑定

```python
def node_function(state: AgentState) -> AgentState:
    """
    节点描述
    
    输入绑定:
        - input_name (局部变量) -> global_state_field (全局状态字段)
    
    输出绑定:
        - output_name (局部变量) -> global_state_field (全局状态字段)
    """
    # 从全局状态读取输入
    input_value = state.get("global_state_field")
    
    # 处理逻辑...
    
    # 写入全局状态
    state["global_state_field"] = output_value
    
    return state
```

### 6.2 模块 __init__.py 必须包含模块信息

```python
"""
{模块名称} 模块

模块描述:
    模块功能描述

模块输入:
    - {input_name} (局部变量) -> {global_field} (全局状态字段: state['{field}'])
    
模块输出:
    - {output_name} (局部变量) -> {global_field} (全局状态字段: state['{field}'])

节点列表:
    1. {节点名} ({类型})
       - 输入: {input} -> state['{field}']
       - 输出: {output} -> state['{field}']
    2. ...

节点连接:
    __START__ -> {节点1} -> {节点2}
    {节点2} --(condition)--> {节点1} (条件边)

模块间连接:
    - 输出连接到: {其他模块}
    - 条件函数: {condition_name}
"""
```

---

## 七、README.md 规范

### 7.1 必须包含的内容

```markdown
# {项目名称} 项目说明

## 项目概述
- 初始输入
- 最终输出

## 全局状态
| 状态字段 | 类型 | 更新机制 | 描述 |

## 模块架构
### 模块1: {模块名}
**描述**: 模块功能
**模块输入**: ...
**模块输出**: ...
**节点列表**: ...
**节点连接**: ...

## 开发规范
### 1. 【非常重要】系统提示词使用规范
- 为什么必须设置系统提示词
- 错误做法 vs 正确做法
- 系统提示词定义位置

### 2. 工具定义与调用规范
- 工具 vs 工具节点
- 工具定义规范
- 工具调用方式
- 重要原则

### 3. 输入输出绑定规范
### 4. 节点返回值规范

## 项目结构
## 快速开始
## 开发注意事项
```

---

## 八、config.py 规范

### 8.1 必须提供共享配置函数

```python
"""
共享配置文件
提供 LLM、工具等共享资源的获取函数
"""

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os

# ==================== LLM 配置 ====================
def get_llm():
    """
    获取 LLM 实例
    
    返回:
        ChatOpenAI 或 ChatAnthropic 实例
    """
    # 根据环境变量选择模型
    model_provider = os.getenv("MODEL_PROVIDER", "openai")
    
    if model_provider == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=0.7
        )
    elif model_provider == "anthropic":
        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-opus"),
            temperature=0.7
        )
    else:
        raise ValueError(f"Unknown model provider: {model_provider}")


# ==================== 工具配置 ====================
def get_tool(tool_name: str):
    """
    获取工具实例
    
    参数:
        tool_name: 工具名称
        
    返回:
        工具实例
    """
    # 根据工具名称返回对应的工具
    pass
```

---

## 九、state.py 规范

### 9.1 必须定义全局状态

```python
"""
全局状态定义
定义整个工作流使用的全局状态
"""

from typing import TypedDict, Annotated, List, Union
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    全局状态定义
    
    属性:
        {field_name}: {type} - {description}
    """
    # 用户输入
    topic: str
    
    # 中间状态
    search_query: str
    search_results: str
    draft_report: str
    
    # 最终输出
    final_report: str
    
    # 消息历史（使用 add_messages reducer）
    messages: Annotated[List, add_messages]
    
    # 条件判断标志
    is_report_passed: bool
```

---

## 十、build.py 规范

### 10.1 模块图构建规范

```python
"""
{模块名称} 模块构建脚本

负责构建 {模块名称} 模块的工作流图

模块架构:
    - 节点1: {节点名} ({类型}) - 节点描述
    - 节点2: {节点名} ({类型}) - 节点描述
    
    连接关系:
        START -> {节点1} -> {节点2}
        {节点2} --(condition)--> {节点1} (循环)

条件函数说明:
    {condition_name}: 条件描述
        - 如果条件满足，返回 "{node_name}"
        - 否则返回 END
"""

from langgraph import StateGraph, END, START
from state import AgentState
from .nodes.{node1} import {node1}
from .nodes.{node2} import {node2}

# 条件边函数
def condition_name(state):
    """
    条件判断函数
    
    参数:
        state: AgentState - 包含全局状态的字典
        
    返回:
        str: "{node_name}" 或 END
    """
    # 读取状态
    value = state.get("field_name")
    
    # 条件判断
    if value:
        return "node_name"
    else:
        return END


def build_{module}_graph():
    """
    构建 {模块名称} 模块的图
    
    节点注册:
        - "{node1}": {节点名} 节点 ({类型})
        - "{node2}": {节点名} 节点 ({类型})
    
    边连接:
        1. START -> "{node1}" (入口点)
        2. "{node1}" -> "{node2}" (普通边)
        3. "{node2}" --(condition)--> {"{node1}": ..., END: END} (条件边)
    
    返回:
        CompiledGraph: 编译后的LangGraph图对象
    """
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("node1", node1)
    workflow.add_node("node2", node2)
    
    # 添加边
    workflow.add_edge("node1", "node2")
    workflow.add_conditional_edges(
        "node2",
        condition_name,
        {"node1": "node1", END: END}
    )
    
    # 设置入口点
    workflow.add_edge(START, "node1")
    
    # 编译图
    return workflow.compile()
```

---

## 十一、LGBS 代码生成器实现要点

### 11.1 必须生成的文件

1. **README.md** - 包含完整的项目说明和开发规范
2. **main.py** - 主入口，构建主图
3. **state.py** - 全局状态定义（TypedDict）
4. **config.py** - 共享配置（get_llm等）
5. **requirements.txt** - 依赖包列表
6. **modules/{module}/__init__.py** - 模块信息注释
7. **modules/{module}/build.py** - 模块图构建
8. **modules/{module}/nodes/prompts.py** - 系统提示词定义（每个LLM节点一个）
9. **modules/{module}/nodes/tools.py** - 工具定义（供LLM和Tool节点共用）
10. **modules/{module}/nodes/{node}.py** - 节点实现

### 11.2 节点代码生成模板

```python
"""
{节点名称} 节点定义

节点类型: {LLM/Tool/Router}
描述: {节点描述}

输入绑定:
    - {局部变量} -> {全局状态字段}
    
输出绑定:
    - {局部变量} -> {全局状态字段}

消息管理:
    - 读取: state['messages']
    - 写入: state['messages']

【重要】系统提示词使用规范:
    每个 LLM 节点必须有独立的系统提示词！
    原因：
    1. messages 列表会累积所有对话历史
    2. 如果不设置系统提示词，节点会继承之前节点的上下文
    3. 每个节点有特定任务，需要明确的角色定义

【重要】工具调用规范:
    本节点从 .tools 导入工具定义，确保与 Tool 节点使用的工具一致。
"""

from typing import Dict, Any
from state import AgentState
from config import get_llm
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from . import prompts
from .tools import {tool_names}

def {node_name}(state: AgentState) -> AgentState:
    """
    {节点描述}
    
    处理流程:
        1. {步骤1}
        2. {步骤2}
        ...
    """
    # 节点类型: {llm/tool/router}
    
    # 【输入绑定】从全局状态读取输入
    {input_code}
    
    # 【消息管理】读取当前消息历史
    messages_history = state.get("messages", [])
    
    # 【重要】构造LLM调用消息列表
    llm_messages = [
        SystemMessage(content=prompts.{NODE_NAME}_SYSTEM_PROMPT),
        HumanMessage(content={user_prompt})
    ]
    
    # 【处理逻辑】
    {processing_code}
    
    # 【输出绑定】更新全局状态
    state["messages"] = messages_history
    state["{output_field}"] = {output_value}
    
    # 【返回值规范】返回完整状态字典
    return state
```

### 11.3 prompts.py 生成模板

```python
"""
{模块名称} 模块 - 系统提示词定义

【重要说明】
每个 LLM 节点必须有独立的系统提示词！
原因：
1. messages 列表会累积所有对话历史
2. 如果不设置系统提示词，节点会继承之前节点的上下文
3. 每个节点有特定任务，需要明确的角色定义
4. 系统提示词确保节点专注于当前任务，不受其他节点干扰

使用方式:
    from . import prompts
    from langchain_core.messages import SystemMessage, HumanMessage
    
    messages = [
        SystemMessage(content=prompts.NODE_NAME_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ]
"""

# ==================== {节点名} 节点系统提示词 ====================
{NODE_NAME}_SYSTEM_PROMPT = """你是一位专业的{角色}。

你的专属任务：
{任务描述}

工作要求：
1. 要求1
2. 要求2
...

输出格式：
{格式说明}

记住：{结束语}"""
```

### 11.4 tools.py 生成模板

```python
"""
{模块名称} 模块 - 工具定义

说明:
    本文件定义模块级别的工具，供 LLM 节点和 Tool 节点共同使用。
    
    工具 vs 工具节点:
    - 工具 (Tool): 实际执行功能的函数或类（如搜索引擎、API调用）
    - 工具节点 (Tool Node): LangGraph 中的节点，负责调用工具并处理结果
    
    使用场景:
    1. LLM 节点通过 bind_tools 绑定工具，让 LLM 决定何时调用
    2. Tool 节点直接执行工具，获取结果并更新状态
    
    两种场景使用同一个工具定义，确保一致性。

工具列表:
    - {tool_name}: {工具描述}
"""

from langchain_community.tools import {ToolClass}
from langchain_core.tools import tool

# ==================== 工具定义 ====================
{tool_definitions}

# ==================== 工具列表 ====================
TOOLS = [{tool_instances}]

# 默认工具
DEFAULT_TOOL = {default_tool}
```

---

## 十二、检查清单

生成代码前，必须检查以下项目：

- [ ] 所有模块都有 `__init__.py` 文件
- [ ] 所有模块都有 `build.py` 文件
- [ ] 所有模块的 `nodes/` 目录下都有 `prompts.py` 文件
- [ ] 所有模块的 `nodes/` 目录下都有 `tools.py` 文件
- [ ] 所有 LLM 节点都有独立的系统提示词
- [ ] 所有节点都有完整的头部注释（输入输出绑定）
- [ ] 所有节点都从 `.tools` 导入工具（如果需要）
- [ ] 所有节点都从 `.prompts` 导入系统提示词（如果是LLM节点）
- [ ] 所有节点都使用 `state['messages']` 管理消息
- [ ] 所有节点都返回完整的状态字典
- [ ] README.md 包含完整的开发规范
- [ ] config.py 提供共享配置函数
- [ ] state.py 定义全局状态

---

## 十三、总结

LGBS 代码生成器的核心原则：

1. **结构化**：遵循标准的项目结构
2. **模块化**：每个模块独立，包含 prompts.py 和 tools.py
3. **规范化**：所有文件都有完整的注释和文档
4. **一致性**：工具定义统一，避免重复
5. **可维护**：清晰的输入输出绑定，便于理解和修改

通过遵循以上规范，生成的项目将：
- ✅ 结构清晰，易于理解
- ✅ 符合 LangGraph 最佳实践
- ✅ 便于团队协作
- ✅ 易于扩展和维护
