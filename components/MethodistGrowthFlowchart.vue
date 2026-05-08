<template>
  <figure class="bg-white border border-gray-200 rounded-2xl p-4 sm:p-6 my-4 overflow-x-auto">
    <figcaption class="text-center text-sm font-medium text-gray-700 mb-3">衛理宗堂會成長計畫流程圖</figcaption>
    <svg viewBox="0 0 880 660" class="w-full max-w-4xl mx-auto" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="衛理宗堂會成長計畫流程圖">
      <defs>
        <marker id="growth-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#475569" />
        </marker>
        <marker id="growth-arrow-dashed" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
        </marker>
      </defs>

      <!-- Responsibility zones (translucent backgrounds) -->
      <g>
        <rect x="10" y="40" width="180" height="380" rx="12" fill="#fef3c7" fill-opacity="0.45" stroke="#fcd34d" stroke-width="1" stroke-dasharray="4 3"/>
        <rect x="200" y="40" width="280" height="380" rx="12" fill="#dbeafe" fill-opacity="0.45" stroke="#93c5fd" stroke-width="1" stroke-dasharray="4 3"/>
        <rect x="490" y="40" width="380" height="380" rx="12" fill="#fce7f3" fill-opacity="0.45" stroke="#f9a8d4" stroke-width="1" stroke-dasharray="4 3"/>
        <text x="100" y="30" text-anchor="middle" font-size="11" fill="#92400e" font-weight="500">教會增長委員會</text>
        <text x="340" y="30" text-anchor="middle" font-size="11" fill="#1e40af" font-weight="500">基督教教育委員會</text>
        <text x="680" y="30" text-anchor="middle" font-size="11" fill="#9d174d" font-weight="500">門徒培育中心</text>
      </g>

      <!-- 外展 boxes (left column) -->
      <g fill="#fff" stroke="#334155" stroke-width="1.5">
        <rect x="30" y="70" width="100" height="40" rx="3"/>
        <rect x="30" y="140" width="100" height="40" rx="3"/>
        <rect x="30" y="210" width="100" height="40" rx="3"/>
        <rect x="30" y="280" width="100" height="40" rx="3"/>
      </g>
      <g fill="#0f172a" font-size="14" text-anchor="middle">
        <text x="80" y="95">外展 1</text>
        <text x="80" y="165">外展 2</text>
        <text x="80" y="235">外展 3</text>
        <text x="80" y="305">外展 4</text>
      </g>

      <!-- 慕道班 diamonds (center column) -->
      <g fill="#fff" stroke="#334155" stroke-width="1.5">
        <polygon points="290,90 240,110 290,130 340,110"/>
        <polygon points="290,160 240,180 290,200 340,180"/>
        <polygon points="290,230 240,250 290,270 340,250"/>
        <polygon points="290,300 240,320 290,340 340,320"/>
        <polygon points="290,370 240,390 290,410 340,390"/>
      </g>
      <g fill="#0f172a" font-size="13" text-anchor="middle">
        <text x="290" y="115">慕道班 1</text>
        <text x="290" y="185">慕道班 2</text>
        <text x="290" y="255">慕道班 3</text>
        <text x="290" y="325">慕道班 4</text>
        <text x="290" y="395">慕道班 5</text>
      </g>

      <!-- 受洗班 box -->
      <g fill="#fff" stroke="#334155" stroke-width="1.5">
        <rect x="380" y="80" width="90" height="40" rx="3"/>
      </g>
      <text x="425" y="105" font-size="14" text-anchor="middle" fill="#0f172a">受洗班</text>

      <!-- 會友課程 -->
      <g fill="#fff" stroke="#334155" stroke-width="1.5">
        <rect x="500" y="160" width="90" height="40" rx="3"/>
      </g>
      <text x="545" y="185" font-size="14" text-anchor="middle" fill="#0f172a">會友課程</text>

      <!-- 主日學 -->
      <g fill="#fff" stroke="#334155" stroke-width="1.5">
        <rect x="500" y="240" width="90" height="40" rx="3"/>
      </g>
      <text x="545" y="265" font-size="14" text-anchor="middle" fill="#0f172a">主日學</text>

      <!-- 堂會學校 -->
      <g fill="#fff" stroke="#334155" stroke-width="1.5">
        <rect x="500" y="320" width="90" height="40" rx="3"/>
      </g>
      <text x="545" y="345" font-size="14" text-anchor="middle" fill="#0f172a">堂會學校</text>

      <!-- 門徒 -->
      <g fill="#fff" stroke="#334155" stroke-width="1.5">
        <rect x="630" y="80" width="90" height="40" rx="3"/>
      </g>
      <text x="675" y="105" font-size="14" text-anchor="middle" fill="#0f172a">門徒</text>

      <!-- 孕育門徒 -->
      <g fill="#fff" stroke="#334155" stroke-width="1.5">
        <rect x="630" y="160" width="90" height="40" rx="3"/>
      </g>
      <text x="675" y="185" font-size="14" text-anchor="middle" fill="#0f172a">孕育門徒</text>

      <!-- 平信徒神學教育 -->
      <g fill="#fff" stroke="#334155" stroke-width="1.5">
        <rect x="620" y="240" width="120" height="40" rx="3"/>
      </g>
      <text x="680" y="265" font-size="13" text-anchor="middle" fill="#0f172a">平信徒神學教育</text>

      <!-- 事奉與佈道訓練 -->
      <g fill="#fff" stroke="#334155" stroke-width="1.5">
        <rect x="755" y="80" width="100" height="60" rx="3"/>
      </g>
      <text x="805" y="105" font-size="13" text-anchor="middle" fill="#0f172a">事奉與佈道</text>
      <text x="805" y="125" font-size="13" text-anchor="middle" fill="#0f172a">訓練</text>

      <!-- Arrows -->
      <g stroke="#475569" stroke-width="1.5" fill="none" marker-end="url(#growth-arrow)">
        <!-- 外展 → 慕道班 -->
        <path d="M 130 90  H 240"/>
        <path d="M 130 160 H 240"/>
        <path d="M 130 230 H 240"/>
        <path d="M 130 300 H 240"/>

        <!-- 慕道班 決志 → 受洗班 (only first one shown horizontally) -->
        <path d="M 340 110 H 380 V 100"/>

        <!-- 慕道班 i 未決志 → 慕道班 i+1 -->
        <path d="M 290 130 V 160"/>
        <path d="M 290 200 V 230"/>
        <path d="M 290 270 V 300"/>
        <path d="M 290 340 V 370"/>

        <!-- 慕道班 2,3,4,5 決志 → 受洗班 (curved) -->
        <path d="M 340 180 H 360 V 100 H 380"/>
        <path d="M 340 250 H 365 V 100 H 380"/>
        <path d="M 340 320 H 370 V 100 H 380"/>
        <path d="M 340 390 H 375 V 100 H 380"/>

        <!-- 受洗班 → 會友課程 -->
        <path d="M 425 120 V 160"/>

        <!-- 會友課程 → 門徒 -->
        <path d="M 590 180 H 620 V 110 H 630"/>

        <!-- 會友課程 → 主日學 -->
        <path d="M 545 200 V 240"/>

        <!-- 會友課程 → 堂會學校 (via 主日學) -->
        <path d="M 545 280 V 320"/>

        <!-- 門徒 → 事奉與佈道訓練 -->
        <path d="M 720 100 H 755"/>

        <!-- 門徒 → 孕育門徒 -->
        <path d="M 675 120 V 160"/>

        <!-- 孕育門徒 → 平信徒神學教育 -->
        <path d="M 680 200 V 240"/>
      </g>

      <!-- 決志/未決志 labels -->
      <g font-size="11" fill="#475569">
        <text x="362" y="105">決志</text>
        <text x="300" y="148">未決志</text>
        <text x="300" y="218">未決志</text>
        <text x="300" y="288">未決志</text>
        <text x="300" y="358">未決志</text>
      </g>

      <!-- Legend -->
      <g transform="translate(30, 460)">
        <text x="0" y="0" font-size="13" font-weight="600" fill="#334155">圖例：三委員會工作範圍</text>

        <g transform="translate(0, 22)">
          <rect x="0" y="-10" width="14" height="14" fill="#fef3c7" stroke="#fcd34d" stroke-dasharray="2 2"/>
          <text x="22" y="0" font-size="12" fill="#0f172a">教會增長委員會：從未信到慕道（外展 1–4）</text>
        </g>
        <g transform="translate(0, 44)">
          <rect x="0" y="-10" width="14" height="14" fill="#dbeafe" stroke="#93c5fd" stroke-dasharray="2 2"/>
          <text x="22" y="0" font-size="12" fill="#0f172a">基督教教育委員會：從慕道到會友（慕道班～堂會學校）</text>
        </g>
        <g transform="translate(0, 66)">
          <rect x="0" y="-10" width="14" height="14" fill="#fce7f3" stroke="#f9a8d4" stroke-dasharray="2 2"/>
          <text x="22" y="0" font-size="12" fill="#0f172a">門徒培育中心：從會友中訓練門徒、儲訓平信徒領袖</text>
        </g>

        <g transform="translate(420, 22)">
          <line x1="0" y1="-3" x2="20" y2="-3" stroke="#475569" stroke-width="1.5" stroke-dasharray="2 2"/>
          <text x="28" y="0" font-size="12" fill="#0f172a">事奉人員的在職進修</text>
        </g>
        <g transform="translate(420, 44)">
          <line x1="0" y1="-3" x2="20" y2="-3" stroke="#475569" stroke-width="1.5" stroke-dasharray="6 3"/>
          <text x="28" y="0" font-size="12" fill="#0f172a">門徒受裝備後投入服事</text>
        </g>
        <g transform="translate(420, 66)">
          <line x1="0" y1="-3" x2="20" y2="-3" stroke="#475569" stroke-width="1.5"/>
          <text x="28" y="0" font-size="12" fill="#0f172a">未信者—慕道者—會友的流程</text>
        </g>
        <g transform="translate(420, 88)">
          <line x1="0" y1="-3" x2="20" y2="-3" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="3 2"/>
          <text x="28" y="0" font-size="12" fill="#0f172a">關懷佈道、信仰分享、啟發課程</text>
        </g>
      </g>
    </svg>
    <p class="text-xs text-gray-400 text-center mt-2">依原稿（第卌四屆年議會第二次會議紀錄，頁 176）重繪</p>
  </figure>
</template>
