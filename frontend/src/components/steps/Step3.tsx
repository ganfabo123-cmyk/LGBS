import React, { useState } from 'react';
import { useStore } from '../../store';
import type { StateVariable } from '../../store';

const Step3: React.FC = () => {
  const { stateDefinition, setGlobalState } = useStore();
  const [newVariable, setNewVariable] = useState<StateVariable>({
    name: '',
    type: 'str',
    reducer: 'overwrite'
  });

  const handleAddVariable = () => {
    if (newVariable.name) {
      const newVariables = [...stateDefinition.variables, newVariable];
      setGlobalState({
        variables: newVariables
      });
      setNewVariable({
        name: '',
        type: 'str',
        reducer: 'overwrite'
      });
    }
  };

  const handleRemoveVariable = (index: number) => {
    const newVariables = stateDefinition.variables.filter((_, i) => i !== index);
    setGlobalState({
      variables: newVariables
    });
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold mb-4">Step 3: 全局状态抽象</h2>
      
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-medium mb-2">全局状态变量</h3>
          <div className="space-y-3 p-3 border border-gray-200 rounded-md">
            <div className="grid grid-cols-4 gap-2 mb-2">
              <div className="font-medium">变量名</div>
              <div className="font-medium">数据类型</div>
              <div className="font-medium">更新机制</div>
              <div className="font-medium">操作</div>
            </div>
            
            {stateDefinition.variables.map((variable, index) => (
              <div key={index} className="grid grid-cols-4 gap-2 items-center">
                <div>{variable.name}</div>
                <div>{variable.type}</div>
                <div>
                  {variable.reducer === 'overwrite' ? '覆盖当前值' : '累加到列表'}
                </div>
                <button
                  onClick={() => handleRemoveVariable(index)}
                  className="px-2 py-1 bg-red-500 text-white rounded-md hover:bg-red-600"
                >
                  删除
                </button>
              </div>
            ))}
            
            <div className="grid grid-cols-4 gap-2 items-center pt-2 border-t border-gray-200">
              <input
                type="text"
                value={newVariable.name}
                onChange={(e) => setNewVariable({ ...newVariable, name: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="变量名"
              />
              <select
                value={newVariable.type}
                onChange={(e) => setNewVariable({ ...newVariable, type: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="str">str</option>
                <option value="list">list</option>
                <option value="dict">dict</option>
                <option value="int">int</option>
                <option value="bool">bool</option>
              </select>
              <select
                value={newVariable.reducer}
                onChange={(e) => setNewVariable({ ...newVariable, reducer: e.target.value as 'overwrite' | 'append' })}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="overwrite">覆盖当前值</option>
                <option value="append">累加到列表</option>
              </select>
              <button
                onClick={handleAddVariable}
                className="px-2 py-1 bg-blue-500 text-white rounded-md hover:bg-blue-600"
              >
                添加
              </button>
            </div>
          </div>
        </div>
        
        <div className="bg-blue-50 p-4 rounded-md">
          <h3 className="text-sm font-medium mb-2">帮助 Tips</h3>
          <ul className="text-sm space-y-1">
            <li><strong>覆盖当前值 (Overwrite):</strong> 每次更新时替换为新值，适用于单次计算结果。</li>
            <li><strong>累加到列表 (Append):</strong> 每次更新时将新值添加到列表末尾，适用于对话历史等需要累积的数据。</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Step3;
