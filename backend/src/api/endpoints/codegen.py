from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Dict, Any, List
import json
import zipfile
import io
import os
import logging
from pathlib import Path

from .templates import (
    REQUIREMENTS_TEMPLATE,
    CONFIG_TEMPLATE,
    README_TEMPLATE,
    MODULE_INIT_TEMPLATE,
    MODELS_TEMPLATE,
    TOOL_MODEL_TEMPLATE,
    THINK_MODEL_TEMPLATE,
    THINK_TOOL_TEMPLATE,
    THINK_NODE_TEMPLATE,
    TOOLS_TEMPLATE,
    CUSTOM_TOOL_TEMPLATE,
    PROMPTS_TEMPLATE,
    NODE_FILE_HEADER_TEMPLATE,
    NODE_FILE_TOOL_CALLS_TEMPLATE,
    NODE_FILE_NORMAL_TEMPLATE,
    NODE_LOGIC_TOOL_TEMPLATE,
    NODE_LOGIC_HUMAN_TEMPLATE,
    NODE_LOGIC_SUBGRAPH_TEMPLATE,
    NODE_LOGIC_CONDITIONAL_TEMPLATE,
    MODULE_BUILD_TEMPLATE,
    CONDITION_FUNCTION_TEMPLATE,
    MAIN_TEMPLATE,
    TEST_INPUT_TEMPLATE
)

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
                        # 检查是否为条件边
                        condition = None
                        if node.get("conditionalEdges"):
                            condition = node["conditionalEdges"].get(next_node_id)
                        connections.append({"from": node_name, "to": next_node_name, "condition": condition})
        
        # 构建模块间连接
        module_connections = []
        for next_module_id in module.get("nextModules", []):
            # 找到目标模块
            for target_module in project.get("modules", []):
                if target_module.get("id") == next_module_id:
                    next_module_name = target_module.get("name", "module_" + next_module_id).replace(" ", "_").lower()
                    # 检查是否为条件边
                    condition = None
                    if module.get("conditionalEdges"):
                        condition = module["conditionalEdges"].get(next_module_id)
                    module_connections.append({"from": module_name, "to": next_module_name, "condition": condition})
        
        # 构建模块
        module_data = {
            "module_name": module_name,
            "module_description": module.get("description", ""),
            "module_inputs": module_inputs,
            "module_outputs": module_outputs,
            "nodes": nodes,
            "connections": connections,
            "module_connections": module_connections
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
    files["state.py"] = generate_state(backend_project['modules'],backend_project["state_definition"])
    print("[LOG] 生成了 state.py")
    files["config.py"] = generate_config()
    print("[LOG] 生成了 config.py")
    files["main.py"] = generate_main(backend_project["app_definition"], backend_project["modules"], advanced_config)
    print("[LOG] 生成了 main.py")
    files["README.md"] = generate_readme(backend_project)
    print("[LOG] 生成了 README.md")
    #加入一个.env文件,里面有LLM_API_KEY,LLM_URL,LLM_MODEL三个固定参数
    # 为每个模块生成文件
    print(f"[LOG] 开始处理 {len(backend_project['modules'])} 个模块")
    for module in backend_project["modules"]:
        module_name = module["module_name"]
        print(f"[LOG] 处理模块: {module_name}")
        
        # 模块目录下的文件
        files[f"modules/{module_name}/__init__.py"] = generate_module_init(module)
        print(f"[LOG] 生成了模块 {module_name} 的 __init__.py")
        files[f"modules/{module_name}/nodes/__init__.py"] = ""
        files[f"modules/{module_name}/build.py"] = generate_module_build(module)
        print(f"[LOG] 生成了模块 {module_name} 的 build.py")
        files[f"modules/{module_name}/test_input.py"] = generate_module_test_input(module, backend_project["state_definition"])
        print(f"[LOG] 生成了模块 {module_name} 的 test_input.py")
        
        # 为 nodes 目录生成统一的 prompts.py
        files[f"modules/{module_name}/nodes/prompts.py"] = generate_module_prompts(module)
        print(f"[LOG] 生成了节点提示词: prompts.py")
        
        # 构建节点到工具节点的连接映射（需要在生成 models 和 tools 之前）
        nodes = module.get("nodes", [])
        connections = module.get("connections", [])
        
        # 收集所有 tool 类型节点名称
        tool_node_names = {n["name"] for n in nodes if n.get("type") == "tool"}
        
        # 构建节点到工具节点的连接映射
        node_to_tools = {}
        for conn in connections:
            from_node = conn.get("from")
            to_node = conn.get("to")
            if to_node in tool_node_names:
                if from_node not in node_to_tools:
                    node_to_tools[from_node] = []
                node_to_tools[from_node].append(to_node)
        
        # 为 nodes 目录生成统一的 models.py（工具参数模型 + 响应模型）
        files[f"modules/{module_name}/nodes/models.py"] = generate_module_models(module, node_to_tools)
        print(f"[LOG] 生成了工具参数模型: models.py")
        
        # 为 nodes 目录生成统一的 tools.py
        files[f"modules/{module_name}/nodes/tools.py"] = generate_module_tools(module, node_to_tools)
        print(f"[LOG] 生成了工具定义: tools.py")
        
        # 为每个节点生成文件（跳过 tool 类型节点，它们会作为工具函数放在 tools.py 中）
        print(f"[LOG] 处理模块 {module_name} 的 {len(nodes)} 个节点")
        
        # 收集所有 LLM 节点
        llm_nodes = [n for n in nodes if n.get("type") == "llm"]
        
        # 为每个 LLM 节点生成思考节点文件
        for node in llm_nodes:
            node_name = node["name"]
            description = node.get("description", "")
            files[f"modules/{module_name}/nodes/think_{node_name}.py"] = generate_think_node(node_name, description)
            print(f"[LOG] 生成了思考节点: think_{node_name}")
        
        for node in nodes:
            node_name = node["name"]
            node_type = node.get("type", "llm")
            
            # 跳过 tool 类型节点，不生成单独的文件
            if node_type == "tool":
                print(f"[LOG] 跳过 tool 节点文件生成: {node_name} (将作为工具函数放在 tools.py 中)")
                continue
            
            # 检查该节点是否与工具节点有连接
            has_tool_connection = node_name in node_to_tools
            
            files[f"modules/{module_name}/nodes/{node_name}.py"] = generate_node_file(
                node, backend_project["mapping_definition"], has_tool_connection
            )
            print(f"[LOG] 生成了节点: {node_name} (tool_calls模式, has_tools={has_tool_connection})")
    
    print("[LOG] 文件生成完成")
    return files

def generate_requirements() -> str:
    return REQUIREMENTS_TEMPLATE

def generate_config() -> str:
    return CONFIG_TEMPLATE

def generate_state(modules: List[Dict[str, Any]], state_definition: Dict[str, Any]) -> str:
    """生成 state.py 文件"""
    variables = state_definition["variables"]
    
    # 构建全局状态类型映射
    global_state_types = {var['name']: var['type'] for var in variables}
    
    # 收集所有模块的输入输出字段
    module_states = []
    for module in modules:
        module_name = module["module_name"]
        module_inputs = module.get("module_inputs", [])
        module_outputs = module.get("module_outputs", [])
        
        # 收集该模块的所有字段 (使用 localName 作为字段名，从 globalState 获取类型)
        fields = set()
        for field_name in module_inputs + module_outputs:
            if field_name:
                # 从全局状态获取类型，默认为 str
                field_type = global_state_types.get(field_name, "str")
                fields.add((field_name, field_type))
        
        if fields:
            module_states.append({
                "name": module_name,
                "class_name": f"{module_name.capitalize()}State",
                "fields": sorted(list(fields), key=lambda x: x[0])
            })
    
    # 生成模块子状态类型定义
    module_state_classes = []
    for ms in module_states:
        class_def = f"\n\nclass {ms['class_name']}(TypedDict):\n    \"\"\"{ms['name']} 模块状态\"\"\""
        for field_name, field_type in ms["fields"]:
            class_def += f"\n    {field_name}: {field_type}"
        module_state_classes.append(class_def)
    
    # 生成 AgentState
    state_code = 'from typing import TypedDict, Any, Annotated, List, Dict\nimport operator\n'
    
    # 添加模块子状态类型定义
    for class_def in module_state_classes:
        state_code += class_def
    
    state_code += '\n\n\nclass AgentState(TypedDict):\n    """全局状态定义"""\n'

    for var in variables:
        if var['reducer'] == 'append':
            state_code += f"    {var['name']}: Annotated[{var['type']}, operator.add]\n"
        else:
            state_code += f"    {var['name']}: {var['type']}\n"

    has_messages = any(var['name'] == 'messages' for var in variables)

    if not has_messages:
        state_code += "    messages: Annotated[list, operator.add]\n"
    
    # 添加模块状态字段
    for ms in module_states:
        state_code += f"    {ms['name']}: {ms['class_name']}\n"

    return state_code

def generate_main(app_definition: Dict[str, Any], modules: List[Dict[str, Any]], advanced_config: Dict[str, Any]) -> str:
    """生成 main.py 文件
    
    main.py 作为项目入口，负责：
    1. 导入各个模块
    2. 构建主图
    3. 运行应用
    
    特殊处理：当检测到同一个模块有多个出边时，自动转换为条件边。
    """
    # 收集所有模块间连接
    all_module_connections = []
    for module in modules:
        module_name = module["module_name"]
        for conn in module.get("module_connections", []):
            all_module_connections.append({
                "from": module_name,
                "to": conn.get("to"),
                "condition": conn.get("condition")
            })
    
    # 分析模块连接关系，检测多分支模块
    # 构建 from_module -> [to_modules] 的映射
    from_module_to_targets = {}
    for conn in all_module_connections:
        from_module = conn["from"]
        to_module = conn["to"]
        condition = conn.get("condition")
        
        if from_module not in from_module_to_targets:
            from_module_to_targets[from_module] = []
        from_module_to_targets[from_module].append({
            "to": to_module,
            "condition": condition
        })
    
    # 生成模块级条件函数
    module_condition_functions_code = ""
    auto_generated_conditions = {}  # 存储自动生成的条件函数名 {from_module: func_name}
    
    # 检测多分支模块并生成自动路由函数
    for from_module, targets in from_module_to_targets.items():
        # 如果该模块有多个出边且没有条件，需要自动生成条件函数
        if len(targets) > 1 and all(not t.get("condition") for t in targets):
            func_name = f"route_{from_module}"
            auto_generated_conditions[from_module] = func_name
            
            # 生成分支映射
            branch_mapping = {}
            for i, target in enumerate(targets):
                to_module = target["to"]
                branch_key = f"branch_{i+1}" if i > 0 else "default"
                branch_mapping[branch_key] = to_module
            
            # 生成自动路由函数
            module_condition_functions_code += f'''def {func_name}(state):
    """自动生成的路由函数 - {from_module}
    
    根据状态决定路由到哪个分支
    """
    # TODO: 实现路由逻辑
    # 根据 state 中的某些字段决定返回哪个分支
    # 返回 "branch_1", "branch_2", ... 或 "default"
    return "default"

'''
    
    # 添加用户自定义的条件函数（排除已自动生成的）
    user_condition_functions = set()
    for conn in all_module_connections:
        condition = conn.get("condition")
        if condition and condition not in auto_generated_conditions.values():
            user_condition_functions.add(condition)
    
    if user_condition_functions:
        module_condition_functions_code += '\n# 用户自定义模块间条件边函数\n'
        for func_name in user_condition_functions:
            module_condition_functions_code += CONDITION_FUNCTION_TEMPLATE.substitute({"func_name": func_name})
    
    # 生成模块导入
    module_imports = ""
    for module in modules:
        module_name = module["module_name"]
        module_imports += f"from modules.{module_name}.build import build_{module_name}_graph\n"
    
    # 生成模块节点
    module_nodes = ""
    for module in modules:
        module_name = module["module_name"]
        module_nodes += f'''    # {module["module_description"]}
    {module_name}_graph = build_{module_name}_graph()
    workflow.add_node("{module_name}", {module_name}_graph)
    
'''
    
    # 生成模块间边 - 处理多分支情况
    module_edges = ""
    processed_modules = set()  # 记录已处理过的源模块
    first_module = True
    
    for module in modules:
        module_name = module["module_name"]
        module_connections = module.get("module_connections", [])
        
        # 第一个模块添加 START 边
        if first_module:
            module_edges += f'    workflow.add_edge(START, "{module_name}")\n'
            first_module = False
        
        # 如果这个模块已经被处理过（作为多分支模块），跳过
        if module_name in processed_modules:
            continue
        
        targets = from_module_to_targets.get(module_name, [])
        
        # 检查是否是多分支模块（多个出边且无显式条件）
        if module_name in auto_generated_conditions:
            # 使用自动生成的条件函数
            func_name = auto_generated_conditions[module_name]
            
            # 构建分支映射
            branch_map = {}
            for i, target in enumerate(targets):
                target_to = target["to"] if target["to"] != "END" else "END"
                branch_key = f"branch_{i+1}" if i > 0 else "default"
                branch_map[branch_key] = target_to
            
            # 生成条件边
            branch_map_str = ", ".join([f'"{k}": "{v}"' for k, v in branch_map.items()])
            module_edges += f'    workflow.add_conditional_edges(\n'
            module_edges += f'        "{module_name}",\n'
            module_edges += f'        {func_name},\n'
            module_edges += f'        {{{branch_map_str}}}\n'
            module_edges += f'    )\n'
            
            processed_modules.add(module_name)
        else:
            # 添加模块间的边（单分支情况）
            for conn in module_connections:
                to_module = conn.get("to")
                condition = conn.get("condition")
                
                if condition:
                    module_edges += f'''    workflow.add_conditional_edges(
        "{module_name}",
        {condition},
        {{"{to_module}": "{to_module}", END: END}}
    )
'''
                else:
                    module_edges += f'    workflow.add_edge("{module_name}", "{to_module}")\n'
            
            # 如果没有模块间连接，且是最后一个模块，连接到 END
            if not module_connections:
                is_last = all(conn.get("to") != module_name for m in modules for conn in m.get("module_connections", []))
                if is_last:
                    module_edges += f'    workflow.add_edge("{module_name}", END)\n'
    
    # 编译配置
    compile_args = []
    
    # 处理 memory 配置
    if advanced_config.get("useMemory", False):
        compile_args.append("checkpointer=MemorySaver()")
    
    # 处理 interrupt_before 配置
    interrupt_before = advanced_config.get("interruptBefore", [])
    if interrupt_before:
        # 将节点名称转换为字符串列表
        interrupt_nodes = ", ".join([f'"{node}"' for node in interrupt_before])
        compile_args.append(f"interrupt_before=[{interrupt_nodes}]")
    
    compile_args_str = ", ".join(compile_args) if compile_args else ""
    
    # 生成初始状态
    initial_state = ""
    for input_name in app_definition["initial_inputs"]:
        initial_state += f'        "{input_name}": "test input",\n'
    
    return MAIN_TEMPLATE.substitute({
        "app_name": app_definition["app_name"],
        "app_description": app_definition["app_description"],
        "initial_inputs": ", ".join(app_definition["initial_inputs"]),
        "final_outputs": ", ".join(app_definition["final_outputs"]),
        "module_imports": module_imports,
        "module_condition_functions": module_condition_functions_code,
        "module_nodes": module_nodes,
        "module_edges":module_edges,
        "compile_args": compile_args_str,
        "initial_state": initial_state
    })

def generate_readme(backend_project: Dict[str, Any]) -> str:
    """生成项目 README.md 文件"""
    app_definition = backend_project["app_definition"]
    modules = backend_project["modules"]
    
    # 生成模块列表
    module_list = ""
    for module in modules:
        module_list += f'''### {module["module_name"]}
- 描述: {module["module_description"]}
- 输入: {", ".join(module.get("module_inputs", []))}
- 输出: {", ".join(module.get("module_outputs", []))}

'''
    
    return README_TEMPLATE.substitute({
        "app_name": app_definition["app_name"],
        "app_description": app_definition["app_description"],
        "module_list": module_list
    })

def generate_module_init(module: Dict[str, Any]) -> str:
    """生成模块的 __init__.py 文件"""
    module_name = module["module_name"]
    module_description = module["module_description"]
    module_inputs = module.get("module_inputs", [])
    module_outputs = module.get("module_outputs", [])
    
    # 生成节点列表
    node_list = ""
    for node in module.get("nodes", []):
        node_list += f'- {node["name"]} ({node.get("type", "llm")}): {node.get("description", "")}\n'
    
    return MODULE_INIT_TEMPLATE.substitute({
        "module_name": module_name,
        "module_description": module_description,
        "module_inputs": ', '.join(module_inputs) if module_inputs else '无',
        "module_outputs": ', '.join(module_outputs) if module_outputs else '无',
        "node_list": node_list
    })

def generate_module_tools(module: Dict[str, Any], node_to_tools: Dict[str, List[str]] = None) -> str:
    """生成模块的 tools.py 文件
    
    将 tool 类型的节点作为被 @tool 装饰器装饰的函数定义在此文件中。
    同时为没有工具连接的 LLM 节点生成响应工具函数。
    """
    if node_to_tools is None:
        node_to_tools = {}
    
    module_name = module["module_name"]
    
    # 收集所有 tool 类型节点
    tool_nodes = [n for n in module["nodes"] if n.get("type") == "tool"]
    
    # 收集没有工具连接的 LLM 节点
    llm_nodes = [n for n in module["nodes"] if n.get("type") == "llm"]
    llm_nodes_without_tools = [n for n in llm_nodes if n["name"] not in node_to_tools]
    
    # 生成工具列表描述
    tool_list_str = ""
    for node in tool_nodes:
        tool_list_str += f'    - {node["name"]}: {node.get("description", "")}\n'
    for node in llm_nodes_without_tools:
        tool_list_str += f'    - {node["name"]}_response: {node.get("description", "")} - 响应工具\n'
    
    if not tool_nodes and not llm_nodes_without_tools:
        tool_list_str = '    (无工具)\n'
    
    # 生成模型导入列表
    model_names = [f"{n['name']}_model" for n in tool_nodes]
    model_names += [f"{n['name']}_response_model" for n in llm_nodes_without_tools]
    model_imports = ", ".join(model_names) if model_names else ""
    
    # 生成自定义工具
    custom_tools = ""
    
    # 生成 tool 类型节点的工具函数
    for node in tool_nodes:
        tool_name = node["name"]
        description = node.get("description", "")
        inputs = node.get("inputs", [])
        
        param_name = "query"
        param_type = "str"
        param_description = "工具输入参数"
        
        if inputs:
            param_name = inputs[0]
        
        custom_tools += CUSTOM_TOOL_TEMPLATE.substitute(
            tool_name=tool_name,
            description=description,
            model_name=f"{tool_name}_model",
            param_name=param_name,
            param_type=param_type,
            param_description=param_description
        )
    
    # 生成 LLM 节点的响应工具函数
    for node in llm_nodes_without_tools:
        node_name = node["name"]
        description = node.get("description", "")
        outputs = node.get("outputs", [])
        
        # 生成响应工具的参数
        if outputs:
            params = ", ".join([f"{o}: str" for o in outputs])
            param_desc = "响应字段"
        else:
            params = "response: str"
            param_desc = "响应内容"
        
        custom_tools += f'''@tool(args_schema={node_name}_response_model)
def {node_name}_response({params}) -> str:
    """
    {description} - 响应工具
    
    Args:
        {param_desc}
        
    Returns:
        结构化响应字符串
    """
    # 响应工具：用于强制 LLM 输出结构化数据
    return "Response recorded"

'''
    
    # 生成思考工具函数（为所有 LLM 节点）
    for node in llm_nodes:
        node_name = node["name"]
        custom_tools += THINK_TOOL_TEMPLATE.substitute(node_name=node_name)
    
    # 生成工具列表
    tool_names = [n["name"] for n in tool_nodes]
    tool_names += [f"{n['name']}_response" for n in llm_nodes_without_tools]
    tool_names += [f"think_{n['name']}_response" for n in llm_nodes]
    tool_list_import = ", ".join(tool_names) if tool_names else ""
    
    # 更新模型导入列表（添加思考模型）
    model_names += [f"think_{n['name']}_model" for n in llm_nodes]
    model_imports = ", ".join(model_names) if model_names else ""
    
    return TOOLS_TEMPLATE.substitute(
        module_name=module_name,
        tool_list=tool_list_str,
        model_imports=model_imports,
        custom_tools=custom_tools,
        tool_list_import=tool_list_import
    )

def generate_module_models(module: Dict[str, Any], node_to_tools: Dict[str, List[str]] = None) -> str:
    """生成模块的 models.py 文件
    
    为每个 tool 类型的节点生成对应的 Pydantic 模型，
    同时为没有工具连接的 LLM 节点生成响应模型，
    为所有 LLM 节点生成思考模型。
    """
    if node_to_tools is None:
        node_to_tools = {}
    
    module_name = module["module_name"]
    
    # 收集所有 tool 类型节点
    tool_nodes = [n for n in module["nodes"] if n.get("type") == "tool"]
    
    # 收集所有 LLM 节点
    llm_nodes = [n for n in module["nodes"] if n.get("type") == "llm"]
    llm_nodes_without_tools = [n for n in llm_nodes if n["name"] not in node_to_tools]
    
    # 生成模型定义
    model_definitions = ""
    
    # 生成工具参数模型
    for node in tool_nodes:
        tool_name = node["name"]
        description = node.get("description", "")
        inputs = node.get("inputs", [])
        
        param_name = "query"
        param_type = "str"
        param_description = "工具输入参数"
        
        if inputs:
            param_name = inputs[0]
        
        model_definitions += TOOL_MODEL_TEMPLATE.substitute(
            tool_name=tool_name,
            description=description,
            param_name=param_name,
            param_type=param_type,
            param_description=param_description
        )
    
    # 生成 LLM 节点响应模型（用于无工具连接的情况）
    for node in llm_nodes_without_tools:
        node_name = node["name"]
        description = node.get("description", "")
        outputs = node.get("outputs", [])
        
        # 生成响应模型的字段
        if outputs:
            fields = ""
            for output in outputs:
                fields += f'    {output}: str = Field(description="{output}输出")\n'
        else:
            fields = '    response: str = Field(description="节点响应内容")\n'
        
        model_definitions += f'''class {node_name}_response_model(BaseModel):
    """
    {description} - 响应模型
    """
{fields}

'''
    
    # 生成思考模型（为所有 LLM 节点）
    for node in llm_nodes:
        node_name = node["name"]
        model_definitions += THINK_MODEL_TEMPLATE.substitute(node_name=node_name)
    
    # 如果没有模型定义，添加占位注释
    if not model_definitions:
        model_definitions = "# 本模块没有工具节点或 LLM 节点，无需定义参数模型\n"
    
    # 生成模型导入列表
    model_names = [f"{n['name']}_model" for n in tool_nodes]
    model_names += [f"{n['name']}_response_model" for n in llm_nodes_without_tools]
    model_names += [f"think_{n['name']}_model" for n in llm_nodes]
    model_imports = ", ".join(model_names) if model_names else ""
    
    return MODELS_TEMPLATE.substitute(
        module_name=module_name,
        model_name=model_imports,
        model_definitions=model_definitions
    )

def generate_module_prompts(module: Dict[str, Any]) -> str:
    """生成模块的 prompts.py 文件"""
    module_name = module["module_name"]
    
    # 生成系统提示词
    system_prompts = ""
    for node in module["nodes"]:
        if node["type"] == "llm":
            node_name = node["name"]
            prompt_template = node.get("prompt_template", "")
            
            if prompt_template:
                system_prompts += f'    "{node_name}": """{prompt_template}""",\n'
            else:
                system_prompts += f'    "{node_name}": """你是一个智能助手，负责处理 {node_name} 节点的任务。请根据输入提供详细、准确的回应。""",\n'
            
            # 为思考节点生成提示词
            system_prompts += f'    "think_{node_name}": """在执行 {node_name} 任务之前，请先进行思考和规划。分析当前状态，确定下一步行动，并说明你的推理过程。""",\n'
    
    return PROMPTS_TEMPLATE.substitute(
        module_name=module_name,
        system_prompts=system_prompts
    )

def generate_think_node(node_name: str, description: str = "") -> str:
    """生成思考节点文件
    
    Args:
        node_name: 目标节点名称
        description: 节点描述
    """
    return THINK_NODE_TEMPLATE.substitute(
        node_name=node_name,
        description=description
    )

def generate_node_file(node: Dict[str, Any], mapping_definition: Dict[str, Any], has_tool_connection: bool = False) -> str:
    """生成节点文件
    
    Args:
        node: 节点配置
        mapping_definition: 映射定义
        has_tool_connection: 是否与工具节点有连接
    """
    node_name = node["name"]
    node_type = node.get("type", "llm")
    description = node.get("description", "")
    node_inputs = node.get("inputs", [])
    node_outputs = node.get("outputs", [])
    
    # 构建输入输出绑定信息
    input_binding = []
    output_binding = []
    for local_input in node_inputs:
        global_var = local_input
        for mapping in mapping_definition.get("mappings", []):
            if mapping["local"] == local_input:
                global_var = mapping["global"]
                break
        input_binding.append(f'{local_input} -> state["{global_var}"]')
    
    for local_output in node_outputs:
        global_var = local_output
        for mapping in mapping_definition.get("mappings", []):
            if mapping["local"] == local_output:
                global_var = mapping["global"]
                break
        output_binding.append(f'{local_output} -> state["{global_var}"]')
    
    # 所有 LLM 节点都使用 tool calls 模式
    use_tool_calls = (node_type == "llm")
    
    # 生成头部
    if use_tool_calls:
        if has_tool_connection:
            tool_call_mode = 'Tool Calling (bind_tools) - 有工具连接'
        else:
            tool_call_mode = 'Tool Calling (bind_tools) - 使用响应模型'
    else:
        tool_call_mode = '直接调用'
    
    node_code = NODE_FILE_HEADER_TEMPLATE.substitute(
        node_name=node_name,
        description=description,
        node_type=node_type,
        input_bindings=', '.join(input_binding) if input_binding else '无',
        output_bindings=', '.join(output_binding) if output_binding else '无',
        tool_call_mode=tool_call_mode
    )
    
    if use_tool_calls:
        # 所有 LLM 节点都使用 tool calls 模式
        node_code += NODE_FILE_TOOL_CALLS_TEMPLATE.substitute(
            node_name=node_name,
            description=description
        )
    else:
        # 生成输入赋值
        input_assignments = ""
        for local_input in node_inputs:
            global_var = local_input
            for mapping in mapping_definition.get("mappings", []):
                if mapping["local"] == local_input:
                    global_var = mapping["global"]
                    break
            input_assignments += f'    {local_input} = state.get("{global_var}")\n'
        
        # 根据节点类型生成不同的逻辑
        if node_type == "tool":
            input_var = node_inputs[0] if node_inputs else '""'
            tool_name = "your_tool"
            node_logic = NODE_LOGIC_TOOL_TEMPLATE.substitute(input_var=input_var, tool_name=tool_name)
        elif node_type == "human":
            node_logic = NODE_LOGIC_HUMAN_TEMPLATE
        elif node_type == "subgraph":
            node_logic = NODE_LOGIC_SUBGRAPH_TEMPLATE
        elif node_type == "conditional":
            node_logic = NODE_LOGIC_CONDITIONAL_TEMPLATE
        else:
            node_logic = '    # 未知节点类型\n    output = ""\n'
        
        # 生成输出赋值
        output_assignments = ""
        for local_output in node_outputs:
            global_var = local_output
            for mapping in mapping_definition.get("mappings", []):
                if mapping["local"] == local_output:
                    global_var = mapping["global"]
                    break
            output_assignments += f'    state["{global_var}"] = output\n'
        
        node_code += NODE_FILE_NORMAL_TEMPLATE.substitute(
            node_name=node_name,
            description=description,
            node_type=node_type,
            input_assignments=input_assignments,
            node_logic=node_logic,
            output_assignments=output_assignments
        )
    
    return node_code

def generate_module_build(module: Dict[str, Any]) -> str:
    """
    生成模块的 build.py 文件

    【开发指导 - 图构建说明】
    本函数生成模块构建脚本的基本框架。由于模板无法精确获取节点和工具信息，
    以示例的方式提供代码，请根据实际需求手动添加节点和边。

    【节点类型说明】
    1. LLM 节点: 使用 LLM 进行推理的节点
       - 每个 LLM 节点都有一个对应的思考节点 (think_{node_name})
       - 每个 LLM 节点都伴随后续的工具调用
       - 工具类型: 要么是工具节点 (tools)，要么是响应工具 ({node_name}_response)

    2. 工具节点: 统一封装在 "tools" 节点中
       - 所有工具函数都在 tools.py 中定义
       - 使用 ToolNode(tools=TOOLS) 包装

    【如何添加节点】
    1. 导入节点函数:
       from .nodes.{node_name} import {node_name}
       from .nodes.think_{node_name} import think_{node_name}

    2. 添加节点到工作流:
       workflow.add_node("think_{node_name}", think_{node_name})
       workflow.add_node("{node_name}", {node_name})
       workflow.add_node("tools", ToolNode(tools=TOOLS))

    【如何添加边】
    1. 普通边 (无条件):
       workflow.add_edge("from_node", "to_node")

    2. 条件边 (需要路由函数):
       workflow.add_conditional_edges(
           "from_node",
           route_function_name,
           {"target_node": "target_node", END: END}
       )

    【路由函数说明】
    路由函数用于根据状态决定路由到哪个节点。
    需要在以下情况添加路由函数:
    1. 存在分支 (一个节点有多个出边)
    2. 需要在状态中增加变量 (从 ToolMessage 中提取数据)

    路由函数示例:
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

    【思考节点说明】
    - 思考节点 (think_{node_name}) 属于 LLM 节点的一部分
    - 每个 LLM 节点前都有一个思考节点
    - 思考节点使用 think_{node_name}_response 工具进行思考
    - 思考完成后通过路由函数路由到目标 LLM 节点

    【LLM 节点的工具调用】
    每个 LLM 节点都伴随后续的工具调用:
    1. 工具节点 (tools): 调用实际的工具函数 (如 websearchtool)
    2. 响应工具 ({node_name}_response): 返回 LLM 的最终响应

    示例流程:
    START -> think_{node_name} -> {node_name} -> tools -> {node_name}_response -> END
    """
    module_name = module["module_name"]

    # 生成基本导入
    imports = f"""from .nodes.think_{module_name}_node1 import think_{module_name}_node1
from .nodes.{module_name}_node1 import {module_name}_node1
from .nodes.tools import TOOLS
"""

    # 生成示例节点代码
    nodes_code = """    # TODO: 请根据模块中的节点列表，手动添加节点
    # 示例:
    # workflow.add_node("think_node1", think_node1)
    # workflow.add_node("node1", node1)
    # workflow.add_node("tools", ToolNode(tools=TOOLS))
"""

    # 生成示例边代码
    edges_code = """    # TODO: 请根据节点间的连接关系，手动添加边
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
"""

    # 生成示例入口点
    entry_code = """    # TODO: 设置入口点
    # 示例: workflow.add_edge(START, "first_node")
"""

    return MODULE_BUILD_TEMPLATE.substitute(
        module_name=module_name,
        imports=imports,
        condition_functions="",
        nodes=nodes_code,
        edges=edges_code,
        entry=entry_code
    )


def generate_module_test_input(module: Dict[str, Any], state_definition: Dict[str, Any]) -> str:
    """
    生成模块的 test_input.py 文件
    
    用于测试模块的独立运行，用户只需修改 TEST_INPUT 字典中的值，
    然后运行此文件即可测试模块。
    """
    module_name = module["module_name"]
    module_inputs = module.get("module_inputs", [])
    module_outputs = module.get("module_outputs", [])
    
    # 构建全局状态类型映射
    global_state_types = {var['name']: var['type'] for var in state_definition.get("variables", [])}
    
    # 收集所有字段（输入和输出）
    all_fields = set(module_inputs + module_outputs)
    
    # 生成测试参数字段
    test_input_fields = []
    for field_name in sorted(all_fields):
        if field_name:
            field_type = global_state_types.get(field_name, "str")
            # 根据类型生成默认值
            if field_type == "str":
                default_value = '""'
            elif field_type == "int":
                default_value = "0"
            elif field_type == "float":
                default_value = "0.0"
            elif field_type == "bool":
                default_value = "False"
            elif field_type in ["list", "List"]:
                default_value = "[]"
            elif field_type in ["dict", "Dict"]:
                default_value = "{}"
            else:
                default_value = "None"
            
            test_input_fields.append(f'    "{field_name}": {default_value},  # {field_type}')
    
    if not test_input_fields:
        test_input_fields = ['    # TODO: 添加测试输入字段']
    
    return TEST_INPUT_TEMPLATE.substitute(
        module_name=module_name,
        module_state_class=f"{module_name.capitalize()}State",
        test_input_fields="\n".join(test_input_fields)
    )