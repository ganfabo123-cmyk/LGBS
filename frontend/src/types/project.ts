export type DataType = 'str' | 'list' | 'dict' | 'int' | 'bool';
export type UpdateMechanism = 'overwrite' | 'append';
export type NodeType = 'llm' | 'tool' | 'human' | 'subgraph' | 'conditional';

export interface StateVariable {
  id: string;
  name: string;
  type: DataType;
  updateMechanism: UpdateMechanism;
  description?: string;
}

export interface NodeIO {
  id: string;
  localName: string;
  mappedStateId?: string;
  nodeId?: string;
  moduleId?: string;
  ioType?: 'input' | 'output';
}

export interface GraphNode {
  id: string;
  type: NodeType;
  name: string;
  description: string;
  inputs: NodeIO[];
  outputs: NodeIO[];
  routerLogic?: string;
  nextNodes?: string[]; // 节点间的联系：下一个节点的ID列表
}

export interface Module {
  id: string;
  name: string;
  description: string;
  inputs: NodeIO[];
  outputs: NodeIO[];
  nodes: GraphNode[];
  nextModules?: string[]; // 模块间的联系：下一个模块的ID列表
}

export interface LGBSProject {
  info: {
    name: string;
    description: string;
    initialInputs: string[];
    finalOutputs: string[];
  };
  globalState: StateVariable[];
  modules: Module[];
  config: {
    useMemory: boolean;
    interruptBefore: string[];
  };
}
