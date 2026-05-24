console.log("PhishGuard: Content script loaded at", window.location.href);

function onDomReady(fn) {
  if (document.body) {
    fn();
  } else {
    document.addEventListener("DOMContentLoaded", fn, { once: true });
  }
}

onDomReady(function () {
  if (document.getElementById("pg-load-indicator")) return;
  var indicator = document.createElement("div");
  indicator.id = "pg-load-indicator";
  indicator.style.cssText =
    "position:fixed;bottom:10px;left:10px;width:10px;height:10px;background:#6366f1;z-index:2147483647;border-radius:50%;opacity:0.5;pointer-events:none;";
  document.body.appendChild(indicator);
});

chrome.runtime.onMessage.addListener(function (request) {
  if (request.action === "show_security_popup") {
    onDomReady(function () {
      createSecurityPopup(request.url, request.data);
    });
  }
});

/** Single UI mapping: score drives category and colors (0-49 SAFE, 50-55 CAUTION, 56+ DANGEROUS) */
function categoryFromScore(score) {
  var s = Math.round(Number(score) || 0);
  if (s >= 56) {
    return {
      category: "DANGEROUS",
      color: "#ef4444",
      bgColor: "rgba(239, 68, 68, 0.2)",
      message: "High-risk phishing indicators detected.",
      summary: "Avoid entering passwords or payment details.",
      autoHide: 0,
    };
  }
  if (s >= 50) {
    return {
      category: "CAUTION",
      color: "#f59e0b",
      bgColor: "rgba(245, 158, 11, 0.2)",
      message: "Some suspicious patterns detected.",
      summary: "Proceed with care on this site.",
      autoHide: 10000,
    };
  }
  return {
    category: "SAFE",
    color: "#10b981",
    bgColor: "rgba(16, 185, 129, 0.15)",
    message: "No significant phishing indicators detected.",
    summary: "PhishGuard verified this domain.",
    autoHide: 5000,
  };
}

function createSecurityPopup(url, data) {
  var popup = document.getElementById("phishguard-security-popup");
  var isUpdate = !!popup;
  var domain = new URL(url).hostname;
  var score =
    data.score !== undefined && data.score !== null
      ? Math.round(Number(data.score))
      : 0;

  var config;

  if (data.status === "scanning") {
    config = {
      category: "SCANNING",
      color: "#6366f1",
      bgColor: "rgba(99, 102, 241, 0.15)",
      message: "Analyzing site with PhishGuard AI...",
      summary: data.summary || "Checking URL patterns and reputation...",
      autoHide: 0,
    };
  } else if (data.status === "error") {
    if (data.errorType === "timeout") {
      config = {
        category: "TIMEOUT",
        color: "#f59e0b",
        bgColor: "rgba(245, 158, 11, 0.15)",
        message: "Scan took too long.",
        summary: "Reload the page to retry.",
        autoHide: 10000,
      };
    } else if (data.errorType === "offline") {
      config = {
        category: "OFFLINE",
        color: "#94a3b8",
        bgColor: "rgba(148, 163, 184, 0.15)",
        message: "Could not reach PhishGuard backend.",
        summary: "Run: cd backend && npm run dev (port 3000)",
        autoHide: 8000,
      };
    } else {
      config = {
        category: "ERROR",
        color: "#94a3b8",
        bgColor: "rgba(148, 163, 184, 0.15)",
        message: "Scan failed unexpectedly.",
        summary: "Use extension popup to check backend.",
        autoHide: 8000,
      };
    }
  } else {
    config = categoryFromScore(score);
    if (data.summary) config.summary = data.summary;
  }

  if (!isUpdate) {
    popup = document.createElement("div");
    popup.id = "phishguard-security-popup";
    document.body.appendChild(popup);
  }

  var pulseDot =
    data.status === "scanning"
      ? '<span style="width:6px;height:6px;border-radius:50%;background:' +
        config.color +
        ';animation:pg-pulse 1s infinite;"></span>'
      : '<span style="width:6px;height:6px;border-radius:50%;background:' +
        config.color +
        ';"></span>';

  var actionButtons;
  if (config.category === "DANGEROUS") {
    actionButtons =
      '<button id="pg-leave-btn" style="flex:2;background:#ef4444;color:#fff;border:none;padding:10px;border-radius:8px;font-weight:700;font-size:12px;cursor:pointer;">LEAVE SITE</button>' +
      '<button id="pg-close-mini" style="flex:1;background:rgba(255,255,255,0.05);color:#94a3b8;border:none;padding:10px;border-radius:8px;font-size:11px;cursor:pointer;">IGNORE</button>';
  } else {
    actionButtons =
      '<button id="pg-close-mini" style="margin-left:auto;background:none;border:none;font-size:11px;color:#64748b;cursor:pointer;text-decoration:underline;padding:5px;">Dismiss</button>';
  }

  popup.style.cssText =
    "position:fixed;top:20px;right:20px;width:320px;background:#0f172a;color:#f8fafc;border-radius:14px;" +
    "box-shadow:0 10px 40px rgba(0,0,0,0.6);z-index:2147483647;font-family:system-ui,sans-serif;" +
    "overflow:hidden;border:1px solid rgba(255,255,255,0.1);" +
    (isUpdate ? "" : "animation:pg-slide-in 0.6s ease;");

  popup.innerHTML =
    '<div style="background:' +
    config.bgColor +
    ';padding:16px;border-bottom:1px solid rgba(255,255,255,0.05);">' +
    '<div style="display:flex;justify-content:space-between;align-items:flex-start;">' +
    '<div><div style="font-size:10px;font-weight:800;color:' +
    config.color +
    ';letter-spacing:0.1em;margin-bottom:4px;display:flex;align-items:center;gap:4px;">' +
    pulseDot +
    " PHISHGUARD LIVE</div>" +
    '<div style="font-size:20px;font-weight:800;color:#fff;">' +
    config.category +
    "</div></div>" +
    '<div style="text-align:right;">' +
    '<div style="font-size:24px;font-weight:900;color:' +
    config.color +
    ';">' +
    score +
    "%</div>" +
    '<div style="font-size:9px;color:#94a3b8;font-weight:600;">RISK INDEX</div>' +
    "</div></div></div>" +
    '<div style="padding:16px;">' +
    '<p style="margin:0 0 6px;font-size:13px;color:#fff;font-weight:600;">' +
    config.message +
    "</p>" +
    '<p style="margin:0 0 12px;font-size:11px;color:#94a3b8;">' +
    config.summary +
    "</p>" +
    '<div style="font-size:10px;background:rgba(0,0,0,0.3);padding:6px 10px;border-radius:6px;color:#64748b;font-family:monospace;overflow:hidden;text-overflow:ellipsis;">' +
    domain +
    "</div>" +
    '<div style="margin-top:16px;display:flex;gap:8px;">' +
    actionButtons +
    "</div></div>" +
    "<style>@keyframes pg-slide-in{from{transform:translateX(120%);opacity:0}to{transform:none;opacity:1}}" +
    "@keyframes pg-fade-out{to{transform:translateX(50px);opacity:0}}" +
    "@keyframes pg-pulse{50%{opacity:0.4}}</style>";

  function closePopup() {
    popup.style.animation = "pg-fade-out 0.3s ease forwards";
    setTimeout(function () {
      if (popup.parentNode) popup.remove();
    }, 300);
  }

  var closeBtn = popup.querySelector("#pg-close-mini");
  if (closeBtn) closeBtn.onclick = closePopup;

  var leaveBtn = popup.querySelector("#pg-leave-btn");
  if (leaveBtn) {
    leaveBtn.onclick = function () {
      window.history.back();
    };
  }

  if (config.autoHide > 0 && data.status === "complete") {
    setTimeout(function () {
      if (document.getElementById("phishguard-security-popup") === popup) {
        closePopup();
      }
    }, config.autoHide);
  }
}
