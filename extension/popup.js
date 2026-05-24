const DEFAULT_API = "http://localhost:3000";

async function getApiBase() {
  const data = await chrome.storage.local.get(["apiBase"]);
  return (data.apiBase || DEFAULT_API).replace(/\/$/, "");
}

async function setApiBase(url) {
  const clean = url.replace(/\/$/, "");
  await chrome.storage.local.set({ apiBase: clean });
  await chrome.runtime.sendMessage({ action: "api_base_updated", apiBase: clean });
  return clean;
}

document.addEventListener("DOMContentLoaded", async () => {
  const apiInput = document.getElementById("api-url");
  const checkResult = document.getElementById("check-result");
  const protectionStatus = document.getElementById("protection-status");

  apiInput.value = await getApiBase();

  document.getElementById("save-api-btn").addEventListener("click", async () => {
    const saved = await setApiBase(apiInput.value.trim() || DEFAULT_API);
    apiInput.value = saved;
    checkResult.textContent = "Saved API: " + saved;
    checkResult.style.color = "#065f46";
  });

  document.getElementById("check-btn").addEventListener("click", runExtensionCheck);

  const data = await chrome.storage.local.get(["token", "user"]);
  if (data.token) {
    showLoggedIn(data.user);
    checkSubscription(data.token);
  } else {
    showLoggedOut();
  }

  document.getElementById("login-btn").addEventListener("click", async () => {
    const apiBase = await getApiBase();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    try {
      const response = await fetch(apiBase + "/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const result = await response.json();
      if (result.success) {
        await chrome.storage.local.set({ token: result.token, user: result.user });
        showLoggedIn(result.user);
        checkSubscription(result.token);
      } else {
        alert(result.error || "Login failed");
      }
    } catch (e) {
      alert("Cannot reach backend at " + apiBase);
    }
  });

  document.getElementById("logout-btn").addEventListener("click", async () => {
    await chrome.storage.local.remove(["token", "user"]);
    showLoggedOut();
  });

  runExtensionCheck();
});

async function runExtensionCheck() {
  const checkResult = document.getElementById("check-result");
  const protectionStatus = document.getElementById("protection-status");
  const apiBase = await getApiBase();
  const lines = [];

  lines.push("Extension: OK (popup loaded)");
  lines.push("API URL: " + apiBase);

  try {
    const health = await fetch(apiBase + "/api/health", { signal: AbortSignal.timeout(4000) });
    if (health.ok) {
      lines.push("Backend: OK");
      protectionStatus.textContent = "Protection: Active (backend online)";
      protectionStatus.className = "status ok";
    } else {
      lines.push("Backend: HTTP " + health.status);
      protectionStatus.textContent = "Protection: Backend error";
      protectionStatus.className = "status err";
    }
  } catch (e) {
    lines.push("Backend: OFFLINE - run npm run dev in backend/");
    protectionStatus.textContent = "Protection: Offline";
    protectionStatus.className = "status err";
  }

  try {
    const scan = await fetch(apiBase + "/scan-url", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: "https://www.google.com" }),
      signal: AbortSignal.timeout(45000),
    });
    const body = await scan.json();
    if (scan.ok) {
      const score =
        body.result?.risk_score ?? body.result?.score ?? body.score ?? "?";
      lines.push("Scan test: OK (google.com score " + score + "%)");
    } else {
      lines.push("Scan test: failed HTTP " + scan.status);
    }
  } catch (e) {
    lines.push("Scan test: failed (start URL ML on port 5001)");
  }

  checkResult.innerHTML = lines.map((l) => "&#8226; " + l).join("<br>");
  checkResult.style.color = "#334155";
}

function showLoggedIn() {
  document.getElementById("auth-section").style.display = "none";
  document.getElementById("logout-section").style.display = "block";
}

function showLoggedOut() {
  document.getElementById("auth-section").style.display = "block";
  document.getElementById("logout-section").style.display = "none";
  document.getElementById("subscription-info").textContent = "";
}

async function checkSubscription(token) {
  const apiBase = await getApiBase();
  try {
    const response = await fetch(apiBase + "/subscription/status", {
      headers: { Authorization: "Bearer " + token },
    });
    const result = await response.json();
    if (result.has_subscription) {
      document.getElementById("subscription-info").innerHTML =
        "Plan: <b>" +
        result.plan +
        "</b> | Expires: " +
        new Date(result.expiry_date).toLocaleDateString();
    }
  } catch (e) {
    /* optional */
  }
}
