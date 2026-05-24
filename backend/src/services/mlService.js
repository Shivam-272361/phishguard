import axios from 'axios' 
import dotenv from 'dotenv'

dotenv.config();

export const predictMessageSpam= async(message)=>{
    try {
        const apiUrl = process.env.SMS_ML_URL;
        const response = await axios.post(`${apiUrl}/predict`, { message: message });
        return response.data
    } catch (error) {
        console.error(
            "ML API Error:",
            error.message
        );

        return {
            success: false,
            error: "ML prediction failed"
        };
    }

}

export const predictURLSpamBetter = async(url)=>{
    try {
        const apiUrl = process.env.URL_ML_URL;
        // Delegate to the reputation endpoint which includes both ML and VirusTotal
        const response = await axios.post(`${apiUrl}/predict_url`, { url : url});
        return response.data
    } catch (error) {
         console.error(
            "ML API Error:",
            error.message
        );

        return {
            success: false,
            error: "ML prediction failed"
        };
    }
}
export const predictURLSpam = async (url) => {
  try {
    const apiUrl = process.env.URL_ML_URL
    const response = await axios.post(
      `${apiUrl}/check_reputation`,
      { url },
      { timeout: 45000 },
    )
    return response.data
  } catch (error) {
    console.error('ML API Error (reputation):', error.message)
    return { success: false, error: 'ML prediction failed' }
  }
}

/** Fast path for extension: no HTML fetch, no VirusTotal, models preloaded in ML service */
export const predictURLSpamFast = async (url) => {
  const apiUrl = process.env.URL_ML_URL
  const response = await axios.post(
    `${apiUrl}/predict_url`,
    { url, fetch: false, fast: true },
    { timeout: 45000 },
  )
  return response.data
}