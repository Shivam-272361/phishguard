# Chrome Extension Production Guide

## 1. Production Configuration
The extension is now configured for production deployment:
- **API Target:** Switched from `localhost` to `https://phishguard-api.onrender.com/api` (HTTPS enforced).
- **Persistence:** Uses `chrome.storage.local` to ensure JWT tokens survive browser restarts.
- **Performance:** Implemented **Domain Throttling** in `background.js` to prevent duplicate API calls for the same site within 3 seconds.

## 2. Security & Optimization
- **Secure JWT:** Token is only sent over HTTPS production endpoints.
- **Throttling:** Reduces backend load and improves browser performance.
- **Thresholding:** Only triggers warnings for threats with a score ≥ 75% to reduce false positives.

## 3. Deployment Steps

### A. Testing Production Build Locally
1. Open Chrome and go to `chrome://extensions/`.
2. Enable **Developer mode** (top right).
3. Click **Load unpacked**.
4. Select the `extension` folder.
5. Verify the extension ID and ensure "Service Worker" is running without errors.

### B. Publishing to Chrome Web Store
1. Zip the contents of the `extension` folder:
   - `manifest.json`
   - `background.js`
   - `content.js`
   - `popup.html` / `popup.js`
   - `icons/` folder
2. Create a developer account at the [Chrome Web Store Dashboard](https://chrome.google.com/webstore/devconsole/).
3. Upload the ZIP file.
4. Fill in descriptions, privacy policy (mentioning URL scanning), and screenshots.
5. Submit for review.

## 4. Maintenance
- To switch back to development, update `CONFIG.API_BASE` in `background.js` and `host_permissions` in `manifest.json`.
