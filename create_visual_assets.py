"""
create_visual_assets.py
Generates clean, elegant, modern agricultural vector illustrations (SVG)
for CROPWISE AI branding, modules, and crop representations.
"""

import os

def generate_assets():
    os.makedirs("static/images/crops", exist_ok=True)
    os.makedirs("static/images/modules", exist_ok=True)
    
    # 1. Main Brand Logo
    logo_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 60" width="240" height="60">
      <defs>
        <linearGradient id="logoLeafGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#52B788"/>
          <stop offset="100%" stop-color="#1B4332"/>
        </linearGradient>
        <linearGradient id="logoSproutGrad" x1="0%" y1="100%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#74C69D"/>
          <stop offset="100%" stop-color="#2D6A4F"/>
        </linearGradient>
      </defs>
      <!-- Farm / Leaf Icon Badge -->
      <rect x="6" y="8" width="44" height="44" rx="12" fill="#E8F5E9"/>
      <path d="M28 42 C 28 32, 38 22, 42 16 C 36 24, 30 28, 28 42 Z" fill="url(#logoLeafGrad)"/>
      <path d="M28 42 C 28 30, 18 20, 14 16 C 20 24, 26 28, 28 42 Z" fill="url(#logoSproutGrad)"/>
      <circle cx="28" cy="42" r="3" fill="#DDB892"/>
      <path d="M12 46 Q 28 42 44 46" stroke="#2D6A4F" stroke-width="2.5" stroke-linecap="round" fill="none"/>
      <!-- Typography -->
      <text x="58" y="32" font-family="'Outfit', 'Inter', -apple-system, sans-serif" font-size="20" font-weight="800" fill="#1B4332" letter-spacing="1">CROPWISE<tspan fill="#52B788"> AI</tspan></text>
      <text x="58" y="45" font-family="'Inter', sans-serif" font-size="9" font-weight="600" fill="#606C38" letter-spacing="0.5">SMART CROP RECOMMENDATION</text>
    </svg>"""
    with open("static/images/logo.svg", "w", encoding="utf-8") as f:
        f.write(logo_svg)

    # 2. Hero Farm Visual
    hero_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 420" width="100%" height="100%">
      <defs>
        <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#E8F4EC"/>
          <stop offset="60%" stop-color="#F2F8F4"/>
          <stop offset="100%" stop-color="#FAFBF8"/>
        </linearGradient>
        <linearGradient id="sunGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#FFE3A8"/>
          <stop offset="100%" stop-color="#F9C74F"/>
        </linearGradient>
        <linearGradient id="hillBack" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#A7D7C5"/>
          <stop offset="100%" stop-color="#74C69D"/>
        </linearGradient>
        <linearGradient id="fieldGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#52B788"/>
          <stop offset="100%" stop-color="#2D6A4F"/>
        </linearGradient>
        <linearGradient id="fieldGrad2" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#40916C"/>
          <stop offset="100%" stop-color="#1B4332"/>
        </linearGradient>
      </defs>
      <rect width="600" height="420" rx="20" fill="url(#skyGrad)"/>
      <!-- Soft Sun -->
      <circle cx="480" cy="110" r="55" fill="url(#sunGrad)" opacity="0.6"/>
      <circle cx="480" cy="110" r="75" fill="#FFE3A8" opacity="0.25"/>
      <!-- Distant Hills -->
      <path d="M0 240 Q 150 170 300 220 T 600 200 L 600 420 L 0 420 Z" fill="url(#hillBack)" opacity="0.5"/>
      <path d="M0 260 Q 200 200 420 250 T 600 230 L 600 420 L 0 420 Z" fill="#74C69D" opacity="0.6"/>
      <!-- Farm Terrace Fields -->
      <path d="M-20 310 Q 180 250 380 290 T 620 270 L 620 420 L -20 420 Z" fill="url(#fieldGrad1)"/>
      <path d="M-20 350 Q 220 310 440 340 T 620 330 L 620 420 L -20 420 Z" fill="url(#fieldGrad2)"/>
      <!-- Field Furrow Lines -->
      <path d="M 60 420 Q 220 330 380 290" stroke="#74C69D" stroke-width="2.5" fill="none" opacity="0.5"/>
      <path d="M 160 420 Q 280 340 440 300" stroke="#74C69D" stroke-width="2.5" fill="none" opacity="0.5"/>
      <path d="M 280 420 Q 360 350 500 310" stroke="#74C69D" stroke-width="2.5" fill="none" opacity="0.5"/>
      <!-- Healthy Crop Plants Silhouettes -->
      <g fill="#D8F3DC" opacity="0.85">
        <path d="M 100 360 Q 105 330 115 320 Q 110 335 105 360 Q 95 335 90 325 Q 98 335 100 360 Z"/>
        <path d="M 140 350 Q 145 320 155 310 Q 150 325 145 350 Q 135 325 130 315 Q 138 325 140 350 Z"/>
        <path d="M 220 340 Q 225 315 235 305 Q 230 320 225 340 Q 215 320 210 310 Q 218 320 220 340 Z"/>
        <path d="M 320 330 Q 325 308 335 298 Q 330 312 325 330 Q 315 312 310 304 Q 318 312 320 330 Z"/>
        <path d="M 400 325 Q 405 305 415 295 Q 410 310 405 325 Q 395 308 390 300 Q 398 310 400 325 Z"/>
      </g>
      <!-- Farmer Character in Field -->
      <g transform="translate(180, 160)">
        <!-- Straw Hat -->
        <ellipse cx="60" cy="50" rx="36" ry="12" fill="#DDB892"/>
        <path d="M 40 48 Q 60 28 80 48 Z" fill="#B08968"/>
        <!-- Head -->
        <circle cx="60" cy="56" r="13" fill="#E0A96D"/>
        <!-- Shirt -->
        <path d="M 40 68 Q 60 62 80 68 L 84 110 L 36 110 Z" fill="#2D6A4F"/>
        <path d="M 48 68 L 60 85 L 72 68" stroke="#E0A96D" stroke-width="3" fill="none"/>
        <!-- Clipboard / Smart Tablet with Crop Icon -->
        <rect x="75" y="80" width="28" height="36" rx="4" fill="#FFFFFF" stroke="#52B788" stroke-width="2"/>
        <path d="M89 90 C 89 85, 95 82, 98 80 C 94 85, 91 88, 89 94 Z" fill="#2D6A4F"/>
        <rect x="80" y="100" width="18" height="3" rx="1.5" fill="#52B788"/>
        <rect x="80" y="106" width="12" height="3" rx="1.5" fill="#74C69D"/>
      </g>
      <!-- Decision Tree AI nodes float overlay -->
      <g transform="translate(390, 80)" opacity="0.9">
        <rect x="0" y="0" width="170" height="90" rx="12" fill="#FFFFFF" filter="drop-shadow(0 8px 16px rgba(0,0,0,0.06))"/>
        <circle cx="28" cy="28" r="14" fill="#E8F5E9"/>
        <text x="28" y="33" text-anchor="middle" font-size="14">🌱</text>
        <text x="50" y="24" font-family="'Inter', sans-serif" font-size="11" font-weight="700" fill="#1B4332">Decision Tree ML</text>
        <text x="50" y="38" font-family="'Inter', sans-serif" font-size="9" fill="#52B788" font-weight="600">89.2% Accuracy</text>
        <!-- Mini Tree Structure -->
        <line x1="28" y1="56" x2="60" y2="72" stroke="#B08968" stroke-width="2"/>
        <line x1="28" y1="56" x2="110" y2="72" stroke="#B08968" stroke-width="2"/>
        <circle cx="28" cy="56" r="6" fill="#52B788"/>
        <circle cx="60" cy="72" r="6" fill="#2D6A4F"/>
        <circle cx="110" cy="72" r="6" fill="#74C69D"/>
        <text x="125" y="75" font-family="'Inter', sans-serif" font-size="9" font-weight="700" fill="#1B4332">Optimal Crop</text>
      </g>
    </svg>"""
    with open("static/images/hero-farm.svg", "w", encoding="utf-8") as f:
        f.write(hero_svg)

    # 3. Farmer Login Visual
    login_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 450 500" width="100%" height="100%">
      <rect width="450" height="500" rx="20" fill="#F4F8F5"/>
      <circle cx="225" cy="180" r="130" fill="#E8F5E9"/>
      <!-- Sun -->
      <circle cx="330" cy="100" r="35" fill="#FFE3A8"/>
      <!-- Hills & Soil -->
      <path d="M 40 380 Q 140 280 240 340 T 410 320 L 410 460 L 40 460 Z" fill="#52B788" opacity="0.7"/>
      <path d="M 20 390 Q 180 340 320 370 T 430 360 L 430 480 L 20 480 Z" fill="#2D6A4F"/>
      <!-- Farmer Character Standing Proudly -->
      <g transform="translate(165, 120)">
        <!-- Hat -->
        <ellipse cx="60" cy="40" rx="42" ry="14" fill="#DDB892"/>
        <path d="M 35 38 Q 60 15 85 38 Z" fill="#B08968"/>
        <!-- Face & Smile -->
        <circle cx="60" cy="50" r="18" fill="#E0A96D"/>
        <path d="M 54 54 Q 60 60 66 54" stroke="#7F4F24" stroke-width="2" fill="none" stroke-linecap="round"/>
        <!-- Torso -->
        <path d="M 32 68 Q 60 60 88 68 L 94 150 L 26 150 Z" fill="#1B4332"/>
        <!-- Plaid / Overalls Vest -->
        <path d="M 42 70 L 48 150 M 78 70 L 72 150" stroke="#74C69D" stroke-width="4"/>
        <!-- Arms holding seedling -->
        <path d="M 30 85 Q 50 110 60 112 Q 70 110 90 85" stroke="#E0A96D" stroke-width="8" fill="none" stroke-linecap="round"/>
        <!-- Sprout in hands -->
        <circle cx="60" cy="112" r="7" fill="#8D6E63"/>
        <path d="M60 112 C 60 100, 68 92, 72 88 C 66 94, 62 98, 60 112 Z" fill="#74C69D"/>
        <path d="M60 112 C 60 102, 52 94, 48 90 C 54 96, 58 100, 60 112 Z" fill="#52B788"/>
      </g>
      <!-- Trust Badge -->
      <g transform="translate(100, 420)">
        <rect x="0" y="0" width="250" height="46" rx="23" fill="#FFFFFF" filter="drop-shadow(0 4px 10px rgba(0,0,0,0.06))"/>
        <circle cx="24" cy="23" r="14" fill="#D8F3DC"/>
        <text x="24" y="28" text-anchor="middle" font-size="14">🛡️</text>
        <text x="50" y="22" font-family="'Inter', sans-serif" font-size="12" font-weight="700" fill="#1B4332">Trusted Farmer Portal</text>
        <text x="50" y="35" font-family="'Inter', sans-serif" font-size="10" font-weight="500" fill="#52B788">Private &amp; Secure Records</text>
      </g>
    </svg>"""
    with open("static/images/login-farmer.svg", "w", encoding="utf-8") as f:
        f.write(login_svg)

    # 4. Farmer Register Visual
    register_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 450 500" width="100%" height="100%">
      <rect width="450" height="500" rx="20" fill="#F4F8F5"/>
      <circle cx="225" cy="190" r="140" fill="#E8F5E9"/>
      <!-- Farm Landscape with Sprouting Crops -->
      <path d="M 30 360 Q 150 290 280 340 T 420 310 L 420 470 L 30 470 Z" fill="#74C69D" opacity="0.6"/>
      <path d="M 20 390 Q 200 330 340 370 T 430 350 L 430 480 L 20 480 Z" fill="#2D6A4F"/>
      <!-- Modern Agriculture Icons Grid -->
      <g transform="translate(85, 90)">
        <rect x="0" y="0" width="130" height="90" rx="14" fill="#FFFFFF" filter="drop-shadow(0 6px 12px rgba(0,0,0,0.06))"/>
        <text x="65" y="42" text-anchor="middle" font-size="28">🌾</text>
        <text x="65" y="68" text-anchor="middle" font-family="'Inter', sans-serif" font-size="11" font-weight="700" fill="#1B4332">Decision Tree ML</text>
      </g>
      <g transform="translate(235, 110)">
        <rect x="0" y="0" width="130" height="90" rx="14" fill="#FFFFFF" filter="drop-shadow(0 6px 12px rgba(0,0,0,0.06))"/>
        <text x="65" y="42" text-anchor="middle" font-size="28">🧪</text>
        <text x="65" y="68" text-anchor="middle" font-family="'Inter', sans-serif" font-size="11" font-weight="700" fill="#1B4332">Soil &amp; Climate</text>
      </g>
      <g transform="translate(155, 220)">
        <rect x="0" y="0" width="140" height="95" rx="14" fill="#FFFFFF" stroke="#52B788" stroke-width="2" filter="drop-shadow(0 6px 14px rgba(45,106,79,0.12))"/>
        <text x="70" y="45" text-anchor="middle" font-size="30">🌱</text>
        <text x="70" y="70" text-anchor="middle" font-family="'Inter', sans-serif" font-size="11" font-weight="800" fill="#2D6A4F">Smart Advisory</text>
      </g>
      <!-- Tamil & English Badge -->
      <g transform="translate(80, 420)">
        <rect x="0" y="0" width="290" height="44" rx="22" fill="#FFFFFF" filter="drop-shadow(0 4px 10px rgba(0,0,0,0.06))"/>
        <text x="145" y="27" text-anchor="middle" font-family="'Inter', sans-serif" font-size="12" font-weight="700" fill="#1B4332">English &amp; தமிழ் முழு ஆதரவு</text>
      </g>
    </svg>"""
    with open("static/images/register-farmer.svg", "w", encoding="utf-8") as f:
        f.write(register_svg)

    # 5. Module Icons & Card Illustrations
    modules = {
        "recommend": ("🌱", "#2D6A4F", "#D8F3DC", "Soil & ML Model", "மண் & மாதிரி"),
        "alternatives": ("🔄", "#40916C", "#E8F5E9", "Top 3 Suitable Crops", "மாற்று தேர்வுகள்"),
        "duration": ("⏱️", "#52B788", "#F2F9F4", "Growth Lifecycle", "பயிர் கால அளவு"),
        "comparison": ("📊", "#1B4332", "#E8F4EC", "Multi-Crop Matrix", "பயிர் ஒப்பீடு"),
        "budget": ("💰", "#B08968", "#FDF8F0", "Cultivation Costs", "செலவு கணிப்பான்"),
        "calendar": ("📅", "#2D6A4F", "#EDF7F1", "Monthly Seasons", "பயிர் கால அட்டவணை"),
        "water": ("💧", "#2B7A78", "#E6F4F1", "Irrigation Guide", "நீர் தேவை"),
        "history": ("📜", "#74C69D", "#F4FAF6", "Farmer Records", "பரிந்துரை வரலாறு"),
        "expenses": ("📝", "#606C38", "#F5F8EC", "Ledger & Notes", "பண்ணை குறிப்புகள்"),
        "report": ("🖨️", "#1B4332", "#E8F5E9", "Printable Advisory", "அறிக்கை அச்சிடுக"),
        "profile": ("👤", "#2D6A4F", "#EAF5EF", "Farmer Settings", "விவசாயி சுயவிவரம்")
    }
    
    for mod_key, (emoji, color, bg, title_en, title_ta) in modules.items():
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120">
          <rect width="120" height="120" rx="24" fill="{bg}"/>
          <circle cx="60" cy="52" r="32" fill="#FFFFFF" filter="drop-shadow(0 4px 8px rgba(0,0,0,0.05))"/>
          <text x="60" y="62" text-anchor="middle" font-size="34">{emoji}</text>
          <text x="60" y="102" text-anchor="middle" font-family="'Inter', sans-serif" font-size="10" font-weight="700" fill="{color}">{title_en}</text>
        </svg>"""
        with open(f"static/images/modules/{mod_key}.svg", "w", encoding="utf-8") as f:
            f.write(svg)

    # 6. Crop Illustrations for all 14 crops
    crops_art = {
        "paddy": ("🌾", "Paddy", "நெல்", "#2D6A4F", "#E8F5E9", "Wetland Grain"),
        "wheat": ("🌾", "Wheat", "கோதுமை", "#B08968", "#FBF5EE", "Winter Rabi"),
        "maize": ("🌽", "Maize", "மக்காச்சோளம்", "#DDA15E", "#FEF8EC", "Golden Corn"),
        "cotton": ("☁️", "Cotton", "பருத்தி", "#52B788", "#F0F9F4", "White Gold"),
        "sugarcane": ("🎋", "Sugarcane", "கரும்பு", "#2D6A4F", "#E9F6ED", "Sweet Cash Crop"),
        "groundnut": ("🥜", "Groundnut", "நிலக்கடலை", "#BC6C25", "#FAF2E8", "Protein Oilseed"),
        "black_gram": ("🌱", "Black Gram", "உளுந்து", "#40916C", "#EEF8F2", "Rich Pulse"),
        "chickpea": ("🌰", "Chickpea", "கொண்டைக்கடலை", "#99582A", "#FDF6F0", "Bengal Gram"),
        "millets": ("🌾", "Millets / Ragi", "கேழ்வரகு", "#8D6E63", "#F8F4F1", "Nutri-Cereal"),
        "banana": ("🍌", "Banana", "வாழை", "#E9C46A", "#FEFAEE", "Horticulture Fruit"),
        "coconut": ("🥥", "Coconut", "தென்னை", "#6B705C", "#F4F6F0", "Kalpavriksha Palm"),
        "coffee": ("☕", "Coffee", "காபி", "#6F4E37", "#F9F3EE", "Highland Beverage"),
        "tea": ("🍃", "Tea", "தேயிலை", "#2D6A4F", "#EAF6EF", "Two Leaves & A Bud"),
        "jute": ("🌿", "Jute", "சணல்", "#B08968", "#FAF4EC", "Golden Fiber")
    }

    for crop_slug, (emoji, name_en, name_ta, color, bg, subtitle) in crops_art.items():
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 200" width="260" height="200">
          <rect width="260" height="200" rx="18" fill="{bg}"/>
          <!-- Soft Background Badge -->
          <circle cx="130" cy="82" r="54" fill="#FFFFFF" filter="drop-shadow(0 6px 14px rgba(0,0,0,0.06))"/>
          <text x="130" y="98" text-anchor="middle" font-size="54">{emoji}</text>
          <!-- Crop Names -->
          <text x="130" y="156" text-anchor="middle" font-family="'Outfit', 'Inter', sans-serif" font-size="18" font-weight="800" fill="{color}">{name_en}</text>
          <text x="130" y="176" text-anchor="middle" font-family="'Inter', sans-serif" font-size="13" font-weight="600" fill="#606C38">{name_ta} • <tspan font-size="11" font-weight="500">{subtitle}</tspan></text>
        </svg>"""
        with open(f"static/images/crops/{crop_slug}.svg", "w", encoding="utf-8") as f:
            f.write(svg)

    print("[OK] Generated all vector agricultural illustrations & branding assets.")

if __name__ == "__main__":
    generate_assets()
