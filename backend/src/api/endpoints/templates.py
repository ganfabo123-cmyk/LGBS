"""
代码生成模板文件

本文件集中管理所有代码生成的模板字符串。
"""

import string

# ==================== 依赖文件模板 ====================

REQUIREMENTS_TEMPLATE = """langgraph>=0.0.40
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-community>=0.0.10
pydantic>=2.0.0
python-dotenv>=1.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
"""

# ==================== 配置文件模板 ====================

CONFIG_TEMPLATE = '''\"\"\"
配置模块

本模块集中管理所有配置信息，包括：
1. LLM 模型配置
2. API 密钥管理
3. 模型参数设置

使用方法:
    from config import get_llm
    llm = get_llm()
\"\"\"

import os
from langchain_openai import ChatOpenAI


# 加载 .env 文件中的环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[config] 已加载 .env 文件")
except ImportError:
    print("[config] 未安装 python-dotenv，跳过 .env 文件加载")
except Exception as e:
    print(f"[config] 加载 .env 文件失败: {e}")


def get_llm():
    \"\"\"获取 LLM 模型实例

    使用环境变量配置的 API 信息

    环境变量说明:
    - LLM_API_KEY / OPENAI_API_KEY: API 密钥 (二选一)
    - LLM_URL: API 端点 (默认: https://api.openai.com/v1)
    - LLM_MODEL: 模型名称 (默认: gpt-4o-mini)
    - USE_OLLAMA: 是否使用 Ollama (设为 true 时启用)
    - OLLAMA_MODEL: Ollama 模型名称
    - OLLAMA_BASE_URL: Ollama 服务地址
    \"\"\"
    # 从环境变量获取 API 配置
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("LLM_URL", "https://api.openai.com/v1")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # 检查 API 密钥是否设置
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        raise ValueError(
            "API 密钥未设置！请设置以下环境变量之一:\\n"
            "  - LLM_API_KEY\\n"
            "  - OPENAI_API_KEY\\n"
            "或者修改 .env 文件中的 API 密钥"
        )

    print(f"[get_llm] 正在初始化 LLM...")
    print(f"[get_llm] 模型: {model}")
    print(f"[get_llm] API 端点: {base_url}")

    # 使用 OpenAI API，添加超时设置
    return ChatOpenAI(
        model=model,
        temperature=0.7,
        api_key=api_key,
        base_url=base_url,
        timeout=60,  # 设置 60 秒超时
        max_retries=2  # 设置最大重试次数
    )
'''

# ==================== README 模板 ====================

README_TEMPLATE = string.Template("""# $app_name

$app_description

## 项目结构

```
.
├── main.py                 # 项目入口
├── state.py               # 状态定义
├── config.py              # 配置管理
├── requirements.txt       # 依赖列表
├── modules/               # 模块目录
$module_list
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件并配置以下环境变量：

```bash
# 使用 OpenAI API
LLM_API_KEY=your_api_key_here
LLM_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# 或使用其他兼容 OpenAI 的 API
# LLM_API_KEY=your_api_key_here
# LLM_URL=https://your-api-endpoint.com/v1
# LLM_MODEL=your-model-name
```

### 3. 运行项目

```bash
python main.py
```

## 模块说明

$module_list

## 开发指南

### 添加新节点

1. 在对应模块的 `nodes/` 目录下创建新的节点文件
2. 实现节点函数，接收和返回 `AgentState`
3. 在 `build.py` 中添加节点到工作流

### 修改提示词

编辑对应模块的 `prompts.py` 文件中的系统提示词。

### 添加工具

1. 在对应模块的 `tools.py` 中定义工具函数
2. 将工具添加到 `TOOLS` 列表
3. 在节点中使用 `bind_tools()` 绑定工具

## 注意事项

1. 确保所有节点正确处理 `state["messages"]`
2. 条件边函数必须返回目标节点名称或 "END"

---

## 详细开发指导

### 一、状态管理 (state.py)

#### 状态结构说明
- 基本变量: 如 `messages` (消息历史)
- 模块状态: 每个模块对应一个子状态字典

#### 如何定义模块子状态
```python
class ModuleNameState(TypedDict):
    field1: str
    field2: List[str]

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    module_name: ModuleNameState  # 模块状态
```

#### 状态读写
- 读取: `state["模块名"]["字段名"]`
- 写入: 返回增量更新字典 `{"模块名": {"字段名": 值}}`

### 二、工具实现 (tools.py)

#### 工具函数规范
1. 使用 `@tool` 装饰器
2. 通过 `args_schema` 绑定参数模型
3. 返回值必须是字符串

#### result 对象说明
- `result` 是包含工具执行结果的对象
- 常用类型:
  - `str`: 纯文本结果
  - `dict`: 结构化结果
  - `list`: 列表结果
  - 自定义类: 根据业务需求定义

#### 示例
```python
@tool(args_schema=search_model)
def websearchtool(query_string: str) -> str:
    \"\"\"搜索工具\"\"\"
    result = search_api(query_string)
    return str(result)
```

### 三、模型定义 (models.py)

#### 思考模型字段建议
- 采用分布式推理,即为任务划分为多步,每一步对应一个属性


#### 示例
```python
class think_node_name_model(BaseModel):
    step1_analysis: str = Field(description="对任务的分析")
    step2_reasoning: str = Field(description="推理过程")
    step3_conclusion: str = Field(description="得出的结论")
```

### 四、提示词编写 (prompts.py)

#### 提示词内容建议
1. 角色定义: 明确 LLM 扮演的角色
2. 任务描述: 详细说明节点需要完成的任务
3. 输入参数: 说明输入数据的来源和含义
4. 输出格式: 指定输出的格式要求
5. 工具使用: 明确指导 LLM 何时、如何使用工具
6. 约束条件: 说明任务的限制和要求
7. 示例: 提供输入输出的示例

#### 提示词示例
```
你是一个专业的{{角色}}。你的任务是{{任务描述}}。
输入: {{输入参数说明}}
输出要求: {{输出格式要求}}
工具使用:
- 使用 think_{{node_name}} 工具进行思考
- 使用 {{node_name}}_response 工具返回结果
```

### 五、节点实现 (nodes/*.py)

#### 节点类型
1. LLM 节点: 使用 LLM 进行推理
2. 思考节点: 在 LLM 节点前进行思考
3. 工具节点: 执行具体的工具函数

#### 工具绑定方式
- 绑定所有工具: `llm.bind_tools(TOOLS)`
- 绑定指定工具: `llm.bind_tools([tool1, tool2])`
- 使用占位符: `llm.bind_tools([t1, t2, t3])`

#### 消息构建方式
1. 从状态获取必要信息后构建:
   ```python
   topic = state.get("模块名", {}).get("字段名", "")
   messages = [SystemMessage(content=system_prompt), HumanMessage(content=f"主题: {topic}")]
   ```
2. 发送完整历史会话:
   ```python
   messages = [SystemMessage(content=system_prompt)] + state["messages"]
   ```

#### 状态更新
- 直接修改: `state["key"] = value`(messages不能采取这种模式)
- 增量更新: `return {"messages": [response], "模块名": {"字段名": 值}}`

### 六、图构建 (build.py)


#### 节点类型说明
1. LLM 节点: 使用 LLM 进行推理
   - 每个 LLM 节点都有一个对应的思考节点
   - 每个 LLM 节点都伴随后续的工具调用
   - 工具类型: 要么是工具节点，要么是响应工具

2. 工具节点: 统一封装在 "tools" 节点中
   - 所有工具函数都在 tools.py 中定义
   - 使用 `ToolNode(tools=TOOLS)` 包装
   - 实际调用时,不调用Tools,因为它包含全部工具,而我们只需要调用当前节点需要的工具

#### 如何添加节点
```python
# 导入节点函数
from .nodes.{node_name} import {node_name}
from .nodes.think_{node_name} import think_{node_name}

# 添加节点到工作流
workflow.add_node("think_{node_name}", think_{node_name})
workflow.add_node("{node_name}", {node_name})
workflow.add_node("tools", ToolNode(tools=TOOLS))
```

#### 如何添加边
1. 普通边 (无条件):
   ```python
   workflow.add_edge("from_node", "to_node")
   ```

2. 条件边 (需要路由函数):
   ```python
   workflow.add_conditional_edges(
       "from_node",
       route_function_name,
       {"target_node": "target_node", END: END}
   )
   ```

#### 路由函数说明
需要在以下情况添加路由函数:
1. 存在分支 (一个节点有多个出边)
2. 需要在状态中增加变量 (从 ToolMessage 中提取数据)

#### 路由函数示例
```python
def route_after_node_name(state: AgentState) -> str:
    \"\"\"路由函数 - 从 state["messages"] 提取 ToolMessage 并决定路由\"\"\"
    for msg in state["messages"]:
        if hasattr(msg, "tool_call_id") and hasattr(msg, "content"):
            tool_name = getattr(msg, "name", None)
            tool_content = msg.content
            # 将提取的信息存入模块状态
            state["模块名"]["字段名"] = tool_content
            # 根据工具名称决定路由
            if tool_name == "xxx_response":
                return "target_node"
    return "default_node"
```

#### 思考节点说明
- 思考节点属于 LLM 节点的一部分
- 每个 LLM 节点前都有一个思考节点
- 思考节点使用 `think_{node_name}_response` 工具进行思考
- 思考完成后通过路由函数路由到目标 LLM 节点
- 可以选择不加入思考节点

#### LLM 节点的工具调用
每个 LLM 节点都伴随后续的工具调用:
1. 工具节点: 调用实际的工具函数 (如 websearchtool)
2. 响应工具: 返回 LLM 的最终响应
可以选择不加入响应节点,直接将LLM的输出作为最终响应

示例流程:
```
START -> think_{node_name}(可选) -> {node_name} -> tools/{node_name}_response(可选) -> END
```

### 七、模块间数据传递 (main.py)

#### 数据传递方式
将需要传递的数据存入 state 的某个属性中

#### 示例
```python
# 在模块A中将数据存入状态
state["modulea"]["output_field"] = value

# 在模块B中从状态读取数据
module_a_output = state.get("modulea", {}).get("output_field", "")
```

#### 状态管理原则
1. 每个模块有独立的状态空间
2. 模块间通过状态读写进行数据传递
3. 确保前序模块的输出字段与后续模块的输入字段对应

### 八、常见问题

#### API 密钥配置
- 确保在 `.env` 文件中设置了 `LLM_API_KEY`
- 或设置环境变量 `LLM_API_KEY`

#### 工具调用失败
- 检查工具函数是否正确实现
- 确保工具返回字符串类型
- 查看错误日志定位问题

#### 状态管理问题
- 确保状态字段名称正确
- 检查模块状态是否正确定义
- 使用正确的状态读写方式
""")

# ==================== 模块初始化模板 ====================

MODULE_INIT_TEMPLATE = string.Template("""\"\"\"
$module_name 模块
$module_description

模块说明:
- 模块名称: $module_name
- 模块描述: $module_description
- 模块输入: $module_inputs
- 模块输出: $module_outputs

节点列表:
$node_list
\"\"\"
""")

# ==================== 模型模板 ====================

MODELS_TEMPLATE = string.Template('''"""
$module_name 模块 - 工具参数模型定义
"""
from pydantic import BaseModel, Field

$model_definitions
''')

TOOL_MODEL_TEMPLATE = string.Template("""class ${tool_name}_model(BaseModel):
    \"\"\"
    $description
    \"\"\"
    $param_name: $param_type = Field(description="$param_description")


""")

# ==================== 思考模型模板 ====================

THINK_MODEL_TEMPLATE = string.Template('''class think_${node_name}_model(BaseModel):
    """
    ${node_name} 节点的思考模型 - 用于思维链推理
    """
    pass  # TODO: 请根据业务需求定义思考模型的字段


''')

# ==================== 思考工具模板 ====================

THINK_TOOL_TEMPLATE = string.Template("""@tool(args_schema=think_${node_name}_model)
def think_${node_name}_response(result) -> str:
    \"\"\"
    ${node_name} 节点的思考工具 - 用于思维链推理
    \"\"\"
    # TODO: 根据 models.py 中定义的字段，返回结构化的思考结果
    return str(result)

""")

# ==================== 思考节点模板 ====================

THINK_NODE_TEMPLATE = string.Template("""\"\"\"
think_${node_name} 思考节点
\"\"\"

from typing import TypedDict, List, Annotated
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from state import AgentState
from config import get_llm
from .prompts import get_system_prompt


def think_${node_name}(state: AgentState) -> AgentState:
    \"\"\"
    ${node_name} 的思考节点
    \"\"\"
    # 获取 LLM 并绑定思考工具
    llm = get_llm()
    from .tools import think_${node_name}_response
    llm_with_tools = llm.bind_tools([think_${node_name}_response])
    
    # 获取系统提示词
    system_prompt = get_system_prompt("think_${node_name}")
    
    # 构建消息列表
    # 这里也可以采取和llm节点同样的构建方式,1 从状态获取必要信息构建系统和用户提示词或者 2 直接发送完整历史会话
    messages = [SystemMessage(content=system_prompt),HumanMessage(content='')] + state["messages"]
    
    # 调用 LLM 进行思考
    response = llm_with_tools.invoke(messages)
    
    # 更新状态
    return {"message":["需要新加入状态的消息"],"其余需要新加入状态的值":""}
""")

# ==================== 思考条件边函数模板 ====================

THINK_CONDITION_TEMPLATE = string.Template('''def route_after_think_${node_name}(state: AgentState) -> str:
    """
    think_${node_name} 后的路由函数
    """
    # TODO: 根据业务需求修改路由逻辑
    return "${node_name}"

''')

# ==================== 工具模板 ====================

TOOLS_TEMPLATE = string.Template("""\"\"\"
$module_name 模块 - 工具定义
\"\"\"

from langchain_core.tools import tool
from .models import $model_imports

$custom_tools

# 工具列表 - 供 LLM 绑定使用
TOOLS = [$tool_list_import]
""")

CUSTOM_TOOL_TEMPLATE = string.Template('''@tool(args_schema=$model_name)
def $tool_name($param_name: $param_type) -> str:
    """
    $description
    """
    # TODO: 实现 $tool_name 的具体逻辑
    result = None  # TODO: 替换为实际的工具执行结果

    # result 可以是:
    # - str: return f"结果: {{result}}"
    # - dict: return json.dumps(result)
    # - list: return "\\n".join(result)
    # - 自定义对象: return result
    return result if result is not None else "TODO: 请实现工具逻辑"


''')

# ==================== 提示词模板 ====================

PROMPTS_TEMPLATE = string.Template('''"""
$module_name 模块 - 系统提示词定义
"""

# 系统提示词定义
# TODO: 请根据业务需求填写以下提示词内容
# 格式: "节点名": """提示词内容""",
SYSTEM_PROMPTS = {
$system_prompts
}


def get_system_prompt(node_name: str) -> str:
    """获取指定节点的系统提示词"""
    return SYSTEM_PROMPTS.get(node_name, "你是一个智能助手，请根据输入提供详细、准确的回应。")
''')

# ==================== 节点文件模板 ====================

NODE_FILE_HEADER_TEMPLATE = string.Template("""\"\"\"
$node_name 节点定义
$description
\"\"\"
from typing import TypedDict, List, Annotated
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from state import AgentState
from config import get_llm
from .prompts import get_system_prompt

""")




NODE_FILE_TOOL_CALLS_TEMPLATE = string.Template('''
def $node_name(state: AgentState) -> AgentState:
    """
    $description
    """
    llm = get_llm()
    # 获取 LLM 并绑定工具
    # TODO: 请根据本节点需要调用的工具修改下面一行
    # 示例: llm_with_tools = llm.bind_tools([t1, t2, t3])

    from .tools import TOOLS
    llm_with_tools = llm.bind_tools(TOOLS)

    # 获取系统提示词
    # TODO: 请确保 prompts.py 中已定义本节点的系统提示词
    system_prompt = get_system_prompt("$node_name")

    # 构建消息列表
    # TODO: 请根据业务需求构建消息列表
    # 示例:
    # 消息构建方式一,从状态获取需要的属性后构建系统提示词和用户提示词:
    # topic = state.get("informationretrieval", {{}}).get("topic_to_analyze", "")
    # messages = [SystemMessage(content=system_prompt), HumanMessage(content=f"主题: {{topic}}")]
    # 或者把完整历史会话发给模型
    # messages = [SystemMessage(content=system_prompt), HumanMessage(content=f"主题: {{topic}}")] + state["messages"]
    
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=f"主题: {{topic}}")]

    # 调用 LLM
    response = llm_with_tools.invoke(messages)

    # 更新状态
    # TODO: 请根据业务需求将输出写入模块状态

    return {"messages": [SystemMessage(content=system_prompt), HumanMessage(content=f"主题: {{topic}}"),response]}#更新状态,把本次会话新增的变量存到字典中返回,比如消息新增
''')

NODE_FILE_NORMAL_TEMPLATE = string.Template('''
def $node_name(state: AgentState) -> AgentState:
    """$description"""
    # 节点类型: $node_type
$input_assignments
    
$node_logic
    
$output_assignments
    
    return state

''')

# ==================== 节点逻辑模板 ====================


NODE_LOGIC_TOOL_TEMPLATE = string.Template("""    # 执行工具
    # TODO: 实现工具调用逻辑
    # 1. 从 models.py 导入工具参数模型: from .models import $tool_name_model
    # 2. 从 tools.py 导入工具函数: from .tools import $tool_name
    # 3. 解析输入参数并调用工具
    # 4. 将结果添加到 state["messages"]
    
    input_value = $input_var if "$input_var" in locals() else ""
    
    # 示例: 调用工具函数
    # result = $tool_name(input_value)
    # state["messages"].append(ToolMessage(content=result, name="$tool_name"))
    
    output = f"工具 $tool_name 执行结果: {{input_value}}""")

NODE_LOGIC_HUMAN_TEMPLATE = """    # 等待人工输入
    print("请提供输入:")
    user_input = input()
    output = user_input
    
    # 添加人工消息到历史
    state["messages"].append(HumanMessage(content=output))"""

NODE_LOGIC_SUBGRAPH_TEMPLATE = """    # 调用子图
    # TODO: 实现子图调用逻辑
    output = "子图执行结果"
    
    # 添加 AI 消息到历史
    state["messages"].append(AIMessage(content=output))"""

NODE_LOGIC_CONDITIONAL_TEMPLATE = """    # 条件判断
    # TODO: 实现条件判断逻辑
    condition_result = True
    
    if condition_result:
        output = "条件为真"
    else:
        output = "条件为假"
    
    # 添加 AI 消息到历史
    state["messages"].append(AIMessage(content=output))"""

# ==================== 模块构建模板 ====================

MODULE_BUILD_TEMPLATE = string.Template('''"""
$module_name 模块构建脚本
"""

from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from state import AgentState
$imports

# TODO: 请根据业务需求添加路由函数
# 示例:
# def route_after_node_name(state: AgentState) -> str:
#     \"\"\"路由函数 - 从 state["messages"] 提取 ToolMessage\"\"\"
#     for msg in state["messages"]:
#         if hasattr(msg, "tool_call_id") and hasattr(msg, "content"):
#             tool_name = getattr(msg, "name", None)
#             tool_content = msg.content
#             state["模块名"]["字段名"] = tool_content
#             if tool_name == "xxx_response":
#                 return "target_node"
#     return "default_node"

$condition_functions

def build_${module_name}_graph():
    """构建 $module_name 模块的图"""
    workflow = StateGraph(AgentState)

    # TODO: 请根据模块中的节点列表，手动添加节点
    # 示例:
    # workflow.add_node("think_node1", think_node1)
    # workflow.add_node("node1", node1)
    # workflow.add_node("tools", ToolNode(tools=TOOLS))

    # TODO: 请根据节点间的连接关系，手动添加边
    # 示例:
    # workflow.add_edge(START, "think_node1")
    # workflow.add_conditional_edges(
    #     "think_node1",
    #     route_after_think_node1,
    #     {"node1": "node1"}
    # )
    # workflow.add_edge("node1", "tools")
    # workflow.add_conditional_edges(
    #     "node1",
    #     route_after_node1,
    #     {"node1_response": "node1", END: END}
    # )


    # TODO: 设置入口点
    # 示例: workflow.add_edge(START, "first_node")

    # 编译图
    app = workflow.compile()

    return app
''')

CONDITION_FUNCTION_TEMPLATE = string.Template('''def $func_name(state: AgentState) -> str:
    """
    条件边函数

    根据状态决定路由到哪个节点

    【开发指导】
    本函数用于根据状态决定路由到哪个节点。

    【使用说明】
    1. 从 state["messages"] 中提取 ToolMessage
    2. 将提取的信息存入模块状态
    3. 根据状态返回目标节点名称或 END
    4. 示例:
       ```python
       for msg in state["messages"]:
           if hasattr(msg, "tool_call_id") and hasattr(msg, "content"):
               tool_name = getattr(msg, "name", None)
               tool_content = msg.content
               if tool_name == "xxx_response":
                   state["模块名"]["字段名"] = tool_content
       return "目标节点"
       ```

    Returns:
        目标节点名称或 END
    """
    # TODO: 实现条件判断逻辑
    # 根据 state 中的某些字段决定路由
    # 1. 从 state["messages"] 提取 ToolMessage
    # 2. 将信息存入模块状态
    # 3. 返回目标节点名称或 END
    return "target_node"

''')

# ==================== 测试输入模板 ====================

TEST_INPUT_TEMPLATE = string.Template('''"""
$module_name 模块 - 测试输入文件

用于测试 $module_name 模块的独立运行。
用户只需修改 TEST_INPUT 字典中的值，然后运行此文件即可测试模块。
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from state import AgentState, $module_state_class
from modules.$module_name.build import build_${module_name}_graph


# ============================================
# 测试输入配置 - 请修改以下字典中的值
# ============================================
TEST_INPUT = {
$test_input_fields
}


def run_module_test():
    """运行模块测试"""
    # 构建模块图
    app = build_${module_name}_graph()
    
    # 构建初始状态
    initial_state = AgentState(
        messages=[],
        $module_name=TEST_INPUT
    )
    
    # 运行模块
    print(f"正在运行 $module_name 模块...")
    print(f"初始输入: {TEST_INPUT}")
    print("-" * 50)
    
    result = app.invoke(initial_state)
    
    print("-" * 50)
    print(f"模块运行完成!")
    print(f"最终状态: {result}")
    
    return result


if __name__ == "__main__":
    run_module_test()
''')

# ==================== 主文件模板 ====================

MAIN_TEMPLATE = string.Template('''"""
$app_name

$app_description

初始输入: $initial_inputs
最终输出: $final_outputs

使用方法:
    python main.py

【开发指导 - 模块间数据传递】
模块间的数据传递通过状态管理实现。

【使用说明】
1. 数据传递方式: 将需要传递的数据存入 state 的某个属性中
2. 例如: 在模块A中将数据存入 state["模块A"]["输出字段"] = 值
3. 在模块B中从 state["模块A"]["输出字段"] 读取数据
4. 状态管理原则:
   - 每个模块有独立的状态空间 (如 state["informationretrieval"])
   - 模块间通过状态读写进行数据传递
   - 确保前序模块的输出字段与后续模块的输入字段对应

【模块通信函数说明】
在 $module_condition_functions 中定义模块间的条件边函数。
这些函数用于:
1. 从前一模块的状态中提取需要传递的数据
2. 将数据传递给后续模块
3. 根据状态决定路由到哪个模块

示例:
```python
def route_after_moduleA(state: AgentState) -> str:
    # 从模块A的状态中提取数据
    module_a_output = state.get("modulea", "").get("output_field", "")

    # 将数据存入下一模块的状态（可选）
    # state["moduleb"]["input_field"] = module_a_output

    # 根据数据决定路由
    if module_a_output:
        return "moduleb"
    return END
```
"""

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from state import AgentState
$module_imports

$module_condition_functions

def build_main_graph():
    """构建主图"""
    workflow = StateGraph(AgentState)

    # 添加模块节点
$module_nodes

    # 添加模块间边
$module_edges

    # 编译图
    app = workflow.compile($compile_args)

    return app


def main():
    """主函数"""
    # 构建主图
    app = build_main_graph()

    # 初始状态
    # TODO: 请根据业务需求填写初始状态
    # 格式: {{"字段名": 值, "模块名": {{"字段名": 值}}}
    initial_state = {{
$initial_state
    }}

    # 配置线程（用于持久化和中断恢复）
    config = {"configurable": {"thread_id": "1"}}

    # 运行图
    result = app.invoke(initial_state, config=config)

    # 输出结果
    # TODO: 请根据业务需求自定义输出格式
    print("\n=== 最终结果 ===")
    print(result)


if __name__ == "__main__":
    main()
''')