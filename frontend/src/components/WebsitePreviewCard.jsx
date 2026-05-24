import React from 'react';
import './WebsitePreviewCard.css';

const WebsitePreviewCard = ({ url, preview, isPhishing }) => {
  const { success, screenshotUrl, analysis, error } = preview || {};
  const backendBaseUrl = 'http://localhost:3000'; // Default backend URL

  const getStatusClass = () => {
    if (isPhishing) return 'status-phishing';
    return 'status-safe';
  };

  return (
    <div className={`preview-card ${getStatusClass()}`}>
      <div className="preview-header">
        <span className="preview-title">Website Live Preview</span>
        {isPhishing ? (
          <span className="badge badge-warning">⚠️ PHISHING DETECTED</span>
        ) : (
          <span className="badge badge-safe">✅ SAFE</span>
        )}
      </div>

      <div className="preview-body">
        <div className="screenshot-container">
          {!preview ? (
            <div className="loading-overlay">
              <div className="spinner"></div>
              <p>Capturing live preview...</p>
            </div>
          ) : success ? (
            <img 
              src={`${backendBaseUrl}${screenshotUrl}`} 
              alt="Website Preview" 
              className="screenshot-img"
            />
          ) : (
            <div className="preview-error">
              <span className="error-icon">🚫</span>
              <p>Preview unavailable</p>
              <small>{error || 'Connection timeout'}</small>
            </div>
          )}
        </div>

        <div className="preview-info">
          <div className="info-item">
            <span className="label">Analyzed URL:</span>
            <span className="value url-text">{url}</span>
          </div>

          {analysis && success && (
            <div className="indicators">
              {analysis.hasPassword && (
                <div className="indicator-chip warning">
                  🔑 Login Form Detected
                </div>
              )}
              {analysis.brandImpersonation && (
                <div className="indicator-chip danger">
                  🪪 Impersonating: {analysis.brandImpersonation}
                </div>
              )}
              {analysis.hasLoginForm && !analysis.hasPassword && (
                <div className="indicator-chip info">
                  📝 Possible Login Page
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      
      <div className="preview-footer">
        <div className="scan-verdict">
          Final Verdict: <strong>{isPhishing ? 'MALICIOUS' : 'TRUSTED'}</strong>
        </div>
      </div>
    </div>
  );
};

export default WebsitePreviewCard;
