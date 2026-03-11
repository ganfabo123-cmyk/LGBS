import requests
import json

# 测试代码生成API - 带模块间条件边
url = "http://localhost:8001/api/codegen/generate"
headers = {"Content-Type": "application/json"}

# 模拟项目数据 - 带模块间条件边
test_project = {
    "info": {
        "id": "test_module_conditional",
        "name": "Test Module Conditional Project",
        "description": "A test project with module conditional edges"
    },
    "modules": [
        {
            "id": "module1",
            "name": "Router Module",
            "description": "Module that routes to other modules",
            "inputs": [
                {"id": "input1", "localName": "query", "type": "string"}
            ],
            "outputs": [
                {"id": "output1", "localName": "route", "type": "string"}
            ],
            "nodes": [
                {
                    "id": "node1",
                    "name": "Router",
                    "type": "conditional",
                    "description": "Route to different modules",
                    "inputs": [
                        {"id": "node_input1", "localName": "query", "type": "string"}
                    ],
                    "outputs": [
                        {"id": "node_output1", "localName": "route", "type": "string"}
                    ],
                    "nextNodes": []
                }
            ],
            "nextModules": ["module2", "module3"],
            "conditionalEdges": {
                "module2": "should_use_search",
                "module3": "should_use_analyze"
            }
        },
        {
            "id": "module2",
            "name": "Search Module",
            "description": "Module for searching",
            "inputs": [
                {"id": "input2", "localName": "query", "type": "string"}
            ],
            "outputs": [
                {"id": "output2", "localName": "results", "type": "string"}
            ],
            "nodes": [
                {
                    "id": "node2",
                    "name": "Search",
                    "type": "tool",
                    "description": "Search the web",
                    "inputs": [
                        {"id": "node_input2", "localName": "query", "type": "string"}
                    ],
                    "outputs": [
                        {"id": "node_output2", "localName": "search_results", "type": "string"}
                    ],
                    "nextNodes": []
                }
            ],
            "nextModules": []
        },
        {
            "id": "module3",
            "name": "Analyze Module",
            "description": "Module for analyzing",
            "inputs": [
                {"id": "input3", "localName": "query", "type": "string"}
            ],
            "outputs": [
                {"id": "output3", "localName": "analysis", "type": "string"}
            ],
            "nodes": [
                {
                    "id": "node3",
                    "name": "Analyze",
                    "type": "llm",
                    "description": "Analyze the query",
                    "inputs": [
                        {"id": "node_input3", "localName": "query", "type": "string"}
                    ],
                    "outputs": [
                        {"id": "node_output3", "localName": "analysis", "type": "string"}
                    ],
                    "nextNodes": []
                }
            ],
            "nextModules": []
        }
    ],
    "globalState": [
        {
            "id": "state1",
            "name": "query",
            "type": "string",
            "description": "User query",
            "updateMechanism": "overwrite"
        },
        {
            "id": "state2",
            "name": "results",
            "type": "string",
            "description": "Results",
            "updateMechanism": "overwrite"
        }
    ],
    "config": {
        "useMemory": False,
        "interruptBefore": []
    }
}

data = {
    "project_id": "test_module_conditional",
    "advanced_config": {
        "useMemory": False,
        "interruptBefore": []
    },
    "project": test_project
}

response = requests.post(url, headers=headers, json=data)
print(f"Status code: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"Files generated: {result.get('files', [])}")
    print(f"Project path: {result.get('project_path', '')}")
    
    # 读取生成的 main.py 文件
    import os
    main_path = os.path.join(result.get('project_path', ''), 'main.py')
    if os.path.exists(main_path):
        print("\n=== Generated main.py ===")
        with open(main_path, 'r', encoding='utf-8') as f:
            print(f.read())
else:
    print(f"Error: {response.text}")
