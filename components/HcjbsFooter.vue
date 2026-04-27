<template>
  <footer style="background:#fff; border-top:1px solid #ddd; font-family:Arial,'Microsoft JhengHei',sans-serif;">

    <!-- Main footer -->
    <div style="width:75%; margin:0 auto; padding:24px 0 20px; display:flex; align-items:flex-start; gap:20px;">
      <img :src="footerLogoUrl" alt="玄奘佛學研究" style="width:120px; height:99px; display:block; flex-shrink:0; object-fit:contain;" />
      <div>
        <p style="font-size:15px; font-weight:bold; color:#222; margin:0 0 6px;">
          玄奘佛學研究 &nbsp;Hsuan Chuang Journal of Buddhism Studies
        </p>
        <p style="font-size:13px; color:#444; margin:0 0 10px;">
          300新竹市香山區玄奘路48號　&nbsp;48 Hsuan Chuang Road, Hsinchu City, Taiwan
        </p>
        <div style="display:flex; align-items:center; gap:20px; font-size:13px; color:#444;">
          <span>
            最後更新日期：
            <span style="background:#3a7cbd; color:#fff; padding:2px 8px; font-size:12px; border-radius:2px; letter-spacing:1px;">
              {{ today }}
            </span>
          </span>
          <span>
            網站瀏覽人數：
            <span style="background:#3a7cbd; color:#fff; padding:2px 8px; font-size:12px; border-radius:2px; letter-spacing:1px;">
              00{{ visitorCount }}
            </span>
          </span>
        </div>
      </div>
    </div>

    <!-- Bottom bar -->
    <div style="border-top:1px solid #e0e0e0; padding:8px 0;">
      <div style="width:75%; margin:0 auto; display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:11px; color:#888;">建議瀏覽器版本：IE10以上及其他瀏覽器裝置</span>
        <span style="font-size:11px; color:#888;">COPYRIGHT 2016 HSUAN CHUANG UNIVERSITY. ALL RIGHTS RESERVED.</span>
      </div>
    </div>

  </footer>
</template>

<script setup lang="ts">
const logoUrl = '/api/xuanzang/logo'
const footerLogoUrl = '/api/xuanzang/footer-logo'

const today = new Date().toISOString().slice(0, 10).replace(/-/g, '-')
const visitorCount = '155123'
</script>
