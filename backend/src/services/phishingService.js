const keywordRules = [
  { pattern: /\burgent\b/i, points: 12, label: 'Urgent language detected', category: 'urgency' },
  { pattern: /click\s+(here|now|this|the link)/i, points: 14, label: 'Click pressure detected', category: 'call_to_action' },
  { pattern: /verify\s+(your\s+)?(account|identity|login|details)/i, points: 18, label: 'Verification request detected', category: 'credential_theft' },
  { pattern: /(account|card|wallet)\s+(suspended|locked|blocked|restricted)/i, points: 22, label: 'Account lock threat detected', category: 'threat' },
  { pattern: /(password|passcode|pin|otp|cvv|ssn|social security|pan|aadhaar|kyc)/i, points: 20, label: 'Sensitive information request detected', category: 'credential_theft' },
  { pattern: /(winner|prize|reward|lottery|gift card|cashback|claim)/i, points: 14, label: 'Reward lure detected', category: 'reward_lure' },
  { pattern: /(limited time|expires|act now|final notice|last chance)/i, points: 14, label: 'Time pressure detected', category: 'urgency' },
  { pattern: /(bank|paypal|amazon|apple|microsoft|netflix|upi|fedex|dhl)/i, points: 8, label: 'Brand or payment keyword detected', category: 'brand_impersonation' },
  { pattern: /(refund|invoice|payment failed|billing issue|tax|customs fee)/i, points: 12, label: 'Payment lure detected', category: 'financial_lure' },
  { pattern: /(update|confirm|restore|activate|unlock).{0,35}(detail|account|kyc|pan|aadhaar|profile|information)/i, points: 20, label: 'Account update request detected', category: 'credential_theft' },
  { pattern: /(avoid|prevent|stop).{0,30}(freeze|block|suspend|lock|closure)|(?:account|card|wallet).{0,25}(freeze|blocked|suspended|locked)/i, points: 24, label: 'Threat of account freeze or blocking detected', category: 'threat' },
]

const shorteners = ['bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly', 'cutt.ly', 'rebrand.ly']

function clampScore(value) {
  const numericValue = Number(value)
  if (!Number.isFinite(numericValue)) return 0
  return Math.max(0, Math.min(100, Math.round(numericValue)))
}

function probabilityToScore(value) {
  const numericValue = Number(value)
  if (!Number.isFinite(numericValue)) return 0
  return clampScore(numericValue <= 1 ? numericValue * 100 : numericValue)
}

function getRiskLevel(score) {
  if (score >= 80) return 'critical'
  if (score >= 60) return 'high'
  if (score >= 40) return 'medium'
  return 'low'
}

function createFinding(label, points, category = 'general', severity = 'medium') {
  return { label, points, category, severity }
}

function countMatches(text, regex) {
  return (text.match(regex) || []).length
}

function buildTextHeuristicAnalysis(text, extractedUrls = []) {
  const findings = []

  keywordRules.forEach((rule) => {
    if (rule.pattern.test(text)) {
      findings.push(createFinding(rule.label, rule.points, rule.category))
    }
  })

  if (extractedUrls.length > 0) {
    findings.push(createFinding('External link included in message', 12, 'embedded_url'))
  }

  if (extractedUrls.length > 1) {
    findings.push(createFinding('Multiple links found', 10, 'embedded_url'))
  }

  if (extractedUrls.some((url) => shorteners.some((shortener) => url.toLowerCase().includes(shortener)))) {
    findings.push(createFinding('Shortened URL detected', 20, 'embedded_url', 'high'))
  }

  if (countMatches(text, /!/g) >= 3) {
    findings.push(createFinding('Excessive punctuation detected', 7, 'formatting', 'low'))
  }

  if (/[A-Z]{8,}/.test(text)) {
    findings.push(createFinding('Large all-caps text detected', 6, 'formatting', 'low'))
  }

  if (/\b\d{4,8}\b/.test(text) && /(otp|code|pin|verify)/i.test(text)) {
    findings.push(createFinding('OTP or code lure detected', 16, 'credential_theft', 'high'))
  }

  const findingsByLabel = new Map()
  findings.forEach((finding) => {
    const existing = findingsByLabel.get(finding.label)
    if (!existing || finding.points > existing.points) {
      findingsByLabel.set(finding.label, finding)
    }
  })

  const dedupedFindings = [...findingsByLabel.values()]
  const score = clampScore(dedupedFindings.reduce((total, finding) => total + finding.points, 0))

  return {
    score,
    riskLevel: getRiskLevel(score),
    isPhishing: score >= 40,
    findings: dedupedFindings,
    indicators: dedupedFindings.length
      ? dedupedFindings.map((finding) => finding.label)
      : ['No suspicious indicators found'],
  }
}

function getMessageMlScore(textAnalysis) {
  const prediction = textAnalysis?.prediction || textAnalysis || {}

  if (prediction.spam_probability != null) {
    return probabilityToScore(prediction.spam_probability)
  }

  if (prediction.is_spam === true || prediction.label === 'spam') {
    return probabilityToScore(prediction.confidence ?? 1)
  }

  return 0
}

function getUrlRuleScore(urlAnalysis) {
  if (!urlAnalysis) return 0
  const prediction = urlAnalysis.prediction || {}
  return clampScore(prediction.risk_score ?? probabilityToScore(prediction.phishing_probability))
}

function getUrlMlScore(urlAnalysis) {
  if (!urlAnalysis) return 0
  return probabilityToScore(
    urlAnalysis.ml_prediction?.phishing_probability ??
    urlAnalysis.scoring?.components?.ml,
  )
}

function getWhoisScore(urlAnalysis) {
  if (!urlAnalysis) return 0
  return probabilityToScore(
    urlAnalysis.whois?.prediction?.risk_score ??
    urlAnalysis.whois_analysis?.whois_prediction?.risk_score ??
    urlAnalysis.scoring?.components?.whois,
  )
}

function combineScores({ textHeuristicScore, messageMlScore, urlRuleScore, urlMlScore, whoisScore, hasUrl }) {
  const components = hasUrl
    ? {
        smsHeuristic: textHeuristicScore,
        smsMl: messageMlScore,
        urlHeuristic: urlRuleScore,
        urlMl: urlMlScore,
        whois: whoisScore,
      }
    : {
        smsHeuristic: textHeuristicScore,
        smsMl: messageMlScore,
      }

  const weights = hasUrl
    ? {
        smsHeuristic: 0.05,
        smsMl: 0.40,
        urlHeuristic: 0.10,
        urlMl: 0.15,
        whois: 0.30,
      }
    : {
        smsHeuristic: 0.05,
        smsMl: 0.95,
      }

  const score = clampScore(
    Object.entries(components).reduce((total, [key, value]) => total + value * weights[key], 0),
  )

  return {
    score,
    riskLevel: getRiskLevel(score),
    isPhishing: score >= 40,
    weights,
    components,
  }
}

function compactMessagePrediction(textAnalysis) {
  const prediction = textAnalysis?.prediction || {}
  return {
    label: prediction.label ?? null,
    isSpam: Boolean(prediction.is_spam),
    confidence: probabilityToScore(prediction.confidence),
    spamProbability: probabilityToScore(prediction.spam_probability),
  }
}

function compactUrlAnalysis(urlAnalysis) {
  if (!urlAnalysis) return null

  const prediction = urlAnalysis.prediction || {}
  const whois = urlAnalysis.whois || urlAnalysis.whois_analysis || null
  const whoisPrediction = whois?.prediction || whois?.whois_prediction || {}

  return {
    url: urlAnalysis.url,
    prediction: {
      predictedClass: prediction.predicted_class ?? null,
      riskScore: clampScore(prediction.risk_score ?? 0),
    },
    indicators: urlAnalysis.indicators || prediction.risk_indicators || [],
    whois: whois
      ? {
          domain: whois.domain ?? null,
          registrar: whois.registrar ?? null,
          creationDate: whois.creation_date ?? null,
          expiryDate: whois.expiry_date ?? null,
          domainAgeDays: whoisPrediction.domain_age_days ?? null,
          daysUntilExpiry: whoisPrediction.days_until_expiry ?? null,
          predictedClass: whoisPrediction.predicted_class ?? null,
          riskScore: probabilityToScore(whoisPrediction.risk_score),
        }
      : null,
  }
}

export function buildSmsScanResult(
  text,
  { extractedUrls = [], textAnalysis = {}, urlAnalysis = null, type = 'sms' } = {},
) {
  const hasUrl = extractedUrls.length > 0
  const textHeuristicAnalysis = buildTextHeuristicAnalysis(text, extractedUrls)

  const scoring = combineScores({
    textHeuristicScore: textHeuristicAnalysis.score,
    messageMlScore: getMessageMlScore(textAnalysis),
    urlRuleScore: getUrlRuleScore(urlAnalysis),
    urlMlScore: getUrlMlScore(urlAnalysis),
    whoisScore: getWhoisScore(urlAnalysis),
    hasUrl,
  })

  const isPhishing = scoring.isPhishing
  const confidence = isPhishing
    ? Math.min(99, 68 + Math.round(scoring.score / 3))
    : Math.max(70, 98 - Math.round(scoring.score / 3))

  const contentLabel = type === 'email' ? 'email' : 'SMS'

  return {
    success: true,
    type,
    message: isPhishing
      ? `Warning: This ${contentLabel} shows signs of phishing.`
      : `This ${contentLabel} appears to be safe.`,
    details: isPhishing
      ? hasUrl
        ? 'Message text patterns and URL risk signals indicate this content may be unsafe.'
        : 'Message text patterns indicate this content may be unsafe.'
      : 'No strong phishing pattern was found. Stay cautious with unexpected links or senders.',
    isPhishing,
    riskLevel: scoring.riskLevel,
    score: scoring.score,
    confidence,
    extractedUrl: extractedUrls,
    prediction: compactMessagePrediction(textAnalysis),
    smsAnalysis: {
      heuristicScore: scoring.components.smsHeuristic,
      mlScore: scoring.components.smsMl,
    },
    scoring,
    urlAnalysis: compactUrlAnalysis(urlAnalysis),
    recommendations: isPhishing
      ? [
          'Do not click any links in this message',
          'Do not share OTP, passwords, or banking details',
          'Verify only through the official app or website',
        ]
      : [
          'Verify the sender if the message was unexpected',
          'Open important services directly from the official app or bookmarked website',
        ],
    indicators: textHeuristicAnalysis.indicators,
  }
}
