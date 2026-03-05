import React, { useEffect } from 'react';
import { useProjectStore } from '../../../store/useProjectStore';


const Step4: React.FC = () => {
  const project = useProjectStore((state) => state.project);
  const setNodeIOMapping = useProjectStore((state) => state.setNodeIOMapping);
  const setCurrentStep = useProjectStore((state) => state.setCurrentStep);

  // Auto-map variables with matching names
  useEffect(() => {
    project.modules.forEach((module) => {
      module.nodes.forEach((node) => {
        node.inputs.forEach((input) => {
          const matchingState = project.globalState.find((state) => state.name === input.localName);
          if (matchingState && !input.mappedStateId) {
            setNodeIOMapping(module.id, node.id, input.id, matchingState.id);
          }
        });
        node.outputs.forEach((output) => {
          const matchingState = project.globalState.find((state) => state.name === output.localName);
          if (matchingState && !output.mappedStateId) {
            setNodeIOMapping(module.id, node.id, output.id, matchingState.id);
          }
        });
      });
    });
  }, [project, setNodeIOMapping]);

  const handleMappingChange = (moduleId: string, nodeId: string, ioId: string, mappedStateId: string | undefined) => {
    setNodeIOMapping(moduleId, nodeId, ioId, mappedStateId);
  };

  return (
    <div className="max-w-6xl">
      <h2 className="text-2xl font-bold mb-6 text-indigo-400">Step 4: Variable Mapping</h2>
      
      <div className="space-y-8">
        {project.modules.map((module) => (
          <div key={module.id} className="bg-zinc-800 border border-zinc-700 rounded-md p-4">
            <h3 className="text-lg font-medium text-indigo-400 mb-4">{module.name}</h3>
            
            {module.nodes.map((node) => (
              <div key={node.id} className="mb-6">
                <h4 className="font-medium text-zinc-300 mb-3">{node.name} ({node.type.toUpperCase()})</h4>
                
                <div className="space-y-4">
                  <div>
                    <h5 className="text-sm font-medium text-zinc-400 mb-2">Inputs</h5>
                    <div className="space-y-2">
                      {node.inputs.map((input) => (
                        <div key={input.id} className="flex items-center space-x-4">
                          <span className="w-32 text-zinc-300">{input.localName}</span>
                          <select
                            value={input.mappedStateId || ''}
                            onChange={(e) => handleMappingChange(module.id, node.id, input.id, e.target.value || undefined)}
                            className="flex-1 px-3 py-2 bg-zinc-700 border border-zinc-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100"
                          >
                            <option value="">Select global state</option>
                            {project.globalState.map((state) => (
                              <option key={state.id} value={state.id}>
                                {state.name} ({state.type})
                              </option>
                            ))}
                          </select>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h5 className="text-sm font-medium text-zinc-400 mb-2">Outputs</h5>
                    <div className="space-y-2">
                      {node.outputs.map((output) => (
                        <div key={output.id} className="flex items-center space-x-4">
                          <span className="w-32 text-zinc-300">{output.localName}</span>
                          <select
                            value={output.mappedStateId || ''}
                            onChange={(e) => handleMappingChange(module.id, node.id, output.id, e.target.value || undefined)}
                            className="flex-1 px-3 py-2 bg-zinc-700 border border-zinc-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100"
                          >
                            <option value="">Select global state</option>
                            {project.globalState.map((state) => (
                              <option key={state.id} value={state.id}>
                                {state.name} ({state.type})
                              </option>
                            ))}
                          </select>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
      
      <div className="mt-8 flex justify-end space-x-4">
        <button
          onClick={() => setCurrentStep(3)}
          className="px-4 py-2 bg-zinc-700 hover:bg-zinc-600 rounded-md text-zinc-100"
        >
          Back
        </button>
        <button
          onClick={() => setCurrentStep(5)}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-md text-white font-medium"
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default Step4;
