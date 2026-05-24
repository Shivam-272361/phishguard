export function analyzeThreat(value, type) {
  const text = value.trim().toLowerCase()
  let score = 18
  const signals = []

  const checks = [
    ['urgent', 12, 'Urgent language detected'],
    ['verify', 10, 'Verification request detected'],
    ['password', 14, 'Password-related wording found'],
    ['bank', 12, 'Banking keyword found'],
    ['prize', 14, 'Prize or reward lure found'],
    ['limited time', 12, 'Time pressure detected'],
    ['click', 8, 'Click instruction found'],
    ['http://', 16, 'Unsecured HTTP link found'],
    ['bit.ly', 18, 'Shortened link detected'],
    ['tinyurl', 18, 'Shortened link detected'],
    ['login', 12, 'Login request detected'],
  ]

  checks.forEach(([pattern, points, label]) => {
    if (text.includes(pattern)) {
      score += points
      signals.push(label)
    }
  })

  if (type === 'url' || type === 'website') {
    if (text.includes('@')) {
      score += 18
      signals.push('URL contains an @ symbol')
    }
    if (!text.startsWith('https://')) {
      score += 10
      signals.push('HTTPS is missing')
    }
    if ((text.match(/\./g) || []).length > 3) {
      score += 12
      signals.push('Many subdomains detected')
    }
  }

  const riskScore = Math.min(score, 100)
  const level = riskScore >= 70 ? 'High risk' : riskScore >= 40 ? 'Medium risk' : 'Low risk'

  return {
    level,
    score: riskScore,
    signals: signals.length ? signals : ['No obvious phishing patterns found'],
  }
}
