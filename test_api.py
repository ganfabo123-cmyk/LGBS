import requests
import json

# 测试代码生成API
url = "http://localhost:8001/api/codegen/generate"
headers = {"Content-Type": "application/json"}

# 模拟项目数据
test_project = {
    "info": {
        "id": "test123",
        "name": "Test Project",
        "description": "A test project for API testing"
    },
    "modules": [
        {
            "id": "module1",
            "name": "Information Retrieval",
            "description": "Module for retrieving information",
            "inputs": [
                {"id": "input1", "localName": "query", "type": "string"}
            ],
            "outputs": [
                {"id": "output1", "localName": "results", "type": "string"}
            ],
            "nodes": [
                {
                    "id": "node1",
                    "name": "Generate Query",
                    "type": "llm",
                    "description": "Generate search query",
                    "inputs": [
                        {"id": "node_input1", "localName": "query", "type": "string"}
                    ],
                    "outputs": [
                        {"id": "node_output1", "localName": "search_query", "type": "string"}
                    ],
                    "nextNodes": ["node2"]
                },
                {
                    "id": "node2",
                    "name": "Web Search",
                    "type": "tool",
                    "description": "Search the web",
                    "inputs": [
                        {"id": "node_input2", "localName": "search_query", "type": "string"}
                    ],
                    "outputs": [
                        {"id": "node_output2", "localName": "results", "type": "string"}
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
            "description": "Search results",
            "updateMechanism": "overwrite"
        }
    ],
    "config": {
        "useMemory": False,
        "interruptBefore": []
    }
}

data = {
    "project_id": "test123",
    "advanced_config": {
        "useMemory": False,
        "interruptBefore": []
    },
    "project": test_project
}

response = requests.post(url, headers=headers, json=data)
print(f"Status code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
