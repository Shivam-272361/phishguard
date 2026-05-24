import React, { useState } from 'react';
import ScanResult from './ScanResult';
import WebsitePreviewCard from './WebsitePreviewCard';
import { scanUrl } from '../services/api';
import './CheckerStyles.css';

function WebsiteChecker() {
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [result, setResult] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const analyzeWebsite = async () => {
    if (!websiteUrl.trim()) return;

    setIsLoading(true);
    setResult(null);
    setPreview(null);

    try {
      const data = await scanUrl(websiteUrl);
      // Backend returns { success, url, result: { mlResult }, preview }
      setResult(data);
      setPreview(data.preview);
    } catch (error) {
      setResult({
        isPhishing: true,
        confidence: 0,
        message: 'Scan failed',
        details: error.message || 'Could not connect to the backend server.',
        indicators: ['Backend request failed'],
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="checker-container">
      <div className="checker-card">
        <div className="checker-header">
          <span className="checker-icon">WEB</span>
          <h1>Website Security Checker</h1>
          <p>Analyze a website URL for phishing and basic security threats</p>
        </div>

        <div className="checker-content">
          <div className="input-section">
            <label>Enter Website URL:</label>
            <input
              type="url"
              value={websiteUrl}
              onChange={(e) => setWebsiteUrl(e.target.value)}
              placeholder="https://example.com"
              className="text-input"
            />
            <button
              onClick={analyzeWebsite}
              disabled={!websiteUrl.trim() || isLoading}
              className="analyze-button"
            >
              {isLoading ? 'Scanning Website...' : 'Scan Website'}
            </button>
          </div>

          <ScanResult result={result} title="Website scan" />
          
          {result && (
            <div className="preview-section">
              <WebsitePreviewCard 
                url={websiteUrl} 
                preview={preview} 
                isPhishing={result.isPhishing || result.phishing} 
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default WebsiteChecker;
