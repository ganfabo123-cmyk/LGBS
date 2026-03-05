import React, { useState } from 'react';
import { useProjectStore } from '../../../store/useProjectStore';
import { generateId } from '../../../lib/utils';
import ModuleCard from './ModuleCard';

const Step2: React.FC = () => {
  const modules = useProjectStore((state) => state.project.modules);
  const addModule = useProjectStore((state) => state.addModule);
  const setCurrentStep = useProjectStore((state) => state.setCurrentStep);
  
  const [newModuleName, setNewModuleName] = useState('');
  const [newModuleDescription, setNewModuleDescription] = useState('');

  const handleAddModule = () => {
    if (newModuleName) {
      addModule({
        id: generateId(),
        name: newModuleName,
        description: newModuleDescription,
        inputs: [],
        outputs: [],
        nodes: [],
      });
      setNewModuleName('');
      setNewModuleDescription('');
    }
  };

  return (
    <div className="max-w-5xl">
      <h2 className="text-2xl font-bold mb-6 text-indigo-400">Step 2: Modules</h2>
      
      <div className="mb-8">
        <h3 className="text-lg font-medium mb-4 text-zinc-300">Add New Module</h3>
        <div className="flex space-x-4">
          <input
            type="text"
            value={newModuleName}
            onChange={(e) => setNewModuleName(e.target.value)}
            className="flex-1 px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100"
            placeholder="Module name"
          />
          <input
            type="text"
            value={newModuleDescription}
            onChange={(e) => setNewModuleDescription(e.target.value)}
            className="flex-1 px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100"
            placeholder="Module description"
          />
          <button
            onClick={handleAddModule}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-md text-white font-medium"
          >
            Add
          </button>
        </div>
      </div>
      
      <div className="space-y-6">
        {modules.length === 0 ? (
          <div className="text-center py-12 bg-zinc-800 border border-zinc-700 rounded-md">
            <p className="text-zinc-400">No modules added yet</p>
            <p className="text-zinc-500 text-sm mt-2">Click "Add" to create your first module</p>
          </div>
        ) : (
          modules.map((module) => (
            <ModuleCard key={module.id} module={module} allModules={modules} />
          ))
        )}
      </div>
      
      <div className="mt-8 flex justify-end space-x-4">
        <button
          onClick={() => setCurrentStep(1)}
          className="px-4 py-2 bg-zinc-700 hover:bg-zinc-600 rounded-md text-zinc-100"
        >
          Back
        </button>
        <button
          onClick={() => setCurrentStep(3)}
          disabled={modules.length === 0}
          className={`px-4 py-2 rounded-md font-medium ${modules.length === 0 ? 'bg-zinc-700 text-zinc-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-500 text-white'}`}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default Step2;
