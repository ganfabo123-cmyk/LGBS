from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Dict, Any, List
import json
import zipfile
import io
import os
import logging
from pathlib import Path

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 设置日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# 添加处理器到logger
if not logger.handlers:
    logger.addHandler(console_handler)

router = APIRouter()

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent  # backend/src/api/endpoints -> 项目根目录
GENERATED_PROJECTS_DIR = PROJECT_ROOT / "generated_projects"

class CodeGenRequest(BaseModel):
    project_id: str
    advanced_config: Dict[str, Any]
    project: Dict[str, Any]  # 接收完整的项目数据

class CodeGenResponse(BaseModel):
    project_path: str

@router.post("/generate")
async def generate_code(request: CodeGenRequest) -> Dict[str, Any]:
    print(f"[LOG] 开始生成代码，项目ID: {request.project_id}")
    
    # 使用前端发送的项目数据
    project = request.project
    print("[LOG] 接收到项目数据")
    print(f"[LOG] 项目名称: {project.get('info', {}).get('name', 'Unknown')}")
    print(f"[LOG] 模块数量: {len(project.get('modules', []))}")
    print(f"[LOG] 全局状态变量数量: {len(project.get('globalState', []))}")
    
    # 生成代码文件
    print("[LOG] 开始生成Python文件")
    files = generate_python_files(project, request.advanced_config)
    print(f"[LOG] 生成了 {len(files)} 个文件")
    
    # 转换前端项目数据结构以获取项目名称
    backend_project = convert_frontend_project_to_backend(project)
    
    # 创建项目目录
    project_name = backend_project["app_definition"]["app_name"].replace(" ", "_").lower()
    project_dir = GENERATED_PROJECTS_DIR / project_name
    print(f"[LOG] 创建项目目录: {project_dir}")
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # 写入文件到项目目录
    print("[LOG] 开始写入文件到项目目录")
    for file_name, content in files.items():
        file_path = project_dir / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[LOG] 写入文件: {file_name}")
    
    # 创建 ZIP 文件
    zip_path = project_dir.with_suffix('.zip')
    print(f"[LOG] 创建ZIP文件: {zip_path}")
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for file_name, content in files.items():
            zip_file.writestr(file_name, content)
    
    print(f"[LOG] 代码生成完成，项目路径: {project_dir}")
    
    # 构建可访问的ZIP文件URL
    zip_url = f"http://localhost:8001/api/codegen/download?path={zip_path}".replace('\\', '/')
    
    return {
        "files": list(files.keys()), 
        "message": f"Code generated successfully at {project_dir}",
        "project_path": str(project_dir),
        "zip_path": str(zip_path),
        "zip_url": zip_url
    }

@router.get("/download")
async def download_zip(path: str):
    """下载生成的ZIP文件"""
    print(f"[LOG] 开始下载ZIP文件: {path}")
    
    # 验证文件路径
    zip_path = Path(path)
    if not zip_path.exists() or not zip_path.is_file() or zip_path.suffix != '.zip':
        raise HTTPException(status_code=404, detail="ZIP file not found")
    
    # 读取ZIP文件内容
    try:
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
    except Exception as e:
        print(f"[LOG] 读取ZIP文件失败: {e}")
        raise HTTPException(status_code=500, detail="Failed to read ZIP file")
    
    print(f"[LOG] ZIP文件下载完成: {path}")
    
    # 返回ZIP文件
    return Response(
        content=zip_content,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={zip_path.name}"
        }
    )

def convert_frontend_project_to_backend(project: Dict[str, Any]) -> Dict[str, Any]:
    """将前端项目数据结构转换为后端期望的结构"""
    print("[LOG] 开始转换项目数据结构")
    
    # 构建应用定义
    app_definition = {
        "app_name": project.get("info", {}).get("name", "Test App"),
        "app_description": project.get("info", {}).get("description", "A test application"),
        "initial_inputs": [],
        "final_outputs": []
    }
    
    # 设置初始输入和最终输出
    global_state = project.get("globalState", [])
    if global_state:
        # 初始输入：第一个全局状态变量
        app_definition["initial_inputs"] = [global_state[0].get("name", "")]
        # 最终输出：最后一个全局状态变量
        app_definition["final_outputs"] = [global_state[-1].get("name", "")]
    
    # 收集所有输入输出
    all_inputs = set()
    all_outputs = set()
    
    # 构建模块列表
    modules = []
    for module in project.get("modules", []):
        module_name = module.get("name", "module_" + module.get("id", "unknown"))
        module_name = module_name.replace(" ", "_").lower()
        
        # 构建模块输入输出
        module_inputs = [io.get("localName") for io in module.get("inputs", [])]
        module_outputs = [io.get("localName") for io in module.get("outputs", [])]
        
        all_inputs.update(module_inputs)
        all_outputs.update(module_outputs)
        
        # 构建节点列表
        nodes = []
        for node in module.get("nodes", []):
            node_name = node.get("name", "node_" + node.get("id", "unknown"))
            node_name = node_name.replace(" ", "_").lower()
            
            # 构建节点输入输出
            node_inputs = [io.get("localName") for io in node.get("inputs", [])]
            node_outputs = [io.get("localName") for io in node.get("outputs", [])]
            
            # 构建节点
            node_data = {
                "name": node_name,
                "type": node.get("type", "llm"),
                "description": node.get("description", ""),
                "inputs": node_inputs,
                "outputs": node_outputs,
                "prompt_template": node.get("promptTemplate", ""),
                "llm_config": node.get("llmConfig", {"model_name": "gpt-4", "temperature": 0.7})
            }
            nodes.append(node_data)
        
        # 构建连接
        connections = []
        # 根据nextNodes构建连接
        for node in module.get("nodes", []):
            node_name = node.get("name", "node_" + node.get("id", "unknown"))
            node_name = node_name.replace(" ", "_").lower()
            
            for next_node_id in node.get("nextNodes", []):
                # 找到目标节点
                for target_node in module.get("nodes", []):
                    if target_node.get("id") == next_node_id:
                        next_node_name = target_node.get("name", "node_" + next_node_id).replace(" ", "_").lower()
                        connections.append({"from": node_name, "to": next_node_name})
        
        # 构建模块
        module_data = {
            "module_name": module_name,
            "module_description": module.get("description", ""),
            "module_inputs": module_inputs,
            "module_outputs": module_outputs,
            "nodes": nodes,
            "connections": connections
        }
        modules.append(module_data)
    
    # 构建状态定义
    state_definition = {
        "variables": []
    }
    for var in project.get("globalState", []):
        state_definition["variables"].append({
            "name": var.get("name", ""),
            "type": var.get("type", "str"),
            "reducer": var.get("updateMechanism", "overwrite")
        })
    
    # 构建映射定义
    mapping_definition = {
        "mappings": []
    }
    # 简单映射：本地变量名与全局变量名相同
    for var in project.get("globalState", []):
        var_name = var.get("name", "")
        if var_name:
            mapping_definition["mappings"].append({"local": var_name, "global": var_name})
    
    # 构建最终项目结构
    backend_project = {
        "app_definition": app_definition,
        "modules": modules,
        "state_definition": state_definition,
        "mapping_definition": mapping_definition
    }
    
    print("[LOG] 项目数据结构转换完成")
    return backend_project

def generate_python_files(project: Dict[str, Any], advanced_config: Dict[str, Any]) -> Dict[str, str]:
    files = {}
    
    # 转换前端项目数据结构
    backend_project = convert_frontend_project_to_backend(project)
    
    # 生成根目录文件
    print("[LOG] 生成根目录文件")
    files["requirements.txt"] = generate_requirements()
    print("[LOG] 生成了 requirements.txt")
    files["state.py"] = generate_state(backend_project["state_definition"])
    print("[LOG] 生成了 state.py")
    files["main.py"] = generate_main(backend_project["app_definition"], backend_project["modules"], advanced_config)
    print("[LOG] 生成了 main.py")
    files["build.py"] = generate_root_build(backend_project["modules"])
    print("[LOG] 生成了 build.py")
    
    # 为每个模块生成文件
    print(f"[LOG] 开始处理 {len(backend_project['modules'])} 个模块")
    for module in backend_project["modules"]:
        module_name = module["module_name"]
        print(f"[LOG] 处理模块: {module_name}")
        
        # 模块目录下的文件
        files[f"modules/{module_name}/__init__.py"] = ""
        files[f"modules/{module_name}/nodes/__init__.py"] = ""
        files[f"modules/{module_name}/build.py"] = generate_module_build(module)
        print(f"[LOG] 生成了模块 {module_name} 的 build.py")
        
        # 为每个节点生成文件
        nodes = module.get("nodes", [])
        print(f"[LOG] 处理模块 {module_name} 的 {len(nodes)} 个节点")
        for node in nodes:
            node_name = node["name"]
            files[f"modules/{module_name}/nodes/{node_name}.py"] = generate_node_file(node, backend_project["mapping_definition"])
            print(f"[LOG] 生成了节点: {node_name}")
    
    print("[LOG] 文件生成完成")
    return files

def generate_requirements() -> str:
    return """langgraph>=0.0.40
langchain>=0.1.0
langchain-openai>=0.0.5
pydantic>=2.0.0
"""

def generate_state(state_definition: Dict[str, Any]) -> str:
    variables = state_definition["variables"]
    state_code = """from typing import TypedDict, Any, Annotated
import operator

class AgentState(TypedDict):
    \"\"\"全局状态定义\"\"\"
"""
    
    for var in variables:
        if var['reducer'] == 'append':
            state_code += f"    {var['name']}: Annotated[{var['type']}, operator.add]\n"
        else:
            state_code += f"    {var['name']}: {var['type']}\n"
    
    return state_code

def generate_main(app_definition: Dict[str, Any], modules: List[Dict[str, Any]], advanced_config: Dict[str, Any]) -> str:
    main_code = f'''"""
{app_definition["app_name"]}
{app_definition["app_description"]}

初始输入: {", ".join(app_definition["initial_inputs"])}
最终输出: {", ".join(app_definition["final_outputs"])}
"""

from langgraph import StateGraph, END
from state import AgentState
'''
    
    # 导入模块
    for module in modules:
        module_name = module["module_name"]
        main_code += f"from modules.{module_name}.build import build_{module_name}_graph\n"
    
    main_code += '''
def build_main_graph():
    """构建主图"""
    workflow = StateGraph(AgentState)
    
'''
    
    # 添加模块作为节点
    for module in modules:
        module_name = module["module_name"]
        main_code += f'''    # {module["module_description"]}
    {module_name}_graph = build_{module_name}_graph()
    workflow.add_node("{module_name}", {module_name}_graph)
    
'''
    
    # 添加边（简单线性连接，可以根据需要修改）
    for i, module in enumerate(modules):
        if i == 0:
            main_code += f'    workflow.set_entry_point("{module["module_name"]}")\n'
        if i < len(modules) - 1:
            current_module = module["module_name"]
            next_module = modules[i + 1]["module_name"]
            main_code += f'    workflow.add_edge("{current_module}", "{next_module}")\n'
        else:
            main_code += f'    workflow.add_edge("{module["module_name"]}", END)\n'
    
    # 编译配置
    compile_args = []
    if advanced_config.get("persistence", False):
        compile_args.append("checkpointer=MemorySaver()")
    if advanced_config.get("human_in_the_loop", False):
        compile_args.append("interrupt_before=[],")
    
    if compile_args:
        main_code += f'''    
    # 编译图
    app = workflow.compile({", ".join(compile_args)})
'''
    else:
        main_code += '''    
    # 编译图
    app = workflow.compile()
'''
    
    main_code += '''    
    return app

if __name__ == "__main__":
    # 测试运行
    app = build_main_graph()
    
    # 初始状态
    initial_state = {
'''
    
    for input_name in app_definition["initial_inputs"]:
        main_code += f'        "{input_name}": "test input",\n'
    
    main_code += '''    }
    
    # 运行
    result = app.invoke(initial_state)
    print("Result:", result)
'''
    
    return main_code

def generate_root_build(modules: List[Dict[str, Any]]) -> str:
    build_code = '''"""
项目构建脚本
用于验证和构建整个项目
"""

import sys
from pathlib import Path

def validate_project():
    """验证项目结构"""
    print("验证项目结构...")
    
    # 检查必要文件
    required_files = [
        "state.py",
        "main.py",
        "requirements.txt",
'''
    
    for module in modules:
        module_name = module["module_name"]
        build_code += f'        "modules/{module_name}/build.py",\n'
    
    build_code += '''    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"错误: 缺少文件 {file}")
            return False
    
    print("项目结构验证通过!")
    return True

def build_project():
    """构建项目"""
    if not validate_project():
        sys.exit(1)
    
    print("构建项目...")
    # 这里可以添加更多的构建逻辑
    print("构建完成!")

if __name__ == "__main__":
    build_project()
'''
    
    return build_code

def generate_module_nodes(module: Dict[str, Any], mapping_definition: Dict[str, Any]) -> str:
    module_name = module["module_name"]
    nodes = module["nodes"]
    
    nodes_code = f'''"""
{module_name} 模块节点定义
{module["module_description"]}

模块输入: {", ".join(module.get("module_inputs", []))}
模块输出: {", ".join(module.get("module_outputs", []))}
"""

from typing import Dict, Any
from state import AgentState
from .tools import *
from .prompts import *
from .models import *

'''
    
    # 生成节点函数
    for node in nodes:
        node_name = node["name"]
        node_type = node["type"]
        description = node.get("description", "")
        
        nodes_code += f'def {node_name}(state: AgentState) -> AgentState:\n'
        nodes_code += f'    \"\"\"{description}\"\"\"\n'
        nodes_code += f'    # 节点类型: {node_type}\n'
        
        # 处理输入
        for local_input in node.get("inputs", []):
            global_var = local_input
            for mapping in mapping_definition.get("mappings", []):
                if mapping["local"] == local_input:
                    global_var = mapping["global"]
                    break
            nodes_code += f'    {local_input} = state.get("{global_var}")\n'
        
        # 根据节点类型生成不同的逻辑
        if node_type == "llm":
            nodes_code += '''    
    # LLM 节点逻辑
    model = get_model()
    prompt = get_prompt("{}")
    result = model.invoke(prompt.format(**locals()))
    output = result.content
'''.format(node_name)
        elif node_type == "tool":
            tool_name = node_name
            input_var = node.get("inputs", [""])[0] if node.get("inputs") else '""'
            nodes_code += f'''    
    # 工具节点逻辑
    output = {tool_name}({input_var})
'''
        elif node_type == "human":
            nodes_code += '''    
    # 人工介入节点
    # 这里会暂停等待人工输入
    output = state.get("human_input", "")
'''
        elif node_type == "subgraph":
            nodes_code += '''    
    # 子图节点
    # 调用子图逻辑
    output = "subgraph result"
'''
        elif node_type == "conditional":
            nodes_code += '''    
    # 条件分支节点
    # 根据条件决定路由
    output = "conditional result"
'''
        
        # 处理输出
        for local_output in node.get("outputs", []):
            global_var = local_output
            for mapping in mapping_definition.get("mappings", []):
                if mapping["local"] == local_output:
                    global_var = mapping["global"]
                    break
            nodes_code += f'    state["{global_var}"] = output\n'
        
        nodes_code += '    return state\n\n'
    
    return nodes_code

def generate_module_tools(module: Dict[str, Any]) -> str:
    tools_code = f'''"""
{module["module_name"]} 模块工具定义
"""

from langchain.tools import tool

'''
    
    # 生成工具函数
    for node in module["nodes"]:
        if node["type"] == "tool":
            tool_name = node["name"]
            description = node.get("description", "")
            
            tools_code += f'@tool\n'
            tools_code += f'def {tool_name}(input: str) -> str:\n'
            tools_code += f'    \"\"\"{description}\"\"\"\n'
            tools_code += f'    # TODO: 实现工具逻辑\n'
            tools_code += f'    return f"Result of {tool_name}: {{input}}"\n\n'
    
    if not any(node["type"] == "tool" for node in module["nodes"]):
        tools_code += '# 本模块没有工具节点\n'
    
    return tools_code

def generate_module_prompts(module: Dict[str, Any]) -> str:
    prompts_code = f'''"""
{module["module_name"]} 模块提示词定义
"""

from langchain.prompts import ChatPromptTemplate

# 提示词模板
PROMPTS = {{}}

'''
    
    # 生成提示词
    for node in module["nodes"]:
        if node["type"] == "llm":
            node_name = node["name"]
            prompt_template = node.get("prompt_template", "")
            
            prompts_code += f'# {node_name} 的提示词\n'
            if prompt_template:
                prompts_code += f'PROMPTS["{node_name}"] = """{prompt_template}"""\n\n'
            else:
                prompts_code += f'PROMPTS["{node_name}"] = """请输入提示词..."""\n\n'
    
    prompts_code += '''
def get_prompt(node_name: str) -> str:
    """获取指定节点的提示词"""
    return PROMPTS.get(node_name, "")
'''
    
    return prompts_code

def generate_module_models(module: Dict[str, Any]) -> str:
    models_code = f'''"""
{module["module_name"]} 模块模型定义
"""

from langchain_openai import ChatOpenAI

# 模型配置
MODELS = {{}}

'''
    
    # 生成模型配置
    for node in module["nodes"]:
        if node["type"] == "llm":
            node_name = node["name"]
            llm_config = node.get("llm_config", {})
            model_name = llm_config.get("model_name", "gpt-4")
            temperature = llm_config.get("temperature", 0.7)
            
            models_code += f'# {node_name} 的模型配置\n'
            models_code += f'MODELS["{node_name}"] = {{\n'
            models_code += f'    "model_name": "{model_name}",\n'
            models_code += f'    "temperature": {temperature},\n'
            models_code += '}\n\n'
    
    models_code += '''
def get_model(node_name: str = None):
    """获取模型实例"""
    if node_name and node_name in MODELS:
        config = MODELS[node_name]
        return ChatOpenAI(**config)
    # 默认模型
    return ChatOpenAI(model_name="gpt-4", temperature=0.7)
'''
    
    return models_code

def generate_node_file(node: Dict[str, Any], mapping_definition: Dict[str, Any]) -> str:
    node_name = node["name"]
    node_type = node["type"]
    description = node.get("description", "")
    
    node_code = f'''"""
{node_name} 节点定义
{description}

节点类型: {node_type}
"""

from typing import Dict, Any
from state import AgentState


def {node_name}(state: AgentState) -> AgentState:
    """{description}"""
    # 节点类型: {node_type}
'''
    
    # 处理输入
    for local_input in node.get("inputs", []):
        global_var = local_input
        for mapping in mapping_definition.get("mappings", []):
            if mapping["local"] == local_input:
                global_var = mapping["global"]
                break
        node_code += f'    {local_input} = state.get("{global_var}")\n'
    
    # 根据节点类型生成不同的逻辑
    if node_type == "llm":
        node_code += '''    
    # LLM 节点逻辑
    # TODO: 实现 LLM 节点逻辑
    output = "llm result"
'''
    elif node_type == "tool":
        input_var = node.get("inputs", [""])[0] if node.get("inputs") else '""'
        node_code += f'''    
    # 工具节点逻辑
    # TODO: 实现工具节点逻辑
    output = "tool result"
'''
    elif node_type == "human":
        node_code += '''    
    # 人工介入节点
    # 这里会暂停等待人工输入
    output = state.get("human_input", "")
'''
    elif node_type == "subgraph":
        node_code += '''    
    # 子图节点
    # 调用子图逻辑
    output = "subgraph result"
'''
    elif node_type == "conditional":
        node_code += '''    
    # 条件分支节点
    # 根据条件决定路由
    output = "conditional result"
'''
    
    # 处理输出
    for local_output in node.get("outputs", []):
        global_var = local_output
        for mapping in mapping_definition.get("mappings", []):
            if mapping["local"] == local_output:
                global_var = mapping["global"]
                break
        node_code += f'    state["{global_var}"] = output\n'
    
    node_code += '    return state\n'
    
    return node_code

def generate_module_build(module: Dict[str, Any]) -> str:
    module_name = module["module_name"]
    nodes = module["nodes"]
    connections = module.get("connections", [])
    
    build_code = f'''"""
{module_name} 模块构建脚本
"""

from langgraph import StateGraph, END
from state import AgentState
'''
    
    # 导入节点
    for node in nodes:
        node_name = node["name"]
        build_code += f'from .nodes.{node_name} import {node_name}\n'
    
    build_code += f'''

def build_{module_name}_graph():
    """构建 {module_name} 模块的图"""
    workflow = StateGraph(AgentState)
    
    # 添加节点
'''
    
    # 添加节点
    for node in nodes:
        node_name = node["name"]
        build_code += f'    workflow.add_node("{node_name}", {node_name})\n'
    
    build_code += '''    
    # 添加边
'''
    
    # 添加边
    for connection in connections:
        from_node = connection.get("from")
        to_node = connection.get("to")
        condition = connection.get("condition")
        
        if to_node == "END":
            to_node = "END"
        
        if condition:
            build_code += f'    workflow.add_conditional_edges(\n'
            build_code += f'        "{from_node}",\n'
            build_code += f'        lambda state: "{to_node}" if {condition} else END,\n'
            build_code += f'        {{"{to_node}": "{to_node}", END: END}}\n'
            build_code += f'    )\n'
        else:
            if to_node == "END":
                build_code += f'    workflow.add_edge("{from_node}", END)\n'
            else:
                build_code += f'    workflow.add_edge("{from_node}", "{to_node}")\n'
    
    # 设置入口点
    if nodes:
        build_code += f'''    
    # 设置入口点
    workflow.set_entry_point("{nodes[0]['name']}")
'''
    
    build_code += '''    
    # 编译图
    return workflow.compile()

if __name__ == "__main__":
    # 测试运行
    graph = build_{}_graph()
    print("{} graph built successfully!")
'''.format(module_name, module_name)
    
    return build_code
