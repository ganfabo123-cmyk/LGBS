import React, { useState } from 'react';
import { useProjectStore } from '../../../store/useProjectStore';
import { validatePythonVariableName } from '../../../lib/utils';

const Step1: React.FC = () => {
  const project = useProjectStore((state) => state.project);
  const updateProjectInfo = useProjectStore((state) => state.updateProjectInfo);
  const setCurrentStep = useProjectStore((state) => state.setCurrentStep);
  
  const [errors, setErrors] = useState<{ name?: string }>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const newErrors: { name?: string } = {};
    if (!project.info.name) {
      newErrors.name = 'Project name is required';
    } else if (!validatePythonVariableName(project.info.name)) {
      newErrors.name = 'Project name must be a valid Python variable name';
    }
    
    setErrors(newErrors);
    
    if (Object.keys(newErrors).length === 0) {
      setCurrentStep(2);
    }
  };

  return (
    <div className="max-w-3xl">
      <h2 className="text-2xl font-bold mb-6 text-indigo-400">Step 1: Project Definition</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">Project Name</label>
          <input
            type="text"
            value={project.info.name}
            onChange={(e) => updateProjectInfo({ name: e.target.value })}
            className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100"
            placeholder="Enter project name"
          />
          {errors.name && <p className="mt-1 text-sm text-red-400">{errors.name}</p>}
        </div>
        
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">Description</label>
          <textarea
            value={project.info.description}
            onChange={(e) => updateProjectInfo({ description: e.target.value })}
            className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100"
            placeholder="Enter project description"
            rows={3}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">Initial Inputs</label>
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={project.info.initialInputs.join(', ')}
              onChange={(e) => updateProjectInfo({ initialInputs: e.target.value.split(',').map((i) => i.trim()) })}
              className="flex-1 px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100"
              placeholder="Enter initial inputs (comma separated)"
            />
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">Final Outputs</label>
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={project.info.finalOutputs.join(', ')}
              onChange={(e) => updateProjectInfo({ finalOutputs: e.target.value.split(',').map((o) => o.trim()) })}
              className="flex-1 px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100"
              placeholder="Enter final outputs (comma separated)"
            />
          </div>
        </div>
        
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => setCurrentStep(1)}
            className="px-4 py-2 bg-zinc-700 hover:bg-zinc-600 rounded-md text-zinc-100"
          >
            Back
          </button>
          <button
            type="submit"
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-md text-white font-medium"
          >
            Next
          </button>
        </div>
      </form>
    </div>
  );
};

export default Step1;
