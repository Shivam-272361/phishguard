import crypto from 'crypto'
import { predictURLSpamFast } from './mlService.js'
import {
  TRUSTED_DOMAINS,
  isTrustedDomain,
  normalizeScanResult,
  logScoreDebug,
  uiMessageForVerdict,
} from './scoreNormalizer.js'

const CACHE_TTL_MS = 24 * 60 * 60 * 1000
const CACHE_VERSION = 2

const scanCache = new Map()
const pendingScans = new Map()

export function normalizeDomain(url) {
  try {
    const host = new URL(url).hostname.toLowerCase()
    return host.replace(/^www\./, '')
  } catch {
    return null
  }
}

function buildTrustedResult(url, domain) {
  return {
    url,
    domain,
    risk_score: 5,
    score: 5,
    final_verdict: 'SAFE',
    ui_verdict: 'SAFE',
    trusted: true,
    fast_path: 'trusted_domain',
    message: uiMessageForVerdict('SAFE'),
    summary: 'Trusted domain — lightweight verification only.',
    score_debug: {
      raw_ml_score: 0,
      heuristic_score: 0,
      trust_score: 100,
      final_normalized_score: 5,
      ui_verdict: 'SAFE',
      trusted_host: true,
    },
    cached: false,
  }
}

function cacheKey(domain) {
  return `${CACHE_VERSION}:${domain}`
}

export function getCachedScan(url) {
  const domain = normalizeDomain(url)
  if (!domain) return null
  const entry = scanCache.get(cacheKey(domain))
  if (!entry) return null
  if (Date.now() > entry.expiresAt) {
    scanCache.delete(cacheKey(domain))
    return null
  }
  return { ...entry.result, cached: true, fast_path: 'cache' }
}

function setCachedScan(url, result) {
  const domain = normalizeDomain(url)
  if (!domain) return
  scanCache.set(cacheKey(domain), {
    result: { ...result, domain },
    expiresAt: Date.now() + CACHE_TTL_MS,
  })
}

export function getScanJob(scanId) {
  return pendingScans.get(scanId) || null
}

export function logScan(event, details = {}) {
  const line = { ts: new Date().toISOString(), event, ...details }
  console.log('[PhishGuard Scan]', JSON.stringify(line))
}

export async function resolveUrlScan(url) {
  const t0 = Date.now()
  logScan('scan_started', { url })

  const cached = getCachedScan(url)
  if (cached) {
    logScan('scan_completed', {
      url,
      durationMs: Date.now() - t0,
      path: 'cache',
      risk_score: cached.risk_score,
    })
    return { immediate: true, result: cached }
  }

  const domain = normalizeDomain(url)
  if (isTrustedDomain(domain)) {
    const trusted = buildTrustedResult(url, domain)
    setCachedScan(url, trusted)
    logScan('scan_completed', {
      url,
      durationMs: Date.now() - t0,
      path: 'trusted_domain',
      risk_score: trusted.risk_score,
    })
    return { immediate: true, result: trusted }
  }

  try {
    const mlRaw = await predictURLSpamFast(url)
    const result = normalizeScanResult(url, mlRaw)
    logScoreDebug(url, result.score_debug)
    setCachedScan(url, result)
    logScan('scan_completed', {
      url,
      durationMs: Date.now() - t0,
      path: result.fast_path,
      risk_score: result.risk_score,
      ui_verdict: result.ui_verdict,
      score_debug: result.score_debug,
    })
    return { immediate: true, result }
  } catch (error) {
    logScan('scan_failed', {
      url,
      durationMs: Date.now() - t0,
      error: error.message,
    })
    throw error
  }
}

export function startAsyncUrlScan(url) {
  const cached = getCachedScan(url)
  if (cached) {
    return { immediate: true, result: cached }
  }

  const domain = normalizeDomain(url)
  if (isTrustedDomain(domain)) {
    const trusted = buildTrustedResult(url, domain)
    setCachedScan(url, trusted)
    return { immediate: true, result: trusted }
  }

  const scanId = crypto.randomUUID()
  pendingScans.set(scanId, {
    status: 'scanning',
    url,
    startedAt: Date.now(),
  })

  logScan('scan_async_started', { url, scanId })

  runAsyncScan(scanId, url).catch(() => {})

  return { immediate: false, scanId, status: 'scanning' }
}

async function runAsyncScan(scanId, url) {
  const t0 = Date.now()
  try {
    const mlRaw = await predictURLSpamFast(url)
    const result = normalizeScanResult(url, mlRaw)
    logScoreDebug(url, result.score_debug)
    setCachedScan(url, result)
    pendingScans.set(scanId, {
      status: 'complete',
      url,
      result,
      durationMs: Date.now() - t0,
    })
    logScan('scan_async_completed', {
      url,
      scanId,
      durationMs: Date.now() - t0,
      risk_score: result.risk_score,
    })
  } catch (error) {
    pendingScans.set(scanId, {
      status: 'error',
      url,
      error: error.message,
      durationMs: Date.now() - t0,
    })
    logScan('scan_async_failed', { url, scanId, error: error.message })
  } finally {
    setTimeout(() => pendingScans.delete(scanId), 5 * 60 * 1000)
  }
}

export async function warmMlConnection() {
  const url = process.env.URL_ML_URL
  if (!url) return
  try {
    const res = await fetch(`${url.replace(/\/$/, '')}/health`, {
      signal: AbortSignal.timeout(5000),
    })
    if (res.ok) {
      logScan('ml_warmup_success', { url })
    }
  } catch (e) {
    logScan('ml_warmup_failed', { error: e.message })
  }
}
