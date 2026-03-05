import React, { useState } from 'react';
import { useProjectStore } from '../../../store/useProjectStore';
import { generateId } from '../../../lib/utils';
import type { GraphNode, NodeType } from '../../../types/project';

interface NodeCardProps {
  moduleId: string;
  node: GraphNode;
  allNodes: GraphNode[]; // 同一模块中的所有节点
}

const NodeCard: React.FC<NodeCardProps> = ({ moduleId, node, allNodes }) => {
  const updateNode = useProjectStore((state) => state.updateNode);
  const deleteNode = useProjectStore((state) => state.deleteNode);
  
  const [editing, setEditing] = useState(false);
  const [nodeName, setNodeName] = useState(node.name);
  const [nodeDescription, setNodeDescription] = useState(node.description);
  const [nodeType, setNodeType] = useState<NodeType>(node.type);
  const [routerLogic, setRouterLogic] = useState(node.routerLogic || '');
  
  const [newInputName, setNewInputName] = useState('');
  const [newOutputName, setNewOutputName] = useState('');
  const [showConnections, setShowConnections] = useState(false);

  const handleSaveNode = () => {
    updateNode(moduleId, node.id, {
      name: nodeName,
      description: nodeDescription,
      type: nodeType,
      routerLogic: nodeType === 'conditional' ? routerLogic : undefined,
    });
    setEditing(false);
  };

  const handleAddInput = () => {
    if (newInputName) {
      updateNode(moduleId, node.id, {
        inputs: [
          ...node.inputs,
          {
            id: generateId(),
            localName: newInputName,
          },
        ],
      });
      setNewInputName('');
    }
  };

  const handleAddOutput = () => {
    if (newOutputName) {
      updateNode(moduleId, node.id, {
        outputs: [
          ...node.outputs,
          {
            id: generateId(),
            localName: newOutputName,
          },
        ],
      });
      setNewOutputName('');
    }
  };

  const handleDeleteInput = (inputId: string) => {
    updateNode(moduleId, node.id, {
      inputs: node.inputs.filter((input) => input.id !== inputId),
    });
  };

  const handleDeleteOutput = (outputId: string) => {
    updateNode(moduleId, node.id, {
      outputs: node.outputs.filter((output) => output.id !== outputId),
    });
  };

  // 处理节点间联系
  const handleToggleNextNode = (targetNodeId: string) => {
    const currentNextNodes = node.nextNodes || [];
    const newNextNodes = currentNextNodes.includes(targetNodeId)
      ? currentNextNodes.filter((id) => id !== targetNodeId)
      : [...currentNextNodes, targetNodeId];
    
    updateNode(moduleId, node.id, {
      nextNodes: newNextNodes,
    });
  };

  // 获取可连接的节点（排除自己）
  const availableNodes = allNodes.filter((n) => n.id !== node.id);

  return (
    <div className="bg-zinc-700 border border-zinc-600 rounded-md p-3">
      {editing ? (
        <div className="space-y-2 mb-3">
          <input
            type="text"
            value={nodeName}
            onChange={(e) => setNodeName(e.target.value)}
            className="w-full px-2 py-1 bg-zinc-600 border border-zinc-500 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100 text-sm"
          />
          <input
            type="text"
            value={nodeDescription}
            onChange={(e) => setNodeDescription(e.target.value)}
            className="w-full px-2 py-1 bg-zinc-600 border border-zinc-500 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100 text-sm"
          />
          <select
            value={nodeType}
            onChange={(e) => setNodeType(e.target.value as NodeType)}
            className="w-full px-2 py-1 bg-zinc-600 border border-zinc-500 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100 text-sm"
          >
            <option value="llm">LLM</option>
            <option value="tool">Tool</option>
            <option value="human">Human</option>
            <option value="subgraph">Subgraph</option>
            <option value="conditional">Conditional</option>
          </select>
          {nodeType === 'conditional' && (
            <textarea
              value={routerLogic}
              onChange={(e) => setRouterLogic(e.target.value)}
              className="w-full px-2 py-1 bg-zinc-600 border border-zinc-500 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100 text-sm"
              placeholder="Router logic"
              rows={2}
            />
          )}
          <div className="flex space-x-2">
            <button
              onClick={handleSaveNode}
              className="px-2 py-1 bg-indigo-600 hover:bg-indigo-500 rounded-md text-white text-xs"
            >
              Save
            </button>
            <button
              onClick={() => setEditing(false)}
              className="px-2 py-1 bg-zinc-600 hover:bg-zinc-500 rounded-md text-zinc-100 text-xs"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="flex justify-between items-start mb-3">
          <div>
            <h4 className="font-medium text-zinc-300">{node.name}</h4>
            <p className="text-xs text-zinc-400">{node.description}</p>
            <span className={`text-xs px-2 py-0.5 rounded-full ${node.type === 'llm' ? 'bg-blue-500' : node.type === 'tool' ? 'bg-green-500' : node.type === 'human' ? 'bg-yellow-500' : node.type === 'subgraph' ? 'bg-purple-500' : 'bg-orange-500'}`}>
              {node.type.toUpperCase()}
            </span>
          </div>
          <div className="flex space-x-1">
            <button
              onClick={() => setEditing(true)}
              className="px-2 py-1 bg-zinc-600 hover:bg-zinc-500 rounded-md text-zinc-100 text-xs"
            >
              Edit
            </button>
            <button
              onClick={() => deleteNode(moduleId, node.id)}
              className="px-2 py-1 bg-red-600 hover:bg-red-500 rounded-md text-white text-xs"
            >
              Delete
            </button>
          </div>
        </div>
      )}

      {/* 节点间联系 */}
      {availableNodes.length > 0 && (
        <div className="mb-3 border-t border-zinc-600 pt-2">
          <button
            onClick={() => setShowConnections(!showConnections)}
            className="flex items-center text-xs text-indigo-400 hover:text-indigo-300 mb-2"
          >
            <span>{showConnections ? '▼' : '▶'} 节点连接</span>
            {node.nextNodes && node.nextNodes.length > 0 && (
              <span className="ml-2 px-2 py-0.5 bg-indigo-600 rounded-full text-white text-xs">
                {node.nextNodes.length}
              </span>
            )}
          </button>
          
          {showConnections && (
            <div className="space-y-1 pl-2">
              <p className="text-xs text-zinc-500 mb-2">选择下一个节点：</p>
              {availableNodes.map((targetNode) => (
                <label key={targetNode.id} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={(node.nextNodes || []).includes(targetNode.id)}
                    onChange={() => handleToggleNextNode(targetNode.id)}
                    className="w-3 h-3 text-indigo-600 rounded"
                  />
                  <span className="text-xs text-zinc-300">{targetNode.name}</span>
                </label>
              ))}
            </div>
          )}
        </div>
      )}
      
      <div className="space-y-3">
        <div>
          <h5 className="text-xs font-medium text-zinc-400 mb-1">Inputs</h5>
          <div className="flex space-x-1 mb-1">
            <input
              type="text"
              value={newInputName}
              onChange={(e) => setNewInputName(e.target.value)}
              className="flex-1 px-2 py-1 bg-zinc-600 border border-zinc-500 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100 text-xs"
              placeholder="Input name"
            />
            <button
              onClick={handleAddInput}
              className="px-2 py-1 bg-indigo-600 hover:bg-indigo-500 rounded-md text-white text-xs"
            >
              Add
            </button>
          </div>
          <div className="space-y-1">
            {node.inputs.map((input) => (
              <div key={input.id} className="flex justify-between items-center bg-zinc-600 rounded-md px-2 py-1 text-xs">
                <span>{input.localName}</span>
                <button
                  onClick={() => handleDeleteInput(input.id)}
                  className="text-red-400 hover:text-red-300"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
        
        <div>
          <h5 className="text-xs font-medium text-zinc-400 mb-1">Outputs</h5>
          <div className="flex space-x-1 mb-1">
            <input
              type="text"
              value={newOutputName}
              onChange={(e) => setNewOutputName(e.target.value)}
              className="flex-1 px-2 py-1 bg-zinc-600 border border-zinc-500 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100 text-xs"
              placeholder="Output name"
            />
            <button
              onClick={handleAddOutput}
              className="px-2 py-1 bg-indigo-600 hover:bg-indigo-500 rounded-md text-white text-xs"
            >
              Add
            </button>
          </div>
          <div className="space-y-1">
            {node.outputs.map((output) => (
              <div key={output.id} className="flex justify-between items-center bg-zinc-600 rounded-md px-2 py-1 text-xs">
                <span>{output.localName}</span>
                <button
                  onClick={() => handleDeleteOutput(output.id)}
                  className="text-red-400 hover:text-red-300"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default NodeCard;
