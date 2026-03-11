import requests
import json

# 测试代码生成API - 带条件边
url = "http://localhost:8001/api/codegen/generate"
headers = {"Content-Type": "application/json"}

# 模拟项目数据 - 带条件边
test_project = {
    "info": {
        "id": "test_conditional",
        "name": "Test Conditional Project",
        "description": "A test project with conditional edges"
    },
    "modules": [
        {
            "id": "module1",
            "name": "Test Module",
            "description": "Module with conditional edges",
            "inputs": [
                {"id": "input1", "localName": "query", "type": "string"}
            ],
            "outputs": [
                {"id": "output1", "localName": "results", "type": "string"}
            ],
            "nodes": [
                {
                    "id": "node1",
                    "name": "Router",
                    "type": "conditional",
                    "description": "Route to different nodes",
                    "inputs": [
                        {"id": "node_input1", "localName": "query", "type": "string"}
                    ],
                    "outputs": [
                        {"id": "node_output1", "localName": "route", "type": "string"}
                    ],
                    "nextNodes": ["node2", "node3"],
                    "conditionalEdges": {
                        "node2": "should_search",
                        "node3": "should_analyze"
                    }
                },
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
                },
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
            ]
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
    "project_id": "test_conditional",
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
    
    # 读取生成的 build.py 文件
    import os
    build_path = os.path.join(result.get('project_path', ''), 'modules', 'test_module', 'build.py')
    if os.path.exists(build_path):
        print("\n=== Generated build.py ===")
        with open(build_path, 'r', encoding='utf-8') as f:
            print(f.read())
else:
    print(f"Error: {response.text}")
