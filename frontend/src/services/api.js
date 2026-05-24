import axios from 'axios'

const API_BASE_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:5005/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add Auth Interceptor to sync with Extension
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

async function postScan(endpoint, payload) {
  try {
    const response = await api.post(endpoint, payload)
    return response.data
  } catch (error) {
    throw new Error(
      error.response?.data?.message || 'Scan request failed'
    )
  }
}

export function scanSms(text) {
  return postScan('/scan-sms', { message : text,})
}

export function scanEmail(content, mode = 'content') {
  return postScan('/scan-email', { content, mode })
}
export function predictEmail(email) {
  return postScan('/predict-email', { email })
}

export function scanUrl(url) {
  return postScan('/scan-url', { url })
}

/**
 * Check URL reputation — combines ML phishing detection with VirusTotal
 * threat intelligence for a comprehensive analysis.
 */
export function checkReputation(url) {
  return postScan('/check_reputation', { url })
}

export function capturePreview(url) {
  return postScan('/capture-preview', { url })
}

export default api;
