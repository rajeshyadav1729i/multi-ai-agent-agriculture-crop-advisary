import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import DashboardPage from './pages/DashboardPage';
import NewAdvisoryPage from './pages/NewAdvisoryPage';
import ControlRoomPage from './pages/ControlRoomPage';
import FinalAdvisoryPage from './pages/FinalAdvisoryPage';
import SchemesPage from './pages/SchemesPage';
import HistoryPage from './pages/HistoryPage';
import SettingsPage from './pages/SettingsPage';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [currentRequestId, setCurrentRequestId] = useState('demo-wheat-ludhiana-01');

  const handleAdvisoryCreated = (requestId) => {
    setCurrentRequestId(requestId);
    setActiveTab('control_room');
  };

  const handleSelectAdvisory = (requestId) => {
    setCurrentRequestId(requestId);
    setActiveTab('final_advisory');
  };

  const renderActivePage = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <DashboardPage
            onNavigate={setActiveTab}
            onSelectAdvisory={handleSelectAdvisory}
          />
        );
      case 'new_advisory':
        return (
          <NewAdvisoryPage
            onAdvisoryCreated={handleAdvisoryCreated}
          />
        );
      case 'control_room':
        return (
          <ControlRoomPage
            requestId={currentRequestId}
            onSelectFinalAdvisory={handleSelectAdvisory}
          />
        );
      case 'final_advisory':
        return (
          <FinalAdvisoryPage
            requestId={currentRequestId}
            onNavigate={setActiveTab}
          />
        );
      case 'schemes':
        return <SchemesPage />;
      case 'history':
        return (
          <HistoryPage
            onSelectAdvisory={handleSelectAdvisory}
          />
        );
      case 'settings':
        return <SettingsPage />;
      default:
        return (
          <DashboardPage
            onNavigate={setActiveTab}
            onSelectAdvisory={handleSelectAdvisory}
          />
        );
    }
  };

  return (
    <div className="flex h-screen bg-slate-100 overflow-hidden font-sans text-slate-800">
      {/* Dark Green Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        currentRequestId={currentRequestId}
      />

      {/* Main Content Pane */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Navbar
          activeTab={activeTab}
        />

        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          {renderActivePage()}
        </main>
      </div>
    </div>
  );
}
