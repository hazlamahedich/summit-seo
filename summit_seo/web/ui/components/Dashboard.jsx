import React, { useState } from 'react';
import Navigation from './Navigation';

/**
 * Main Dashboard component that displays SEO analysis results
 * Follows accessibility guidelines with proper headings, focus management,
 * semantic HTML structure, and screen reader considerations
 */
const Dashboard = () => {
  const [activeNavItem, setActiveNavItem] = useState('dashboard');
  const [loaded, setLoaded] = useState(true);
  
  // Sample data for the dashboard
  const scoreData = {
    overall: 78,
    categories: [
      { name: 'SEO', score: 82, color: 'success' },
      { name: 'Accessibility', score: 68, color: 'warning' },
      { name: 'Performance', score: 91, color: 'success' },
      { name: 'Best Practices', score: 75, color: 'warning' },
      { name: 'Security', score: 64, color: 'danger' }
    ],
    recentAnalyses: [
      { id: 1, url: 'https://example.com', date: '2023-04-15', score: 78 },
      { id: 2, url: 'https://example.com/about', date: '2023-04-14', score: 65 },
      { id: 3, url: 'https://example.com/services', date: '2023-04-13', score: 92 },
    ]
  };
  
  // Handle navigation item changes
  const handleNavigate = (itemId) => {
    setLoaded(false);
    // Simulating loading content
    setTimeout(() => {
      setActiveNavItem(itemId);
      setLoaded(true);
    }, 300);
  };
  
  // Render category score card
  const renderCategoryCard = (category, index) => (
    <div 
      key={index} 
      className={`card category-card bg-${category.color}-light`}
      aria-labelledby={`category-heading-${index}`}
    >
      <h3 id={`category-heading-${index}`} className="card-title">{category.name}</h3>
      <div className="score-display" aria-label={`Score: ${category.score} out of 100`}>
        <div className="score-value">
          {category.score}
          <span className="score-max" aria-hidden="true">/100</span>
        </div>
      </div>
      <div 
        className={`progress-bar progress-${category.color}`}
        role="progressbar"
        aria-valuenow={category.score}
        aria-valuemin="0"
        aria-valuemax="100"
        style={{ width: `${category.score}%` }}
      >
        <span className="sr-only">{category.score}%</span>
      </div>
    </div>
  );
  
  // Render content for the dashboard
  const renderDashboardContent = () => (
    <>
      <section className="overview-section" aria-labelledby="overview-heading">
        <h2 id="overview-heading" className="section-heading">Overview</h2>
        <div className="card main-score-card">
          <div className="main-score-display">
            <div className="score-circle" aria-label={`Overall score: ${scoreData.overall} out of 100`}>
              <div className="score-circle-inner">
                <div className="score-value">{scoreData.overall}</div>
                <div className="score-label">Overall Score</div>
              </div>
            </div>
          </div>
          <div className="main-score-details">
            <p>Your site's SEO health is <strong>Good</strong>. There are some improvements that could boost your rank.</p>
            <button className="button button-primary">View Detailed Report</button>
          </div>
        </div>
      </section>
      
      <section className="categories-section" aria-labelledby="categories-heading">
        <h2 id="categories-heading" className="section-heading">Category Scores</h2>
        <div className="grid-3">
          {scoreData.categories.map(renderCategoryCard)}
        </div>
      </section>
      
      <section className="recent-section" aria-labelledby="recent-heading">
        <h2 id="recent-heading" className="section-heading">Recent Analyses</h2>
        <div className="card">
          <table className="data-table">
            <caption className="sr-only">Recent SEO Analyses</caption>
            <thead>
              <tr>
                <th scope="col">URL</th>
                <th scope="col">Date</th>
                <th scope="col">Score</th>
                <th scope="col"><span className="sr-only">Actions</span></th>
              </tr>
            </thead>
            <tbody>
              {scoreData.recentAnalyses.map(analysis => (
                <tr key={analysis.id}>
                  <td>{analysis.url}</td>
                  <td>{analysis.date}</td>
                  <td>
                    <span className="pill-score">{analysis.score}</span>
                  </td>
                  <td>
                    <button 
                      className="button button-sm button-secondary"
                      aria-label={`View details for ${analysis.url}`}
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
  
  // Render content based on active navigation item
  const renderContent = () => {
    switch (activeNavItem) {
      case 'dashboard':
        return renderDashboardContent();
      case 'projects':
        return <h2>Projects</h2>;
      case 'analyses':
        return <h2>Analyses</h2>;
      case 'reports':
        return <h2>Reports</h2>;
      case 'settings':
        return <h2>Settings</h2>;
      default:
        return <h2>Dashboard</h2>;
    }
  };
  
  return (
    <div className="dashboard-container">
      <Navigation 
        activeItem={activeNavItem} 
        onNavigate={handleNavigate} 
      />
      
      <main id="main-content" className="main-content" tabIndex="-1">
        {/* Loading state with aria-live for screen readers */}
        {!loaded ? (
          <div className="loading-indicator" aria-live="polite">
            <span className="sr-only">Loading content...</span>
            <div className="spinner" aria-hidden="true"></div>
          </div>
        ) : (
          renderContent()
        )}
      </main>
    </div>
  );
};

export default Dashboard; 