/**
 * Single source of truth for UI verdict + score (extension popup).
 * Ranges: 0-49 SAFE | 50-55 CAUTION | 56+ DANGEROUS
 */

export const TRUSTED_DOMAINS = new Set([
  'google.com',
  'gmail.com',
  'googlemail.com',
  'github.com',
  'microsoft.com',
  'live.com',
  'office.com',
  'outlook.com',
  'youtube.com',
  'linkedin.com',
  'apple.com',
  'pw.live',
])

const TRUSTED_CAP = 35
const ML_OVERRIDE = 92

export function uiVerdictFromScore(score) {
  const s = Math.round(Number(score) || 0)
  if (s >= 56) return 'DANGEROUS'
  if (s >= 50) return 'CAUTION'
  return 'SAFE'
}

export function uiMessageForVerdict(verdict) {
  switch (verdict) {
    case 'DANGEROUS':
      return 'High-risk phishing indicators detected.'
    case 'CAUTION':
      return 'Some suspicious patterns detected — proceed with care.'
    default:
      return 'No significant phishing indicators detected.'
  }
}

export function isTrustedDomain(domain) {
  if (!domain) return false
  for (const trusted of TRUSTED_DOMAINS) {
    if (domain === trusted || domain.endsWith(`.${trusted}`)) return true
  }
  return false
}

function capTrustedScore(domain, score, mlScore) {
  if (!isTrustedDomain(domain)) return score
  if (mlScore != null && mlScore >= ML_OVERRIDE) return score
  return Math.min(score, TRUSTED_CAP)
}

/**
 * Normalize ML API payload into one consistent result for the extension.
 */
export function normalizeScanResult(url, mlData) {
  const prediction = mlData?.prediction || {}
  const scoring = mlData?.scoring || {}

  const heuristicScore = Math.round(
    scoring.heuristic_raw ?? scoring.components?.heuristic ?? 0,
  )
  const mlScore = Math.round(
    scoring.components?.ml ??
      (prediction.phishing_probability != null
        ? prediction.phishing_probability * 100
        : 0),
  )
  const trustScore = Math.round(scoring.trust_score ?? 0)

  let rawScore = Math.round(
    scoring.final_normalized_score ??
      prediction.risk_score ??
      mlData?.risk_score ??
      mlScore,
  )

  const domain =
    mlData?.domain ||
    (() => {
      try {
        return new URL(url).hostname.replace(/^www\./, '').toLowerCase()
      } catch {
        return ''
      }
    })()

  const finalScore = capTrustedScore(domain, rawScore, mlScore)
  const uiVerdict =
    prediction.ui_verdict ||
    scoring.ui_verdict ||
    uiVerdictFromScore(finalScore)

  const debug = {
    raw_ml_score: mlScore,
    heuristic_score: heuristicScore,
    trust_score: trustScore,
    final_normalized_score: finalScore,
    ui_verdict: uiVerdict,
    trusted_host: isTrustedDomain(domain),
    components: scoring.components || {},
  }

  return {
    url,
    domain,
    risk_score: finalScore,
    score: finalScore,
    final_verdict: uiVerdict,
    ui_verdict: uiVerdict,
    message: uiMessageForVerdict(uiVerdict),
    summary: debug.trusted_host
      ? 'Verified trusted domain with reduced heuristic weight.'
      : 'Score from balanced ML + heuristic analysis.',
    trusted: isTrustedDomain(domain),
    fast_path: mlData?.fast_path || 'ml_predict_url',
    ml_prediction: prediction,
    indicators: mlData?.indicators,
    score_debug: debug,
    cached: false,
  }
}

export function logScoreDebug(url, debug) {
  console.log(
    '[PhishGuard Score]',
    JSON.stringify({
      url,
      ...debug,
    }),
  )
}
