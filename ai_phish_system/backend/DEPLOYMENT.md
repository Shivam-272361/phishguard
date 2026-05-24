# --- DEPLOYMENT GUIDE: PhishGuard Backend ---

## 1. Production Folder Structure
After preparation, your backend folder [ai_phish_system/backend](ai_phish_system/backend) is production-ready with:
- `Dockerfile`: Containerizes the Flask app for any cloud provider.
- `requirements.txt`: Locked dependencies for production stability.
- `app.py`: Pre-configured for Production (`Talisman`, `Limiter`, `CORS`).

## 2. Environment Variables Setup
Create these in your Cloud Provider's (Render/Azure/Railway) Dashboard:

| Key | Value (Example) | Description |
| :--- | :--- | :--- |
| `FLASK_ENV` | `production` | Enables HTTPS and secure headers. |
| `SECRET_KEY` | `your-random-long-secret-key` | Used for session signing. |
| `JWT_SECRET_KEY` | `another-random-secret-key` | Used for JWT encryption. |
| `MONGO_URI` | `mongodb+srv://user:pass@cluster.mongodb.net/phishguard` | Production MongoDB Atlas URI. |
| `CORS_ORIGIN_FRONTEND` | `https://your-frontend-domain.com` | Your deployed Vite app URL. |
| `CORS_ORIGIN_EXTENSION` | `chrome-extension://your-extension-id`| Your Chrome Extension ID. |

## 3. Deployment Steps (Recommended: Render / Azure App Service)

### Option A: Render (Easiest)
1. Connect your GitHub repository to [Render](https://render.com).
2. Create a new **Web Service**.
3. Select the `ai_phish_system/backend` folder as the root.
4. Render will automatically detect the `Dockerfile`.
5. Add the environment variables listed above.
6. Deploy.

### Option B: Azure App Service
1. Initialize Azure CLI and login.
2. Run: `az webapp up --name phishguard-api --resource-group phish-rg --plan phish-plan --sku B1`.
3. Configure "Application Settings" in the Azure Portal with the Env Vars above.

## 4. Connectivity Check
Your endpoints will now be available at: `https://your-app-name.onrender.com/api`

Update your Frontend and Extension to point to this new production URL.
