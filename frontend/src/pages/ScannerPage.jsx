import { useState, useEffect } from 'react'
import { analyzeThreat } from './scannerUtils'

function ScannerPage({ config, goToPage }) {
  const [input, setInput] = useState('')
  const [result, setResult] = useState(null)
  const [isExtensionLinkActive, setIsExtensionLinkActive] = useState(false)

  useEffect(() => {
    // Check if the user is logged in (synced with extension)
    const token = localStorage.getItem('token');
    setIsExtensionLinkActive(!!token);
  }, []);

  function handleSubmit(event) {
    event.preventDefault()
    if (!input.trim()) {
      setResult(null)
      return
    }
    setResult(analyzeThreat(input, config.type))
  }

  return (
    <section className="scanner-page">
      <button className="back-btn" type="button" onClick={() => goToPage('home')}>
        Back to home
      </button>

      <div className="scanner-layout">
        <div className="scanner-copy">
          <p className="eyebrow">{config.kicker}</p>
          <h1>{config.title}</h1>
          <p>{config.description}</p>
          <ul className="check-list">
            {config.points.map((point) => (
              <li key={point}>{point}</li>
            ))}
          </ul>
        </div>

        <form className="scanner-form" onSubmit={handleSubmit}>
          <label htmlFor={config.type}>{config.label}</label>
          <textarea
            id={config.type}
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder={config.placeholder}
            rows={config.rows}
          />
          <button type="submit" className="primary-btn">Scan now</button>

          {!isExtensionLinkActive && (
            <p className="extension-hint" style={{ fontSize: '0.8rem', color: '#666', marginTop: '10px' }}>
              💡 Pro Tip: Install the <strong>PhishGuard Extension</strong> and login to enable 24/7 background protection.
            </p>
          )}

          {result && (
            <div className={`result-box ${result.level.toLowerCase().replace(' ', '-')}`}>
              <div>
                <span className="result-label">{result.level}</span>
                <strong>{result.score}/100</strong>
              </div>
              <ul>
                {result.signals.map((signal) => (
                  <li key={signal}>{signal}</li>
                ))}
              </ul>
            </div>
          )}
        </form>
      </div>
    </section>
  )
}

export default ScannerPage
