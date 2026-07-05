<template>
  <div class="sd-wrap">
    <!-- Hero -->
    <section class="sdh-hero">
      <p class="sd-eyebrow">MILITARY SELF-DISCIPLINE SIMULATOR</p>
      <h1 class="sdh-title">大兵日記</h1>
      <p class="sdh-tagline">
        以軍事化的紀律養成自己：每日操課、記錄、回報，<br />
        累積 XP 晉升軍階，鍛鍊力量、耐力、紀律與儀態。
      </p>

      <div class="sdh-cta">
        <NuxtLink :to="primaryTo" class="sd-btn sd-btn--lg">{{ primaryLabel }}</NuxtLink>
        <NuxtLink v-if="!isLoggedIn" to="/soldier-diary/login" class="sd-btn sd-btn--ghost sd-btn--lg">
          我已有帳號
        </NuxtLink>
      </div>
    </section>

    <!-- Feature strip -->
    <section class="sdh-grid">
      <div v-for="f in features" :key="f.t" class="sd-panel sdh-card">
        <div class="sdh-card-icon">{{ f.icon }}</div>
        <h3 class="sdh-card-t">{{ f.t }}</h3>
        <p class="sdh-card-d">{{ f.d }}</p>
      </div>
    </section>

    <!-- 軍階階梯預覽 -->
    <section class="sd-panel sd-panel--raised sdh-ranks">
      <p class="sd-eyebrow">晉升階梯</p>
      <div class="sdh-rank-row">
        <span v-for="r in RANKS" :key="r.key" class="sdh-rank-chip">
          <span class="sdh-rank-ins">{{ r.insignia }}</span>{{ r.name }}
        </span>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSoldierSession } from '~/composables/useSoldierSession'
import { RANKS } from '~/data/soldierDiaryConfig'

definePageMeta({ layout: 'soldier-diary' })
useHead({ title: '大兵日記 — 軍事化自律養成' })

const { isLoggedIn, isChief, loadSession } = useSoldierSession()
onMounted(() => loadSession())

const primaryTo = computed(() =>
  !isLoggedIn.value ? '/soldier-diary/login' : isChief.value ? '/soldier-diary/barracks' : '/soldier-diary/diary',
)
const primaryLabel = computed(() =>
  !isLoggedIn.value ? '登入報到' : isChief.value ? '進入營區' : '我的日記',
)

const features = [
  { icon: '🪖', t: '儀隊操課', d: '記錄立正、正步、操槍等科目與時長，換算成長。' },
  { icon: '📈', t: '屬性成長', d: '力量 · 耐力 · 紀律 · 儀態，隨訓練逐日累積。' },
  { icon: '🎖️', t: '軍階晉升', d: '累積 XP 由二等兵一路晉升，解鎖榮譽徽章。' },
  { icon: '📓', t: '每日回報', d: '寫下當日日記交由長官批閱、評分與獎懲。' },
]
</script>

<style scoped>
.sdh-hero { text-align: center; padding: 46px 12px 40px; }
.sdh-title {
  font-weight: 900; font-size: clamp(2.4rem, 8vw, 4rem); color: var(--sd-sand);
  letter-spacing: 0.24em; margin: 10px 0 18px; text-shadow: 0 2px 0 #0d0f09;
}
.sdh-tagline { color: var(--sd-khaki); font-size: 0.98rem; line-height: 2; letter-spacing: 0.04em; }
.sdh-cta { display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; margin-top: 28px; }
.sd-btn--lg { padding: 13px 34px; font-size: 0.95rem; }

.sdh-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 14px; margin-top: 18px;
}
.sdh-card { padding: 22px 20px; text-align: center; }
.sdh-card-icon { font-size: 1.8rem; margin-bottom: 8px; }
.sdh-card-t { font-weight: 700; color: var(--sd-sand); letter-spacing: 0.08em; margin: 0 0 6px; font-size: 0.98rem; }
.sdh-card-d { color: var(--sd-muted); font-size: 0.8rem; line-height: 1.75; margin: 0; }

.sdh-ranks { margin-top: 22px; padding: 20px 22px; }
.sdh-rank-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.sdh-rank-chip {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 0.76rem; color: var(--sd-khaki); letter-spacing: 0.06em;
  padding: 5px 10px; border: 1px solid var(--sd-line); border-radius: 2px; background: #171a11;
}
.sdh-rank-ins { color: var(--sd-brass); font-weight: 700; }
</style>
