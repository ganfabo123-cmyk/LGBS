import type { LGBSProject, NodeIO } from '../types/project';

export const getUnmappedVariables = (project: LGBSProject): NodeIO[] => {
  const unmapped: NodeIO[] = [];
  
  project.modules.forEach((module) => {
    module.nodes.forEach((node) => {
      node.inputs.forEach((input) => {
        if (!input.mappedStateId) {
          unmapped.push({ ...input, nodeId: node.id, moduleId: module.id, ioType: 'input' });
        }
      });
      node.outputs.forEach((output) => {
        if (!output.mappedStateId) {
          unmapped.push({ ...output, nodeId: node.id, moduleId: module.id, ioType: 'output' });
        }
      });
    });
  });
  
  return unmapped;
};

export const getStateVariablesByName = (project: LGBSProject) => {
  return project.globalState.reduce((acc, variable) => {
    acc[variable.name] = variable;
    return acc;
  }, {} as Record<string, typeof project.globalState[0]>);
};

export const getNodesByModule = (project: LGBSProject) => {
  return project.modules.reduce((acc, module) => {
    acc[module.id] = module.nodes;
    return acc;
  }, {} as Record<string, typeof project.modules[0]['nodes']>);
};
