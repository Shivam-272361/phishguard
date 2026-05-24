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

/* ─── Shared risk config ─────────────────────────────────────────── */
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

/* ─── Reusable UI primitives ─────────────────────────────────────── */
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
      <strong style={{ color: config.color, fontSize: '2rem', fontWeight: '900' }}>
        {score}
      </strong>
    </div>
  );
}

function SectionCard({ children }) {
  return (
    <div style={{
      background  : 'rgba(0,0,0,0.2)',
      borderRadius: '16px',
      border      : '1px solid rgba(255,255,255,0.05)',
      padding     : '1rem',
      marginBottom: '1.5rem',
    }}>
      {children}
    </div>
  );
}

function SectionLabel({ text }) {
  return (
    <h4 style={{ color:'#666', fontSize:'0.75rem', textTransform:'uppercase', fontWeight:'800', margin:'0 0 1rem 0', letterSpacing:'0.5px' }}>
      {text}
    </h4>
  );
}

function KVRow({ label, value, valueColor, last }) {
  return (
    <li style={{
      display      : 'flex',
      justifyContent: 'space-between',
      gap          : '1rem',
      padding      : '8px 0',
      borderBottom : last ? 'none' : '1px solid rgba(255,255,255,0.04)',
      listStyle    : 'none',
    }}>
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
      <div style={{ width:`${Math.min(percent, 100)}%`, height:'100%', background: color, borderRadius:'99px', transition:'width 0.6s ease' }} />
    </div>
  );
}

function ActionButtons({ roundedScore, config }) {
  return (
    <div style={{ display:'flex', gap:'1rem', borderTop:'1px solid rgba(255,255,255,0.05)', paddingTop:'1.5rem', marginTop:'0.5rem' }}>
      <button
        onClick={() => alert(roundedScore > 35 ? 'This number has been added to the blocklist.' : 'This number has been added to your Safe List.')}
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
        {roundedScore > 35 ? 'BLOCK NUMBER' : 'MARK AS SAFE'}
      </button>
      <button
        onClick={() => alert('A detailed security report for this message has been generated.')}
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
function SmsScanResult({ result }) {
  if (!result) return null;

  /* ── Error state ── */
  if (result.error || result.success === false) {
    return (
      <div style={{
        background  : 'rgba(15,23,42,0.6)',
        borderRadius: '24px',
        padding     : '2rem',
        border      : '1px solid rgba(255,77,77,0.2)',
        marginTop   : '2rem',
        fontFamily  : 'system-ui, sans-serif',
      }}>
        <h3 style={{ color:'#ff4d4d', margin:0 }}>Scan Failed</h3>
        <p style={{ color:'#aaa', marginTop:'0.5rem' }}>{result.details || 'Could not connect to service.'}</p>
      </div>
    );
  }

  /* ── Data extraction (Doc 3 logic) ── */
  const score        = Number(result.score) || 0;
  const roundedScore = Math.round(score);
  const isHighRisk   = Boolean(result.isPhishing) || roundedScore >= 50;
  const components   = result.scoring?.components || {};
  const weights      = result.scoring?.weights    || {};
  const urlAnalysis  = result.urlAnalysis;
  const whois        = urlAnalysis?.whois;
  const smsAnalysis  = result.smsAnalysis;

  /* ── Style config ── */
  const config = getRiskConfig(roundedScore);

  const titleText = roundedScore <= 35
    ? 'Message Appears Safe'
    : roundedScore <= 60
      ? 'Suspicious Message Detected'
      : 'High-Risk / Smishing Attempt';

  return (
    <div style={{
      background  : 'rgba(15, 23, 42, 0.6)',
      borderRadius: '24px',
      padding     : '2rem',
      border      : `1px solid ${config.border}`,
      marginTop   : '2rem',
      fontFamily  : 'system-ui, sans-serif',
    }}>

      {/* ── Top-line ── */}
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:'1.5rem', gap:'1rem' }}>
        <div>
          <RiskPill config={config} />
          <h2 style={{ fontSize:'1.8rem', fontWeight:'800', margin:'1.2rem 0 0 0', color:'#fff', letterSpacing:'-0.5px' }}>
            {titleText}
          </h2>
          {isHighRisk && (
            <p style={{ color: config.color, fontWeight:'700', margin:'6px 0 0 0', fontSize:'0.85rem', textTransform:'uppercase' }}>
              Do not interact with this message
            </p>
          )}
        </div>
        <ScoreBadge score={roundedScore} config={config} />
      </div>

      {/* ── Summary message ── */}
      {result.message && (
        <p style={{ color:'#aaa', fontSize:'0.95rem', margin:'0 0 1.5rem 0' }}>{result.message}</p>
      )}

      {/* ── Analysis summary card ── */}
      <SectionCard>
        <span style={{ display:'block', fontSize:'0.65rem', color:'#666', textTransform:'uppercase', fontWeight:'700', marginBottom:'6px' }}>
          Analysis Summary
        </span>
        <p style={{ color:'#ccc', margin:0, fontSize:'0.95rem' }}>
          {roundedScore < 40
            ? 'This message contains patterns typical of legitimate communication.'
            : 'Warning: Found patterns commonly used in smishing / phishing campaigns.'}
        </p>
      </SectionCard>

      {/* ── Phishing probability bar ── */}
      {result.confidence !== undefined && (
        <div style={{ marginBottom:'1.5rem' }}>
          <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'4px' }}>
            <span style={{ color:'#888', fontSize:'0.85rem' }}>Confidence</span>
            <span style={{ color: config.color, fontSize:'0.85rem', fontWeight:'700' }}>{asPercent(result.confidence)}%</span>
          </div>
          <ProgressBar percent={Number(asPercent(result.confidence))} color={config.color} />
        </div>
      )}

      {/* ── Detected links ── */}
      {result.extractedUrl?.length > 0 && (
        <div style={{ marginBottom:'1.5rem' }}>
          <SectionLabel text="Detected Links" />
          {result.extractedUrl.map((url, i) => (
            <div key={i} style={{
              display        : 'flex',
              justifyContent : 'space-between',
              alignItems     : 'center',
              gap            : '1rem',
              padding        : '0.8rem',
              background     : 'rgba(0,0,0,0.2)',
              borderRadius   : '12px',
              border         : `1px solid ${config.border}`,
              marginBottom   : '0.5rem',
            }}>
              <code style={{ color:'#ccc', fontWeight:'600', overflowWrap:'anywhere', fontSize:'0.85rem' }}>{url}</code>
              <span style={{ flexShrink:0, fontSize:'0.65rem', background: config.bg, color: config.color, padding:'3px 10px', borderRadius:'6px', fontWeight:'800', border:`1px solid ${config.border}` }}>
                {isHighRisk ? 'SUSPECTED PHISHING' : 'LEGITIMATE'}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* ── URL Intelligence ── */}
      {urlAnalysis && (
        <div style={{ marginBottom:'1.5rem' }}>
          <SectionLabel text="URL Intelligence" />
          <ul style={{ padding:0, margin:0 }}>
            <KVRow
              label="URL Verdict"
              value={`${urlAnalysis.prediction?.predictedClass || 'Unknown'} (${urlAnalysis.prediction?.riskScore ?? 0}/100)`}
              valueColor={urlAnalysis.prediction?.predictedClass === 'Phishing' ? '#ff4d4d' : '#00ff88'}
            />
            <KVRow
              label="Domain"
              value={whois?.domain || 'Not available'}
              valueColor={whois?.domain ? '#ccc' : '#ff4d4d'}
            />
            <KVRow
              label="Registrar"
              value={whois?.registrar || 'Not registered'}
              valueColor={whois?.registrar ? '#ccc' : '#ff4d4d'}
            />
            <KVRow
              label="Domain Age"
              value={formatDomainAge(whois?.domainAgeDays)}
              valueColor={Number(whois?.domainAgeDays) < 180 || whois?.domainAgeDays === undefined ? '#ff4d4d' : '#00ff88'}
            />
            <KVRow
              label="WHOIS Risk"
              value={`${whois?.predictedClass || 'Unknown'} (${whois?.riskScore ?? 0}/100)`}
              valueColor={(whois?.riskScore ?? 0) >= 40 ? '#ff4d4d' : '#00ff88'}
              last
            />
          </ul>
        </div>
      )}

      {/* ── SMS Indicators grid ── */}
      {result.indicators?.length > 0 && (
        <div style={{ marginBottom:'1.5rem' }}>
          <SectionLabel text={`Security Findings (${result.indicators.length})`} />
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(240px, 1fr))', gap:'0.8rem' }}>
            {result.indicators.map((ind, i) => (
              <IndicatorChip key={i} text={displayIndicator(ind)} color={config.color} />
            ))}
          </div>
        </div>
      )}

      {/* ── Recommendations ── */}
      {result.recommendations?.length > 0 && (
        <div style={{ marginBottom:'1.5rem' }}>
          <SectionLabel text="Recommended Actions" />
          <ul style={{ padding:0, margin:0 }}>
            {result.recommendations.map((rec, i) => (
              <li key={i} style={{
                display      : 'flex',
                alignItems   : 'flex-start',
                gap          : '10px',
                padding      : '8px 0',
                borderBottom : i < result.recommendations.length - 1 ? '1px solid rgba(255,255,255,0.04)' : 'none',
                color        : '#ccc',
                fontSize     : '0.85rem',
                listStyle    : 'none',
              }}>
                <span style={{ color: config.color, marginTop:'2px' }}>›</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ── Safe state ── */}
      {!isHighRisk && (
        <SectionCard>
          <div style={{ display:'flex', gap:'8px', alignItems:'center', marginBottom:'8px' }}>
            <span style={{ color:'#00ff88' }}>✓</span>
            <span style={{ color:'#00ff88', fontWeight:'700', fontSize:'0.85rem' }}>No critical threats detected</span>
          </div>
          <div style={{ display:'flex', gap:'8px', alignItems:'center' }}>
            <span style={{ color:'#00ff88' }}>✓</span>
            <span style={{ color:'#00ff88', fontWeight:'700', fontSize:'0.85rem' }}>Message scan completed</span>
          </div>
        </SectionCard>
      )}

      {/* ── Action buttons ── */}
      <ActionButtons roundedScore={roundedScore} config={config} />
    </div>
  );
}

export default SmsScanResult;