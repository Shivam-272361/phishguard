import React from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

function HomePage() {
  const navigate = useNavigate();

  const cards = [
    {
      id: 3,
      title: 'Web Scanner',
      description: 'Real-time neural analysis of suspicious URLs and domain reputation.',
      icon: '🕸️',
      path: '/url-checker',
      color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
    },
    {
      id: 1,
      title: 'SMS Verify',
      description: 'Protect yourself from Smishing by analyzing incoming text alerts.',
      icon: '📱',
      path: '/sms-checker',
      color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    {
      id: 2,
      title: 'Email Shield',
      description: 'Analyze headers and sender identity to detect sophisticated phishing attempts.',
      icon: '📧',
      path: '/email-checker',
      color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
    }
  ];

  return (
    <div className="homepage">
      <div className="hero-section">
        <h1 className="hero-title">
          Next-Gen <span className="gradient-text">Cyber Defense</span> for the Modern Web
        </h1>
        <p className="hero-subtitle">
          Advanced AI-powered protection against phishing, smishing, and malicious infrastructure. Verify any link or message before you act.
        </p>
      </div>

      <div className="cards-container">
        {cards.map((card) => (
          <div
            key={card.id}
            className="card"
            onClick={() => navigate(card.path)}
            style={{ '--card-color': card.color }}
          >
            <div className="card-icon">{card.icon}</div>
            <h2 className="card-title">{card.title}</h2>
            <p className="card-description">{card.description}</p>
            <button className="card-button">
              Check Now →
            </button>
          </div>
        ))}
      </div>

      <div className="stats-section">
        <div className="stat-item">
          <div className="stat-number">99.9%</div>
          <div className="stat-label">Accuracy Rate</div>
        </div>
        <div className="stat-item">
          <div className="stat-number">1M+</div>
          <div className="stat-label">Threats Blocked</div>
        </div>
        <div className="stat-item">
          <div className="stat-number">24/7</div>
          <div className="stat-label">Protection</div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;