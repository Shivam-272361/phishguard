import dotenv from 'dotenv'
import app from './app.js'
import { warmMlConnection } from './services/urlScanPipeline.js'

dotenv.config()

const PORT = process.env.PORT || 5000

app.listen(PORT, () => {
  console.log(`PhishGuard backend running on http://localhost:${PORT}`)
  warmMlConnection()
})
