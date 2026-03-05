import React, { useState, useEffect } from 'react';
import { useStore } from '../../store';
import type { Mapping } from '../../store';

const Step4: React.FC = () => {
  const { modules, stateDefinition, mappingDefinition, setMapping } = useStore();
  const [mappings, setMappings] = useState<Mapping[]>([]);
  const [localVariables, setLocalVariables] = useState<{ name: string; type: 'input' | 'output' }[]>([]);

  // 提取所有局部变量
  useEffect(() => {
    const variables: { name: string; type: 'input' | 'output' }[] = [];
    
    modules.forEach(module => {
      module.nodes.forEach(node => {
        // 添加输入变量
        node.inputs.forEach(input => {
          if (!variables.some(v => v.name === input)) {
            variables.push({ name: input, type: 'input' });
          }
        });
        // 添加输出变量
        node.outputs.forEach(output => {
          if (!variables.some(v => v.name === output)) {
            variables.push({ name: output, type: 'output' });
          }
        });
      });
    });
    
    setLocalVariables(variables);
  }, [modules]);

  // 初始化映射（当局部变量变化时）
  useEffect(() => {
    if (localVariables.length === 0) return;
    
    const initialMappings: Mapping[] = localVariables.map(localVar => {
      const existingMapping = mappingDefinition.mappings.find(m => m.local === localVar.name);
      return existingMapping || { local: localVar.name, global: '' };
    });
    setMappings(initialMappings);
  }, [localVariables]);

  const handleMappingChange = (local: string, global: string) => {
    const updatedMappings = mappings.map(mapping => {
      if (mapping.local === local) {
        return { ...mapping, global };
      }
      return mapping;
    });
    setMappings(updatedMappings);
    setMapping({ mappings: updatedMappings });
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold mb-4">Step 4: 变量统一化与映射</h2>
      
      <div className="space-y-4">
        <div className="grid grid-cols-3 gap-4">
          <div className="col-span-1">
            <h3 className="text-lg font-medium mb-2">局部变量 (模块/节点 I/O)</h3>
            <div className="border border-gray-200 rounded-md p-3 space-y-2">
              {localVariables.map((localVar, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs ${localVar.type === 'input' ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'}`}>
                    {localVar.type === 'input' ? '输入' : '输出'}
                  </span>
                  <span>{localVar.name}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div className="col-span-1">
            <h3 className="text-lg font-medium mb-2">映射关系</h3>
            <div className="border border-gray-200 rounded-md p-3 space-y-2">
              {mappings.map((mapping, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <span>{mapping.local}</span>
                  <span className="text-gray-500">→</span>
                  <select
                    value={mapping.global}
                    onChange={(e) => handleMappingChange(mapping.local, e.target.value)}
                    className="px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">选择全局变量</option>
                    {stateDefinition.variables.map(variable => (
                      <option key={variable.name} value={variable.name}>
                        {variable.name} ({variable.type})
                      </option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          </div>
          
          <div className="col-span-1">
            <h3 className="text-lg font-medium mb-2">全局状态属性</h3>
            <div className="border border-gray-200 rounded-md p-3 space-y-2">
              {stateDefinition.variables.map((variable, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <span>{variable.name}</span>
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                    {variable.type}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <div className="bg-blue-50 p-4 rounded-md">
          <h3 className="text-sm font-medium mb-2">帮助 Tips</h3>
          <p className="text-sm">
            请将左侧的局部变量（模块/节点的输入/输出）映射到右侧的全局状态属性。
            这样可以确保不同模块之间的数据流转和状态管理的一致性。
          </p>
        </div>
      </div>
    </div>
  );
};

export default Step4;
