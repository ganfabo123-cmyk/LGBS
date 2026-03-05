import React from 'react';
import { useProjectStore } from '../../store/useProjectStore';
import { Download, Upload, RefreshCw } from 'lucide-react';
import { downloadFile } from '../../lib/utils';

const Sidebar: React.FC = () => {
  const project = useProjectStore((state) => state.project);
  const resetProject = useProjectStore((state) => state.resetProject);

  const handleExport = () => {
    const jsonString = JSON.stringify(project, null, 2);
    downloadFile(jsonString, `${project.info.name || 'project'}.json`);
  };

  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const json = JSON.parse(event.target?.result as string);
          useProjectStore.getState().importProject(json);
        } catch (error) {
          alert('Invalid JSON file');
        }
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="w-64 bg-zinc-800 border-r border-zinc-700 p-4">
      <div className="mb-8">
        <h1 className="text-xl font-bold text-indigo-400 mb-2">LangGraph Builder</h1>
        <p className="text-zinc-400 text-sm">Create and manage LangGraph projects</p>
      </div>

      <div className="space-y-4">
        <div>
          <h2 className="text-sm font-medium text-zinc-400 mb-2">Project</h2>
          <div className="space-y-2">
            <button
              onClick={handleExport}
              className="w-full flex items-center gap-2 px-3 py-2 bg-zinc-700 hover:bg-zinc-600 rounded-md text-sm"
            >
              <Download size={16} />
              Export
            </button>
            <label className="w-full flex items-center gap-2 px-3 py-2 bg-zinc-700 hover:bg-zinc-600 rounded-md text-sm cursor-pointer">
              <Upload size={16} />
              Import
              <input type="file" accept=".json" className="hidden" onChange={handleImport} />
            </label>
            <button
              onClick={resetProject}
              className="w-full flex items-center gap-2 px-3 py-2 bg-zinc-700 hover:bg-zinc-600 rounded-md text-sm"
            >
              <RefreshCw size={16} />
              Reset
            </button>
          </div>
        </div>

        <div>
          <h2 className="text-sm font-medium text-zinc-400 mb-2">Project Info</h2>
          <div className="space-y-1 text-sm">
            <p className="text-zinc-400">Name: {project.info.name || 'Not set'}</p>
            <p className="text-zinc-400">Modules: {project.modules.length}</p>
            <p className="text-zinc-400">Global State: {project.globalState.length}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
