export function logHealth(success, details = {}) {
  console.log(
    '[PhishGuard Health]',
    JSON.stringify({
      ts: new Date().toISOString(),
      success,
      ...details,
    }),
  )
}
