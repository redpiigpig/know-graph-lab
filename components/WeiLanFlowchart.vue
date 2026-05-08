<template>
  <figure class="bg-white border border-gray-200 rounded-2xl p-4 sm:p-6 my-4">
    <figcaption class="text-center text-sm font-medium text-gray-700 mb-3">衛蘭都會宣教流程圖</figcaption>
    <svg viewBox="0 0 640 760" class="w-full max-w-2xl mx-auto" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="衛蘭都會宣教流程圖">
      <defs>
        <marker id="wl-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#475569" />
        </marker>
      </defs>

      <!-- Phase brackets (right side) -->
      <g stroke="#cbd5e1" stroke-width="1.5" fill="none">
        <path d="M 600 30 H 612 V 270 H 600" />
        <path d="M 600 290 H 612 V 580 H 600" />
        <path d="M 600 610 H 612 V 680 H 600" />
      </g>
      <g fill="#64748b" font-size="13" text-anchor="middle">
        <text x="624" y="115"><tspan x="624" dy="0">第</tspan><tspan x="624" dy="16">一</tspan><tspan x="624" dy="16">階</tspan><tspan x="624" dy="16">段</tspan></text>
        <text x="624" y="385"><tspan x="624" dy="0">第</tspan><tspan x="624" dy="16">二</tspan><tspan x="624" dy="16">階</tspan><tspan x="624" dy="16">段</tspan></text>
        <text x="624" y="625"><tspan x="624" dy="0">第</tspan><tspan x="624" dy="16">三</tspan><tspan x="624" dy="16">階</tspan><tspan x="624" dy="16">段</tspan></text>
      </g>

      <!-- Arrows -->
      <g stroke="#475569" stroke-width="1.6" fill="none" marker-end="url(#wl-arrow)">
        <!-- 1 → 2 (籌備 → 橋樑事工) -->
        <path d="M 320 76 V 130 H 135 V 178" />
        <!-- 1 → 3 (籌備 → 教會事工) -->
        <path d="M 320 76 V 130 H 495 V 158" />
        <!-- 3 → 4 (教會事工 → 社區事工1) -->
        <path d="M 495 270 V 298" />
        <!-- 4 → 5 (社區事工1 → 社區事工2) -->
        <path d="M 495 364 V 388" />
        <!-- 5 → 6 (社區事工2 → 衛蘭團契) -->
        <path d="M 495 454 V 480 H 360 V 508" />
        <!-- 2 → 6 (橋樑事工 → 衛蘭團契) -->
        <path d="M 135 224 V 480 H 280 V 508" />
        <!-- 6 → 7 (衛蘭團契 → 衛蘭佈道所) -->
        <path d="M 320 556 V 618" />
      </g>

      <!-- Boxes -->
      <g fill="#fff" stroke="#334155" stroke-width="1.5">
        <rect x="240" y="30"  width="160" height="46" rx="3" />
        <rect x="70"  y="180" width="130" height="44" rx="3" />
        <rect x="420" y="160" width="150" height="110" rx="3" />
        <rect x="410" y="300" width="170" height="64" rx="3" />
        <rect x="410" y="390" width="170" height="64" rx="3" />
        <rect x="240" y="510" width="160" height="46" rx="3" />
        <rect x="240" y="618" width="160" height="46" rx="3" />
      </g>

      <!-- Box labels -->
      <g fill="#0f172a" font-size="14" text-anchor="middle" font-weight="500">
        <text x="320" y="58">衛蘭事工籌備</text>
        <text x="135" y="207">橋樑事工</text>

        <text x="495" y="184">教會事工</text>
        <text x="495" y="216" font-size="13" font-weight="400" fill="#475569">沛恩</text>
        <text x="495" y="244" font-size="13" font-weight="400" fill="#475569">安素城區</text>

        <text x="495" y="324">社區事工 1</text>
        <text x="495" y="350" font-size="12" font-weight="400" fill="#475569">田野調查／策略擬定</text>

        <text x="495" y="414">社區事工 2</text>
        <text x="495" y="440" font-size="12" font-weight="400" fill="#475569">社區報／文化活動</text>

        <text x="320" y="538">衛蘭團契</text>
        <text x="320" y="646">衛蘭佈道所</text>
      </g>
    </svg>
    <p class="text-xs text-gray-400 text-center mt-2">依原稿（第卅八屆年議會第二次會議紀錄，頁 147）重繪</p>
  </figure>
</template>
