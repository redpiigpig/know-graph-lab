<template>
  <div class="cover" ref="root">
    <div class="purple-strip"></div>

    <!-- Title band -->
    <div class="title-band">
      <div class="title-cn">衛&nbsp;報</div>
      <div class="title-en">Wesleyan News</div>
    </div>

    <!-- Rules under title -->
    <div class="rules">
      <div class="rule"></div>
      <div class="rule rule-dark"></div>
    </div>

    <!-- UMC shield on purple strip -->
    <div class="umc-shield">
      <svg viewBox="0 0 100 120" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
        <!-- Shield outline -->
        <path d="M 10 8 L 90 8 L 90 75 Q 90 110 50 116 Q 10 110 10 75 Z"
              fill="#ffffff" stroke="#1f1f1f" stroke-width="2.5" />
        <!-- Cross (black) -->
        <rect x="40" y="22" width="14" height="78" fill="#1a1a1a" />
        <rect x="22" y="45" width="50" height="14" fill="#1a1a1a" />
        <!-- Flame (red) on cross -->
        <path d="M 56 28
                 Q 70 38 64 54
                 Q 80 50 74 70
                 Q 80 64 80 78
                 Q 70 78 62 70
                 Q 60 60 54 58
                 Q 50 50 56 28 Z"
              fill="#c43a2f" />
      </svg>
    </div>

    <!-- Bottom address block on purple -->
    <div class="addr">
      <div>中華基督教衛理公會衛蘭中心</div>
      <div>台北市中正區寧波東街 9 巷 4 號</div>
      <div>電話：(02)2393-0705 · 23922960</div>
      <div>傳真：(02)2394-6772</div>
      <div>http://wf.fhl.net&nbsp;&nbsp;Email:wf@fhl.net</div>
    </div>

    <!-- Right column: issue meta + TOC -->
    <div class="meta">
      <div class="meta-row">
        <span class="date">2002/11/30</span>
        <span class="issue-no">No.{{ issue }}</span>
      </div>
      <div class="theme">將臨節第一主日</div>
    </div>

    <div class="toc">
      <div class="toc-row"><span>一、編者案頭</span><span class="dots"></span><span class="pg">1</span></div>
      <div class="toc-row"><span>二、崇拜資源：將臨節期</span><span class="dots"></span><span class="pg">2</span></div>
      <div class="toc-row toc-sub"><span>將臨節第一、二、三、四主日</span><span class="dots"></span><span class="pg">3</span></div>
      <div class="toc-row"><span>三、普世教會消息</span><span class="dots"></span><span class="pg">11</span></div>
      <div class="toc-row"><span>四、衛理宗消息</span></div>
      <div class="toc-row toc-sub"><span>評論：對於全球愛滋病危機，約翰衛斯理會怎麼作？</span><span class="dots"></span><span class="pg">13</span></div>
      <div class="toc-row"><span>五、國際瞭望：賽普勒斯問題</span><span class="dots"></span><span class="pg">16</span></div>
      <div class="toc-row"><span>六、衛蘭專文：誰是我的鄰舍</span><span class="dots"></span><span class="pg">18</span></div>
      <div class="toc-row"><span>七、衛報連載小說：我不敢傳福音（九）</span><span class="dots"></span><span class="pg">21</span></div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ issue?: string }>();
</script>

<style scoped>
.cover {
  position: relative;
  width: 100%;
  height: 100%;
  background: #fbfaf6;
  color: #1a1a1a;
  font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Times New Roman', serif;
  overflow: hidden;
  /* Container query for scaling */
  container-type: size;
}

.purple-strip {
  position: absolute;
  top: 0; bottom: 0; left: 0;
  width: 28%;
  background: linear-gradient(180deg, #8b7c97 0%, #7c6d88 50%, #8b7c97 100%);
}

.title-band {
  position: absolute;
  top: 4%;
  left: 5%;
  right: 5%;
  height: 18%;
  background: #fbfaf6;
  display: flex;
  align-items: center;
  gap: 4%;
  padding-left: 2%;
  z-index: 2;
}
.title-cn {
  font-family: 'Noto Serif TC', 'Source Han Serif TC', serif;
  font-weight: 900;
  font-size: 14cqw;
  letter-spacing: 0.05em;
  color: #1f1f1f;
  line-height: 1;
}
.title-en {
  font-family: 'Pinyon Script', 'Brush Script MT', 'Lucida Handwriting', cursive;
  font-style: italic;
  font-size: 6cqw;
  color: #4a4a4a;
  letter-spacing: 0.02em;
  margin-top: 3cqw;
}

.rules {
  position: absolute;
  top: 22%;
  left: 5%;
  right: 5%;
  z-index: 2;
}
.rule {
  height: 0.4cqw;
  background: #b8b8b8;
  margin-bottom: 0.6cqw;
}
.rule-dark {
  height: 0.6cqw;
  background: #6a6a6a;
}

.umc-shield {
  position: absolute;
  left: 7%;
  top: 30%;
  width: 14%;
  z-index: 2;
}

.addr {
  position: absolute;
  bottom: 4%;
  left: 3%;
  width: 24%;
  color: #ffffff;
  font-size: 1.6cqw;
  line-height: 1.5;
  z-index: 2;
}
.addr div {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.meta {
  position: absolute;
  top: 26%;
  left: 36%;
  right: 6%;
  z-index: 2;
}
.meta-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 1.5cqw;
}
.date {
  font-size: 2.5cqw;
  color: #4a4a4a;
}
.issue-no {
  font-family: 'Georgia', serif;
  font-weight: 700;
  font-size: 5cqw;
  color: #1a1a1a;
}
.theme {
  font-size: 2.3cqw;
  color: #2a2a2a;
  margin-bottom: 2cqw;
  margin-left: 2cqw;
}

.toc {
  position: absolute;
  top: 44%;
  left: 36%;
  right: 6%;
  font-size: 2.1cqw;
  color: #1a1a1a;
  z-index: 2;
}
.toc-row {
  display: flex;
  align-items: baseline;
  gap: 0.6cqw;
  margin-bottom: 1.6cqw;
  line-height: 1.4;
}
.toc-sub {
  padding-left: 4cqw;
  margin-bottom: 1.6cqw;
}
.dots {
  flex: 1;
  border-bottom: 0.2cqw dotted #888;
  transform: translateY(-0.4cqw);
}
.pg {
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
</style>
