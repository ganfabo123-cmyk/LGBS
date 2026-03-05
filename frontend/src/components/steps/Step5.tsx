import React, { useState } from 'react';
import { useStore } from '../../store';

const Step5: React.FC = () => {
  const { advancedConfig, setAdvancedConfig, generateCode } = useStore();
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationResult, setGenerationResult] = useState<{ files: string[]; message: string; project_path?: string; zip_path?: string } | null>(null);

  const handleConfigChange = (key: keyof typeof advancedConfig, value: boolean) => {
    setAdvancedConfig({
      ...advancedConfig,
      [key]: value
    });
  };

  const handleGenerateCode = async () => {
    setIsGenerating(true);
    try {
      const result = await generateCode();
      setGenerationResult(result);
    } catch (error) {
      console.error('Error generating code:', error);
      setGenerationResult({ files: [], message: '生成代码失败，请检查后端服务是否运行' });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold mb-4">Step 5: 高级配置与代码生成</h2>
      
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-medium mb-2">高级配置</h3>
          <div className="border border-gray-200 rounded-md p-4 space-y-3">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="persistence"
                checked={advancedConfig.persistence}
                onChange={(e) => handleConfigChange('persistence', e.target.checked)}
              />
              <label htmlFor="persistence" className="font-medium">持久化配置 (Memory/Checkpointer)</label>
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="human_in_the_loop"
                checked={advancedConfig.human_in_the_loop}
                onChange={(e) => handleConfigChange('human_in_the_loop', e.target.checked)}
              />
              <label htmlFor="human_in_the_loop" className="font-medium">Human-in-the-loop (中断确认机制)</label>
            </div>
          </div>
        </div>
        
        <div>
          <h3 className="text-lg font-medium mb-2">代码生成</h3>
          <div className="border border-gray-200 rounded-md p-4 space-y-3">
            <button
              onClick={handleGenerateCode}
              disabled={isGenerating}
              className="px-6 py-3 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400"
            >
              {isGenerating ? '生成中...' : '一键生成代码'}
            </button>
            
            {generationResult && (
              <div className="mt-4 space-y-2">
                <h4 className="font-medium">生成结果</h4>
                <p className="text-sm">{generationResult.message}</p>
                {generationResult.files.length > 0 && (
                  <div className="mt-2">
                    <h5 className="text-sm font-medium">生成的文件：</h5>
                    <ul className="text-sm space-y-1">
                      {generationResult.files.map((file, index) => (
                        <li key={index}>{file}</li>
                      ))}
                    </ul>
                    {generationResult.project_path && (
                      <div className="mt-3 p-3 bg-gray-100 rounded-md">
                        <h5 className="text-sm font-medium mb-1">项目路径：</h5>
                        <p className="text-sm text-gray-700 font-mono">{generationResult.project_path}</p>
                      </div>
                    )}
                    {generationResult.zip_path && (
                      <div className="mt-2 p-3 bg-gray-100 rounded-md">
                        <h5 className="text-sm font-medium mb-1">ZIP 文件路径：</h5>
                        <p className="text-sm text-gray-700 font-mono">{generationResult.zip_path}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Step5;
