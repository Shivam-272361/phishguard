import { Router } from 'express'


import {
  scanEmailController,
  scanSmsController,
  scanUrlController,
  scanUrlResultController,
  capturePreviewController,
  predictEmailController,
} from '../controllers/scanController.js'
import { checkReputationController } from '../controllers/reputationController.js'

const router = Router()

router.post('/scan-sms', scanSmsController)
router.post('/scan-email', scanEmailController)
router.post('/scan-url', scanUrlController)
router.get('/api/scan/result/:scanId', scanUrlResultController)
router.post('/predict-email', predictEmailController)
router.post('/capture-preview', capturePreviewController)

// URL Reputation Checker — combines ML detection with VirusTotal threat intelligence
router.post('/check-reputation', checkReputationController)
router.post('/check_reputation', checkReputationController)
router.post('/check_reputation', checkReputationController)

export default router
