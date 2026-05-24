/**
 * Reputation Controller
 * =====================
 * Handles URL reputation check requests by delegating to Flask
 * `/check_reputation` through the backend service layer.
 */

import { checkUrlReputation } from '../services/reputationService.js'
import { captureScreenshot } from '../services/screenshotService.js'

/**
 * Validate that the request body contains a URL field.
 */
function requireUrl(value) {
  if (typeof value !== 'string' || !value.trim()) {
    const error = new Error('URL is required')
    error.statusCode = 400
    throw error
  }
  return value.trim()
}

/**
 * Controller for the reputation endpoint aliases.
 */
export const checkReputationController = async (req, res, next) => {
  try {
    const url = requireUrl(req.body.url || req.body.websiteUrl)
    
    // Run Reputation report and Screenshot in parallel
    const [reputationResult, screenshotData] = await Promise.all([
      checkUrlReputation(url),
      captureScreenshot(url)
    ]);

    // Attach screenshot data to the response
    const combinedResult = {
      ...reputationResult,
      preview: screenshotData
    };

    return res.status(200).json(combinedResult)
  } catch (error) {
    next(error)
  }
}
