import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import SafetyAnalysis from './components/SafetyAnalysis';
import CrackDetection from './components/CrackDetection';
import PropertyValuation from './components/PropertyValuation';
import ProjectPlanner from './components/ProjectPlanner';
import AIAssistant from './components/AIAssistant';

function App() {
  const [activePage, setActivePage] = useState('dashboard');

  const renderActivePage = () => {
    const page = (activePage || '').toLowerCase();

    switch (page) {
      case 'dashboard':
        return <Dashboard onNavigate={setActivePage} />;
      case 'safety analysis':
      case 'safety':
      case 'safetyanalysis':
        return <SafetyAnalysis />;
      case 'crack detection':
      case 'crack':
      case 'crackdetection':
        return <CrackDetection />;
      case 'property valuation':
      case 'valuation':
      case 'propertyvaluation':
        return <PropertyValuation />;
      case 'project planner':
      case 'planner':
      case 'planning':
      case 'projectplanner':
        return <ProjectPlanner />;
      case 'ai assistant':
      case 'assistant':
      case 'chat':
      case 'aiassistant':
        return <AIAssistant />;
      default:
        return <Dashboard onNavigate={setActivePage} />;
    }
  };

  return (
    <div className="app-layout">
      <Sidebar activePage={activePage} onNavigate={setActivePage} />
      <main className="main-content">
        {renderActivePage()}
      </main>
    </div>
  );
}

export default App;
