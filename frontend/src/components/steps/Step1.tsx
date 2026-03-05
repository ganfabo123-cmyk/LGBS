import React, { useState } from 'react';
import { useStore } from '../../store';

const Step1: React.FC = () => {
  const { appDefinition, setAppDefinition, modules, stateDefinition, mappingDefinition, advancedConfig } = useStore();
  const [inputs, setInputs] = useState<string[]>(appDefinition.initial_inputs);
  const [outputs, setOutputs] = useState<string[]>(appDefinition.final_outputs);
  const [newInput, setNewInput] = useState('');
  const [newOutput, setNewOutput] = useState('');
  const [importJson, setImportJson] = useState('');
  const [showImportModal, setShowImportModal] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setAppDefinition({
      ...appDefinition,
      [e.target.name]: e.target.value
    });
  };

  const handleAddInput = () => {
    if (newInput && !inputs.includes(newInput)) {
      const newInputs = [...inputs, newInput];
      setInputs(newInputs);
      setAppDefinition({
        ...appDefinition,
        initial_inputs: newInputs
      });
      setNewInput('');
    }
  };

  const handleRemoveInput = (input: string) => {
    const newInputs = inputs.filter(i => i !== input);
    setInputs(newInputs);
    setAppDefinition({
      ...appDefinition,
      initial_inputs: newInputs
    });
  };

  const handleAddOutput = () => {
    if (newOutput && !outputs.includes(newOutput)) {
      const newOutputs = [...outputs, newOutput];
      setOutputs(newOutputs);
      setAppDefinition({
        ...appDefinition,
        final_outputs: newOutputs
      });
      setNewOutput('');
    }
  };

  const handleRemoveOutput = (output: string) => {
    const newOutputs = outputs.filter(o => o !== output);
    setOutputs(newOutputs);
    setAppDefinition({
      ...appDefinition,
      final_outputs: newOutputs
    });
  };

  const handleExport = () => {
    const projectData = {
      appDefinition,
      modules,
      stateDefinition,
      mappingDefinition,
      advancedConfig
    };
    const jsonStr = JSON.stringify(projectData, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${appDefinition.app_name || 'project'}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImport = () => {
    try {
      const data = JSON.parse(importJson);
      if (data.appDefinition) setAppDefinition(data.appDefinition);
      if (data.modules) {
        data.modules.forEach((module: any) => {
          useStore.getState().importModule(module);
        });
      }
      if (data.stateDefinition) useStore.getState().setGlobalState(data.stateDefinition);
      if (data.mappingDefinition) useStore.getState().setMapping(data.mappingDefinition);
      if (data.advancedConfig) useStore.getState().setAdvancedConfig(data.advancedConfig);
      setShowImportModal(false);
      setImportJson('');
      alert('导入成功！');
    } catch (error) {
      alert('导入失败，请检查 JSON 格式');
    }
  };

  const handleFileImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const data = JSON.parse(event.target?.result as string);
          if (data.appDefinition) setAppDefinition(data.appDefinition);
          if (data.modules) {
            data.modules.forEach((module: any) => {
              useStore.getState().importModule(module);
            });
          }
          if (data.stateDefinition) useStore.getState().setGlobalState(data.stateDefinition);
          if (data.mappingDefinition) useStore.getState().setMapping(data.mappingDefinition);
          if (data.advancedConfig) useStore.getState().setAdvancedConfig(data.advancedConfig);
          alert('导入成功！');
        } catch (error) {
          alert('导入失败，请检查 JSON 格式');
        }
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="space-y-6">
      {/* Import/Export Buttons */}
      <div className="flex justify-end space-x-3 mb-6">
        <button
          onClick={() => setShowImportModal(true)}
          className="flex items-center px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          导入项目
        </button>
        <button
          onClick={handleExport}
          className="flex items-center px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          导出项目
        </button>
      </div>

      {/* App Name */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-100">
        <label className="block text-sm font-semibold text-slate-700 mb-2">应用名称</label>
        <input
          type="text"
          name="app_name"
          value={appDefinition.app_name}
          onChange={handleInputChange}
          className="w-full px-4 py-3 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-lg"
          placeholder="输入应用名称"
        />
      </div>

      {/* App Description */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <label className="block text-sm font-semibold text-slate-700 mb-2">应用描述</label>
        <textarea
          name="app_description"
          value={appDefinition.app_description}
          onChange={handleInputChange}
          className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
          placeholder="描述您的应用是做什么的..."
          rows={3}
        />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Initial Inputs */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
              <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16l-4-4m0 0l4-4m-4 4h18" />
              </svg>
            </div>
            <label className="text-sm font-semibold text-slate-700">初始输入参数</label>
          </div>
          <div className="flex space-x-2 mb-3">
            <input
              type="text"
              value={newInput}
              onChange={(e) => setNewInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddInput()}
              className="flex-1 px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              placeholder="输入参数名称"
            />
            <button
              onClick={handleAddInput}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {inputs.map((input, index) => (
              <div key={index} className="flex items-center space-x-2 bg-green-50 px-3 py-2 rounded-lg border border-green-200">
                <span className="text-green-800 font-medium">{input}</span>
                <button
                  onClick={() => handleRemoveInput(input)}
                  className="text-green-600 hover:text-green-800 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
            {inputs.length === 0 && (
              <span className="text-slate-400 text-sm italic">暂无输入参数</span>
            )}
          </div>
        </div>

        {/* Final Outputs */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center mr-3">
              <svg className="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </div>
            <label className="text-sm font-semibold text-slate-700">最终期望输出</label>
          </div>
          <div className="flex space-x-2 mb-3">
            <input
              type="text"
              value={newOutput}
              onChange={(e) => setNewOutput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddOutput()}
              className="flex-1 px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              placeholder="输入输出名称"
            />
            <button
              onClick={handleAddOutput}
              className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {outputs.map((output, index) => (
              <div key={index} className="flex items-center space-x-2 bg-orange-50 px-3 py-2 rounded-lg border border-orange-200">
                <span className="text-orange-800 font-medium">{output}</span>
                <button
                  onClick={() => handleRemoveOutput(output)}
                  className="text-orange-600 hover:text-orange-800 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
            {outputs.length === 0 && (
              <span className="text-slate-400 text-sm italic">暂无输出参数</span>
            )}
          </div>
        </div>
      </div>

      {/* Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-2xl mx-4 shadow-2xl">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-slate-800">导入项目</h3>
              <button
                onClick={() => setShowImportModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">选择 JSON 文件</label>
                <input
                  type="file"
                  accept=".json"
                  onChange={handleFileImport}
                  className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-200"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-slate-500">或者</span>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">粘贴 JSON 内容</label>
                <textarea
                  value={importJson}
                  onChange={(e) => setImportJson(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none font-mono text-sm"
                  placeholder="在此粘贴项目 JSON..."
                  rows={10}
                />
              </div>
              
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowImportModal(false)}
                  className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  取消
                </button>
                <button
                  onClick={handleImport}
                  className="px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all"
                >
                  导入
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Step1;
