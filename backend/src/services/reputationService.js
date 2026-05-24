import axios from 'axios'
/**
 * Reputation Service
 * ==================
 * Delegates URL reputation checks to the Flask ML API endpoint
 * so API keys stay server-side and verdict logic is centralized.
 */

const API_TIMEOUT = 20_000

function requireUrl(rawUrl) {
  const value = String(rawUrl || '').trim()
  if (!value) {
    const error = new Error('URL is required')
    error.statusCode = 400
    throw error
  }
  return value
}

export async function checkUrlReputation(rawUrl) {
  const url = requireUrl(rawUrl)
  const apiUrl = process.env.URL_ML_URL

  if (!apiUrl) {
    const error = new Error('URL_ML_URL is not configured in backend environment')
    error.statusCode = 500
    throw error
  }

  try {
    const response = await axios.post(
      `${apiUrl}/check_reputation`,
      { url },
      { timeout: API_TIMEOUT },
    )

    return response.data
  } catch (error) {
    const statusCode = error.response?.status || (error.code === 'ECONNABORTED' ? 504 : 502)
    const message = error.response?.data?.message || error.response?.data?.error || 'Reputation service unavailable'
    const wrapped = new Error(message)
    wrapped.statusCode = statusCode
    throw wrapped
  }
}
