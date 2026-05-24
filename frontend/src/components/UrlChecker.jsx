import React, { useState } from 'react';
import ScanResult from './ScanResult';
import { checkReputation } from '../services/api';
import './CheckerStyles.css';

function UrlChecker() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const analyzeUrl = async () => {
    if (!url.trim()) return;

    setIsLoading(true);
    setResult(null);
    setPreview(null);

    try {
      const data = await checkReputation(url);
      setResult(data);
      setPreview(data.preview);
    } catch (error) {
      setResult({
        isPhishing: true,
        confidence: 0,
        message: 'Scan failed',
        details: error.message || 'Could not connect to the backend server.',
        urlAnalysis: {
          domain: 'Unknown',
          hasHTTPs: false,
          length: url.length,
        },
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="checker-container">
      <div className="checker-card">
        <div className="checker-header">
          <span className="checker-icon">🛡️</span>
          <h1>Web Intelligence Scanner</h1>
          <p>Deploying multi-layered AI verification for suspicious domains and infrastructure.</p>
        </div>

        <div className="checker-content">
          <div className="input-section">
            <label>ENTER TARGET URL</label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/suspicious-link"
              className="text-input"
            />
            <button
              onClick={analyzeUrl}
              disabled={!url.trim() || isLoading}
              className="analyze-button"
            >
              {isLoading ? 'EXECUTING NEURAL SCAN...' : 'SCAN DOMAIN'}
            </button>
          </div>

          <ScanResult result={result} />
        </div>
      </div>
    </div>
  );
}

export default UrlChecker;
