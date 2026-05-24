import React, { useState } from 'react';
import { scanEmail } from '../services/api';
import EmailScanResult from './EmailScanResult';
import './CheckerStyles.css';

function EmailChecker() {
  const [activeTab, setActiveTab] = useState('content');
  const [emailContent, setEmailContent] = useState('');
  const [emailAddress, setEmailAddress] = useState('');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const analyzeEmail = async () => {
    const content = activeTab === 'content' ? emailContent : emailAddress;
    if (!content.trim()) return;

    setIsLoading(true);
    setResult(null);

    try {
      const response = await scanEmail(content, activeTab);
      console.log('Active Tab:', activeTab);
      
      // Check if response has data property (axios wraps response in data)
      const data = response.data || response;
      
      if (activeTab === 'address') {
        // For address mode, the response structure is different
        // It comes with urlAnalysis at the top level
        const riskPercent = data.urlAnalysis?.prediction?.risk_score || 0;
        let verdict = 'Legitimate Identity Detected';
        let riskLvl = 'safe';

        if (riskPercent > 70) {
          verdict = 'High-Risk Phishing Identity';
          riskLvl = 'danger';
        } else if (riskPercent > 40) {
          verdict = 'Suspicious Identity Detected';
          riskLvl = 'warning';
        } else if (riskPercent > 15) {
          verdict = 'Low Suspicion Detected';
          riskLvl = 'caution';
        }

        setResult({
          ...data,
          mode: 'address',
          emailAddress: content,
          score: Math.round(riskPercent),
          isPhishing: riskPercent > 40,
          riskLevel: riskLvl,
          message: verdict,
          indicators: data.reasons || data.urlAnalysis?.reasons || [],
        });
      } else {
        // For content mode
        setResult({
          ...data,
          mode: 'content',
        });
      }
      
      console.log('Set result with mode:', activeTab);
    } catch (error) {
      console.error('Scan error:', error);
      setResult({
        mode: activeTab,
        isPhishing: true,
        confidence: 0,
        message: 'Scan failed',
        details: error.message || 'Could not connect to the backend server.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="checker-container">
      <div className="checker-card">
        <div className="checker-header">
          <span className="checker-icon">EMAIL</span>
          <h1>Email Phishing Checker</h1>
          <p>Check email content and sender addresses for phishing attempts</p>
        </div>

        <div className="checker-content">
          <div className="tab-buttons">
            <button
              className={`tab-button ${activeTab === 'content' ? 'active' : ''}`}
              onClick={() => {
                setActiveTab('content');
                setResult(null);
              }}
            >
              Email Content
            </button>
            <button
              className={`tab-button ${activeTab === 'address' ? 'active' : ''}`}
              onClick={() => {
                setActiveTab('address');
                setResult(null);
              }}
            >
              Email Address
            </button>
          </div>

          {activeTab === 'content' ? (
            <div className="input-section">
              <label>Enter Email Content:</label>
              <textarea
                value={emailContent}
                onChange={(e) => setEmailContent(e.target.value)}
                placeholder="Paste the email body and subject here..."
                rows="6"
                className="text-input"
              />
            </div>
          ) : (
            <div className="input-section">
              <label>Enter Sender's Email Address:</label>
              <input
                type="email"
                value={emailAddress}
                onChange={(e) => setEmailAddress(e.target.value)}
                placeholder="e.g., suspicious@example.com"
                className="text-input"
              />
            </div>
          )}

          <button
            onClick={analyzeEmail}
            disabled={isLoading || !(activeTab === 'content' ? emailContent : emailAddress).trim()}
            className="analyze-button"
          >
            {isLoading ? 'Analyzing...' : 'Check Email'}
          </button>

          <EmailScanResult result={result} title="Email scan" />
        </div>
      </div>
    </div>
  );
}

export default EmailChecker;