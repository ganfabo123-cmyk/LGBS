import React from 'react';
import { useProjectStore } from '../../store/useProjectStore';

const ProgressBar: React.FC = () => {
  const currentStep = useProjectStore((state) => state.currentStep);
  const setCurrentStep = useProjectStore((state) => state.setCurrentStep);
  const project = useProjectStore((state) => state.project);

  const steps = [
    { id: 1, label: 'Definition' },
    { id: 2, label: 'Modules' },
    { id: 3, label: 'State' },
    { id: 4, label: 'Mapping' },
    { id: 5, label: 'Generation' },
  ];

  const canNavigateToStep = (step: number): boolean => {
    if (step === 1) return true;
    if (step === 2 && project.info.name) return true;
    if (step === 3 && project.modules.length > 0) return true;
    if (step === 4 && project.globalState.length > 0) return true;
    if (step === 5 && project.modules.length > 0) return true;
    return false;
  };

  return (
    <div className="bg-zinc-800 border-b border-zinc-700 py-4 px-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-8">
          {steps.map((step) => (
            <button
              key={step.id}
              onClick={() => {
                if (canNavigateToStep(step.id)) {
                  setCurrentStep(step.id);
                }
              }}
              className={`flex flex-col items-center cursor-pointer ${canNavigateToStep(step.id) ? 'hover:opacity-100' : 'opacity-50 cursor-not-allowed'}`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center mb-1 ${currentStep >= step.id ? 'bg-indigo-500' : 'bg-zinc-700'}`}>
                {step.id}
              </div>
              <span className={`text-xs ${currentStep >= step.id ? 'text-indigo-400' : 'text-zinc-400'}`}>
                {step.label}
              </span>
            </button>
          ))}
        </div>
        <div className="text-sm text-zinc-400">
          Step {currentStep} of 5
        </div>
      </div>
    </div>
  );
};

export default ProgressBar;
