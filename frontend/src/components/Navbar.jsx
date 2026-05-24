import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
  const location = useLocation();

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          <span className="logo-icon">🛡️</span>
          <span className="logo-text">Phish<span className="logo-accent" style={{ color: '#4facfe' }}>Guard</span></span>
        </Link>
        
        <div className="nav-links">
          <Link 
            to="/" 
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
          >
            Dashboard
          </Link>
          <Link 
            to="/url-checker" 
            className={`nav-link ${location.pathname === '/url-checker' ? 'active' : ''}`}
          >
            Web Scanner
          </Link>
          <Link 
            to="/sms-checker" 
            className={`nav-link ${location.pathname === '/sms-checker' ? 'active' : ''}`}
          >
            SMS Verify
          </Link>
          <Link 
            to="/email-checker" 
            className={`nav-link ${location.pathname === '/email-checker' ? 'active' : ''}`}
          >
            Email Shield
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;