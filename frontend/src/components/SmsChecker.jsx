import React, { useState } from 'react';
import SmsScanResult from './SmsScanResult';
import { scanSms } from '../services/api';
import './CheckerStyles.css';

function SmsChecker() {
  const [smsText, setSmsText] = useState('');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const analyzeSms = async () => {
    if (!smsText.trim()) return;

    setIsLoading(true);
    setResult(null);

    try {
      const data = await scanSms(smsText);
      setResult(data);
    } catch (error) {
      setResult({
        error: true,
        message: 'Scan failed',
        details:
          error.response?.data?.message ||
          error.message ||
          'Could not connect to backend server.',
      });
    }
    finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="checker-container">
      <div className="checker-card">
        <div className="checker-header">
          <span className="checker-icon">SMS</span>
          <h1>SMS Phishing Checker</h1>
          <p>Analyze text messages for potential phishing attempts</p>
        </div>

        <div className="checker-content">
          <div className="input-section">
            <label>Enter SMS Content:</label>
            <textarea
              value={smsText}
              onChange={(e) => setSmsText(e.target.value)}
              placeholder="Paste the suspicious SMS message here..."
              rows="5"
              className="text-input"
            />
            <button
              onClick={analyzeSms}
              disabled={!smsText.trim() || isLoading}
              className="analyze-button"
            >
              {isLoading ? 'Analyzing...' : 'Analyze SMS'}
            </button>
          </div>

          <SmsScanResult result={result} />
        </div>
      </div>
    </div>
  );
}

export default SmsChecker;
