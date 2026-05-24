import React, { useState } from 'react';
import { capturePreview } from '../services/api';

function asPercent(value) {
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) return '0';
  const percentValue = numericValue <= 1 ? numericValue * 100 : numericValue;
  return percentValue.toFixed(0);
}

function isPositiveIndicator(indicator) {
  const normalized = String(indicator)
    .toLowerCase()
    .replace(/[_-]+/g, ' ');

  return [
    'well known domain',
    'legitimate',
    'trusted',
    'safe',
  ].some((signal) => normalized.includes(signal));
}

function domainAgeStatus(days) {
  const numericDays = Number(days);

  if (!Number.isFinite(numericDays)) {
    return {
      label: 'Not available',
      color: '#ff6b6b',
    };
  }

  const formatAge = () => {
    if (numericDays < 30) {
      return `${numericDays} days`;
    }

    const years = Math.floor(numericDays / 365);
    const months = Math.floor((numericDays % 365) / 30);

    if (years > 0 && months > 0) {
      return `${years} yr ${months} mo`;
    }

    if (years > 0) {
      return `${years} yr`;
    }

    return `${Math.floor(numericDays / 30)} mo`;
  };

  if (numericDays < 30) {
    return {
      label: `${formatAge()} (very new)`,
      color: '#ff6b6b',
    };
  }

  if (numericDays < 180) {
    return {
      label: `${formatAge()} (young domain)`,
      color: '#ff6b6b',
    };
  }

  return {
    label: formatAge(),
    color: '#208847',
  };
}

function ScanResult({ result }) {
  const [screenshotUrl, setScreenshotUrl] = useState(null);
  const [currentUrl, setCurrentUrl] = useState(null);
  const [isCapturing, setIsCapturing] = useState(false);
  const [captureError, setCaptureError] = useState(null);

  if (!result) return null;

  // Reset screenshot when a new URL is scanned
  const data = result.result || result;
  const url = data.url || result.url || 'Unknown URL';
  
  if (url !== currentUrl) {
    setCurrentUrl(url);
    setScreenshotUrl(null);
    setCaptureError(null);
  }

  const handleCapturePreview = async () => {
    setIsCapturing(true);
    setCaptureError(null);
    try {
      const data = result.result || result;
      const targetUrl = result.url || data.url;
      console.log("Target URL for capture:", targetUrl);
      const response = await capturePreview(targetUrl);
      console.log("Response from capture:", response);
      if (response && response.success === true && response.screenshotUrl) {
        setScreenshotUrl(response.screenshotUrl);
      } else if (response && response.screenshotUrl) {
        setScreenshotUrl(response.screenshotUrl);
      } else if (response && response.screenshot_url) {
        setScreenshotUrl(response.screenshot_url);
      } else {
        setCaptureError(response.error || "Failed to generate preview. The site might be offline or blocked.");
      }
    } catch (err) {
      setCaptureError("Error capturing preview: " + err.message);
    } finally {
      setIsCapturing(false);
    }
  };

  // Normalize the data format.
  // The backend returns it directly in 'result' (or within 'result.result') depending on the endpoint.
  // data and url are already extracted above for the reset logic.

  if (!result.success && !data.success) {
    return (
      <div className="result-section danger">
        <h3 className="result-message">Scan Failed</h3>
        <p className="result-details">{result.message || data.error || 'The URL could not be analyzed.'}</p>
      </div>
    );
  }

  // Safely extract properties
  const prediction = data.ml_prediction || data.prediction || {};
  const scoring = data.scoring || {};
  const indicators = data.indicators || [];
  const whois = data.whois || {};
  const reputation_checks = data.reputation_checks || data;
  const domainAge = domainAgeStatus(whois?.prediction?.domain_age_days);
  const domainName = whois?.domain;

  // Use the central reputation status if available, else fallback to ML score
  const finalVerdict = data.final_verdict || reputation_checks?.final_verdict || '';
  const isMaliciousValue = finalVerdict === 'PHISHING DETECTED' || finalVerdict === 'HIGH RISK' || reputation_checks?.reputation === 'malicious';
  const risk_score = data.risk_score || prediction.risk_score || 0;
  const isSuspiciousValue = finalVerdict === 'SUSPICIOUS' || reputation_checks?.reputation === 'suspicious' || risk_score >= 40;
  
  const score = risk_score;
  const isHighRisk = score >= 75 || isMaliciousValue || finalVerdict === 'PHISHING DETECTED';
  const isSuspicious = (score >= 40 && score < 75) || isSuspiciousValue || finalVerdict === 'SUSPICIOUS';

  const statusClass = isHighRisk ? 'danger' : (isSuspicious ? 'suspicious' : 'safe');
  const statusIcon = isHighRisk ? '🛑' : (isSuspicious ? '⚠️' : '🛡️');

  // Dynamic Theme Definitions
  const isDanger = isHighRisk || isSuspicious;
  const themeColors = isDanger ? {
    accent: '#ff4d4d', // Intense Red
    accentSecondary: '#f9cb28', // Warning Orange/Yellow
    bgGradient: 'linear-gradient(145deg, rgba(45, 10, 10, 0.95) 0%, rgba(15, 5, 5, 0.98) 100%)',
    border: 'rgba(255, 77, 77, 0.4)',
    glow: 'rgba(255, 77, 77, 0.15)',
    cardBg: 'rgba(30, 10, 10, 0.4)',
    textMuted: 'rgba(255, 200, 200, 0.7)',
    progressBar: 'linear-gradient(90deg, #ff1f1f, #f9cb28)'
  } : {
    accent: '#43e97b', // Secure Green
    accentSecondary: '#00f2fe', // Cyan
    bgGradient: 'linear-gradient(145deg, rgba(10, 30, 25, 0.95) 0%, rgba(5, 15, 12, 0.98) 100%)',
    border: 'rgba(67, 233, 123, 0.3)',
    glow: 'rgba(67, 233, 123, 0.1)',
    cardBg: 'rgba(10, 40, 30, 0.3)',
    textMuted: 'rgba(200, 255, 220, 0.7)',
    progressBar: 'linear-gradient(90deg, #43e97b, #38f9d7)'
  };

  const colors = {
    bgCard: 'rgba(15, 23, 42, 0.8)',
    borderHigh: 'rgba(255, 77, 77, 0.3)',
    borderSafe: 'rgba(67, 233, 123, 0.3)',
    accentDanger: '#ffeb3b', // Light / Yellow for suspicious/malicious
    accentSafe: '#43e97b',   // Green for safe
    accentNeutral: '#4facfe',
    textDim: 'rgba(255, 255, 255, 0.6)',
    textBright: '#ffffff'
  };

  const getRiskLabel = () => {
    if (isMaliciousValue || score >= 75) return 'CRITICAL';
    if (score >= 60) return 'HIGH';
    if (isSuspiciousValue || score >= 40) return 'SUSPICIOUS';
    return 'LOW';
  };

  const vtStats = reputation_checks?.virustotal?.stats;
  const gsbStatus = reputation_checks?.google_safe_browsing?.status;

  return (
    <div className={`result-section ${statusClass}`} style={{ 
      background: themeColors.bgGradient, 
      backdropFilter: 'blur(16px)',
      border: `2px solid ${themeColors.border}`,
      padding: '2.5rem',
      borderRadius: '28px',
      color: colors.textBright,
      boxShadow: `0 25px 60px rgba(0,0,0,0.5), 0 0 30px ${themeColors.glow}`,
      transition: 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Decorative Scanner Line */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '2px',
        background: `linear-gradient(90deg, transparent, ${themeColors.accent}, transparent)`,
        animation: 'scan-move 3s linear infinite',
        opacity: 0.5
      }} />

      <div className="result-topline" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <span style={{ 
            fontSize: '4.5rem', 
            lineHeight: 1, 
            filter: `drop-shadow(0 0 20px ${themeColors.accent})`,
            transition: 'transform 0.5s ease'
          }}>{statusIcon}</span>
          <div>
            <div style={{ display: 'flex', gap: '0.8rem', marginBottom: '0.5rem' }}>
              <span className={`risk-pill ${getRiskLabel().toLowerCase()}`} style={{
                background: isDanger ? 'rgba(255, 50, 50, 0.15)' : 'rgba(67, 233, 123, 0.15)',
                color: isDanger ? '#ff4d4d' : themeColors.accent,
                padding: '0.5rem 1.4rem',
                borderRadius: '10px',
                fontSize: '0.8rem',
                fontWeight: '900',
                letterSpacing: '1.5px',
                border: `1px solid ${themeColors.border}`,
                textTransform: 'uppercase',
                boxShadow: `0 0 10px ${themeColors.glow}`
              }}>
                {getRiskLabel()} RISK
              </span>
            </div>
            <h2 className="result-message" style={{ 
              fontSize: '2.5rem', 
              fontWeight: '800', 
              margin: '0 0 0.5rem 0', 
              letterSpacing: '-0.03em',
              color: 'white',
              textShadow: `0 0 20px ${themeColors.glow}`,
              lineHeight: '1.1'
            }}>
              {isHighRisk ? 'Malicious Detected' : (isSuspicious ? 'Suspicious Alert' : 'Infrastructure Secure')}
            </h2>
            <code style={{ 
              fontSize: '0.9rem', 
              color: themeColors.accentSecondary, 
              background: 'rgba(0,0,0,0.5)', 
              padding: '0.4rem 0.8rem', 
              borderRadius: '8px',
              border: `1px solid ${themeColors.border}`,
              display: 'inline-block',
              fontFamily: 'JetBrains Mono, monospace',
              letterSpacing: '0',
              wordBreak: 'break-all'
            }}>
              {url}
            </code>
          </div>
        </div>
        <div className="score-badge" style={{ 
          textAlign: 'right',
          background: 'rgba(0,0,0,0.4)',
          padding: '1.5rem',
          borderRadius: '24px',
          border: `1px solid ${themeColors.border}`,
          minWidth: '130px',
          boxShadow: `0 10px 20px rgba(0,0,0,0.3), inset 0 0 15px ${themeColors.glow}`
        }}>
          <span style={{ 
            display: 'block', 
            fontSize: '0.75rem', 
            color: themeColors.textMuted, 
            textTransform: 'uppercase', 
            fontWeight: '900', 
            letterSpacing: '2px',
            marginBottom: '0.5rem'
          }}>Safety Index</span>
          <strong style={{ 
            fontSize: '3.5rem', 
            color: themeColors.accent,
            lineHeight: 1,
            fontWeight: '1000',
            filter: `drop-shadow(0 0 10px ${themeColors.accent})`
          }}>
            {score.toFixed(0)}
          </strong>
        </div>
      </div>

      <p className="result-details" style={{ 
        fontWeight: '450', 
        marginTop: '2.5rem', 
        fontSize: '1.05rem', 
        lineHeight: '1.6',
        color: '#e2e8f0',
        padding: '1.8rem',
        background: 'rgba(0,0,0,0.25)',
        borderRadius: '20px',
        borderLeft: `6px solid ${themeColors.accent}`,
        boxShadow: 'inset 0 0 20px rgba(0,0,0,0.1)'
      }}>
        {isHighRisk || isSuspicious
          ? "CRITICAL ALERT: Our engine has identified high-risk characteristics associated with phishing and malicious domains. Protect your data by avoiding this URL immediately."
          : "CLEAN SCAN: No malicious associations were identified in our database or AI neural scan. Infrastructure integrity is confirmed across multiple vectors."}
      </p>

      {/* Probability Bar */}
      <div className="confidence-bar" style={{ marginTop: '3rem' }}>
        <div className="check-item" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <span className="confidence-label" style={{ fontWeight: '800', color: themeColors.textMuted, textTransform: 'uppercase', letterSpacing: '1px' }}>AI Confidence Radar</span>
          <span style={{ fontWeight: '1000', color: themeColors.accent, fontSize: '1.2rem' }}>{asPercent(prediction.phishing_probability)}%</span>
        </div>
        <div className="progress-bar" style={{ 
          height: '16px', 
          background: 'rgba(0,0,0,0.5)', 
          borderRadius: '8px', 
          overflow: 'hidden',
          border: `1px solid ${isDanger ? 'rgba(255,0,0,0.2)' : 'rgba(0,255,0,0.1)'}`
        }}>
          <div
            className={`progress-fill ${(isHighRisk || isSuspicious) ? 'danger-fill' : 'safe-fill'}`}
            style={{ 
              width: `${asPercent(prediction.phishing_probability)}%`,
              height: '100%',
              background: themeColors.progressBar,
              boxShadow: `0 0 20px ${themeColors.accent}`,
              transition: 'width 1.5s cubic-bezier(0.34, 1.56, 0.64, 1)'
            }}
          ></div>
        </div>
      </div>

      {/* Intelligence Breakdown Grid */}
      <div className="url-analysis" style={{ marginTop: '3.5rem' }}>
        <h4 style={{ 
          fontSize: '1.4rem', 
          fontWeight: '900', 
          marginBottom: '1.8rem', 
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          gap: '0.8rem'
        }}>
          <span style={{ color: themeColors.accent }}>■</span> Cyber Threat Intelligence
        </h4>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', 
          gap: '1.5rem' 
        }}>
          {reputation_checks?.virustotal?.available && (
            <div style={{ 
              background: themeColors.cardBg, 
              padding: '1.5rem', 
              borderRadius: '20px', 
              border: `1px solid ${themeColors.border}`,
              transition: 'transform 0.3s ease',
              boxShadow: `0 10px 20px rgba(0,0,0,0.2)`
            }}>
              <span style={{ display: 'block', fontSize: '0.8rem', color: themeColors.textMuted, marginBottom: '0.6rem', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '1px' }}>VirusTotal Analysis</span>
              <strong style={{ color: vtStats?.malicious > 0 ? '#ff1f1f' : '#43e97b', fontSize: '1.3rem', fontWeight: '950' }}>
                {vtStats?.malicious > 0 ? `${vtStats.malicious} Threats Detected` : 'Registry Clean'}
              </strong>
            </div>
          )}
          <div style={{ 
            background: themeColors.cardBg, 
            padding: '1.5rem', 
            borderRadius: '20px', 
            border: `1px solid ${themeColors.border}`,
            boxShadow: `0 10px 20px rgba(0,0,0,0.2)`
          }}>
            <span style={{ display: 'block', fontSize: '0.75rem', color: themeColors.textMuted, marginBottom: '0.6rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Infrastructure Age</span>
            <strong style={{ color: domainAge.color === '#208847' ? '#43e97b' : '#ff4d4d', fontSize: '1.2rem', fontWeight: '700' }}>
              {domainAge.label}
            </strong>
          </div>
          <div style={{ 
            background: themeColors.cardBg, 
            padding: '1.5rem', 
            borderRadius: '20px', 
            border: `1px solid ${themeColors.border}`,
            boxShadow: `0 10px 20px rgba(0,0,0,0.2)`
          }}>
            <span style={{ display: 'block', fontSize: '0.75rem', color: themeColors.textMuted, marginBottom: '0.6rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Protocol Security</span>
            <strong style={{ color: url.startsWith('https') ? '#43e97b' : '#ff4d4d', fontSize: '1.2rem', fontWeight: '700' }}>
              {url.startsWith('https') ? 'HTTPS Mandatory' : 'Insecure HTTP Trace'}
            </strong>
          </div>
          <div style={{ 
            background: themeColors.cardBg, 
            padding: '1.5rem', 
            borderRadius: '20px', 
            border: `1px solid ${themeColors.border}`,
            boxShadow: `0 10px 20px rgba(0,0,0,0.2)`
          }}>
            <span style={{ display: 'block', fontSize: '0.75rem', color: themeColors.textMuted, marginBottom: '0.6rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Verified Authority</span>
            <strong style={{ color: whois?.registrar ? '#43e97b' : '#ff4d4d', fontSize: '1.2rem', fontWeight: '700' }}>
              {whois?.registrar || 'Non-Authoritative'}
            </strong>
          </div>
        </div>
      </div>


      {/* Indicators Section */}
      {indicators && indicators.length > 0 && (
        <div className="security-checklist" style={{ marginTop: '3.5rem' }}>
          <h4 style={{ 
            fontSize: '1.4rem', 
            fontWeight: '900', 
            marginBottom: '1.8rem', 
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            gap: '0.8rem'
          }}>
            <span style={{ color: themeColors.accent }}>■</span> Risk Vectors Detected
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1.2rem' }}>
            {indicators.map((indicator, index) => {
              const isPositiveSignal = isPositiveIndicator(indicator);

              return (
                <div
                  key={index}
                  className={`check-item ${isPositiveSignal ? 'pass' : 'fail'}`}
                  style={{ 
                    padding: '1.2rem',
                    background: isPositiveSignal ? 'rgba(67, 233, 123, 0.08)' : 'rgba(255, 77, 77, 0.08)',
                    borderRadius: '16px',
                    border: `1px solid ${isPositiveSignal ? 'rgba(67, 233, 123, 0.2)' : 'rgba(255, 77, 77, 0.2)'}`,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.6rem',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                  }}
                >
                  <span style={{ 
                    textTransform: 'uppercase', 
                    fontWeight: '800',
                    fontSize: '0.8rem',
                    color: 'white',
                    letterSpacing: '0.5px'
                  }}>
                    {indicator.replace(/_/g, ' ')}
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ 
                      fontSize: '0.7rem', 
                      color: isPositiveSignal ? '#43e97b' : '#ff4d4d', 
                      letterSpacing: '1px', 
                      fontWeight: '900',
                      background: 'rgba(0,0,0,0.3)',
                      padding: '2px 8px',
                      borderRadius: '4px'
                    }}>
                      {isPositiveSignal ? 'SECURE' : 'WARNING'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Website Preview Section */}
      <div className="preview-container-modern" style={{ 
        marginTop: '3.5rem',
        background: 'rgba(0, 0, 0, 0.4)',
        borderRadius: '28px',
        overflow: 'hidden',
        border: `2px solid ${themeColors.border}`,
        boxShadow: `0 15px 35px rgba(0,0,0,0.3)`
      }}>
        <div className="preview-header" style={{ 
          padding: '1.5rem 2.5rem', 
          background: 'rgba(255,255,255,0.02)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: `1px solid ${themeColors.border}`
        }}>
          <h4 style={{ margin: 0, fontWeight: '900', fontSize: '1.2rem' }}>Visual Forensic Analysis</h4>
          <span style={{ 
            fontSize: '0.75rem', 
            color: themeColors.accentSecondary, 
            fontWeight: '900', 
            letterSpacing: '1.5px',
            background: 'rgba(0,0,0,0.3)',
            padding: '4px 12px',
            borderRadius: '6px'
          }}>QUARANTINED VIEW</span>
        </div>
        
        <div style={{ padding: '3rem', textAlign: 'center' }}>
          {!(screenshotUrl || data.screenshot_url) ? (
            <div style={{ maxWidth: '450px', margin: '0 auto' }}>
              <p style={{ color: themeColors.textMuted, marginBottom: '2rem', fontSize: '1rem', fontWeight: '600' }}>
                To optimize speed, website rendering is on-demand. Generate a visual preview to inspect the site's layout safely.
              </p>
              <button 
                onClick={handleCapturePreview}
                disabled={isCapturing}
                style={{
                  background: isDanger 
                    ? 'linear-gradient(135deg, #ff4d4d 0%, #ff8c00 100%)' 
                    : 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                  color: 'white',
                  border: 'none',
                  padding: '1rem 2.5rem',
                  borderRadius: '16px',
                  fontWeight: '900',
                  fontSize: '1rem',
                  letterSpacing: '1px',
                  cursor: isCapturing ? 'not-allowed' : 'pointer',
                  opacity: isCapturing ? 0.7 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '1rem',
                  margin: '0 auto',
                  boxShadow: `0 10px 25px ${themeColors.glow}`,
                  transition: 'all 0.3s ease'
                }}>
                {isCapturing ? (
                  <>
                    <span className="spinner" style={{
                      width: '20px',
                      height: '20px',
                      border: '3px solid rgba(255,255,255,0.3)',
                      borderTopColor: 'white',
                      borderRadius: '50%',
                      animation: 'spin 1s linear infinite'
                    }}></span>
                    INITIALIZING...
                  </>
                ) : (
                  <>
                    <span style={{ fontSize: '1.4rem' }}>🖼️</span>
                    GENERATE FORENSIC PREVIEW
                  </>
                )}
              </button>
            </div>
          ) : (
            <div className="screenshot-display" style={{ animation: 'fade-in 1s ease' }}>
              <img 
                src={screenshotUrl ? `http://localhost:3000${screenshotUrl}` : (data.screenshot_url ? `http://localhost:3000${data.screenshot_url}` : '')} 
                alt="Website Preview" 
                style={{ 
                  width: '100%', 
                  borderRadius: '16px', 
                  border: `1px solid ${themeColors.border}`,
                  boxShadow: '0 20px 40px rgba(0,0,0,0.4)',
                  maxHeight: '600px',
                  objectFit: 'contain',
                  background: '#0f172a'
                }} 
              />
              <div style={{ 
                marginTop: '1.5rem', 
                color: themeColors.accent, 
                fontSize: '0.85rem', 
                fontWeight: '800',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem'
              }}>
                <span style={{ fontSize: '1.2rem' }}>✓</span> FORENSIC CAPTURE SECURED
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>


      {/* Technical Panel */}
      {scoring && scoring.components && (
        <details className="feature-panel" style={{ 
          marginTop: '3rem',
          background: 'rgba(0,0,0,0.2)',
          borderRadius: '16px',
          padding: '0.5rem 1.5rem',
          cursor: 'pointer',
          border: '1px solid rgba(255,255,255,0.05)'
        }}>
          <summary style={{ 
            padding: '1rem 0', 
            fontWeight: '700', 
            color: 'rgba(255,255,255,0.6)',
            fontSize: '0.9rem'
          }}>Technical Engine Metrics</summary>
          <div className="feature-grid" style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
            gap: '1.5rem',
            paddingBottom: '1.5rem',
            paddingTop: '1rem',
            borderTop: '1px solid rgba(255,255,255,0.05)'
          }}>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.4)', marginBottom: '0.4rem', textTransform: 'uppercase' }}>Heuristic</span>
              <strong style={{ fontSize: '1.2rem', color: '#fff' }}>{scoring.components.heuristic || 0}</strong>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.4)', marginBottom: '0.4rem', textTransform: 'uppercase' }}>ML Confidence</span>
              <strong style={{ fontSize: '1.2rem', color: '#fff' }}>{scoring.components.ml || 0}</strong>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.4)', marginBottom: '0.4rem', textTransform: 'uppercase' }}>WHOIS Score</span>
              <strong style={{ fontSize: '1.2rem', color: '#fff' }}>{scoring.components.whois || 0}</strong>
            </div>
          </div>
        </details>
      )}

    </div>
  );
}

export default ScanResult;
