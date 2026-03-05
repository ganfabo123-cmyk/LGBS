import React, { useState } from 'react';
import { useProjectStore } from '../../../store/useProjectStore';
import { generateProjectZip } from '../../../lib/code-gen';

const Step5: React.FC = () => {
  const project = useProjectStore((state) => state.project);
  const updateConfig = useProjectStore((state) => state.updateConfig);
  const setCurrentStep = useProjectStore((state) => state.setCurrentStep);
  
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    setSuccess(null);
    
    try {
      console.log('Starting code generation...');
      const zipBlob = await generateProjectZip(project);
      console.log('Code generation completed, creating download link...');
      
      const url = URL.createObjectURL(zipBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${project.info.name || 'project'}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      setSuccess('Project generated successfully!');
      console.log('Project downloaded successfully');
    } catch (error) {
      console.error('Error generating project:', error);
      setError('Failed to generate project. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-5xl">
      <h2 className="text-2xl font-bold mb-6 text-indigo-400">Step 5: Code Generation</h2>
      
      <div className="mb-8">
        <h3 className="text-lg font-medium mb-4 text-zinc-300">Project Configuration</h3>
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <input
              type="checkbox"
              checked={project.config.useMemory}
              onChange={(e) => updateConfig({ useMemory: e.target.checked })}
              className="w-4 h-4 text-indigo-600 rounded"
            />
            <label className="text-zinc-300">Use Memory</label>
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">Interrupt Before (node IDs)</label>
            <input
              type="text"
              value={project.config.interruptBefore.join(', ')}
              onChange={(e) => updateConfig({ interruptBefore: e.target.value.split(',').map((id) => id.trim()) })}
              className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100"
              placeholder="Enter node IDs (comma separated)"
            />
          </div>
        </div>
      </div>
      
      <div className="mb-8">
        <h3 className="text-lg font-medium mb-4 text-zinc-300">Generated Files</h3>
        <div className="bg-zinc-800 border border-zinc-700 rounded-md p-4">
          <ul className="space-y-2 text-zinc-300">
            <li>state.py - Global state definition</li>
            <li>tools.py - Tool function stubs</li>
            {project.modules.map((module) => (
              <li key={module.id}>{module.name.replace(/\s+/g, '_').toLowerCase()}_graph.py - Module graph implementation</li>
            ))}
            <li>main_graph.py - Main graph orchestration</li>
            <li>requirements.txt - Dependencies</li>
          </ul>
        </div>
      </div>
      
      {error && (
        <div className="mb-8 p-4 bg-red-900/30 border border-red-700 rounded-md text-red-300">
          {error}
        </div>
      )}
      
      {success && (
        <div className="mb-8 p-4 bg-green-900/30 border border-green-700 rounded-md text-green-300">
          {success}
        </div>
      )}
      
      <div className="flex justify-end space-x-4">
        <button
          onClick={() => setCurrentStep(4)}
          className="px-4 py-2 bg-zinc-700 hover:bg-zinc-600 rounded-md text-zinc-100"
        >
          Back
        </button>
        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className={`px-4 py-2 rounded-md font-medium ${isGenerating ? 'bg-zinc-700 text-zinc-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-500 text-white'}`}
        >
          {isGenerating ? 'Generating...' : 'Generate & Download'}
        </button>
      </div>
    </div>
  );
};

export default Step5;
