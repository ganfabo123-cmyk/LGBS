import React, { useState } from 'react';
import { useProjectStore } from '../../../store/useProjectStore';
import { generateId } from '../../../lib/utils';
import type { Module, NodeType } from '../../../types/project';
import NodeCard from './NodeCard';

interface ModuleCardProps {
  module: Module;
  allModules: Module[]; // 所有模块列表
}

const ModuleCard: React.FC<ModuleCardProps> = ({ module, allModules }) => {
  const updateModule = useProjectStore((state) => state.updateModule);
  const addNode = useProjectStore((state) => state.addNode);
  const deleteModule = useProjectStore((state) => state.deleteModule);
  
  const [editing, setEditing] = useState(false);
  const [moduleName, setModuleName] = useState(module.name);
  const [moduleDescription, setModuleDescription] = useState(module.description);
  const [newNodeName, setNewNodeName] = useState('');
  const [newNodeDescription, setNewNodeDescription] = useState('');
  const [newNodeType, setNewNodeType] = useState<NodeType>('llm');
  const [showModuleConnections, setShowModuleConnections] = useState(false);

  const handleSaveModule = () => {
    updateModule(module.id, {
      name: moduleName,
      description: moduleDescription,
    });
    setEditing(false);
  };

  const handleAddNode = () => {
    if (newNodeName) {
      addNode(module.id, {
        id: generateId(),
        type: newNodeType,
        name: newNodeName,
        description: newNodeDescription,
        inputs: [],
        outputs: [],
      });
      setNewNodeName('');
      setNewNodeDescription('');
      setNewNodeType('llm');
    }
  };

  const handleAddModuleInput = () => {
    updateModule(module.id, {
      inputs: [
        ...module.inputs,
        {
          id: generateId(),
          localName: '',
        },
      ],
    });
  };

  const handleUpdateModuleInput = (inputId: string, localName: string) => {
    updateModule(module.id, {
      inputs: module.inputs.map((input) =>
        input.id === inputId ? { ...input, localName } : input
      ),
    });
  };

  const handleDeleteModuleInput = (inputId: string) => {
    updateModule(module.id, {
      inputs: module.inputs.filter((input) => input.id !== inputId),
    });
  };

  const handleAddModuleOutput = () => {
    updateModule(module.id, {
      outputs: [
        ...module.outputs,
        {
          id: generateId(),
          localName: '',
        },
      ],
    });
  };

  const handleUpdateModuleOutput = (outputId: string, localName: string) => {
    updateModule(module.id, {
      outputs: module.outputs.map((output) =>
        output.id === outputId ? { ...output, localName } : output
      ),
    });
  };

  const handleDeleteModuleOutput = (outputId: string) => {
    updateModule(module.id, {
      outputs: module.outputs.filter((output) => output.id !== outputId),
    });
  };

  // 处理模块间联系
  const handleToggleNextModule = (targetModuleId: string) => {
    const currentNextModules = module.nextModules || [];
    const newNextModules = currentNextModules.includes(targetModuleId)
      ? currentNextModules.filter((id) => id !== targetModuleId)
      : [...currentNextModules, targetModuleId];
    
    updateModule(module.id, {
      nextModules: newNextModules,
    });
  };

  // 处理模块间条件边
  const handleToggleConditionalEdge = (targetModuleId: string, isConditional: boolean) => {
    const currentConditionalEdges = module.conditionalEdges || {};
    const newConditionalEdges = { ...currentConditionalEdges };
    
    if (isConditional) {
      newConditionalEdges[targetModuleId] = newConditionalEdges[targetModuleId] || '';
    } else {
      delete newConditionalEdges[targetModuleId];
    }
    
    updateModule(module.id, {
      conditionalEdges: newConditionalEdges,
    });
  };

  // 处理模块间条件函数名称
  const handleUpdateConditionFunction = (targetModuleId: string, conditionFunction: string) => {
    const currentConditionalEdges = module.conditionalEdges || {};
    const newConditionalEdges = { ...currentConditionalEdges };
    newConditionalEdges[targetModuleId] = conditionFunction;
    
    updateModule(module.id, {
      conditionalEdges: newConditionalEdges,
    });
  };

  // 获取可连接的模块（排除自己）
  const availableModules = allModules.filter((m) => m.id !== module.id);

  return (
    <div className="bg-zinc-800 border border-zinc-700 rounded-md p-4">
      {editing ? (
        <div className="space-y-2 mb-4">
          <input
            type="text"
            value={moduleName}
            onChange={(e) => setModuleName(e.target.value)}
            className="w-full px-3 py-2 bg-zinc-700 border border-zinc-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100"
          />
          <input
            type="text"
            value={moduleDescription}
            onChange={(e) => setModuleDescription(e.target.value)}
            className="w-full px-3 py-2 bg-zinc-700 border border-zinc-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100"
          />
          <div className="flex space-x-2">
            <button
              onClick={handleSaveModule}
              className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 rounded-md text-white text-sm"
            >
              Save
            </button>
            <button
              onClick={() => setEditing(false)}
              className="px-3 py-1 bg-zinc-700 hover:bg-zinc-600 rounded-md text-zinc-100 text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-lg font-medium text-indigo-400">{module.name}</h3>
            <p className="text-sm text-zinc-400">{module.description}</p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setEditing(true)}
              className="px-3 py-1 bg-zinc-700 hover:bg-zinc-600 rounded-md text-zinc-100 text-sm"
            >
              Edit
            </button>
            <button
              onClick={() => deleteModule(module.id)}
              className="px-3 py-1 bg-red-600 hover:bg-red-500 rounded-md text-white text-sm"
            >
              Delete
            </button>
          </div>
        </div>
      )}

      {/* 模块间联系 */}
      {availableModules.length > 0 && (
        <div className="mb-4 border border-zinc-600 rounded-md p-3 bg-zinc-750">
          <button
            onClick={() => setShowModuleConnections(!showModuleConnections)}
            className="flex items-center text-sm text-indigo-400 hover:text-indigo-300 mb-2"
          >
            <span>{showModuleConnections ? '▼' : '▶'} 模块连接</span>
            {module.nextModules && module.nextModules.length > 0 && (
              <span className="ml-2 px-2 py-0.5 bg-indigo-600 rounded-full text-white text-xs">
                {module.nextModules.length}
              </span>
            )}
          </button>
          
          {showModuleConnections && (
            <div className="space-y-1 pl-2">
              <p className="text-xs text-zinc-500 mb-2">选择下一个模块：</p>
              {availableModules.map((targetModule) => {
                const isConnected = (module.nextModules || []).includes(targetModule.id);
                const isConditional = module.conditionalEdges && module.conditionalEdges[targetModule.id] !== undefined;
                const conditionFunction = module.conditionalEdges ? module.conditionalEdges[targetModule.id] : '';
                
                return (
                  <div key={targetModule.id} className="space-y-1">
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={isConnected}
                        onChange={() => handleToggleNextModule(targetModule.id)}
                        className="w-4 h-4 text-indigo-600 rounded"
                      />
                      <span className="text-sm text-zinc-300">{targetModule.name}</span>
                      {isConnected && (
                        <input
                          type="checkbox"
                          checked={isConditional}
                          onChange={(e) => handleToggleConditionalEdge(targetModule.id, e.target.checked)}
                          className="w-3 h-3 text-orange-500 rounded ml-2"
                        />
                      )}
                      {isConnected && (
                        <span className="text-xs text-zinc-500 ml-1">条件边</span>
                      )}
                    </label>
                    {isConnected && isConditional && (
                      <div className="ml-6 space-y-1">
                        <input
                          type="text"
                          value={conditionFunction}
                          onChange={(e) => handleUpdateConditionFunction(targetModule.id, e.target.value)}
                          className="w-full px-2 py-1 bg-zinc-700 border border-zinc-600 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 text-zinc-100 text-xs"
                          placeholder="条件函数名称"
                        />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Module Inputs */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <h4 className="text-sm font-medium text-zinc-300">Module Inputs</h4>
          <button
            onClick={handleAddModuleInput}
            className="px-2 py-1 bg-indigo-600 hover:bg-indigo-500 rounded-md text-white text-xs"
          >
            Add Input
          </button>
        </div>
        <div className="space-y-2">
          {module.inputs.length === 0 ? (
            <p className="text-xs text-zinc-500">No module inputs defined</p>
          ) : (
            module.inputs.map((input) => (
              <div key={input.id} className="flex items-center space-x-2">
                <input
                  type="text"
                  value={input.localName}
                  onChange={(e) => handleUpdateModuleInput(input.id, e.target.value)}
                  className="flex-1 px-2 py-1 bg-zinc-700 border border-zinc-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100 text-sm"
                  placeholder="Input name"
                />
                <button
                  onClick={() => handleDeleteModuleInput(input.id)}
                  className="px-2 py-1 bg-red-600 hover:bg-red-500 rounded-md text-white text-xs"
                >
                  Delete
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Module Outputs */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <h4 className="text-sm font-medium text-zinc-300">Module Outputs</h4>
          <button
            onClick={handleAddModuleOutput}
            className="px-2 py-1 bg-indigo-600 hover:bg-indigo-500 rounded-md text-white text-xs"
          >
            Add Output
          </button>
        </div>
        <div className="space-y-2">
          {module.outputs.length === 0 ? (
            <p className="text-xs text-zinc-500">No module outputs defined</p>
          ) : (
            module.outputs.map((output) => (
              <div key={output.id} className="flex items-center space-x-2">
                <input
                  type="text"
                  value={output.localName}
                  onChange={(e) => handleUpdateModuleOutput(output.id, e.target.value)}
                  className="flex-1 px-2 py-1 bg-zinc-700 border border-zinc-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100 text-sm"
                  placeholder="Output name"
                />
                <button
                  onClick={() => handleDeleteModuleOutput(output.id)}
                  className="px-2 py-1 bg-red-600 hover:bg-red-500 rounded-md text-white text-xs"
                >
                  Delete
                </button>
              </div>
            ))
          )}
        </div>
      </div>
      
      <div className="mb-4 border-t border-zinc-700 pt-4">
        <h4 className="text-sm font-medium text-zinc-300 mb-2">Add Node</h4>
        <div className="flex space-x-2">
          <input
            type="text"
            value={newNodeName}
            onChange={(e) => setNewNodeName(e.target.value)}
            className="flex-1 px-3 py-2 bg-zinc-700 border border-zinc-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100 text-sm"
            placeholder="Node name"
          />
          <select
            value={newNodeType}
            onChange={(e) => setNewNodeType(e.target.value as NodeType)}
            className="px-3 py-2 bg-zinc-700 border border-zinc-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100 text-sm"
          >
            <option value="llm">LLM</option>
            <option value="tool">Tool</option>
            <option value="human">Human</option>
            <option value="subgraph">Subgraph</option>
            <option value="conditional">Conditional</option>
          </select>
          <button
            onClick={handleAddNode}
            className="px-3 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-md text-white text-sm"
          >
            Add
          </button>
        </div>
      </div>
      
      <div className="space-y-3">
        {module.nodes.length === 0 ? (
          <p className="text-sm text-zinc-400">No nodes added yet</p>
        ) : (
          module.nodes.map((node) => (
            <NodeCard key={node.id} moduleId={module.id} node={node} allNodes={module.nodes} />
          ))
        )}
      </div>
    </div>
  );
};

export default ModuleCard;
