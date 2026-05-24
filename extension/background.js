console.log("PhishGuard: Service worker starting");

const DEFAULT_API_BASE = "http://localhost:3000";
const HEALTH_TIMEOUT_MS = 4000;
const SCAN_TIMEOUT_MS = 45000;
const POLL_INTERVAL_MS = 1000;

const CONFIG = {
  API_BASE: DEFAULT_API_BASE,
  THROTTLE_MS: 3000,
};

let lastCheckedUrls = new Map();

async function loadApiBase() {
  try {
    const data = await chrome.storage.local.get(["apiBase"]);
    CONFIG.API_BASE = (data.apiBase || DEFAULT_API_BASE).replace(/\/$/, "");
  } catch (e) {
    CONFIG.API_BASE = DEFAULT_API_BASE;
  }
}

chrome.runtime.onInstalled.addListener(() => loadApiBase());
chrome.runtime.onStartup.addListener(() => loadApiBase());
loadApiBase();

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.action === "api_base_updated" && msg.apiBase) {
    CONFIG.API_BASE = msg.apiBase.replace(/\/$/, "");
    sendResponse({ ok: true });
  }
  return true;
});

function logExt(event, details = {}) {
  console.log("[PhishGuard]", event, details);
}

function extractRiskScore(scanData, envelope) {
  const raw =
    scanData?.risk_score ??
    scanData?.riskScore ??
    scanData?.score ??
    scanData?.ml_prediction?.risk_score ??
    scanData?.prediction?.risk_score ??
    envelope?.risk_score ??
    envelope?.score ??
    0;
  const n = Number(raw);
  if (Number.isNaN(n)) return 0;
  if (n > 0 && n <= 1) return Math.round(n * 100);
  return Math.round(Math.min(100, Math.max(0, n)));
}

async function checkBackendHealth() {
  const bases = [CONFIG.API_BASE];
  const errors = [];

  for (const base of bases) {
    for (const path of ["/api/health", "/health"]) {
      try {
        const res = await fetch(`${base}${path}`, {
          signal: AbortSignal.timeout(HEALTH_TIMEOUT_MS),
        });
        if (res.ok) {
          const body = await res.json().catch(() => ({}));
          if (body.status === "ok" || body.success === true) {
            logExt("health_ok", { path, base });
            return true;
          }
        }
        errors.push(`${path} HTTP ${res.status}`);
      } catch (e) {
        errors.push(`${path}: ${e.name || e.message}`);
      }
    }
  }

  logExt("health_failed", { errors });
  return false;
}

async function pollScanResult(scanId, startedAt) {
  while (Date.now() - startedAt < SCAN_TIMEOUT_MS) {
    await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS));
    const res = await fetch(`${CONFIG.API_BASE}/api/scan/result/${scanId}`, {
      signal: AbortSignal.timeout(HEALTH_TIMEOUT_MS),
    });
    if (res.status === 202) continue;
    if (!res.ok) throw new Error("SCAN_FAILED");
    const data = await res.json();
    if (data.status === "complete") return data;
    if (data.status === "error") throw new Error("SCAN_FAILED");
  }
  const err = new Error("SCAN_TIMEOUT");
  err.name = "AbortError";
  throw err;
}

async function requestUrlScan(url) {
  const startedAt = Date.now();
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), SCAN_TIMEOUT_MS);

  try {
    const response = await fetch(
      `${CONFIG.API_BASE}/scan-url?async=1`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
        signal: controller.signal,
      },
    );

    clearTimeout(timeoutId);

    if (response.status === 202) {
      const pending = await response.json();
      logExt("scan_async_poll", { scanId: pending.scanId });
      const polled = await pollScanResult(pending.scanId, startedAt);
      return polled;
    }

    if (!response.ok) throw new Error("Backend unavailable");
    return await response.json();
  } catch (e) {
    clearTimeout(timeoutId);
    throw e;
  }
}

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.url && tab.url.startsWith("http")) {
    initiateScan(tab.url, tabId);
  }
});

chrome.webNavigation.onCompleted.addListener((details) => {
  if (details.frameId === 0 && details.url.startsWith("http")) {
    initiateScan(details.url, details.tabId);
  }
});

function initiateScan(urlStr, tabId) {
  if (!urlStr || !urlStr.startsWith("http")) return;

  const now = Date.now();
  if (
    lastCheckedUrls.get(tabId) === urlStr &&
    now - (lastCheckedUrls.get(tabId + "_time") || 0) < CONFIG.THROTTLE_MS
  ) {
    return;
  }

  lastCheckedUrls.set(tabId, urlStr);
  lastCheckedUrls.set(tabId + "_time", now);

  logExt("scan_initiated", { url: urlStr, tabId });

  safeSendMessage(tabId, {
    action: "show_security_popup",
    url: urlStr,
    data: { score: 0, status: "scanning" },
  });

  checkUrlPhishing(urlStr, tabId);
}

async function safeSendMessage(tabId, message) {
  try {
    await chrome.tabs.sendMessage(tabId, message);
  } catch (e) {
    try {
      await chrome.scripting.executeScript({
        target: { tabId },
        files: ["content.js"],
      });
      setTimeout(() => chrome.tabs.sendMessage(tabId, message).catch(() => {}), 100);
    } catch (err) {
      logExt("message_failed", { tabId });
    }
  }
}

async function checkUrlPhishing(url, tabId) {
  const scanStarted = Date.now();
  await loadApiBase();

  try {
    const healthy = await checkBackendHealth();
    if (!healthy) {
      throw new Error("BACKEND_OFFLINE");
    }

    logExt("scan_started", { url, api: CONFIG.API_BASE });

    const envelope = await requestUrlScan(url);
    const scanData = envelope.result || envelope;
    const scoreValue = extractRiskScore(scanData, envelope);
    const durationMs = Date.now() - scanStarted;
    const uiVerdict = scanData.ui_verdict || scanData.final_verdict || "SAFE";
    const debug = scanData.score_debug || {};

    logExt("scan_completed", {
      url,
      score: scoreValue,
      ui_verdict: uiVerdict,
      durationMs,
      path: scanData.fast_path || (scanData.cached ? "cache" : "ml"),
      raw_ml_score: debug.raw_ml_score,
      heuristic_score: debug.heuristic_score,
      trust_score: debug.trust_score,
      final_normalized_score: debug.final_normalized_score ?? scoreValue,
    });

    safeSendMessage(tabId, {
      action: "show_security_popup",
      url,
      data: {
        status: "complete",
        score: scoreValue,
        ui_verdict: uiVerdict,
        message: scanData.message,
        summary: scanData.summary,
        durationMs,
        score_debug: debug,
      },
    });
  } catch (error) {
    const durationMs = Date.now() - scanStarted;
    const isOffline = error.message === "BACKEND_OFFLINE";
    const isTimeout =
      error.name === "AbortError" || error.message === "SCAN_TIMEOUT";

    if (isTimeout) {
      logExt("scan_timeout", { url, durationMs, limitMs: SCAN_TIMEOUT_MS });
    } else if (isOffline) {
      logExt("scan_offline", { url, durationMs });
    } else {
      logExt("scan_error", { url, durationMs, error: error.message });
    }

    safeSendMessage(tabId, {
      action: "show_security_popup",
      url,
      data: {
        score: 0,
        status: "error",
        errorType: isOffline ? "offline" : isTimeout ? "timeout" : "unknown",
      },
    });
  }
}
