import { create } from 'zustand';
import type { LGBSProject, Module, GraphNode, StateVariable } from '../types/project';

interface ProjectStore {
  project: LGBSProject;
  currentStep: number;
  setCurrentStep: (step: number) => void;
  updateProjectInfo: (info: Partial<LGBSProject['info']>) => void;
  addModule: (module: Module) => void;
  updateModule: (moduleId: string, module: Partial<Module>) => void;
  deleteModule: (moduleId: string) => void;
  addNode: (moduleId: string, node: GraphNode) => void;
  updateNode: (moduleId: string, nodeId: string, node: Partial<GraphNode>) => void;
  deleteNode: (moduleId: string, nodeId: string) => void;
  addStateVariable: (variable: StateVariable) => void;
  updateStateVariable: (variableId: string, variable: Partial<StateVariable>) => void;
  deleteStateVariable: (variableId: string) => void;
  setNodeIOMapping: (moduleId: string, nodeId: string, ioId: string, mappedStateId: string | undefined) => void;
  updateConfig: (config: Partial<LGBSProject['config']>) => void;
  importProject: (project: LGBSProject) => void;
  resetProject: () => void;
}

const initialProject: LGBSProject = {
  info: {
    name: '',
    description: '',
    initialInputs: [],
    finalOutputs: [],
  },
  globalState: [],
  modules: [],
  config: {
    useMemory: false,
    interruptBefore: [],
  },
};

export const useProjectStore = create<ProjectStore>((set) => ({
  project: initialProject,
  currentStep: 1,
  setCurrentStep: (step) => set({ currentStep: step }),
  updateProjectInfo: (info) =>
    set((state) => ({
      project: {
        ...state.project,
        info: {
          ...state.project.info,
          ...info,
        },
      },
    })),
  addModule: (module) =>
    set((state) => ({
      project: {
        ...state.project,
        modules: [...state.project.modules, module],
      },
    })),
  updateModule: (moduleId, module) =>
    set((state) => ({
      project: {
        ...state.project,
        modules: state.project.modules.map((m) =>
          m.id === moduleId ? { ...m, ...module } : m
        ),
      },
    })),
  deleteModule: (moduleId) =>
    set((state) => ({
      project: {
        ...state.project,
        modules: state.project.modules.filter((m) => m.id !== moduleId),
      },
    })),
  addNode: (moduleId, node) =>
    set((state) => ({
      project: {
        ...state.project,
        modules: state.project.modules.map((m) =>
          m.id === moduleId
            ? {
                ...m,
                nodes: [...m.nodes, node],
              }
            : m
        ),
      },
    })),
  updateNode: (moduleId, nodeId, node) =>
    set((state) => ({
      project: {
        ...state.project,
        modules: state.project.modules.map((m) =>
          m.id === moduleId
            ? {
                ...m,
                nodes: m.nodes.map((n) => (n.id === nodeId ? { ...n, ...node } : n)),
              }
            : m
        ),
      },
    })),
  deleteNode: (moduleId, nodeId) =>
    set((state) => ({
      project: {
        ...state.project,
        modules: state.project.modules.map((m) =>
          m.id === moduleId
            ? {
                ...m,
                nodes: m.nodes.filter((n) => n.id !== nodeId),
              }
            : m
        ),
      },
    })),
  addStateVariable: (variable) =>
    set((state) => ({
      project: {
        ...state.project,
        globalState: [...state.project.globalState, variable],
      },
    })),
  updateStateVariable: (variableId, variable) =>
    set((state) => ({
      project: {
        ...state.project,
        globalState: state.project.globalState.map((v) =>
          v.id === variableId ? { ...v, ...variable } : v
        ),
      },
    })),
  deleteStateVariable: (variableId) =>
    set((state) => ({
      project: {
        ...state.project,
        globalState: state.project.globalState.filter((v) => v.id !== variableId),
      },
    })),
  setNodeIOMapping: (moduleId, nodeId, ioId, mappedStateId) =>
    set((state) => ({
      project: {
        ...state.project,
        modules: state.project.modules.map((m) =>
          m.id === moduleId
            ? {
                ...m,
                nodes: m.nodes.map((n) =>
                  n.id === nodeId
                    ? {
                        ...n,
                        inputs: n.inputs.map((io) =>
                          io.id === ioId ? { ...io, mappedStateId } : io
                        ),
                        outputs: n.outputs.map((io) =>
                          io.id === ioId ? { ...io, mappedStateId } : io
                        ),
                      }
                    : n
                ),
              }
            : m
        ),
      },
    })),
  updateConfig: (config) =>
    set((state) => ({
      project: {
        ...state.project,
        config: {
          ...state.project.config,
          ...config,
        },
      },
    })),
  importProject: (project) => set({ project }),
  resetProject: () => set({ project: initialProject, currentStep: 1 }),
}));
