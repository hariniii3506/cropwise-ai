// Hardcoded Flask backend server URL for CROPWISE AI
const BACKEND_URL = "http://192.168.1.14:5000";

document.addEventListener("DOMContentLoaded", () => {
  // Automatically and directly connect to the existing Flask backend
  setTimeout(() => {
    window.location.href = BACKEND_URL + "/android-splash";
  }, 1000);
});
