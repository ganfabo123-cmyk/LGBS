import requests
import json

# 测试代码生成API - 带模块间条件边
url = "http://localhost:8001/api/codegen/generate"
headers = {"Content-Type": "application/json"}

# 模拟项目数据 - 带模块间条件边
test_project = {
    "info": {
        "name": "Debug Test",
        "description": "Debug"
    },
    "modules": [
        {
            "id": "module1",
            "name": "Module A",
            "description": "First module",
            "inputs": [],
            "outputs": [],
            "nodes": [],
            "nextModules": ["module2"],
            "conditionalEdges": {
                "module2": "should_go_to_b"
            }
        },
        {
            "id": "module2",
            "name": "Module B",
            "description": "Second module",
            "inputs": [],
            "outputs": [],
            "nodes": [],
            "nextModules": []
        }
    ],
    "globalState": [
        {"id": "s1", "name": "query", "type": "string", "updateMechanism": "overwrite"}
    ],
    "config": {"useMemory": False, "interruptBefore": []}
}

data = {
    "project_id": "debug_test",
    "advanced_config": {"useMemory": False, "interruptBefore": []},
    "project": test_project
}

response = requests.post(url, headers=headers, json=data)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"Path: {result.get('project_path', '')}")
    
    import os
    main_path = os.path.join(result.get('project_path', ''), 'main.py')
    if os.path.exists(main_path):
        print("\n=== main.py ===")
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
            
            # 检查是否包含条件函数
            if "should_go_to_b" in content:
                print("\n✓ 条件函数已生成")
            else:
                print("\n✗ 条件函数未生成")
                
            if "add_conditional_edges" in content:
                print("✓ 条件边已生成")
            else:
                print("✗ 条件边未生成")
