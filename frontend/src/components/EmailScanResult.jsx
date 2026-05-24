import React from 'react';

/* ─── Helpers ────────────────────────────────────────────────────── */
function asPercent(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return '0';
  return (n <= 1 ? n * 100 : n).toFixed(0);
}

function formatDomainAge(days) {
  const n = Number(days);
  if (!Number.isFinite(n)) return 'Not available';
  if (n < 30) return `${n} days`;
  const years  = Math.floor(n / 365);
  const months = Math.floor((n % 365) / 30);
  if (years > 0 && months > 0) return `${years} yr ${months} mo`;
  if (years > 0) return `${years} yr`;
  return `${Math.floor(n / 30)} mo`;
}

function displayIndicator(value) {
  return String(value).replace(/_/g, ' ');
}

/* ─── Shared risk config (File-1 style) ──────────────────────────── */
function getRiskConfig(score) {
  if (score <= 35) {
    return {
      badge : 'VERIFIED',
      color : '#00ff88',
      bg    : 'rgba(0, 255, 136, 0.1)',
      border: 'rgba(0, 255, 136, 0.2)',
    };
  }
  if (score <= 60) {
    return {
      badge : 'SUSPICIOUS',
      color : '#ffa500',
      bg    : 'rgba(255, 165, 0, 0.1)',
      border: 'rgba(255, 165, 0, 0.2)',
    };
  }
  return {
    badge : 'CRITICAL',
    color : '#ff4d4d',
    bg    : 'rgba(255, 77, 77, 0.1)',
    border: 'rgba(255, 77, 77, 0.2)',
  };
}

/* ─── Small reusable bits ────────────────────────────────────────── */
function RiskPill({ config }) {
  return (
    <span style={{
      background   : config.bg,
      color        : config.color,
      padding      : '0.5rem 1rem',
      borderRadius : '12px',
      fontSize     : '0.75rem',
      fontWeight   : '800',
      letterSpacing: '1px',
      border       : `1px solid ${config.border}`,
      display      : 'inline-block',
    }}>
      {config.badge}
    </span>
  );
}

function ScoreBadge({ score, config }) {
  return (
    <div style={{
      textAlign   : 'center',
      background  : 'rgba(255,255,255,0.03)',
      padding     : '1rem',
      borderRadius: '20px',
      border      : '1px solid rgba(255,255,255,0.05)',
      flexShrink  : 0,
    }}>
      <span style={{ display:'block', fontSize:'0.7rem', color:'#888', textTransform:'uppercase', fontWeight:'700', marginBottom:'4px' }}>
        Risk Score
      </span>
      <strong style={{ color: config.color, fontSize: '2rem', fontWeight: '900', textAlign: 'center' }}>
        {score}
      </strong>
    </div>
  );
}

function SectionCard({ children, border }) {
  return (
    <div style={{
      background  : 'rgba(0,0,0,0.2)',
      borderRadius: '16px',
      border      : border || '1px solid rgba(255,255,255,0.05)',
      padding     : '1rem',
      marginBottom: '1.5rem',
    }}>
      {children}
    </div>
  );
}

function SectionLabel({ text }) {
  return (
    <h4 style={{ color:'#666', fontSize:'0.75rem', textTransform:'uppercase', fontWeight:'800', marginBottom:'1rem', letterSpacing:'0.5px', margin:'0 0 1rem 0' }}>
      {text}
    </h4>
  );
}

function KVRow({ label, value, valueColor }) {
  return (
    <li style={{ display:'flex', justifyContent:'space-between', gap:'1rem', padding:'8px 0', borderBottom:'1px solid rgba(255,255,255,0.04)', listStyle:'none' }}>
      <span style={{ color:'#888', fontSize:'0.85rem' }}>{label}</span>
      <strong style={{ color: valueColor || '#ccc', fontSize:'0.85rem', textAlign:'right', overflowWrap:'anywhere' }}>{value}</strong>
    </li>
  );
}

function IndicatorChip({ text, color }) {
  return (
    <div style={{
      display     : 'flex',
      alignItems  : 'center',
      gap         : '10px',
      fontSize    : '0.85rem',
      color       : '#ccc',
      background  : 'rgba(255,255,255,0.03)',
      padding     : '10px 14px',
      borderRadius: '12px',
      border      : '1px solid rgba(255,255,255,0.02)',
    }}>
      <span style={{ color }}>•</span>
      {text}
    </div>
  );
}

function ProgressBar({ percent, color }) {
  return (
    <div style={{ background:'rgba(255,255,255,0.06)', borderRadius:'99px', height:'6px', overflow:'hidden', margin:'6px 0 0 0' }}>
      <div style={{ width:`${percent}%`, height:'100%', background: color, borderRadius:'99px', transition:'width 0.6s ease' }} />
    </div>
  );
}

function ActionButtons({ emailAddress, roundedScore, config }) {
  return (
    <div style={{ display:'flex', gap:'1rem', borderTop:'1px solid rgba(255,255,255,0.05)', paddingTop:'1.5rem', marginTop:'0.5rem' }}>
      <button
        onClick={() => {
          if (roundedScore > 35) alert(`Sender ${emailAddress} has been added to the blocklist.`);
          else alert(`${emailAddress} has been added to your Safe List.`);
        }}
        style={{
          flex        : 1,
          padding     : '1rem',
          borderRadius: '14px',
          background  : roundedScore > 60
            ? 'linear-gradient(135deg, #ff4d4d 0%, #b30000 100%)'
            : 'rgba(255,255,255,0.05)',
          color      : roundedScore > 60 ? '#fff' : '#888',
          border     : 'none',
          fontWeight : '700',
          cursor     : 'pointer',
          fontSize   : '0.8rem',
          letterSpacing: '0.5px',
        }}
      >
        {roundedScore > 35 ? 'BLOCK SENDER' : 'ADD TO SAFE LIST'}
      </button>
      <button
        onClick={() => alert(`A detailed security report for ${emailAddress || 'this email'} has been generated.`)}
        style={{
          flex        : 1,
          padding     : '1rem',
          borderRadius: '14px',
          background  : 'rgba(255,255,255,0.03)',
          color       : '#fff',
          border      : '1px solid rgba(255,255,255,0.1)',
          fontWeight  : '700',
          cursor      : 'pointer',
          fontSize    : '0.8rem',
          letterSpacing: '0.5px',
        }}
      >
        VIEW FULL REPORT
      </button>
    </div>
  );
}

/* ─── Root component ─────────────────────────────────────────────── */
function EmailScanResult({ result }) {
  if (!result) return null;
  console.log(result);
  if (result.mode === 'content') return <ContentScanResult result={result} />;
  return <AddressScanResult result={result} />;
}

/* ─── Address Scanner ────────────────────────────────────────────── */
function AddressScanResult({ result }) {
  if (!result) return null;

  // --- data extraction (File 2 logic) ---
  const emailAddress      = result.emailAddress || result.content;
  const urlAnalysis       = result.urlAnalysis;
  const reputationChecks  = urlAnalysis?.reputation_checks;
  const whois             = urlAnalysis?.whois;
  const vtStats           = reputationChecks?.virustotal?.stats;
  const indicators        = urlAnalysis?.indicators || [];
  const scoring           = urlAnalysis?.scoring;
  const components        = scoring?.components || {};

  const score        = result.score || urlAnalysis?.prediction?.risk_score || 0;
  const roundedScore = Math.round(score);
  const isPhishing   = result.isPhishing || urlAnalysis?.prediction?.predicted_class === 'Phishing';
  const riskLevel    = result.riskLevel || (roundedScore >= 70 ? 'high' : roundedScore >= 40 ? 'medium' : 'low');
  const message      = result.message || (isPhishing ? 'Suspicious sender detected.' : 'This sender appears to be safe.');

  // --- style config (File 1) ---
  const config = getRiskConfig(roundedScore);

  const titleText = roundedScore <= 35
    ? 'Genuine Identity Detected'
    : roundedScore <= 60
      ? 'Suspicious Identity Detected'
      : 'High-Risk / Phishing Attempt';

  return (
    <div style={{
      background  : 'rgba(15, 23, 42, 0.6)',
      borderRadius: '24px',
      padding     : '2rem',
      border      : `1px solid ${config.border}`,
      marginTop   : '2rem',
      fontFamily  : 'system-ui, sans-serif',
    }}>
      {/* Top-line */}
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:'1.5rem', gap:'1rem' }}>
        <div>
          <RiskPill config={config} />
          <h2 style={{ fontSize:'1.8rem', fontWeight:'800', marginTop:'1.2rem', color:'#fff', letterSpacing:'-0.5px', margin:'1.2rem 0 0 0' }}>
            {titleText}
          </h2>
          {roundedScore > 35 && (
            <p style={{ color: config.color, fontWeight:'700', margin:'6px 0 0 0', fontSize:'0.85rem', textTransform:'uppercase' }}>
              Do not interact with emails from this sender
            </p>
          )}
        </div>
        <ScoreBadge score={roundedScore} config={config} />
      </div>

      {/* Summary message */}
      <p style={{ color:'#aaa', fontSize:'0.95rem', marginBottom:'1.5rem', margin:'0 0 1.5rem 0' }}>{message}</p>

      {/* Analyzed address */}
      {emailAddress && (
        <SectionCard>
          <div style={{ display:'flex', alignItems:'center', gap:'12px' }}>
            <div style={{ width:'40px', height:'40px', borderRadius:'10px', background: config.bg, display:'flex', alignItems:'center', justifyContent:'center', fontSize:'1.2rem', flexShrink:0 }}>
              📧
            </div>
            <div style={{ overflow:'hidden' }}>
              <span style={{ display:'block', fontSize:'0.65rem', color:'#666', textTransform:'uppercase', fontWeight:'700' }}>Analyzed Identity</span>
              <code style={{ color:'#fff', fontSize:'0.95rem', fontWeight:'600', opacity:0.9 }}>{emailAddress}</code>
            </div>
            <span style={{ marginLeft:'auto', flexShrink:0, fontSize:'0.7rem', background: config.bg, color: config.color, padding:'3px 10px', borderRadius:'6px', fontWeight:'800', border:`1px solid ${config.border}` }}>
              {config.badge}
            </span>
          </div>
        </SectionCard>
      )}

      {/* Reputation Intelligence */}
      {reputationChecks && (
        <div style={{ marginBottom:'1.5rem' }}>
          <SectionLabel text={`Reputation Intelligence (${riskLevel} risk)`} />
          <ul style={{ padding:0, margin:0 }}>
            {urlAnalysis?.prediction && (
              <>
                <KVRow
                  label="Domain Verdict"
                  value={`${urlAnalysis.prediction.predicted_class || 'Unknown'} (${urlAnalysis.prediction.risk_score ?? 0}/100)`}
                  valueColor={urlAnalysis.prediction.predicted_class === 'Phishing' ? '#ff4d4d' : '#00ff88'}
                />
              </>
            )}
            {reputationChecks.google_safe_browsing?.enabled && (
              <KVRow
                label="Google Safe Browsing"
                value={reputationChecks.google_safe_browsing.status === 'error' ? 'Lookup Failed' : reputationChecks.google_safe_browsing.status}
                valueColor={reputationChecks.google_safe_browsing.status === 'ok' ? '#00ff88' : '#ff4d4d'}
              />
            )}
            {/* Phishing probability bar */}
            {urlAnalysis?.prediction?.confidence_score !== undefined && (
              <li style={{ listStyle:'none', padding:'10px 0' }}>
                <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'2px' }}>
                  <span style={{ color:'#888', fontSize:'0.85rem' }}>Confidence</span>
                  <span style={{ color: config.color, fontSize:'0.85rem', fontWeight:'700' }}>{asPercent(urlAnalysis.prediction.confidence_score)}%</span>
                </div>
                <ProgressBar percent={Number(asPercent(urlAnalysis.prediction.confidence_score))} color={config.color} />
              </li>
            )}
          </ul>
        </div>
      )}

      {/* Risk Indicators grid */}
      {indicators.length > 0 && (
        <div style={{ marginBottom:'1.5rem' }}>
          <SectionLabel text={`Security Findings (${indicators.length})`} />
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(240px, 1fr))', gap:'0.8rem' }}>
            {indicators.map((ind, i) => (
              <IndicatorChip key={i} text={displayIndicator(ind)} color={config.color} />
            ))}
          </div>
        </div>
      )}

      {/* Safe state */}
      {!isPhishing && roundedScore <= 35 && (
        <SectionCard>
          <div style={{ display:'flex', gap:'8px', alignItems:'center', marginBottom:'8px' }}>
            <span style={{ color:'#00ff88', fontSize:'1rem' }}>✓</span>
            <span style={{ color:'#00ff88', fontWeight:'700', fontSize:'0.85rem' }}>No critical threats detected</span>
          </div>
          <div style={{ display:'flex', gap:'8px', alignItems:'center' }}>
            <span style={{ color:'#00ff88', fontSize:'1rem' }}>✓</span>
            <span style={{ color:'#00ff88', fontWeight:'700', fontSize:'0.85rem' }}>Reputation check completed</span>
          </div>
        </SectionCard>
      )}


      {/* Action buttons */}
      <ActionButtons emailAddress={emailAddress} roundedScore={roundedScore} config={config} />
    </div>
  );
}

/* ─── Content Scanner ────────────────────────────────────────────── */
function ContentScanResult({ result }) {
  if (!result) return null;

  if (result.error || result.success === false) {
    return (
      <div style={{ background:'rgba(15,23,42,0.6)', borderRadius:'24px', padding:'2rem', border:'1px solid rgba(255,77,77,0.2)', marginTop:'2rem' }}>
        <h3 style={{ color:'#ff4d4d', margin:0 }}>Scan Failed</h3>
        <p style={{ color:'#aaa', marginTop:'0.5rem' }}>{result.details || 'Could not connect to service.'}</p>
      </div>
    );
  }


  const scanResult   = result.result;
  const score        = result.score || scanResult?.score || 0;
  const roundedScore = Math.round(score);
  const components   = scanResult?.scoring?.components || {};
  const weights      = scanResult?.scoring?.weights     || {};
  const urlAnalysis  = scanResult?.urlAnalysis;
  const smsAnalysis  = scanResult?.smsAnalysis;
  const isHighRisk   = Boolean(result.isPhishing) || roundedScore >= 50;


  const config = getRiskConfig(roundedScore);

  const titleText = roundedScore <= 35
    ? 'Genuine Content Detected'
    : roundedScore <= 60
      ? 'Suspicious Content Detected'
      : 'High-Risk / Phishing Content';

  return (
    <div style={{
      background  : 'rgba(15, 23, 42, 0.6)',
      borderRadius: '24px',
      padding     : '2rem',
      border      : `1px solid ${config.border}`,
      marginTop   : '2rem',
      fontFamily  : 'system-ui, sans-serif',
    }}>
      {/* Top-line */}
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:'1.5rem', gap:'1rem' }}>
        <div>
          <RiskPill config={config} />
          <h2 style={{ fontSize:'1.8rem', fontWeight:'800', marginTop:'1.2rem', color:'#fff', letterSpacing:'-0.5px', margin:'1.2rem 0 0 0' }}>
            {titleText}
          </h2>
          {isHighRisk && (
            <p style={{ color: config.color, fontWeight:'700', margin:'6px 0 0 0', fontSize:'0.85rem', textTransform:'uppercase' }}>
              Do not interact with this email
            </p>
          )}
        </div>
        <ScoreBadge score={roundedScore} config={config} />
      </div>

      {/* Summary message */}
      {result.message && (
        <p style={{ color:'#aaa', fontSize:'0.95rem', margin:'0 0 1.5rem 0' }}>{result.message}</p>
      )}

      {/* Analysis summary */}
      <SectionCard>
        <span style={{ display:'block', fontSize:'0.65rem', color:'#666', textTransform:'uppercase', fontWeight:'700', marginBottom:'6px' }}>
          Analysis Summary
        </span>
        <p style={{ color:'#ccc', margin:0, fontSize:'0.95rem' }}>
          {result.details || (roundedScore < 40
            ? 'This email contains patterns typical of legitimate communication.'
            : 'Warning: Found patterns commonly used in phishing campaigns.')}
        </p>
      </SectionCard>

      {/* Confidence bar */}
      {(result.confidence !== undefined) && (
        <div style={{ marginBottom:'1.5rem' }}>
          <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'4px' }}>
            <span style={{ color:'#888', fontSize:'0.85rem' }}>Detection Confidence</span>
            <span style={{ color: config.color, fontSize:'0.85rem', fontWeight:'700' }}>{result.confidence}%</span>
          </div>
          <ProgressBar percent={result.confidence} color={config.color} />
        </div>
      )}

      {/* Detected links */}
      {scanResult?.extractedUrl?.length > 0 && (
        <div style={{ marginBottom:'1.5rem' }}>
          <SectionLabel text="Detected Links" />
          {scanResult.extractedUrl.map((url, i) => (
            <div key={i} style={{ display:'flex', justifyContent:'space-between', alignItems:'center', gap:'1rem', padding:'0.8rem', background:'rgba(0,0,0,0.2)', borderRadius:'12px', border:`1px solid ${config.border}`, marginBottom:'0.5rem' }}>
              <code style={{ color:'#ccc', fontWeight:'600', overflowWrap:'anywhere', fontSize:'0.85rem' }}>{url}</code>
              <span style={{ flexShrink:0, fontSize:'0.65rem', background: config.bg, color: config.color, padding:'3px 10px', borderRadius:'6px', fontWeight:'800', border:`1px solid ${config.border}` }}>
                {isHighRisk ? 'SUSPECTED PHISHING' : 'LEGITIMATE'}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* URL Intelligence */}
      {urlAnalysis?.url && (
        <div style={{ marginBottom:'1.5rem' }}>
          <SectionLabel text="URL Intelligence" />
          <ul style={{ padding:0, margin:0 }}>
            <KVRow label="URL" value={urlAnalysis.url} valueColor="#ccc" />
            <KVRow
              label="Risk Score"
              value={`${urlAnalysis.prediction?.riskScore ?? 0}/100`}
              valueColor={(urlAnalysis.prediction?.riskScore || 0) >= 40 ? '#ff4d4d' : '#00ff88'}
            />
            {urlAnalysis.indicators?.length > 0 && (
              <KVRow label="URL Indicators" value={`${urlAnalysis.indicators.length} found`} valueColor="#ffa500" />
            )}
          </ul>
        </div>
      )}

      {/* Indicators grid */}
      {scanResult?.indicators?.length > 0 && (
        <div style={{ marginBottom:'1.5rem' }}>
          <SectionLabel text={`Security Findings (${scanResult.indicators.length})`} />
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(240px, 1fr))', gap:'0.8rem' }}>
            {scanResult.indicators.map((ind, i) => (
              <IndicatorChip key={i} text={displayIndicator(ind)} color={config.color} />
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {scanResult?.recommendations?.length > 0 && (
        <div style={{ marginBottom:'1.5rem' }}>
          <SectionLabel text="Recommended Actions" />
          <ul style={{ padding:0, margin:0 }}>
            {scanResult.recommendations.map((rec, i) => (
              <li key={i} style={{ display:'flex', alignItems:'flex-start', gap:'10px', padding:'8px 0', borderBottom:'1px solid rgba(255,255,255,0.04)', color:'#ccc', fontSize:'0.85rem', listStyle:'none' }}>
                <span style={{ color: config.color, marginTop:'2px' }}>›</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Technical Breakdown
      <details style={{ marginBottom:'1.5rem' }}>
        <summary style={{ color:'#666', fontSize:'0.75rem', textTransform:'uppercase', fontWeight:'800', cursor:'pointer', letterSpacing:'0.5px', userSelect:'none' }}>
          Technical Score Breakdown
        </summary>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(140px, 1fr))', gap:'0.6rem', marginTop:'1rem' }}>
          {[
            { label:'Final Score',    value:`${roundedScore}/100` },
            { label:'Email Heuristic',value:`${components.smsHeuristic ?? smsAnalysis?.heuristicScore ?? 0}/100` },
            { label:'URL Heuristic',  value:`${components.urlHeuristic ?? 0}/100` },
            { label:'Email ML',       value:`${components.smsMl ?? smsAnalysis?.mlScore ?? 0}/100` },
            { label:'URL ML',         value:`${components.urlMl ?? 0}/100` },
            { label:'ML Prediction',  value:`${scanResult?.prediction?.label || 'unknown'} (${scanResult?.prediction?.spamProbability ?? 0}%)` },
            // { label:'Weights',        value:`H ${asPercent(weights.smsHeuristic)} / URLh ${asPercent(weights.urlHeuristic)} / ML ${asPercent((weights.smsMl||0)+(weights.urlMl||0))}` },
          ].map(({ label, value }) => (
            <div key={label} style={{ background:'rgba(255,255,255,0.02)', borderRadius:'12px', padding:'10px 14px', border:'1px solid rgba(255,255,255,0.04)' }}>
              <span style={{ display:'block', color:'#666', fontSize:'0.65rem', textTransform:'uppercase', fontWeight:'700', marginBottom:'4px' }}>{label}</span>
              <strong style={{ color:'#ccc', fontSize:'0.85rem' }}>{value}</strong>
            </div>
          ))}
        </div>
      </details> */}

      {/* Action buttons */}
      <ActionButtons emailAddress={null} roundedScore={roundedScore} config={config} />
    </div>
  );
}

export default EmailScanResult;