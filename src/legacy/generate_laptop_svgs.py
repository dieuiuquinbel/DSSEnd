"""Script lịch sử sinh SVG minh họa cho laptop pilot.
Ensures 100% local availability with zero network failures or broken image links.
"""

from pathlib import Path

IMG_DIR = Path(__file__).resolve().parents[2] / "data" / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

LAPTOP_STYLES = {
    "00931215": {  # Asus Vivobook
        "brand": "ASUS Vivobook",
        "sub": "Snapdragon X · 14\" WUXGA",
        "base_color": "#e2e8f0",
        "screen_color": "#0284c7",
        "accent": "#38bdf8",
        "badge": "VĂN PHÒNG MỎNG NHẸ",
    },
    "00934102": {  # MSI Cyborg 15
        "brand": "MSI Cyborg 15",
        "sub": "RTX 5060 · i7-13620H · 15.6\"",
        "base_color": "#1e293b",
        "screen_color": "#0f172a",
        "accent": "#06b6d4",
        "badge": "GAMING CYBERPUNK",
    },
    "00932588": {  # Lenovo LOQ
        "brand": "LENOVO LOQ 15",
        "sub": "RTX 4050 · i7-13650HX · 144Hz",
        "base_color": "#334155",
        "screen_color": "#475569",
        "accent": "#ef4444",
        "badge": "GAMING ESPORTS",
    },
    "00933110": {  # HP Victus 15
        "brand": "HP Victus 15",
        "sub": "RTX 3050 6GB · i5-13420H · 144Hz",
        "base_color": "#1e293b",
        "screen_color": "#1e1b4b",
        "accent": "#3b82f6",
        "badge": "GAMING PERFORMANCE",
    },
    "00930069": {  # Acer Aspire 7
        "brand": "ACER Aspire 7",
        "sub": "RTX 3050 4GB · Core 5 210H",
        "base_color": "#1e293b",
        "screen_color": "#064e3b",
        "accent": "#10b981",
        "badge": "GAMING & ĐỒ HỌA",
    },
    "00931104": {  # Asus TUF A15
        "brand": "ASUS TUF A15",
        "sub": "RTX 3050 · Ryzen 7 155 · 144Hz",
        "base_color": "#334155",
        "screen_color": "#78350f",
        "accent": "#f59e0b",
        "badge": "CHUẨN QUÂN ĐỘI",
    },
    "00932014": {  # Asus Zenbook 14
        "brand": "ASUS Zenbook 14",
        "sub": "Ultra 5 225H · OLED 3K · 1.2kg",
        "base_color": "#1e293b",
        "screen_color": "#172554",
        "accent": "#60a5fa",
        "badge": "CAO CẤP OLED",
    },
    "00930882": {  # HP 250R G10
        "brand": "HP 250R G10",
        "sub": "Core 5 120U · 15.6\" FHD",
        "base_color": "#cbd5e1",
        "screen_color": "#334155",
        "accent": "#64748b",
        "badge": "KINH TẾ & BỀN BỈ",
    },
    "00939901": {  # MacBook Air M5
        "brand": "MacBook Air 13",
        "sub": "Apple M5 · Liquid Retina · 1.24kg",
        "base_color": "#e2e8f0",
        "screen_color": "#581c87",
        "accent": "#c084fc",
        "badge": "CONCEPT MINH HỌA",
    },
    "00939902": {  # MacBook Neo 13
        "brand": "MacBook Neo 13",
        "sub": "A18 Pro · Siêu Tiết Kiệm · 1.1kg",
        "base_color": "#f1f5f9",
        "screen_color": "#831843",
        "accent": "#f472b6",
        "badge": "CONCEPT MINH HỌA",
    },
}


def make_svg(brand, sub, base_color, screen_color, accent, badge):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 270" width="100%" height="100%">
  <defs>
    <linearGradient id="screen_grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{screen_color}" />
      <stop offset="100%" stop-color="#020617" />
    </linearGradient>
    <linearGradient id="body_grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{base_color}" />
      <stop offset="100%" stop-color="#475569" />
    </linearGradient>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%">
      <feDropShadow dx="0" dy="6" stdDeviation="6" flood-opacity="0.15" />
    </filter>
  </defs>

  <!-- Background subtle card -->
  <rect width="400" height="270" rx="16" fill="#f8fafc" />

  <!-- Badge Top -->
  <rect x="24" y="16" width="140" height="22" rx="4" fill="{accent}" opacity="0.15" />
  <text x="94" y="31" font-family="-apple-system, sans-serif" font-size="10" font-weight="700" fill="{accent}" text-anchor="middle">{badge}</text>

  <!-- Laptop Display (Open Bezel) -->
  <g filter="url(#shadow)">
    <!-- Display Lid Outer -->
    <rect x="70" y="45" width="260" height="155" rx="8" fill="#0f172a" />
    <!-- Display Screen -->
    <rect x="78" y="53" width="244" height="139" rx="4" fill="url(#screen_grad)" />

    <!-- Screen Content Graphic -->
    <circle cx="200" cy="115" r="32" fill="{accent}" opacity="0.2" />
    <polygon points="190,105 215,115 190,125" fill="{accent}" />
    <text x="200" y="152" font-family="-apple-system, sans-serif" font-size="13" font-weight="700" fill="#ffffff" text-anchor="middle">{brand}</text>
    <text x="200" y="168" font-family="-apple-system, sans-serif" font-size="10" font-weight="500" fill="#94a3b8" text-anchor="middle">{sub}</text>

    <!-- Webcam dot -->
    <circle cx="200" cy="49" r="2" fill="#64748b" />

    <!-- Laptop Base / Keyboard Deck -->
    <path d="M 40 205 L 360 205 L 340 226 L 60 226 Z" fill="url(#body_grad)" />
    <!-- Hinge -->
    <rect x="150" y="202" width="100" height="5" rx="2.5" fill="#334155" />
    <!-- Trackpad cutout -->
    <rect x="175" y="210" width="50" height="12" rx="2" fill="#0f172a" opacity="0.25" />
    <!-- Rubber feet shadow base -->
    <ellipse cx="200" cy="230" rx="140" ry="4" fill="#000000" opacity="0.1" />
  </g>
</svg>"""


def generate():
    for pid, info in LAPTOP_STYLES.items():
        svg_content = make_svg(
            brand=info["brand"],
            sub=info["sub"],
            base_color=info["base_color"],
            screen_color=info["screen_color"],
            accent=info["accent"],
            badge=info["badge"],
        )
        file_path = IMG_DIR / f"laptop_{pid}.svg"
        file_path.write_text(svg_content, encoding="utf-8")
    print(f"Generated {len(LAPTOP_STYLES)} SVG laptop images in {IMG_DIR}")


if __name__ == "__main__":
    generate()
