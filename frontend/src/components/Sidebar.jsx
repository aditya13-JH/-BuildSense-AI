import React from 'react';

function Sidebar({ activePage, onNavigate }) {
  const menuItems = [
    { name: 'Dashboard', icon: '📊' },
    { name: 'Safety Analysis', icon: '🦺' },
    { name: 'Crack Detection', icon: '🔍' },
    { name: 'Property Valuation', icon: '💰' },
    { name: 'Project Planner', icon: '📋' },
    { name: 'AI Assistant', icon: '🤖' },
  ];

  const handleItemClick = (pageName) => {
    if (onNavigate) {
      onNavigate(pageName);
    }
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h2>🏗️ BuildSense AI</h2>
        <p>Construction Intelligence</p>
      </div>

      <ul className="sidebar-menu">
        {menuItems.map((item) => {
          const isActive =
            activePage === item.name ||
            activePage?.toLowerCase() === item.name.toLowerCase();

          return (
            <li
              key={item.name}
              className={`sidebar-item ${isActive ? 'active' : ''}`.trim()}
              onClick={() => handleItemClick(item.name)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  handleItemClick(item.name);
                }
              }}
            >
              <span className="sidebar-icon">{item.icon}</span>
              <span className="sidebar-label">{item.name}</span>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}

export default Sidebar;
