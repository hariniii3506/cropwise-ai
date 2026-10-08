// =============================================================================
// CROPWISE AI - Client Application Logic (main.js)
// =============================================================================
// Manages dynamic frontend user interactions across the application:
// - Responsive mobile navigation drawer toggle and active page highlighting.
// - Real-time soil parameter sliders and synced numeric inputs (N, P, K, pH, rainfall).
// - Interactive farm budget calculator computing total and per-acre estimates.
// - Dynamic water volume converter between Acres and Cents.
// - PWA service worker registration and push notification lifecycle hooks.
// =============================================================================

/**
 * CROPWISE AI - Client Application Logic
 * Interactive handlers, reactive calculations, and DOM events.
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Mobile Menu Toggle
  const mobileToggle = document.getElementById("mobileToggle");
  const navMenu = document.getElementById("navMenu");
  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener("click", () => {
      navMenu.classList.toggle("open");
    });
  }

  // Highlight the navigation link for the current route.
  const currentPath = window.location.pathname;
  navMenu?.querySelectorAll(".nav-item a").forEach((link) => {
    const linkPath = new URL(link.href, window.location.origin).pathname;
    if (linkPath === currentPath) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
  });

  // 2. pH Slider Interactive Visual Feedback
  const phSlider = document.getElementById("phRange");
  const phDisplay = document.getElementById("phValDisplay");
  const phStatus = document.getElementById("phStatusText");

  function updatePhUI(val) {
    const num = parseFloat(val);
    if (phDisplay) phDisplay.textContent = num.toFixed(1);
    
    if (phStatus) {
      const currentLang = localStorage.getItem("cropwise_lang") || "en";
      if (num < 5.5) {
        phStatus.textContent = currentLang === "ta" ? "அதிக அமிலத்தன்மை (Strongly Acidic)" : "Strongly Acidic";
        phStatus.style.color = "#D90429";
      } else if (num < 6.5) {
        phStatus.textContent = currentLang === "ta" ? "மிதமான அமிலம் (Slightly Acidic)" : "Slightly Acidic";
        phStatus.style.color = "#B08968";
      } else if (num <= 7.5) {
        phStatus.textContent = currentLang === "ta" ? "நடுநிலை / உகந்தது (Neutral / Ideal)" : "Neutral / Optimal (Ideal)";
        phStatus.style.color = "#2D6A4F";
      } else if (num <= 8.5) {
        phStatus.textContent = currentLang === "ta" ? "மிதமான காரத்தன்மை (Mildly Alkaline)" : "Mildly Alkaline";
        phStatus.style.color = "#40916C";
      } else {
        phStatus.textContent = currentLang === "ta" ? "அதிக காரத்தன்மை (Strongly Alkaline)" : "Strongly Alkaline";
        phStatus.style.color = "#8338EC";
      }
    }
  }

  if (phSlider) {
    phSlider.addEventListener("input", (e) => {
      updatePhUI(e.target.value);
    });
    updatePhUI(phSlider.value);
  }

  // 3. Live Reactive Farm Budget Calculator
  const budgetForm = document.getElementById("budgetCalcForm");
  const totalCostDisplay = document.getElementById("calcTotalCost");
  const costPerAcreDisplay = document.getElementById("calcCostPerAcre");

  function recalculateBudget() {
    if (!budgetForm) return;
    
    const landArea = parseFloat(document.getElementById("calcLandArea")?.value) || 1.0;
    const seed = parseFloat(document.getElementById("calcSeed")?.value) || 0.0;
    const labour = parseFloat(document.getElementById("calcLabour")?.value) || 0.0;
    const fert = parseFloat(document.getElementById("calcFert")?.value) || 0.0;
    const irrig = parseFloat(document.getElementById("calcIrrig")?.value) || 0.0;
    const mach = parseFloat(document.getElementById("calcMach")?.value) || 0.0;
    const other = parseFloat(document.getElementById("calcOther")?.value) || 0.0;

    const costPerAcre = seed + labour + fert + irrig + mach + other;
    const totalCost = costPerAcre * landArea;

    if (totalCostDisplay) {
      totalCostDisplay.textContent = "₹" + totalCost.toLocaleString("en-IN", { maximumFractionDigits: 0 });
    }
    if (costPerAcreDisplay) {
      costPerAcreDisplay.textContent = "₹" + costPerAcre.toLocaleString("en-IN", { maximumFractionDigits: 0 }) + " / acre";
    }
  }

  if (budgetForm) {
    budgetForm.querySelectorAll("input").forEach(input => {
      input.addEventListener("input", recalculateBudget);
    });
    recalculateBudget();
  }

  // 4. Dynamic Crop Calendar Selector
  const calCropSelect = document.getElementById("calCropSelect");
  if (calCropSelect) {
    calCropSelect.addEventListener("change", (e) => {
      const selectedCrop = e.target.value;
      document.querySelectorAll(".crop-calendar-view").forEach(view => {
        if (view.getAttribute("data-crop") === selectedCrop) {
          view.style.display = "block";
        } else {
          view.style.display = "none";
        }
      });
    });
  }

  // 5. Dynamic Crop Comparator Selector
  const compCheckboxes = document.querySelectorAll(".comp-crop-toggle");
  if (compCheckboxes.length > 0) {
    compCheckboxes.forEach(cb => {
      cb.addEventListener("change", () => {
        const targetCrop = cb.getAttribute("data-crop");
        const rows = document.querySelectorAll(`.comp-row-${targetCrop}`);
        rows.forEach(r => {
          r.style.display = cb.checked ? "table-row" : "none";
        });
      });
    });
  }

  // 6. Print Report Trigger
  const printBtn = document.getElementById("triggerPrintBtn");
  if (printBtn) {
    printBtn.addEventListener("click", (e) => {
      e.preventDefault();
      window.print();
    });
  }

  // 7. Water Page Land Area Unit Selector & Water Requirement Display (in mm)
  const unitAcreBtn = document.getElementById("unitAcreBtn");
  const unitCentBtn = document.getElementById("unitCentBtn");
  const waterLandAreaInput = document.getElementById("waterLandAreaInput");
  const waterCalcPrompt = document.getElementById("waterCalcPrompt");
  const waterCalcOutput = document.getElementById("waterCalcOutput");
  const waterCalcVolumeText = document.getElementById("waterCalcVolumeText");
  const waterNeedCard = document.getElementById("waterNeedCard");
  let selectedWaterUnit = "Acre";

  function getBaseWaterRange() {
    const rangeText = waterNeedCard ? (waterNeedCard.getAttribute("data-water-range") || "") : "";
    const values = rangeText.match(/[\d.]+/g);
    if (!values || values.length < 2) return [1100, 1500];
    return [Number(values[0]), Number(values[1])];
  }

  function recalculateWater() {
    if (!waterLandAreaInput || !waterCalcPrompt || !waterCalcOutput) return;

    const rawVal = waterLandAreaInput.value.trim();
    const val = parseFloat(rawVal);

    if (!rawVal || isNaN(val) || val <= 0) {
      waterCalcPrompt.style.display = "flex";
      waterCalcOutput.style.display = "none";
      return;
    }

    waterCalcPrompt.style.display = "none";
    waterCalcOutput.style.display = "block";

    if (waterCalcVolumeText) {
      const areaInAcres = selectedWaterUnit === "Cent" ? val * 0.01 : val;
      const [baseMin, baseMax] = getBaseWaterRange();
      const calculatedMin = baseMin * areaInAcres;
      const calculatedMax = baseMax * areaInAcres;
      const formatValue = (value) => Number.isInteger(value) ? String(value) : value.toFixed(2);
      waterCalcVolumeText.textContent = `${formatValue(calculatedMin)} - ${formatValue(calculatedMax)} mm`;
    }
  }

  if (unitAcreBtn && unitCentBtn) {
    unitAcreBtn.addEventListener("click", () => {
      selectedWaterUnit = "Acre";
      unitAcreBtn.classList.add("active");
      unitCentBtn.classList.remove("active");
      recalculateWater();
    });

    unitCentBtn.addEventListener("click", () => {
      selectedWaterUnit = "Cent";
      unitCentBtn.classList.add("active");
      unitAcreBtn.classList.remove("active");
      recalculateWater();
    });
  }

  if (waterLandAreaInput) {
    waterLandAreaInput.value = "";
    waterLandAreaInput.addEventListener("input", recalculateWater);
    recalculateWater();
  }

  // Listen for language change to update dynamic strings
  window.addEventListener("languageChanged", (e) => {
    if (phSlider) updatePhUI(phSlider.value);
    recalculateWater();
  });
});
