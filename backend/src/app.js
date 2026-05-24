import cors from 'cors'
import express from 'express'
import path from 'path'
import { fileURLToPath } from 'url'
import scanRoutes from './routes/scanRoutes.js'
import { errorHandler, notFoundHandler } from './middleware/errorHandler.js'
import { logHealth } from './middleware/scanLogger.js'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const app = express()

app.use(cors())
app.use(express.json({ limit: '1mb' }))
app.use('/previews', express.static(path.join(__dirname, '../public/previews')))

app.get('/', (req, res) => {
  res.json({
    success: true,
    message: 'PhishGuard API is running',
    endpoints: ['/scan-sms', '/scan-email', '/scan-url', '/check-reputation', '/check_reputation'],
  })
})

app.get('/health', (req, res) => {
  logHealth(true, { path: '/health' })
  res.json({ success: true, status: 'ok' })
})

app.get('/api/health', (req, res) => {
  logHealth(true, { path: '/api/health' })
  res.json({ status: 'ok' })
})

app.use('/', scanRoutes)
app.use(notFoundHandler)
app.use(errorHandler)

export default app
