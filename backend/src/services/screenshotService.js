import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Ensure previews directory exists
const PREVIEWS_DIR = path.join(__dirname, '../../public/previews');
if (!fs.existsSync(PREVIEWS_DIR)) {
    fs.mkdirSync(PREVIEWS_DIR, { recursive: true });
}

export const captureScreenshot = async (url) => {
    let browser;
    try {
        // Basic URL validation
        const parsedUrl = new URL(url);
        if (!['http:', 'https:'].includes(parsedUrl.protocol)) {
            throw new Error('Invalid protocol. Only http and https are supported.');
        }

        browser = await puppeteer.launch({
            headless: 'new',
            args: [
                '--no-sandbox', 
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security'
            ]
        });

        const page = await browser.newPage();
        
        // Use a realistic user agent to avoid being blocked
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36');
        
        // Set viewport to target thumbnail aspect ratio
        await page.setViewport({ width: 1280, height: 720 });
        
        // Navigate with timeout and better wait condition
        try {
            await page.goto(url, {
                waitUntil: 'domcontentloaded', // Faster than networkidle2
                timeout: 30000 
            });
            
            // Wait a bit more for dynamic content
            await new Promise(r => setTimeout(r, 2000));
        } catch (gotoError) {
            console.warn(`Navigation warning for ${url}:`, gotoError.message);
            // Continue anyway to try and capture what loaded (if anything)
        }

        // 1. Phishing Indicators: Check for login forms and suspicious keywords
        const analysis = await page.evaluate(() => {
            const indicators = {
                hasPassword: !!document.querySelector('input[type="password"]'),
                hasLoginForm: false,
                suspiciousKeywords: [],
                pageTitle: document.title,
                brandImpersonation: null
            };

            // Detect forms that look like login forms
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {
                const text = form.innerText.toLowerCase();
                if (text.includes('login') || text.includes('sign in') || text.includes('password')) {
                    indicators.hasLoginForm = true;
                }
            });

            // suspicious brand keywords
            const brands = ['paypal', 'facebook', 'instagram', 'google', 'amazon', 'microsoft', 'netflix', 'apple', 'banking', 'secure-check'];
            const pageText = document.body.innerText.toLowerCase();
            brands.forEach(brand => {
                if (pageText.includes(brand)) {
                    indicators.suspiciousKeywords.push(brand);
                }
            });

            // Simple title-based brand match
            const title = document.title.toLowerCase();
            const matchedBrand = brands.find(brand => title.includes(brand));
            if (matchedBrand) {
                indicators.brandImpersonation = matchedBrand.charAt(0).toUpperCase() + matchedBrand.slice(1);
            }

            return indicators;
        });

        // Generate unique filename
        const filename = `preview_${Date.now()}_${Math.random().toString(36).substring(7)}.jpg`;
        const filePath = path.join(PREVIEWS_DIR, filename);

        // Take a screenshot (optimized as jpeg)
        await page.screenshot({
            path: filePath,
            type: 'jpeg',
            quality: 70
        });

        return {
            success: true,
            screenshotUrl: `/previews/${filename}`,
            analysis
        };

    } catch (error) {
        console.error('Screenshot capture failed:', error.message);
        return {
            success: false,
            error: error.message
        };
    } finally {
        if (browser) await browser.close();
    }
};
