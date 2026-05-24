import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './components/HomePage';
import SmsChecker from './components/SmsChecker';
import EmailChecker from './components/EmailChecker';
import UrlChecker from './components/UrlChecker';
import WebsiteChecker from './components/WebsiteChecker';
import AdminDashboard from './pages/AdminDashboard';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/sms-checker" element={<SmsChecker />} />
          <Route path="/email-checker" element={<EmailChecker />} />
          <Route path="/url-checker" element={<UrlChecker />} />
          <Route path="/website-checker" element={<WebsiteChecker />} />
          <Route path="/admin" element={<AdminDashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;