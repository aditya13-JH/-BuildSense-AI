import React from 'react';

function Dashboard({ onNavigate }) {
  const cards = [
    {
      title: 'Safety Analysis',
      description: 'AI-powered site safety inspection',
      icon: '🦺',
      page: 'Safety Analysis',
    },
    {
      title: 'Crack Detection',
      description: 'Structural damage assessment',
      icon: '🔍',
      page: 'Crack Detection',
    },
    {
      title: 'Property Valuation',
      description: 'Smart property estimation',
      icon: '💰',
      page: 'Property Valuation',
    },
    {
      title: 'AI Assistant',
      description: 'Ask construction questions',
      icon: '🤖',
      page: 'AI Assistant',
    },
  ];

  const handleCardClick = (page) => {
    if (onNavigate) {
      onNavigate(page);
    }
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Welcome to BuildSense AI</h1>
        <p>Your Construction Intelligence Platform</p>
      </header>

      <div className="stat-cards">
        {cards.map((card) => (
          <div
            key={card.title}
            className="stat-card"
            onClick={() => handleCardClick(card.page)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                handleCardClick(card.page);
              }
            }}
          >
            <div className="stat-card-icon">{card.icon}</div>
            <div className="stat-card-info">
              <h3>{card.title}</h3>
              <p>{card.description}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="quick-start">
        <h2>Quick Start Guide</h2>
        <ol>
          <li>
            <strong>Select a Tool:</strong> Choose an analysis module from the cards above or use the sidebar navigation.
          </li>
          <li>
            <strong>Upload Your Data:</strong> Upload site inspection photos, concrete surface images, or property details.
          </li>
          <li>
            <strong>Generate AI Insights:</strong> Click analyze to review intelligent diagnostics, safety recommendations, and reports.
          </li>
        </ol>
      </div>
    </div>
  );
}

export default Dashboard;
