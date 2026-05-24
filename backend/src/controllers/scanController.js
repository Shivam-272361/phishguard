import {
  buildSmsScanResult,
} from '../services/phishingService.js'
import {
  predictMessageSpam,
  predictURLSpam,
  predictURLSpamBetter,
} from '../services/mlService.js'
import { checkUrlReputation } from '../services/reputationService.js'
import { extractUrls } from '../utils/extractUrls.js'
import { captureScreenshot } from '../services/screenshotService.js'
import {
  resolveUrlScan,
  startAsyncUrlScan,
  getScanJob,
  logScan,
} from '../services/urlScanPipeline.js'

function requireText(value, fieldName) {
  if (typeof value !== 'string' || !value.trim()) {
    const error = new Error(`${fieldName} is required`)
    error.statusCode = 400
    throw error
  }

  return value.trim()
}

export const predictEmailController = async (req, res, next) => {
  try {
    const email = requireText(req.body.email, 'Email address')
    const result = await scanEmailId(email)
    
    return res.status(200).json(result)
  } catch (error) {
    next(error)
  }
}

export const scanSmsController = async (req, res, next) => {
  try {
    const message = requireText(req.body.message || req.body.text, 'Message')

    const extractedUrl = extractUrls(message)
    let urlAnalysisData = null
    if (extractedUrl.length > 0) {
      urlAnalysisData = await predictURLSpamBetter(extractedUrl[0])
    }

    const textAnalysis = await predictMessageSpam(message)
    const result = buildSmsScanResult(message, {
      extractedUrls: extractedUrl,
      textAnalysis,
      urlAnalysis: urlAnalysisData,
    })
    console.log(result);
    return res.status(200).json(result)
  } catch (error) {
    next(error)
  }
}

export async function scanEmailController(req, res, next) {
  try {
    const content = requireText(
      req.body.content || req.body.emailContent || req.body.emailAddress,
      'Email content or address',
    )
    const mode = req.body.mode === 'address' ? 'address' : 'content'

    let urlAnalysis = null
    let textAnalysis = null
    let urlAnalysisData = null
    let extractedUrl = []

    let result = null
    if (mode === 'address') {
      const domain = content.split('@')[1]?.trim()
      const domainUrl = domain ? `https://${domain}` : null
      urlAnalysis = domainUrl ? await predictURLSpamBetter(domainUrl) : null
      console.log(urlAnalysis);
    } else {
      extractedUrl = extractUrls(content)


      if (extractedUrl.length > 0) {
        urlAnalysisData = await predictURLSpamBetter(extractedUrl[0])
      }

      textAnalysis = await predictMessageSpam(content)
      console.log("Text Analysis:", textAnalysis);
      result = buildSmsScanResult(content, {
        extractedUrls: extractedUrl,
        textAnalysis,
        urlAnalysis: urlAnalysisData,
        type: 'email',
      })
    }


    return res.status(200).json({
      success: true,
      mode:mode,
      content,
      ...(result || {}),
      result: (result) ? result : null,
      urlAnalysis: (urlAnalysis) ? urlAnalysis : null,
    })
  } catch (error) {
    next(error)
  }
}


export const scanUrlController = async (req, res, next) => {
  try {
    const url = requireText(req.body.url || req.body.websiteUrl, 'URL')
    const useAsync = req.query.async === '1' || req.body.async === true

    if (useAsync) {
      const started = startAsyncUrlScan(url)
      if (started.immediate) {
        return res.status(200).json({
          success: true,
          status: 'complete',
          url,
          result: started.result,
          durationMs: 0,
        })
      }
      return res.status(202).json({
        success: true,
        status: 'scanning',
        scanId: started.scanId,
        url,
      })
    }

    const outcome = await resolveUrlScan(url)
    return res.status(200).json({
      success: true,
      message: 'Url analysis completed',
      status: 'complete',
      url,
      result: outcome.result,
    })
  } catch (error) {
    logScan('scan_controller_error', { error: error.message })
    next(error)
  }
}

export const scanUrlResultController = (req, res) => {
  const job = getScanJob(req.params.scanId)
  if (!job) {
    return res.status(404).json({ success: false, error: 'Scan not found' })
  }
  if (job.status === 'scanning') {
    return res.status(202).json({
      success: true,
      status: 'scanning',
      scanId: req.params.scanId,
    })
  }
  if (job.status === 'error') {
    return res.status(500).json({
      success: false,
      status: 'error',
      error: job.error,
    })
  }
  return res.status(200).json({
    success: true,
    status: 'complete',
    scanId: req.params.scanId,
    result: job.result,
    durationMs: job.durationMs,
  })
}

export const capturePreviewController = async (req, res, next) => {
  try {
    const url = requireText(req.body.url, 'URL')
    const screenshotData = await captureScreenshot(url)
    res.status(200).json(screenshotData)
  } catch (error) {
    next(error)
  }
}
