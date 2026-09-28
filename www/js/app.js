/**
 * ===============================================================================
 * CROPWISE AI - ANDROID CLIENT CONFIGURATION & INITIALIZATION
 * ===============================================================================
 * 
 * BACKEND URL CONFIGURATION:
 * When your Flask backend is deployed online (e.g. Render, Railway, Vercel, VPS),
 * replace the placeholder below with your live production HTTPS URL.
 * 
 * Example:
 * const PRODUCTION_BACKEND_URL = "https://cropwise-ai.onrender.com";
 * ===============================================================================
 */

const PRODUCTION_BACKEND_URL = "https://YOUR-LIVE-FLASK-BACKEND-URL";

document.addEventListener("DOMContentLoaded", () => {
  const cleanUrl = (PRODUCTION_BACKEND_URL || "").trim().replace(/\/+$/, "");

  // If a valid production URL has been configured, automatically navigate the Android WebView
  if (cleanUrl && !cleanUrl.includes("YOUR-LIVE-FLASK-BACKEND-URL")) {
    setTimeout(() => {
      window.location.href = cleanUrl + "/android-splash";
    }, 800);
  } else {
    // Graceful notice shown if APK is built without changing the placeholder URL
    console.warn("[CROPWISE AI] Please configure PRODUCTION_BACKEND_URL in www/js/app.js with your live server address.");
    const subtitle = document.querySelector(".subtitle");
    if (subtitle) {
      subtitle.textContent = "Connecting to Live Server...";
    }
  }
});
