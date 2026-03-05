import { create } from 'zustand';

// 类型定义
export interface AppDefinition {
  app_name: string;
  app_description: string;
  initial_inputs: string[];
  final_outputs: string[];
}

export interface Node {
  name: string;
  description: string;
  type: 'llm' | 'tool' | 'human' | 'subgraph' | 'conditional';
  inputs: string[];
  outputs: string[];
  prompt_template?: string;
  model_config?: {
    model_name: string;
    temperature: number;
  };
}

export interface Connection {
  from: string;
  to: string;
  condition?: string;
}

export interface Module {
  module_name: string;
  module_description: string;
  module_inputs: string[];
  module_outputs: string[];
  nodes: Node[];
  connections: Connection[];
}

export interface StateVariable {
  name: string;
  type: string;
  reducer: 'overwrite' | 'append';
}

export interface StateDefinition {
  variables: StateVariable[];
}

export interface Mapping {
  local: string;
  global: string;
}

export interface MappingDefinition {
  mappings: Mapping[];
}

export interface AdvancedConfig {
  persistence: boolean;
  human_in_the_loop: boolean;
}

export interface ProjectState {
  // 步骤 1: 应用定义
  appDefinition: AppDefinition;
  setAppDefinition: (appDefinition: AppDefinition) => void;
  
  // 步骤 2: 模块定义
  modules: Module[];
  addModule: (module: Module) => void;
  updateModule: (index: number, module: Module) => void;
  deleteModule: (index: number) => void;
  addConnection: (moduleIndex: number, connection: Connection) => void;
  updateConnection: (moduleIndex: number, connectionIndex: number, connection: Connection) => void;
  deleteConnection: (moduleIndex: number, connectionIndex: number) => void;
  exportModule: (moduleName: string) => Module | undefined;
  importModule: (module: Module) => void;
  
  // 步骤 3: 全局状态定义
  stateDefinition: StateDefinition;
  setGlobalState: (stateDefinition: StateDefinition) => void;
  
  // 步骤 4: 变量映射
  mappingDefinition: MappingDefinition;
  setMapping: (mappingDefinition: MappingDefinition) => void;
  
  // 步骤 5: 高级配置
  advancedConfig: AdvancedConfig;
  setAdvancedConfig: (config: AdvancedConfig) => void;
  
  // 代码生成
  generateCode: () => Promise<{ files: string[]; message: string }>;
}

// 创建状态存储
export const useStore = create<ProjectState>((set, get) => ({
  // 步骤 1: 应用定义
  appDefinition: {
    app_name: '',
    app_description: '',
    initial_inputs: [],
    final_outputs: []
  },
  setAppDefinition: (appDefinition) => set({ appDefinition }),
  
  // 步骤 2: 模块定义
  modules: [],
  addModule: (module) => set((state) => ({ modules: [...state.modules, module] })),
  updateModule: (index, module) => set((state) => {
    const newModules = [...state.modules];
    newModules[index] = module;
    return { modules: newModules };
  }),
  deleteModule: (index) => set((state) => {
    const newModules = [...state.modules];
    newModules.splice(index, 1);
    return { modules: newModules };
  }),
  addConnection: (moduleIndex, connection) => set((state) => {
    const newModules = [...state.modules];
    newModules[moduleIndex] = {
      ...newModules[moduleIndex],
      connections: [...newModules[moduleIndex].connections, connection]
    };
    return { modules: newModules };
  }),
  updateConnection: (moduleIndex, connectionIndex, connection) => set((state) => {
    const newModules = [...state.modules];
    const newConnections = [...newModules[moduleIndex].connections];
    newConnections[connectionIndex] = connection;
    newModules[moduleIndex] = {
      ...newModules[moduleIndex],
      connections: newConnections
    };
    return { modules: newModules };
  }),
  deleteConnection: (moduleIndex, connectionIndex) => set((state) => {
    const newModules = [...state.modules];
    const newConnections = [...newModules[moduleIndex].connections];
    newConnections.splice(connectionIndex, 1);
    newModules[moduleIndex] = {
      ...newModules[moduleIndex],
      connections: newConnections
    };
    return { modules: newModules };
  }),
  exportModule: (moduleName) => {
    const { modules } = get();
    return modules.find(module => module.module_name === moduleName);
  },
  importModule: (module) => set((state) => {
    const existingIndex = state.modules.findIndex(m => m.module_name === module.module_name);
    const newModules = [...state.modules];
    if (existingIndex >= 0) {
      newModules[existingIndex] = module;
    } else {
      newModules.push(module);
    }
    return { modules: newModules };
  }),
  
  // 步骤 3: 全局状态定义
  stateDefinition: {
    variables: []
  },
  setGlobalState: (stateDefinition) => set({ stateDefinition }),
  
  // 步骤 4: 变量映射
  mappingDefinition: {
    mappings: []
  },
  setMapping: (mappingDefinition) => set({ mappingDefinition }),
  
  // 步骤 5: 高级配置
  advancedConfig: {
    persistence: false,
    human_in_the_loop: false
  },
  setAdvancedConfig: (config) => set({ advancedConfig: config }),
  
  // 代码生成
  generateCode: async () => {
    const state = get();
    try {
      const response = await fetch('http://localhost:8000/api/codegen/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          project_id: 'test_project',
          advanced_config: state.advancedConfig
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate code');
      }
      
      const result = await response.json();
      return {
        files: result.files || [],
        message: result.message || 'Code generated successfully',
        zip_file: result.zip_file
      };
    } catch (error) {
      console.error('Error generating code:', error);
      return { files: [], message: 'Error generating code' };
    }
  }
}));
