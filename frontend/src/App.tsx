
import Layout from './components/layout/Layout';
import Step1 from './components/steps/step1-definition/Step1';
import Step2 from './components/steps/step2-modules/Step2';
import Step3 from './components/steps/step3-state/Step3';
import Step4 from './components/steps/step4-mapping/Step4';
import Step5 from './components/steps/step5-generation/Step5';
import { useProjectStore } from './store/useProjectStore';
import './App.css';

function App() {
  const currentStep = useProjectStore((state) => state.currentStep);

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <Step1 />;
      case 2:
        return <Step2 />;
      case 3:
        return <Step3 />;
      case 4:
        return <Step4 />;
      case 5:
        return <Step5 />;
      default:
        return <Step1 />;
    }
  };

  return (
    <Layout>
      {renderStep()}
    </Layout>
  );
}

export default App;
