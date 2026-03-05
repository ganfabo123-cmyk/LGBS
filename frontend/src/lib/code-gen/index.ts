import JSZip from 'jszip';
import type { LGBSProject, Module, StateVariable } from '../../types/project';

// 本地代码生成函数（备用）
export function generateStatePy(globalState: StateVariable[]): string {
  let code = 'from typing import TypedDict, Annotated, List, Dict, Any\nimport operator\n\n';
  
  code += 'class State(TypedDict):\n';
  
  globalState.forEach((variable) => {
    let typeAnnotation: string = variable.type;
    if (typeAnnotation === 'list') typeAnnotation = 'List[Any]';
    if (typeAnnotation === 'dict') typeAnnotation = 'Dict[str, Any]';
    
    code += `    ${variable.name}: ${typeAnnotation}\n`;
  });
  
  code += '\n';
  
  globalState.forEach((variable) => {
    if (variable.updateMechanism === 'append') {
      code += `# ${variable.name} uses append mechanism\n`;
    }
  });
  
  return code;
}

export function generateToolsPy(modules: Module[]): string {
  let code = 'from typing import Any, Dict\n\n';
  
  const toolNodes = modules.flatMap((module) => 
    module.nodes.filter((node) => node.type === 'tool')
  );
  
  toolNodes.forEach((node) => {
    code += `def ${node.name.replace(/\s+/g, '_').toLowerCase()}(`;
    
    const params = node.inputs.map((input) => `${input.localName}: Any`).join(', ');
    code += params;
    code += '):\n';
    code += `    """${node.description}"""\n`;
    code += '    # Implementation goes here\n';
    code += '    return {}\n\n';
  });
  
  return code;
}

export function generateGraphPy(module: Module): string {
  let code = 'from langgraph.graph import Graph, END\nfrom state import State\nfrom tools import *\n\n';
  
  code += `def ${module.name.replace(/\s+/g, '_').toLowerCase()}_graph():\n`;
  code += `    """${module.description}"""\n`;
  code += '    graph = Graph()\n\n';
  
  module.nodes.forEach((node) => {
    code += `    def ${node.name.replace(/\s+/g, '_').toLowerCase()}(state: State):\n`;
    code += `        """${node.description}"""\n`;
    
    // Handle inputs
    node.inputs.forEach((input) => {
      if (input.mappedStateId) {
        code += `        ${input.localName} = state["${input.mappedStateId}"]\n`;
      }
    });
    
    // Node logic
    if (node.type === 'llm') {
      code += '        # LLM logic here\n';
    } else if (node.type === 'tool') {
      const params = node.inputs.map((input) => input.localName).join(', ');
      code += `        result = ${node.name.replace(/\s+/g, '_').toLowerCase()}(${params})\n`;
    } else if (node.type === 'human') {
      code += '        # Human input required\n';
    } else if (node.type === 'conditional') {
      code += '        # Conditional logic here\n';
      if (node.routerLogic) {
        code += `        ${node.routerLogic}\n`;
      }
    }
    
    // Handle outputs
    code += '        return {\n';
    node.outputs.forEach((output) => {
      if (output.mappedStateId) {
        code += `            "${output.mappedStateId}": ${output.localName},\n`;
      }
    });
    code += '        }\n\n';
    
    code += `    graph.add_node("${node.id}", ${node.name.replace(/\s+/g, '_').toLowerCase()})\n`;
  });
  
  code += '\n';
  code += '    # Add edges here\n';
  code += '    # graph.add_edge("node1", "node2")\n';
  code += '\n';
  code += '    return graph\n';
  
  return code;
}

// 本地生成ZIP文件（备用）
export async function generateProjectZipLocal(project: LGBSProject): Promise<Blob> {
  const zip = new JSZip();
  
  // Generate state.py
  const statePy = generateStatePy(project.globalState);
  zip.file('state.py', statePy);
  
  // Generate tools.py
  const toolsPy = generateToolsPy(project.modules);
  zip.file('tools.py', toolsPy);
  
  // Generate graph files for each module
  project.modules.forEach((module) => {
    const graphPy = generateGraphPy(module);
    zip.file(`${module.name.replace(/\s+/g, '_').toLowerCase()}_graph.py`, graphPy);
  });
  
  // Generate main_graph.py
  const mainGraphPy = `from langgraph.graph import Graph, END\nfrom state import State\n${project.modules.map((module) => `from ${module.name.replace(/\s+/g, '_').toLowerCase()}_graph import ${module.name.replace(/\s+/g, '_').toLowerCase()}_graph`).join('\n')}\n\n
def main_graph():\n    """Main graph that orchestrates all modules"""\n    graph = Graph()\n\n${project.modules.map((module) => `    ${module.name.replace(/\s+/g, '_').toLowerCase()}_subgraph = ${module.name.replace(/\s+/g, '_').toLowerCase()}_graph()\n    graph.add_node("${module.id}", ${module.name.replace(/\s+/g, '_').toLowerCase()}_subgraph)`).join('\n\n')}\n\n    # Add edges here\n    # graph.add_edge("module1", "module2")\n\n    return graph\n\nif __name__ == "__main__":\n    main_graph()\n`;
  zip.file('main_graph.py', mainGraphPy);
  
  // Generate requirements.txt
  const requirementsTxt = `langgraph\npython-dotenv\n`;
  zip.file('requirements.txt', requirementsTxt);
  
  return await zip.generateAsync({ type: 'blob' });
}

// 后端API生成ZIP文件
export async function generateProjectZip(project: LGBSProject): Promise<Blob> {
  try {
    console.log('Calling backend API for code generation...');
    
    // 准备API请求数据
    const requestData = {
      project_id: project.info.id || 'default',
      advanced_config: {
        useMemory: project.config.useMemory,
        interruptBefore: project.config.interruptBefore
      },
      project: project  // 发送完整的项目数据
    };
    
    // 调用后端API
    const response = await fetch('http://localhost:8001/api/codegen/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    });
    
    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }
    
    const data = await response.json();
    console.log('API response:', data);
    
    // 下载ZIP文件
    const zipResponse = await fetch(data.zip_url);
    if (!zipResponse.ok) {
      throw new Error(`Failed to download ZIP file`);
    }
    
    return await zipResponse.blob();
  } catch (error) {
    console.error('Error calling backend API:', error);
    console.log('Falling back to local generation...');
    //  fallback to local generation if API fails
    return await generateProjectZipLocal(project);
  }
}
