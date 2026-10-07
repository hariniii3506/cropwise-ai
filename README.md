# 🌱 CROPWISE AI — Smart Crop Recommendation System
### ஸ்மார்ட் பயிர் பரிந்துரை அமைப்பு
**Product:** Smart Crop Recommendation System for practical farm guidance
**Tagline:** Smart Farming. Better Crop Decisions. (சிறந்த விவசாயம் • சிறந்த பயிர் தேர்வு)

---

## 📌 Project Abstract
**CROPWISE AI** is a decision-support web application engineered for farmers and agricultural extension officers. It uses a **Decision Tree Classifier (CART Algorithm)** trained on agro-climatic datasets calibrated against Indian Council of Agricultural Research (ICAR) and Tamil Nadu Agricultural University (TNAU) benchmarks.

By analyzing five core manual parameters—**Soil Type, Soil pH Level (0.0–14.0), Ambient Temperature (°C), Relative Humidity (%), and Annual Rainfall (mm)**—the system accurately predicts the most optimal crop for the land, determines viable alternative crops, estimates cultivation budgets, displays 4-stage lifecycle timelines, and outputs printable advisory reports.

The application features full dual-language support in **English** and **தமிழ் (Tamil)**.

---

## 🏗️ System Architecture & Workflow

```text
Manual Farmer Inputs
(Soil Type + pH + Temp + Humidity + Rainfall)
                   │
                   ▼
       Preprocessing & Encoding
                   │
                   ▼
      Scikit-Learn Decision Tree
        (CART Gini Criterion)
                   │
                   ▼
    Recommended Primary Crop + Alternatives
                   │
        ┌──────────┴─────────────────────────┐
        │                                    │
        ▼                                    ▼
Decision-Support Modules             Print Advisory Report
- ⏱️ Crop Growth Duration            - Official PDF / Print Layout
- 🔄 Alternative Crops               - Verified Agronomic Stamp
- 📊 Multi-Crop Comparison           - Budget & Lifecycle Details
- 💰 Farm Budget Calculator
- 📅 Month-by-Month Calendar
- 💧 Water Requirement Guide
- 📝 Expense Ledger & Field Notes
```

---

## 🚀 Key Modules & Capabilities

1. **🌾 Crop Recommendation (ML Engine):**
   - Inputs: Soil Type (Dropdown), pH slider (0.0–14.0 with colored acidity/alkalinity scale), Temperature, Humidity, Rainfall.
   - Inference: Traverses trained Decision Tree branches and outputs primary crop with authentic suitability logic.

2. **🔄 Alternative Crops:**
   - Evaluates tree class probability distribution and soil texture compatibility to show 2–3 viable secondary crops.

3. **⏱️ Crop Growth Duration & Lifecycle:**
   - 4-phase interactive visual timeline: 🌱 Sowing ➔ 🌿 Vegetative ➔ 🌾 Flowering/Maturity ➔ ✂️ Harvesting with day count breakdowns.

4. **📊 Crop Comparison Matrix:**
   - Dynamic comparison of Duration, Water Need, Soil Tolerances, Temperature/Rainfall ranges, and Cost per Acre.

5. **💰 Farm Budget Calculator:**
   - Pre-populates baseline costs (Seeds, Labour, Fertilizer, Irrigation, Machinery, Other) scaled to farmer's land area with instant total cost calculation.

6. **📅 Crop Calendar:**
   - Month-by-month agricultural activities and seasonal windows (Kharif, Rabi, Zaid, Kuruvai, Samba, Navarai).

7. **💧 Water Requirement & Irrigation Advisory:**
   - Water volume rating (Low/Moderate/High), seasonal mm ranges, irrigation methods (Drip, Sprinkler, AWD), and water-saving tips.

8. **📜 Recommendation History:**
   - Complete chronological logs for the logged-in farmer with view, print, and delete capabilities.

9. **📝 Farm Expenses & Notes:**
   - Financial ledger for farm inputs and categorized field notebooks.

10. **🖨️ Official Print Report:**
    - Clean `@media print` formatted advisory sheet for viva demonstration and farmer records.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.14, Flask 3.1, Werkzeug
- **Machine Learning:** Scikit-Learn 1.9 (`DecisionTreeClassifier`), Pandas, NumPy, Joblib
- **Database:** SQLite with standard relational schema (Users, Recommendations, Expenses, Notes)
- **Frontend:** Vanilla HTML5, CSS3 (Custom Agricultural Design System), JavaScript (ES6)
- **Language Support:** Bilingual Engine (English & தமிழ்)

---

## 📦 Setup & Execution Guide

### 1. Prerequisites
Ensure Python 3.10+ is installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate Dataset & Train Decision Tree Model
```bash
python generate_dataset.py
python train_model.py
```
*Output: `models/crop_decision_tree.pkl` and `models/model_metadata.json`*

### 4. Initialize Database
```bash
python database/db.py
```

### 5. Launch the Web Application
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

To test SMTP reachability, TLS, and authentication without sending an email:

```bash
python app.py --check-smtp
```

This command reports the exception type and traceback for connection or authentication failures, while never printing the SMTP password or sending a test message.

### 6. Configure real registration OTP email

The registration flow sends OTPs through the existing Flask-Mail SMTP integration. Create a `.env` file in the project root (`d:\farmer\.env`) or set these variables in the shell before starting Flask:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-sender@gmail.com
SMTP_PASSWORD=your-16-character-gmail-app-password
SENDER_EMAIL=your-sender@gmail.com
SECRET_KEY=replace-with-a-long-random-secret
```

For Gmail, enable 2-Step Verification and create a Gmail App Password. Use that App Password as `SMTP_PASSWORD`; do not use your normal Gmail account password. Never commit `.env` or expose these values in frontend files.

Install the mail dependency and run the existing application with:

```bash
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000/register`, complete the form with your real email address, select **Send OTP**, and check the inbox and spam folder. The OTP expires after 1 minute, and the account can be completed only after the received OTP is verified. If SMTP credentials are missing or rejected, the page reports an email service configuration problem instead of blaming the recipient address.

---

## 🎓 College Viva & Examination Q&A

### Q1: Why did you choose Decision Tree Classifier over other ML algorithms?
**Answer:** In agriculture, decision transparency (white-box explainability) is critical. Unlike black-box models (e.g. Deep Neural Networks), Decision Trees evaluate human-readable if-then rule splits on physical boundaries (e.g., *Rainfall > 1200mm AND Soil = Clayey*). This allows agronomists and farmers to inspect and verify the exact rationale behind every recommendation.

### Q2: What split criterion is used in your Decision Tree?
**Answer:** We used **Gini Impurity** ($Gini = 1 - \sum p_i^2$) via the CART algorithm. Gini measures the probability of misclassifying a randomly chosen element from the set if it were randomly labeled according to the distribution of labels in the subset.

### Q3: Why does your system use manual input instead of live IoT sensors?
**Answer:** In real-world Indian agriculture, small and marginal farmers cannot afford expensive telemetry sensors or IoT field hardware. Manual soil testing lab reports (Soil Health Cards) provide accurate Soil Type, pH, and local weather averages, making manual input accessible and reliable.

### Q4: How are alternative crops calculated?
**Answer:** When the Decision Tree classifies an input vector, we extract the leaf class probability distribution (`predict_proba`). Crops with non-zero probability or matching agro-ecological soil zones are ranked as secondary alternatives.

---

## Product Notes
Built to support farmers and agricultural extension teams with practical crop guidance.
**CROPWISE AI • Smart Farming. Better Crop Decisions.**
