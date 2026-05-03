<template>
  <div class="wk-page">

    <div class="wk-topbar">
      <NuxtLink to="/pong-archive/daily-office" class="wk-back">← 三讀三禱</NuxtLink>
    </div>

    <header class="wk-header" :style="{ backgroundColor: seasonColor.bg }">
      <div class="wk-header-inner">
        <p class="wk-eyebrow">{{ yearLabel }}　·　{{ seasonColor.name }}</p>
        <h1 class="wk-title-main">{{ titleMain }}</h1>
        <p v-if="titleTheme" class="wk-title-theme">{{ titleTheme }}</p>
        <div
          class="wk-year-picker"
          @mousedown="onDragStart"
          @mouseup="onDragEnd"
          @mouseleave="onDragCancel"
          @touchstart.passive="onDragStart"
          @touchend="onDragEnd"
          @wheel.prevent="onWheel"
        >
          <button
            v-for="y in nearbyYears"
            :key="y"
            class="wk-year-btn"
            :class="{ 'wk-year-btn--active': selectedChurchYear === y }"
            @click="selectedChurchYear = y"
          >{{ y }}</button>
        </div>
        <p v-if="dateRangeLabel" class="wk-date-range">{{ dateRangeLabel }}</p>
        <p v-else-if="!weekExistsInYear" class="wk-date-range wk-no-week">
          本禮儀年度無{{ SEASON_CHINESE[season] }}第 {{ week }} 週
        </p>
      </div>
    </header>

    <div v-if="pending" class="wk-loading">載入中…</div>

    <template v-else-if="!weekExistsInYear">
      <div class="wk-empty wk-no-week-body">
        <p>{{ selectedChurchYear }}-{{ selectedChurchYear + 1 }} 教會年</p>
        <p class="wk-empty-sub">本年度的{{ SEASON_CHINESE[season] }}只有 {{ lectionaryTable.length }} 週，無第 {{ week }} 週</p>
      </div>
    </template>

    <template v-else>

      <!-- Lectionary overview table — always visible when RCL data exists -->
      <section v-if="lectionaryTable.length" class="wk-lectionary">
        <div class="wk-lectionary-inner">
          <h3 class="wk-lec-heading">{{ YEAR_CHINESE[yearParam] }}{{ SEASON_CHINESE[season] }}的主日經課表</h3>
          <p class="wk-lec-source">以下根據《修訂版通用經課》The Revised Common Lectionary</p>
          <table class="wk-lec-table">
            <thead>
              <tr>
                <th>{{ SEASON_CHINESE[season] }}</th>
                <th>舊約</th>
                <th>詩篇</th>
                <th>書信</th>
                <th>福音</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in pagedLectionaryTable"
                :key="row.week"
                :class="{ 'wk-lec-current': row.week === week }"
              >
                <td>{{ row.label }}</td>
                <td>{{ row.ot }}</td>
                <td v-html="row.ps.replace(/\n/g, '<br>')"></td>
                <td>{{ row.ep }}</td>
                <td>{{ row.gos }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="lecPageCount > 1" class="wk-lec-nav">
            <button class="wk-lec-nav-btn" :disabled="lecPage === 0" @click="lecPage--">&#8249;</button>
            <span class="wk-lec-nav-label">
              第 {{ lecPage * 4 + 1 }}–{{ Math.min((lecPage + 1) * 4, lectionaryTable.length) }} 週
              <span class="wk-lec-nav-page">（{{ lecPage + 1 }} / {{ lecPageCount }}）</span>
            </span>
            <button class="wk-lec-nav-btn" :disabled="lecPage >= lecPageCount - 1" @click="lecPage++">&#8250;</button>
          </div>
        </div>
      </section>

      <!-- No content uploaded -->
      <div v-if="!weekData" class="wk-empty">
        <p>日讀資料尚未上傳</p>
        <p class="wk-empty-sub">{{ yearLabel }}　{{ seasonColor.name }}　第 {{ week }} 週</p>
      </div>

      <template v-else>

      <!-- Intro letter — 乙年無靈修引言，不顯示此區段 -->
      <section v-if="yearParam !== 'B' && (weekData.intro_letter || editMode)" class="wk-intro">
        <div class="wk-intro-inner">
          <p class="wk-section-label">本週靈修引言</p>
          <div v-if="!editMode" class="wk-intro-body" v-html="renderBody(weekData.intro_letter)"></div>
          <textarea v-else class="wk-edit-area wk-edit-area--tall" :value="weekData.intro_letter || ''" @blur="onWeekBlur($event, 'intro_letter')" placeholder="本週靈修引言…"></textarea>
        </div>
      </section>

      <!-- Theme essay -->
      <section v-if="weekData.theme_essay || editMode" class="wk-essay">
        <div class="wk-essay-inner">
          <p class="wk-section-label">主題默想</p>
          <template v-if="!editMode">
            <h2 v-if="weekData.theme_essay_title" class="wk-essay-title" v-html="essayTitleHtml"></h2>
            <div class="wk-essay-body" v-html="renderBody(weekData.theme_essay)"></div>
          </template>
          <template v-else>
            <p class="wk-edit-field-label">標題</p>
            <textarea class="wk-edit-area wk-edit-area--sm" :value="weekData.theme_essay_title || ''" @blur="onWeekBlur($event, 'theme_essay_title')" placeholder="主題默想標題…"></textarea>
            <p class="wk-edit-field-label">內文</p>
            <textarea class="wk-edit-area wk-edit-area--tall" :value="weekData.theme_essay || ''" @blur="onWeekBlur($event, 'theme_essay')" placeholder="主題默想內文…"></textarea>
          </template>
        </div>
      </section>

      <!-- Day navigation -->
      <section class="wk-days-section">
        <div class="wk-days-inner">
          <div class="wk-day-tabs">
            <button
              v-for="d in days"
              :key="d.day_of_week"
              class="wk-day-tab"
              :class="{
                'wk-day-tab--active': activeDay === d.day_of_week,
                'wk-day-tab--locked': lockedDays.has(d.day_of_week),
              }"
              :disabled="lockedDays.has(d.day_of_week)"
              @click="activeDay = d.day_of_week"
            >
              {{ DAY_LABELS[d.day_of_week] }}<span v-if="dayDateMap[d.day_of_week]" class="wk-day-date">（{{ dayDateMap[d.day_of_week] }}）</span>
            </button>
          </div>

          <div v-if="currentDay" class="wk-day-content">
            <div
              v-for="(reading, ri) in currentDay.readings"
              :key="ri"
              class="wk-reading"
            >
              <button
                class="wk-reading-head"
                :class="{ 'wk-reading-head--open': openReadings[ri] }"
                @click="toggleReading(ri)"
              >
                <span class="wk-reading-num">{{ ri + 1 }}</span>
                <span class="wk-reading-ref">
                  <span class="wk-reading-book">{{ reading.book }}</span>
                  <span v-if="reading.passage" class="wk-reading-passage">{{ reading.passage }}</span>
                </span>
                <span v-if="reading.title" class="wk-reading-title">{{ reading.title }}</span>
                <span class="wk-reading-chevron" :class="{ open: openReadings[ri] }">›</span>
              </button>

              <div v-if="openReadings[ri]" class="wk-reading-body">
                <!-- 讀 -->
                <div class="wk-rp-section wk-rp-section--read">
                  <span class="wk-rp-label">經文</span>
                  <div class="wk-rp-content">
                    <template v-if="!editMode">
                      <div v-if="reading.text" class="wk-scripture" v-html="renderScripture(reading.text)"></div>
                    </template>
                    <textarea v-else class="wk-edit-area wk-edit-area--tall" :value="reading.text || ''" @blur="onReadingBlur($event, currentDay, ri, 'text')" placeholder="經文…"></textarea>
                  </div>
                </div>
                <!-- 禱 -->
                <div class="wk-rp-section">
                  <span class="wk-rp-label">祈禱</span>
                  <div class="wk-rp-content">
                    <template v-if="!editMode">
                      <div v-if="reading.meditation" class="wk-meditation">
                        <div v-html="renderPara(reading.meditation)"></div>
                      </div>
                      <div v-if="reading.key_verse" class="wk-key-verse">
                        <span class="wk-key-verse-label">金句</span>
                        <blockquote class="wk-key-verse-text" v-html="renderKeyVerse(reading.key_verse)"></blockquote>
                      </div>
                    </template>
                    <template v-else>
                      <p class="wk-edit-field-label">默想</p>
                      <textarea class="wk-edit-area wk-edit-area--tall" :value="reading.meditation || ''" @blur="onReadingBlur($event, currentDay, ri, 'meditation')" placeholder="默想…"></textarea>
                      <p class="wk-edit-field-label">金句</p>
                      <textarea class="wk-edit-area wk-edit-area--sm" :value="reading.key_verse || ''" @blur="onReadingBlur($event, currentDay, ri, 'key_verse')" placeholder="金句…"></textarea>
                    </template>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Liturgy Appendices (optional, e.g. 點燭儀式) -->
      <section v-if="liturgyAppendices.length" class="wk-appendices">
        <div class="wk-appendices-inner">
          <p class="wk-section-label">附註</p>
          <div v-for="app in liturgyAppendices" :key="'lit-' + app._idx" class="wk-appendix">
            <template v-if="editMode">
              <p class="wk-edit-field-label">附錄標題</p>
              <textarea class="wk-edit-area wk-edit-area--sm" :value="app.title || ''" @blur="onAppendixBlur($event, app._idx, 'title')" placeholder="標題…"></textarea>
              <p class="wk-edit-field-label">附錄內文</p>
              <textarea class="wk-edit-area wk-edit-area--tall" :value="app.body || ''" @blur="onAppendixBlur($event, app._idx, 'body')" placeholder="附錄內文…"></textarea>
            </template>
            <template v-else>
              <h3 v-if="app.title" class="wk-appendix-title">{{ app.title }}</h3>
              <div v-if="app.body" class="wk-appendix-body" v-html="isHtml(app.body) ? app.body : renderPara(app.body)"></div>
            </template>
          </div>
        </div>
      </section>

      <!-- Discussion (本週小組討論) -->
      <section v-if="discussionAppendices.length" class="wk-discussion">
        <div class="wk-discussion-inner">
          <div v-for="app in discussionAppendices" :key="'disc-' + app._idx" class="wk-appendix">
            <template v-if="editMode">
              <p class="wk-edit-field-label">討論標題</p>
              <textarea class="wk-edit-area wk-edit-area--sm" :value="app.title || ''" @blur="onAppendixBlur($event, app._idx, 'title')" placeholder="標題…"></textarea>
              <p class="wk-edit-field-label">討論內文</p>
              <textarea class="wk-edit-area wk-edit-area--tall" :value="app.body || ''" @blur="onAppendixBlur($event, app._idx, 'body')" placeholder="討論內文…"></textarea>
            </template>
            <template v-else>
              <h3 v-if="app.title" class="wk-appendix-title">{{ app.title }}</h3>
              <div v-if="app.body" class="wk-appendix-body" v-html="isHtml(app.body) ? app.body : renderPara(app.body)"></div>
            </template>
          </div>
        </div>
      </section>

      </template><!-- end v-else weekData -->

    </template><!-- end v-else pending -->

    <!-- Team credits -->
    <footer class="wk-credits">
      <div class="wk-credits-inner">
        <div class="wk-credits-grid">
          <div v-for="c in (weekData?.team_credits || [])" :key="c.role" class="wk-credit-row">
            <span class="wk-credit-role">{{ c.role }}</span>
            <span class="wk-credit-names">{{ c.names }}</span>
          </div>
        </div>
        <p class="wk-credits-site-label">官方網站</p>
        <a href="https://www.1day3read3pray.com/" target="_blank" rel="noopener" class="wk-credits-link">www.1day3read3pray.com</a>
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { createClient } from '@supabase/supabase-js'
import { usePongEditor } from '~/composables/usePongEditor'
import {
  getChurchYearSundays,
  getCurrentChurchYear,
  SEASON_COLORS,
} from '~/composables/useChurchCalendar.js'

definePageMeta({ layout: 'pong-archive' })

// ── Edit mode (shared singleton from layout) ──────────────────
const { isEditing: editMode, saveField, saveFields } = usePongEditor()

function onReadingBlur(event, day, ri, field) {
  if (!day || !weekData.value) return
  const value = event.target.value
  const dayRow = weekData.value.pong_lectionary_days.find(d => d.id === day.id)
  if (!dayRow) return
  const updatedReadings = dayRow.readings.map((r, i) => i === ri ? { ...r, [field]: value } : r)
  dayRow.readings = updatedReadings
  saveFields('pong_lectionary_days', day.id, { readings: updatedReadings })
}

function onWeekBlur(event, field) {
  if (!weekData.value) return
  const value = event.target.value
  weekData.value[field] = value
  saveField('pong_lectionary_weeks', weekData.value.id, field, value)
}

function onAppendixBlur(event, ai, key) {
  if (!weekData.value?.appendices) return
  const value = event.target.value
  const updated = weekData.value.appendices.map((a, i) => i === ai ? { ...a, [key]: value } : a)
  weekData.value.appendices = updated
  saveFields('pong_lectionary_weeks', weekData.value.id, { appendices: updated })
}

const route = useRoute()
const yearParam = route.params.year
const season = route.params.season
const week = parseInt(route.params.week)

const YEAR_LABELS  = { A: '甲年（Year A）', B: '乙年（Year B）', C: '丙年（Year C）' }
const YEAR_CHINESE = { A: '甲年', B: '乙年', C: '丙年' }
const SEASON_CHINESE = {
  advent: '將臨節期', christmas: '聖誕節期', epiphany: '主顯節期',
  lent: '四旬節期', easter: '復活節期', pentecost: '聖靈降臨節期',
}
const DAY_LABELS = ['主日', '週一', '週二', '週三', '週四', '週五', '週六']
const CYCLE_OFFSET = { A: 0, B: 1, C: 2 }

// ── Revised Common Lectionary 主日經課（依年份/節期）──────────────
const RCL = {
  A: {
    advent: [
      { week: 1, label: '第一週（主日）', ot: '賽 2:1-5',   ps: '詩 122',               ep: '羅 13:11-14', gos: '太 24:36-44' },
      { week: 2, label: '第二週（主日）', ot: '賽 11:1-10', ps: '詩 72:1-7, 18-19',      ep: '羅 15:4-13',  gos: '太 3:1-12'   },
      { week: 3, label: '第三週（主日）', ot: '賽 35:1-10', ps: '詩 146:5-10\n或路 1:47-55', ep: '雅 5:7-10',  gos: '太 11:2-11'  },
      { week: 4, label: '第四週（主日）', ot: '賽 7:10-16', ps: '詩 80:1-7, 17-19',      ep: '羅 1:1-7',    gos: '太 1:18-25'  },
    ],
    christmas: [
      { week: 1, label: '第一週（主日）', ot: '耶 31:7-14',         ps: '詩 147:12-20',          ep: '弗 1:3-14',        gos: '約 1:1-18'    },
      { week: 2, label: '第二週（主日）', ot: '賽 42:1-9',          ps: '詩 29',                 ep: '徒 10:34-43',      gos: '太 3:13-17'   },
    ],
    epiphany: [
      { week: 1, label: '第一週（主日）', ot: '賽 49:1-7',          ps: '詩 40:1-11',            ep: '林前 1:1-9',       gos: '約 1:29-42'  },
      { week: 2, label: '第二週（主日）', ot: '賽 9:1-4',           ps: '詩 27:1, 4-9',          ep: '林前 1:10-18',     gos: '太 4:12-23'  },
      { week: 3, label: '第三週（主日）', ot: '彌 6:1-8',           ps: '詩 15',                 ep: '林前 1:18-31',     gos: '太 5:1-12'   },
      { week: 4, label: '第四週（主日）', ot: '賽 58:1-9',          ps: '詩 112:1-9',            ep: '林前 2:1-12',      gos: '太 5:13-20'  },
      { week: 5, label: '第五週（主日）', ot: '出 24:12-18',        ps: '詩 2',                  ep: '彼後 1:16-21',     gos: '太 17:1-9'   },
      { week: 6, label: '第六週（主日）', ot: '創 2:15-17; 3:1-7', ps: '詩 32',                 ep: '羅 5:12-19',       gos: '太 4:1-11'   },
    ],
    lent: [
      { week: 1, label: '第一週（主日）', ot: '創 12:1-4',          ps: '詩 121',                ep: '羅 4:1-5, 13-17',  gos: '約 3:1-17'   },
      { week: 2, label: '第二週（主日）', ot: '出 17:1-7',          ps: '詩 95',                 ep: '羅 5:1-11',        gos: '約 4:5-42'   },
      { week: 3, label: '第三週（主日）', ot: '撒上 16:1-13',       ps: '詩 23',                 ep: '弗 5:8-14',        gos: '約 9:1-41'   },
      { week: 4, label: '第四週（主日）', ot: '結 37:1-14',         ps: '詩 130',                ep: '羅 8:6-11',        gos: '約 11:1-45'  },
      { week: 5, label: '第五週（主日）', ot: '賽 50:4-9',          ps: '詩 118:1-2, 19-29',     ep: '腓 2:5-11',        gos: '太 21:1-11'  },
      { week: 6, label: '第六週（主日）', ot: '徒 10:34-43',        ps: '詩 118:1-2, 14-24',     ep: '西 3:1-4',         gos: '約 20:1-18'  },
    ],
    easter: [
      { week: 1, label: '第一週（主日）', ot: '徒 2:14, 22-32',     ps: '詩 16',                 ep: '彼前 1:3-9',       gos: '約 20:19-31' },
      { week: 2, label: '第二週（主日）', ot: '徒 2:14, 36-41',     ps: '詩 116:1-4, 12-19',     ep: '彼前 1:17-23',     gos: '路 24:13-35' },
      { week: 3, label: '第三週（主日）', ot: '徒 2:42-47',         ps: '詩 23',                 ep: '彼前 2:19-25',     gos: '約 10:1-10'  },
      { week: 4, label: '第四週（主日）', ot: '徒 7:55-60',         ps: '詩 31:1-5, 15-16',      ep: '彼前 2:2-10',      gos: '約 14:1-14'  },
      { week: 5, label: '第五週（主日）', ot: '徒 17:22-31',        ps: '詩 66:8-20',            ep: '彼前 3:13-22',     gos: '約 14:15-21' },
      { week: 6, label: '第六週（主日）', ot: '徒 1:1-11',          ps: '詩 47',                 ep: '弗 1:15-23',       gos: '路 24:44-53' },
      { week: 7, label: '第七週（主日）', ot: '徒 1:6-14',          ps: '詩 68:1-10, 32-35',     ep: '彼前 4:12-14; 5:6-11', gos: '約 17:1-11' },
    ],
    pentecost: [
      { week:  1, label: '聖靈降臨主日',     ot: '徒 2:1-21',               ps: '詩 104:24-34, 35b',     ep: '林前 12:3b-13',         gos: '約 20:19-23'   },
      { week:  2, label: '三一主日',         ot: '創 1:1-2:4',              ps: '詩 8',                  ep: '林後 13:11-13',         gos: '太 28:16-20'   },
      { week:  3, label: '第三週（主日）',   ot: '創 6:9-22; 8:14-19',      ps: '詩 46',                 ep: '羅 1:16-17; 3:22b-28',  gos: '太 7:21-29'    },
      { week:  4, label: '第四週（主日）',   ot: '創 12:1-9',               ps: '詩 33:1-12',            ep: '羅 4:13-25',            gos: '太 9:9-13, 18-26' },
      { week:  5, label: '第五週（主日）',   ot: '創 18:1-15; 21:1-7',      ps: '詩 116:1-2, 12-19',     ep: '羅 5:1-8',              gos: '太 9:35-10:8'  },
      { week:  6, label: '第六週（主日）',   ot: '創 21:8-21',              ps: '詩 86:1-10, 16-17',     ep: '羅 6:1b-11',            gos: '太 10:24-39'   },
      { week:  7, label: '第七週（主日）',   ot: '創 22:1-14',              ps: '詩 13',                 ep: '羅 6:12-23',            gos: '太 10:40-42'   },
      { week:  8, label: '第八週（主日）',   ot: '創 24:34-38, 42-49, 58-67',ps: '詩 45:10-17',          ep: '羅 7:15-25',            gos: '太 11:16-19, 25-30' },
      { week:  9, label: '第九週（主日）',   ot: '創 25:19-34',             ps: '詩 119:105-112',        ep: '羅 8:1-11',             gos: '太 13:1-9, 18-23' },
      { week: 10, label: '第十週（主日）',   ot: '創 28:10-19',             ps: '詩 139:1-12, 23-24',    ep: '羅 8:12-25',            gos: '太 13:24-30, 36-43' },
      { week: 11, label: '第十一週（主日）', ot: '創 29:15-28',             ps: '詩 105:1-11, 45b',      ep: '羅 8:26-39',            gos: '太 13:31-33, 44-52' },
      { week: 12, label: '第十二週（主日）', ot: '創 32:22-31',             ps: '詩 17:1-7, 15',         ep: '羅 9:1-5',              gos: '太 14:13-21'   },
      { week: 13, label: '第十三週（主日）', ot: '創 37:1-4, 12-28',        ps: '詩 105:1-6, 16-22',     ep: '羅 10:5-15',            gos: '太 14:22-33'   },
      { week: 14, label: '第十四週（主日）', ot: '創 45:1-15',              ps: '詩 133',                ep: '羅 11:1-2, 29-32',      gos: '太 15:10-28'   },
      { week: 15, label: '第十五週（主日）', ot: '出 1:8-2:10',             ps: '詩 124',                ep: '羅 12:1-8',             gos: '太 16:13-20'   },
      { week: 16, label: '第十六週（主日）', ot: '出 3:1-15',               ps: '詩 105:1-6, 23-26',     ep: '羅 12:9-21',            gos: '太 16:21-28'   },
      { week: 17, label: '第十七週（主日）', ot: '出 12:1-14',              ps: '詩 149',                ep: '羅 13:8-14',            gos: '太 18:15-20'   },
      { week: 18, label: '第十八週（主日）', ot: '出 14:19-31',             ps: '詩 114',                ep: '羅 14:1-12',            gos: '太 18:21-35'   },
      { week: 19, label: '第十九週（主日）', ot: '出 16:2-15',              ps: '詩 105:1-6, 37-45',     ep: '腓 1:21-30',            gos: '太 20:1-16'    },
      { week: 20, label: '第二十週（主日）', ot: '出 17:1-7',               ps: '詩 78:1-4, 12-16',      ep: '腓 2:1-13',             gos: '太 21:23-32'   },
      { week: 21, label: '第二十一週（主日）', ot: '出 20:1-4, 7-9, 12-20', ps: '詩 19',                 ep: '腓 3:4b-14',            gos: '太 21:33-46'   },
      { week: 22, label: '第二十二週（主日）', ot: '出 32:1-14',            ps: '詩 106:1-6, 19-23',     ep: '腓 4:1-9',              gos: '太 22:1-14'    },
      { week: 23, label: '第二十三週（主日）', ot: '出 33:12-23',           ps: '詩 99',                 ep: '帖前 1:1-10',           gos: '太 22:15-22'   },
      { week: 24, label: '第二十四週（主日）', ot: '申 34:1-12',            ps: '詩 90:1-6, 13-17',      ep: '帖前 2:1-8',            gos: '太 22:34-46'   },
      { week: 25, label: '第二十五週（主日）', ot: '書 3:7-17',             ps: '詩 107:1-7, 33-37',     ep: '帖前 2:9-13',           gos: '太 23:1-12'    },
      { week: 26, label: '第二十六週（主日）', ot: '書 24:1-3, 14-25',      ps: '詩 78:1-7',             ep: '帖前 4:13-18',          gos: '太 25:1-13'    },
      { week: 27, label: '基督君王主日',     ot: '結 34:11-16, 20-24',      ps: '詩 100',                ep: '弗 1:15-23',            gos: '太 25:31-46'   },
    ],
  },
  B: {
    advent: [
      { week: 1, label: '第一週（主日）', ot: '賽 64:1-9',          ps: '詩 80:1-7, 17-19',      ep: '林前 1:3-9',       gos: '可 13:24-37' },
      { week: 2, label: '第二週（主日）', ot: '賽 40:1-11',         ps: '詩 85:1-2, 8-13',       ep: '彼後 3:8-15',      gos: '可 1:1-8'    },
      { week: 3, label: '第三週（主日）', ot: '賽 61:1-4, 8-11',    ps: '詩 126\n或路 1:47-55',  ep: '帖前 5:16-24',     gos: '約 1:6-8, 19-28' },
      { week: 4, label: '第四週（主日）', ot: '撒下 7:1-11, 16',    ps: '路 1:47-55',            ep: '羅 16:25-27',      gos: '路 1:26-38'  },
    ],
    christmas: [
      { week: 1, label: '第一週（主日）', ot: '耶 31:7-14',         ps: '詩 147:12-20',          ep: '弗 1:3-14',        gos: '約 1:1-18'   },
      { week: 2, label: '第二週（主日）', ot: '創 1:1-5',           ps: '詩 29',                 ep: '徒 19:1-7',        gos: '可 1:4-11'   },
    ],
    epiphany: [
      { week: 1, label: '第一週（主日）', ot: '撒上 3:1-10',        ps: '詩 139:1-6, 13-18',     ep: '林前 6:12-20',     gos: '約 1:43-51'  },
      { week: 2, label: '第二週（主日）', ot: '拿 3:1-5, 10',       ps: '詩 62:5-12',            ep: '林前 7:29-31',     gos: '可 1:14-20'  },
      { week: 3, label: '第三週（主日）', ot: '申 18:15-20',        ps: '詩 111',                ep: '林前 8:1-13',      gos: '可 1:21-28'  },
      { week: 4, label: '第四週（主日）', ot: '賽 40:21-31',        ps: '詩 147:1-11',           ep: '林前 9:16-23',     gos: '可 1:29-39'  },
      { week: 5, label: '第五週（主日）', ot: '王下 2:1-12',        ps: '詩 50:1-6',             ep: '林後 4:3-6',       gos: '可 9:2-9'    },
      { week: 6, label: '第六週（主日）', ot: '創 9:8-17',          ps: '詩 25:1-10',            ep: '彼前 3:18-22',     gos: '可 1:9-15'   },
    ],
    lent: [
      { week: 1, label: '第一週（主日）', ot: '創 17:1-7, 15-16',   ps: '詩 22:23-31',           ep: '羅 4:13-25',       gos: '可 8:31-38'  },
      { week: 2, label: '第二週（主日）', ot: '出 20:1-17',         ps: '詩 19',                 ep: '林前 1:18-25',     gos: '約 2:13-22'  },
      { week: 3, label: '第三週（主日）', ot: '民 21:4-9',          ps: '詩 107:1-3, 17-22',     ep: '弗 2:1-10',        gos: '約 3:14-21'  },
      { week: 4, label: '第四週（主日）', ot: '耶 31:31-34',        ps: '詩 51:1-12',            ep: '來 5:5-10',        gos: '約 12:20-33' },
      { week: 5, label: '第五週（主日）', ot: '賽 50:4-9',          ps: '詩 118:1-2, 19-29',     ep: '腓 2:5-11',        gos: '可 11:1-11'  },
      { week: 6, label: '第六週（主日）', ot: '徒 10:34-43',        ps: '詩 118:1-2, 14-24',     ep: '林前 15:1-11',     gos: '可 16:1-8'   },
    ],
    easter: [
      { week: 1, label: '第一週（主日）', ot: '徒 4:32-35',         ps: '詩 133',                ep: '約一 1:1-2:2',     gos: '約 20:19-31' },
      { week: 2, label: '第二週（主日）', ot: '徒 3:12-19',         ps: '詩 4',                  ep: '約一 3:1-7',       gos: '路 24:36-48' },
      { week: 3, label: '第三週（主日）', ot: '徒 4:5-12',          ps: '詩 23',                 ep: '約一 3:16-24',     gos: '約 10:11-18' },
      { week: 4, label: '第四週（主日）', ot: '徒 8:26-40',         ps: '詩 22:25-31',           ep: '約一 4:7-21',      gos: '約 15:1-8'   },
      { week: 5, label: '第五週（主日）', ot: '徒 10:44-48',        ps: '詩 98',                 ep: '約一 5:1-6',       gos: '約 15:9-17'  },
      { week: 6, label: '第六週（主日）', ot: '徒 1:1-11',          ps: '詩 47',                 ep: '弗 1:15-23',       gos: '路 24:44-53' },
      { week: 7, label: '第七週（主日）', ot: '徒 1:15-17, 21-26',  ps: '詩 1',                  ep: '約一 5:9-13',      gos: '約 17:6-19'  },
    ],
    pentecost: [
      { week:  1, label: '聖靈降臨主日',     ot: '徒 2:1-21',               ps: '詩 104:24-34, 35b',     ep: '羅 8:22-27',            gos: '約 15:26-27; 16:4b-15' },
      { week:  2, label: '三一主日',         ot: '賽 6:1-8',                ps: '詩 29',                 ep: '羅 8:12-17',            gos: '約 3:1-17'   },
      { week:  3, label: '第三週（主日）',   ot: '撒上 3:1-10',             ps: '詩 139:1-6, 13-18',     ep: '林後 4:5-12',           gos: '可 2:23-3:6' },
      { week:  4, label: '第四週（主日）',   ot: '撒上 8:4-20',             ps: '詩 138',                ep: '林後 4:13-5:1',         gos: '可 3:20-35'  },
      { week:  5, label: '第五週（主日）',   ot: '撒上 15:34-16:13',        ps: '詩 20',                 ep: '林後 5:6-17',           gos: '可 4:26-34'  },
      { week:  6, label: '第六週（主日）',   ot: '撒上 17:57-18:5, 10-16',  ps: '詩 9:9-20',             ep: '林後 6:1-13',           gos: '可 4:35-41'  },
      { week:  7, label: '第七週（主日）',   ot: '撒下 1:1, 17-27',         ps: '詩 130',                ep: '林後 8:7-15',           gos: '可 5:21-43'  },
      { week:  8, label: '第八週（主日）',   ot: '撒下 5:1-5, 9-10',        ps: '詩 48',                 ep: '林後 12:2-10',          gos: '可 6:1-13'   },
      { week:  9, label: '第九週（主日）',   ot: '撒下 6:1-5, 12b-19',      ps: '詩 24',                 ep: '弗 1:3-14',             gos: '可 6:14-29'  },
      { week: 10, label: '第十週（主日）',   ot: '撒下 7:1-14',             ps: '詩 89:20-37',           ep: '弗 2:11-22',            gos: '可 6:30-34, 53-56' },
      { week: 11, label: '第十一週（主日）', ot: '撒下 11:1-15',            ps: '詩 14',                 ep: '弗 3:14-21',            gos: '約 6:1-21'   },
      { week: 12, label: '第十二週（主日）', ot: '撒下 11:26-12:13',        ps: '詩 51:1-12',            ep: '弗 4:1-16',             gos: '約 6:24-35'  },
      { week: 13, label: '第十三週（主日）', ot: '撒下 18:5-9, 31-33',      ps: '詩 130',                ep: '弗 4:25-5:2',           gos: '約 6:35, 41-51' },
      { week: 14, label: '第十四週（主日）', ot: '王上 2:10-12; 3:3-14',    ps: '詩 111',                ep: '弗 5:15-20',            gos: '約 6:51-58'  },
      { week: 15, label: '第十五週（主日）', ot: '王上 8:22-30',            ps: '詩 84',                 ep: '弗 6:10-20',            gos: '約 6:56-69'  },
      { week: 16, label: '第十六週（主日）', ot: '申 4:1-2, 6-9',           ps: '詩 15',                 ep: '雅 1:17-27',            gos: '可 7:1-8, 14-15, 21-23' },
      { week: 17, label: '第十七週（主日）', ot: '箴 22:1-2, 8-9, 22-23',   ps: '詩 125',                ep: '雅 2:1-17',             gos: '可 7:24-37'  },
      { week: 18, label: '第十八週（主日）', ot: '箴 1:20-33',              ps: '詩 19',                 ep: '雅 3:1-12',             gos: '可 8:27-38'  },
      { week: 19, label: '第十九週（主日）', ot: '箴 31:10-31',             ps: '詩 1',                  ep: '雅 3:13-4:3, 7-8',      gos: '可 9:30-37'  },
      { week: 20, label: '第二十週（主日）', ot: '民 11:4-6, 10-16, 24-29', ps: '詩 19:7-14',            ep: '雅 5:13-20',            gos: '可 9:38-50'  },
      { week: 21, label: '第二十一週（主日）', ot: '伯 1:1; 2:1-10',        ps: '詩 26',                 ep: '來 1:1-4; 2:5-12',      gos: '可 10:2-16'  },
      { week: 22, label: '第二十二週（主日）', ot: '伯 23:1-9, 16-17',      ps: '詩 22:1-15',            ep: '來 4:12-16',            gos: '可 10:17-31' },
      { week: 23, label: '第二十三週（主日）', ot: '伯 38:1-7',             ps: '詩 104:1-9, 24',        ep: '來 5:1-10',             gos: '可 10:35-45' },
      { week: 24, label: '第二十四週（主日）', ot: '伯 42:1-6, 10-17',      ps: '詩 34:1-8',             ep: '來 7:23-28',            gos: '可 10:46-52' },
      { week: 25, label: '第二十五週（主日）', ot: '申 6:1-9',              ps: '詩 119:1-8',            ep: '來 9:11-14',            gos: '可 12:28-34' },
      { week: 26, label: '第二十六週（主日）', ot: '得 3:1-5; 4:13-17',     ps: '詩 127',                ep: '來 9:24-28',            gos: '可 12:38-44' },
      { week: 27, label: '第二十七週（主日）', ot: '但 12:1-3',             ps: '詩 16',                 ep: '來 10:11-14, 19-25',    gos: '可 13:1-8'   },
      { week: 28, label: '基督君王主日',     ot: '但 7:9-10, 13-14',        ps: '詩 93',                 ep: '啟 1:4b-8',             gos: '約 18:33-37' },
    ],
  },
  C: {
    advent: [
      { week: 1, label: '第一週（主日）', ot: '耶 33:14-16',         ps: '詩 25:1-10',            ep: '帖前 3:9-13',      gos: '路 21:25-36' },
      { week: 2, label: '第二週（主日）', ot: '瑪 3:1-4',            ps: '路 1:68-79',            ep: '腓 1:3-11',        gos: '路 3:1-6'    },
      { week: 3, label: '第三週（主日）', ot: '番 3:14-20',          ps: '賽 12:2-6',             ep: '腓 4:4-7',         gos: '路 3:7-18'   },
      { week: 4, label: '第四週（主日）', ot: '彌 5:2-5',            ps: '詩 80:1-7',             ep: '來 10:5-10',       gos: '路 1:39-55'  },
    ],
    christmas: [
      { week: 1, label: '第一週（主日）', ot: '耶 31:7-14',         ps: '詩 147:12-20',          ep: '弗 1:3-14',        gos: '約 1:1-18'   },
      { week: 2, label: '第二週（主日）', ot: '賽 43:1-7',          ps: '詩 29',                 ep: '徒 8:14-17',       gos: '路 3:15-17, 21-22' },
    ],
    epiphany: [
      { week: 1, label: '第一週（主日）', ot: '賽 62:1-5',           ps: '詩 36:5-10',            ep: '林前 12:1-11',     gos: '約 2:1-11'   },
      { week: 2, label: '第二週（主日）', ot: '尼 8:1-3, 5-6, 8-10', ps: '詩 19',                ep: '林前 12:12-31',    gos: '路 4:14-21'  },
      { week: 3, label: '第三週（主日）', ot: '耶 1:4-10',           ps: '詩 71:1-6',             ep: '林前 13:1-13',     gos: '路 4:21-30'  },
      { week: 4, label: '第四週（主日）', ot: '賽 6:1-8',            ps: '詩 138',                ep: '林前 15:1-11',     gos: '路 5:1-11'   },
      { week: 5, label: '第五週（主日）', ot: '耶 17:5-10',          ps: '詩 1',                  ep: '林前 15:12-20',    gos: '路 6:17-26'  },
      { week: 6, label: '第六週（主日）', ot: '創 45:3-11, 15',      ps: '詩 37:1-11, 39-40',     ep: '林前 15:35-38, 42-50', gos: '路 6:27-38' },
      { week: 7, label: '第七週（主日）', ot: '出 34:29-35',         ps: '詩 99',                 ep: '林後 3:12-4:2',    gos: '路 9:28-36'  },
      { week: 8, label: '第八週（主日）', ot: '申 26:1-11',          ps: '詩 91:1-2, 9-16',       ep: '羅 10:8-13',       gos: '路 4:1-13'   },
    ],
    lent: [
      { week: 1, label: '第一週（主日）', ot: '創 15:1-12, 17-18',   ps: '詩 27',                 ep: '腓 3:17-4:1',      gos: '路 13:31-35' },
      { week: 2, label: '第二週（主日）', ot: '賽 55:1-9',           ps: '詩 63:1-8',             ep: '林前 10:1-13',     gos: '路 13:1-9'   },
      { week: 3, label: '第三週（主日）', ot: '書 5:9-12',           ps: '詩 32',                 ep: '林後 5:16-21',     gos: '路 15:1-3, 11b-32' },
      { week: 4, label: '第四週（主日）', ot: '賽 43:16-21',         ps: '詩 126',                ep: '腓 3:4b-14',       gos: '約 12:1-8'   },
      { week: 5, label: '第五週（主日）', ot: '賽 50:4-9',           ps: '詩 118:1-2, 19-29',     ep: '腓 2:5-11',        gos: '路 19:28-40' },
      { week: 6, label: '第六週（主日）', ot: '徒 10:34-43',         ps: '詩 118:1-2, 14-24',     ep: '林前 15:19-26',    gos: '路 24:1-12'  },
    ],
    easter: [
      { week: 1, label: '第一週（主日）', ot: '徒 5:27-32',          ps: '詩 118:14-29',          ep: '啟 1:4-8',         gos: '約 20:19-31' },
      { week: 2, label: '第二週（主日）', ot: '徒 9:1-6',            ps: '詩 30',                 ep: '啟 5:11-14',       gos: '約 21:1-19'  },
      { week: 3, label: '第三週（主日）', ot: '徒 9:36-43',          ps: '詩 23',                 ep: '啟 7:9-17',        gos: '約 10:22-30' },
      { week: 4, label: '第四週（主日）', ot: '徒 11:1-18',          ps: '詩 148',                ep: '啟 21:1-6',        gos: '約 13:31-35' },
      { week: 5, label: '第五週（主日）', ot: '徒 16:9-15',          ps: '詩 67',                 ep: '啟 21:10, 22-22:5',gos: '約 14:23-29' },
      { week: 6, label: '第六週（主日）', ot: '徒 1:1-11',           ps: '詩 47',                 ep: '弗 1:15-23',       gos: '路 24:44-53' },
      { week: 7, label: '第七週（主日）', ot: '徒 16:16-34',         ps: '詩 97',                 ep: '啟 22:12-14, 16-17, 20-21', gos: '約 17:20-26' },
    ],
    pentecost: [
      { week:  1, label: '聖靈降臨主日',     ot: '徒 2:1-21',               ps: '詩 104:24-34, 35b',     ep: '羅 8:14-17',            gos: '約 14:8-17, 25-27' },
      { week:  2, label: '三一主日',         ot: '箴 8:1-4, 22-31',         ps: '詩 8',                  ep: '羅 5:1-5',              gos: '約 16:12-15' },
      { week:  3, label: '第三週（主日）',   ot: '王上 19:1-4, 8-15',       ps: '詩 42',                 ep: '加 3:23-29',            gos: '路 8:26-39'  },
      { week:  4, label: '第四週（主日）',   ot: '王下 2:1-2, 6-14',        ps: '詩 77:1-2, 11-20',      ep: '加 5:1, 13-25',         gos: '路 9:51-62'  },
      { week:  5, label: '第五週（主日）',   ot: '王下 5:1-14',             ps: '詩 30',                 ep: '加 6:1-16',             gos: '路 10:1-11, 16-20' },
      { week:  6, label: '第六週（主日）',   ot: '申 30:9-14',              ps: '詩 25:1-10',            ep: '西 1:1-14',             gos: '路 10:25-37' },
      { week:  7, label: '第七週（主日）',   ot: '創 18:1-10',              ps: '詩 15',                 ep: '西 1:15-28',            gos: '路 10:38-42' },
      { week:  8, label: '第八週（主日）',   ot: '創 18:20-32',             ps: '詩 138',                ep: '西 2:6-15',             gos: '路 11:1-13'  },
      { week:  9, label: '第九週（主日）',   ot: '傳 1:2; 2:18-23',         ps: '詩 49:1-12',            ep: '西 3:1-11',             gos: '路 12:13-21' },
      { week: 10, label: '第十週（主日）',   ot: '創 15:1-6',               ps: '詩 33:12-22',           ep: '來 11:1-3, 8-16',       gos: '路 12:32-40' },
      { week: 11, label: '第十一週（主日）', ot: '耶 23:23-29',             ps: '詩 82',                 ep: '來 11:29-12:2',         gos: '路 12:49-56' },
      { week: 12, label: '第十二週（主日）', ot: '賽 58:9b-14',             ps: '詩 103:1-8',            ep: '來 12:18-29',           gos: '路 13:10-17' },
      { week: 13, label: '第十三週（主日）', ot: '箴 25:6-7',               ps: '詩 112',                ep: '來 13:1-8, 15-16',      gos: '路 14:1, 7-14' },
      { week: 14, label: '第十四週（主日）', ot: '申 30:15-20',             ps: '詩 1',                  ep: '腓 1:21-30',            gos: '路 14:25-33' },
      { week: 15, label: '第十五週（主日）', ot: '出 32:7-14',              ps: '詩 51:1-10',            ep: '提前 1:12-17',          gos: '路 15:1-10'  },
      { week: 16, label: '第十六週（主日）', ot: '摩 8:4-7',                ps: '詩 113',                ep: '提前 2:1-7',            gos: '路 16:1-13'  },
      { week: 17, label: '第十七週（主日）', ot: '摩 6:1, 4-7',             ps: '詩 146',                ep: '提前 6:6-19',           gos: '路 16:19-31' },
      { week: 18, label: '第十八週（主日）', ot: '哈 1:1-4; 2:1-4',         ps: '詩 37:1-9',             ep: '提後 1:1-14',           gos: '路 17:5-10'  },
      { week: 19, label: '第十九週（主日）', ot: '王下 5:1-3, 7-15',        ps: '詩 111',                ep: '提後 2:8-15',           gos: '路 17:11-19' },
      { week: 20, label: '第二十週（主日）', ot: '創 32:22-31',             ps: '詩 121',                ep: '提後 3:14-4:5',         gos: '路 18:1-8'   },
      { week: 21, label: '第二十一週（主日）', ot: '耶 14:7-10, 19-22',     ps: '詩 84:1-7',             ep: '提後 4:6-8, 16-18',     gos: '路 18:9-14'  },
      { week: 22, label: '第二十二週（主日）', ot: '賽 1:10-18',            ps: '詩 32:1-7',             ep: '帖後 1:1-4, 11-12',     gos: '路 19:1-10'  },
      { week: 23, label: '第二十三週（主日）', ot: '伯 19:23-27',           ps: '詩 17:1-9',             ep: '帖後 2:1-5, 13-17',     gos: '路 20:27-38' },
      { week: 24, label: '第二十四週（主日）', ot: '賽 65:17-25',           ps: '詩 98',                 ep: '帖後 3:6-13',           gos: '路 21:5-19'  },
      { week: 25, label: '基督君王主日',     ot: '耶 23:1-6',               ps: '詩 46',                 ep: '西 1:11-20',            gos: '路 23:33-43' },
    ],
  },
}

// 依所選年度過濾：optional 的週次（如某年聖誕期只有一週）不顯示
const lectionaryTable = computed(() => {
  const allRows = RCL[yearParam]?.[season] ?? []
  const yearSlots = getChurchYearSundays(selectedChurchYear.value)
  return allRows.filter(row => {
    const slot = yearSlots.find(s => s.season === season && s.week === row.week)
    return !slot?.optional
  })
})

const lecPage = ref(Math.max(0, Math.floor((week - 1) / 4)))
const lecPageCount = computed(() => Math.ceil(lectionaryTable.value.length / 4))
const pagedLectionaryTable = computed(() => {
  const page = Math.min(lecPage.value, Math.max(0, lecPageCount.value - 1))
  return lectionaryTable.value.slice(page * 4, page * 4 + 4)
})

const yearLabel = YEAR_LABELS[yearParam] || yearParam
const seasonColor = SEASON_COLORS[season] || SEASON_COLORS.pentecost

// ── Year selector（無限滑動，純算術）──────────────────────────
const cycleTarget = (CYCLE_OFFSET[yearParam] ?? 0)

// 找最接近今天但未超過的同週期年份
const todayChurchYear = getCurrentChurchYear()
const defaultYear = (() => {
  // 同週期：(y - 2022) % 3 === cycleTarget（mod 3 修正負數）
  const rem = ((todayChurchYear - 2022) % 3 + 3) % 3
  return rem === cycleTarget ? todayChurchYear : todayChurchYear - ((rem - cycleTarget + 3) % 3)
})()

// 中心年份 ref，左右拖曳時 ±3
const centerYear = ref(defaultYear)
// 5 顆 pill：center-6, center-3, center, center+3, center+6
const nearbyYears = computed(() => [-6, -3, 0, 3, 6].map(d => centerYear.value + d))

const selectedChurchYear = ref(defaultYear)

// 拖曳
const dragStartX = ref(null)
function onDragStart(e) {
  dragStartX.value = e.touches ? e.touches[0].clientX : e.clientX
}
function onDragEnd(e) {
  if (dragStartX.value === null) return
  const endX = e.changedTouches ? e.changedTouches[0].clientX : e.clientX
  const delta = dragStartX.value - endX
  if (delta > 40) centerYear.value += 3
  else if (delta < -40) centerYear.value -= 3
  dragStartX.value = null
}
function onDragCancel() { dragStartX.value = null }

// 滑鼠滾輪
function onWheel(e) {
  e.preventDefault()
  if (e.deltaX > 20 || e.deltaY > 20) centerYear.value += 3
  else if (e.deltaX < -20 || e.deltaY < -20) centerYear.value -= 3
}

// 鍵盤左右方向鍵
function onKeydown(e) {
  if (e.key === 'ArrowRight') { e.preventDefault(); centerYear.value += 3 }
  else if (e.key === 'ArrowLeft') { e.preventDefault(); centerYear.value -= 3 }
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))

// 單次計算，供 slot、weekExistsInYear、dateRangeLabel 共用
const _yearSlotData = computed(() => {
  const slots = getChurchYearSundays(selectedChurchYear.value)
  const idx   = slots.findIndex(s => s.season === season && s.week === week)
  return { slots, idx, slot: idx >= 0 ? slots[idx] : null }
})

const selectedYearSlot  = computed(() => _yearSlotData.value.slot)
const weekExistsInYear  = computed(() => {
  const s = _yearSlotData.value.slot
  return s ? !s.optional : true
})

const dateRangeLabel = computed(() => {
  const { slots, idx, slot: s } = _yearSlotData.value
  if (!s || !s.sunday) return ''
  const nextSun = slots.slice(idx + 1).find(x => x.sunday)?.sunday
  const end = nextSun
    ? new Date(nextSun.getTime() - 86400000)
    : new Date(s.sunday.getTime() + 6 * 86400000)
  const sy = s.sunday.getFullYear(), sm = s.sunday.getMonth() + 1, sd = s.sunday.getDate()
  const em = end.getMonth() + 1, ed = end.getDate()
  return `${sy}年${sm}月${sd}日 – ${em}月${ed}日`
})

// ── Supabase ──────────────────────────────────────────────────
const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_KEY
)

const { data: weekData, pending } = await useAsyncData(
  `pong-lec-week-${yearParam}-${season}-${week}`,
  async () => {
    const { data, error } = await supabase
      .from('pong_lectionary_weeks')
      .select('*, pong_lectionary_days(*)')
      .eq('lectionary_year', yearParam)
      .eq('season', season)
      .eq('week_num', week)
      .eq('is_published', true)
      .single()
    if (error) return null
    return data
  }
)

const days = computed(() =>
  (weekData.value?.pong_lectionary_days || []).slice().sort((a, b) => a.day_of_week - b.day_of_week)
)
const activeDay = ref(0)
const currentDay = computed(() =>
  days.value.find(d => d.day_of_week === activeDay.value) || days.value[0] || null
)
const openReadings = ref({})
function toggleReading(i) { openReadings.value[i] = !openReadings.value[i] }
watch(activeDay, () => { openReadings.value = { 0: true } }, { immediate: true })

// ── Appendices split ──────────────────────────────────────────
const liturgyAppendices = computed(() =>
  (weekData.value?.appendices || []).map((a, i) => ({ ...a, _idx: i })).filter(a => !a.title?.includes('討論'))
)
const discussionAppendices = computed(() =>
  (weekData.value?.appendices || []).map((a, i) => ({ ...a, _idx: i })).filter(a => a.title?.includes('討論'))
)

// ── Day date map（跟著 selectedChurchYear 更新）─────────────────
const dayDateMap = computed(() => {
  const slots = getChurchYearSundays(selectedChurchYear.value)
  const idx = slots.findIndex(s => s.season === season && s.week === week)
  if (idx < 0 || !slots[idx]?.sunday) return {}
  const sunday = slots[idx].sunday
  const map = {}
  for (let d = 0; d <= 6; d++) {
    const date = new Date(sunday.getTime() + d * 86400000)
    map[d] = `${date.getMonth() + 1}/${String(date.getDate()).padStart(2, '0')}`
  }
  return map
})

// ── Advent Week 4：12/24（含）之後的日子進入聖誕期，不可點擊 ──
const lockedDays = computed(() => {
  if (season !== 'advent' || week !== 4) return new Set()
  const locked = new Set()
  const slots = getChurchYearSundays(selectedChurchYear.value)
  const idx = slots.findIndex(s => s.season === 'advent' && s.week === 4)
  if (idx < 0 || !slots[idx]?.sunday) return locked
  const sunday = slots[idx].sunday
  for (let d = 0; d <= 6; d++) {
    const date = new Date(sunday.getTime() + d * 86400000)
    if (date.getMonth() === 11 && date.getDate() >= 25) locked.add(d)
  }
  return locked
})

// 換年份時若目前選中的日子被鎖，退回最後一個未鎖的日子
watch(lockedDays, (locked) => {
  if (locked.has(activeDay.value)) {
    let fallback = activeDay.value - 1
    while (fallback >= 0 && locked.has(fallback)) fallback--
    activeDay.value = Math.max(0, fallback)
  }
})

// ── Title ─────────────────────────────────────────────────────
const titleMain = computed(() => {
  const t = weekData.value?.title || ''
  const idx = t.indexOf('（')
  return idx > 0 ? t.substring(0, idx) : (t || `${seasonColor.name}第${week}週`)
})
const titleTheme = computed(() => {
  const t = weekData.value?.title || ''
  const idx = t.indexOf('（')
  return idx >= 0 ? t.substring(idx) : ''
})
const essayTitleHtml = computed(() =>
  (weekData.value?.theme_essay_title || '').replace(/\n/g, '')
)

// ── Rendering helpers ─────────────────────────────────────────
function isHtml(str) {
  return str && str.trimStart().startsWith('<')
}

// Scripture: merge PDF-wrapped continuation lines into their verse
function renderScripture(text) {
  if (!text) return ''
  if (isHtml(text)) return text
  const verses = []
  for (const line of text.split('\n')) {
    const t = line.trim()
    if (!t) continue
    if (/^\d+:\d+\s/.test(t) || verses.length === 0) {
      verses.push(t)
    } else {
      verses[verses.length - 1] += t
    }
  }
  return verses.map(v => `<p class="wk-verse">${v}</p>`).join('')
}

// Single-block text: collapse PDF-wrapped single newlines, keep \n\n as paragraph break
function renderPara(text) {
  if (!text) return ''
  if (isHtml(text)) return text
  return text.split('\n\n').map(p => `<p>${p.replace(/\n/g, '')}</p>`).join('')
}

// Intro letter renderer: splits into greeting / body / signature three sections.
// Handles all known signature formats: 主內末龐君華、陳繼賢弟兄、工作團隊、於20XX日期行，
// including the case where the org name is embedded at the end of the last body paragraph.
function renderBody(text) {
  if (!text) return ''
  if (isHtml(text)) return text

  const SIG_END_RE   = /^於\s*20\d{2}/                         // date line starting sig
  const SIG_PARA_RE  = /主內|敬上|謹識|奉上|陳繼賢|工作團隊/   // para entirely is a sig block
  const SIG_TAIL_RE  = /([\s\S]+[。！？])([^。！？\n]{2,30})$/ // body text ending with sig name
  const SIG_NAME_RE  = /工作團隊|陳繼賢|龐君華|謹識/           // recognisable sig names in tail

  // Normalise to \n\n-separated paragraphs
  const paras = text.trim().split('\n\n').map(p => p.trim()).filter(Boolean)
  if (!paras.length) return ''

  // ── Locate signature block (scan up to last 4 paragraphs) ──────────────
  let sigStartIdx = paras.length
  for (let i = paras.length - 1; i >= Math.max(0, paras.length - 4); i--) {
    const lines = paras[i].split('\n').filter(l => l.trim())
    // A line counts as "sig-like" only if it's short (≤40 chars) AND matches sig markers,
    // or it's a date line. This prevents long body paragraphs ending in 工作團隊 from being
    // mis-classified as signature blocks.
    const allSig = lines.every(l => SIG_END_RE.test(l) || (l.trim().length <= 40 && SIG_PARA_RE.test(l)))
    if (allSig || SIG_END_RE.test(lines[0] || '')) {
      sigStartIdx = i
    } else {
      break
    }
  }

  // ── Handle sig name embedded at end of last body paragraph ─────────────
  // e.g. "...上主與我們同在。「每日三讀三禱」工作團隊" + next para = "於 2026 年..."
  let extractedSigName = ''
  if (sigStartIdx < paras.length && sigStartIdx >= 1) {
    const prevIdx = sigStartIdx - 1
    if (prevIdx >= 1) {  // never strip the greeting
      const m = SIG_TAIL_RE.exec(paras[prevIdx])
      if (m && SIG_NAME_RE.test(m[2])) {
        paras[prevIdx] = m[1].trimEnd()
        extractedSigName = m[2].trim()
      }
    }
  }

  // If still no sig found, try: does the last para end with a sig name?
  if (sigStartIdx === paras.length && paras.length >= 2) {
    const m = SIG_TAIL_RE.exec(paras[paras.length - 1])
    if (m && SIG_NAME_RE.test(m[2])) {
      paras[paras.length - 1] = m[1].trimEnd()
      extractedSigName = m[2].trim()
      sigStartIdx = paras.length  // extractedSigName will be prepended to sigParas below
    }
  }

  // ── Assemble three sections ─────────────────────────────────────────────
  const greeting  = paras[0]
  const bodyParas = paras.slice(1, sigStartIdx)
  let   sigParas  = paras.slice(sigStartIdx)
  if (extractedSigName) sigParas = [extractedSigName, ...sigParas]

  const greetHtml   = greeting
    ? `<p class="wk-greeting">${greeting.replace(/\n/g, '')}</p>` : ''

  const contentHtml = bodyParas
    .map(p => `<p>${p.replace(/\n/g, '')}</p>`).join('')

  const sigHtml = sigParas.length
    ? `<p class="wk-signature">${sigParas.map(p => p.replace(/\n/g, '<br>')).join('<br>')}</p>` : ''

  return greetHtml + contentHtml + sigHtml
}

// Key verse: merge PDF-wrapped continuation lines, keep verse-starting lines separate
function renderKeyVerse(text) {
  if (!text) return ''
  if (isHtml(text)) return text
  const verses = []
  for (const line of text.split('\n')) {
    const t = line.trim()
    if (!t) continue
    if (/^\d+:\d+\s/.test(t) || verses.length === 0) {
      verses.push(t)
    } else {
      verses[verses.length - 1] += t
    }
  }
  return verses.join('<br>')
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500&family=Noto+Serif+TC:wght@400;500;600&display=swap');

/* ── Base ─────────────────────────────────────────────────── */
.wk-page { background-color: #F9F8F6; min-height: 100vh; font-family: 'Noto Sans TC', sans-serif; color: #2C2C2C; }

/* ── Topbar ───────────────────────────────────────────────── */
.wk-topbar { padding: 20px 48px; border-bottom: 1px solid #DDD8CF; }
.wk-back { font-size: 0.8rem; color: #8A8278; text-decoration: none; letter-spacing: 0.06em; transition: color 0.2s; }
.wk-back:hover { color: #3A3025; }

/* ── Header ───────────────────────────────────────────────── */
.wk-header { padding: 48px 40px 40px; text-align: center; }
.wk-header-inner { max-width: 720px; margin: 0 auto; }
.wk-eyebrow { font-size: 0.72rem; font-weight: 300; color: rgba(255,255,255,0.7); letter-spacing: 0.2em; text-transform: uppercase; margin: 0 0 12px; }
.wk-title-main { font-family: 'Noto Serif TC', serif; font-size: 1.8rem; font-weight: 500; color: #fff; letter-spacing: 0.12em; margin: 0 0 6px; }
.wk-title-theme { font-family: 'Noto Serif TC', serif; font-size: 1.05rem; font-weight: 700; color: rgba(255,255,255,0.88); letter-spacing: 0.1em; margin: 0 0 22px; }

/* ── Year picker ──────────────────────────────────────────── */
.wk-year-picker { display: flex; gap: 6px; justify-content: center; margin-bottom: 8px; cursor: grab; user-select: none; }
.wk-year-picker:active { cursor: grabbing; }
.wk-year-btn {
  padding: 4px 14px;
  border: 1px solid rgba(255,255,255,0.35);
  border-radius: 20px;
  background: transparent;
  color: rgba(255,255,255,0.65);
  font-size: 0.75rem;
  font-family: 'Noto Sans TC', sans-serif;
  letter-spacing: 0.06em;
  cursor: pointer;
  transition: all 0.15s;
}
.wk-year-btn:hover { border-color: rgba(255,255,255,0.7); color: #fff; }
.wk-year-btn--active { background: rgba(255,255,255,0.18); border-color: rgba(255,255,255,0.8); color: #fff; font-weight: 500; }
.wk-date-range { font-size: 0.78rem; font-weight: 300; color: rgba(255,255,255,0.7); letter-spacing: 0.08em; margin: 0; }
.wk-no-week { opacity: 0.6; font-style: italic; }

/* ── Loading / Empty ──────────────────────────────────────── */
.wk-loading, .wk-empty { max-width: 720px; margin: 80px auto; text-align: center; font-size: 0.9rem; color: #A09280; letter-spacing: 0.06em; line-height: 2; }
.wk-empty-sub { font-size: 0.75rem; color: #C0B8A8; }
.wk-no-week-body { margin: 60px auto; }

/* ── Section label ────────────────────────────────────────── */
.wk-section-label { font-size: 0.68rem; font-weight: 300; color: #A09280; letter-spacing: 0.22em; text-transform: uppercase; margin: 0 0 20px; }

/* ── Intro letter ─────────────────────────────────────────── */
.wk-intro { border-top: 1px solid #DDD8CF; }
.wk-intro-inner { max-width: 720px; margin: 0 auto; padding: 2rem 40px; }
.wk-intro-body { font-family: 'Noto Serif TC', serif; font-size: 1rem; line-height: 2.1; color: #3A3025; }
.wk-intro-body :deep(p) { text-indent: 2em; margin-bottom: 0.9em; }
.wk-intro-body :deep(.wk-greeting) { text-indent: 0; margin-bottom: 1.6em; font-weight: 500; letter-spacing: 0.04em; }
.wk-intro-body :deep(.wk-signature) { text-indent: 0; text-align: right; margin-top: 2.2em; margin-bottom: 0; color: #5A5040; line-height: 2; font-size: 0.93rem; }
.wk-intro-body :deep(p:last-child) { margin-bottom: 0; }

/* ── Theme essay ──────────────────────────────────────────── */
/* ── Lectionary overview ──────────────────────────────────── */
.wk-lectionary { border-top: 1px solid #DDD8CF; }
.wk-lectionary-inner { max-width: 860px; margin: 0 auto; padding: 2rem 32px; }
.wk-lec-heading {
  font-family: 'Noto Serif TC', serif;
  font-size: 1.1rem;
  font-weight: 500;
  color: #5A5048;
  letter-spacing: 0.08em;
  text-align: center;
  margin: 0 0 8px;
}
.wk-lec-source {
  font-size: 0.78rem;
  color: #9A9080;
  letter-spacing: 0.04em;
  text-align: center;
  margin: 0 0 20px;
}
.wk-lec-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
  color: #3A3025;
  line-height: 1.6;
}
.wk-lec-table th {
  font-family: 'Noto Serif TC', serif;
  font-weight: 500;
  font-size: 0.75rem;
  color: #7A7268;
  letter-spacing: 0.06em;
  padding: 6px 10px;
  border-bottom: 2px solid #DDD8CF;
  text-align: left;
  white-space: nowrap;
}
.wk-lec-table td {
  padding: 8px 10px;
  border-bottom: 1px solid #EAE6DF;
  vertical-align: top;
}
.wk-lec-table tr:last-child td { border-bottom: none; }
.wk-lec-current td {
  background-color: rgba(180, 155, 100, 0.1);
  font-weight: 500;
  color: #2C2C2C;
}
.wk-lec-table td:first-child { white-space: nowrap; color: #7A7268; font-size: 0.78rem; }

.wk-lec-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.2rem;
  padding: 0.8rem 0 0.2rem;
}
.wk-lec-nav-btn {
  background: none;
  border: 1px solid #C8C0B0;
  border-radius: 4px;
  width: 2rem;
  height: 2rem;
  font-size: 1.2rem;
  line-height: 1;
  color: #6B6050;
  cursor: pointer;
  transition: background 0.15s;
}
.wk-lec-nav-btn:hover:not(:disabled) { background: #EDE8E0; }
.wk-lec-nav-btn:disabled { opacity: 0.3; cursor: default; }
.wk-lec-nav-label { font-size: 0.85rem; color: #5A5040; }
.wk-lec-nav-page { color: #9A9080; margin-left: 0.3em; }

.wk-essay { background-color: #F2EFE9; border-top: 1px solid #DDD8CF; }
.wk-essay-inner { max-width: 720px; margin: 0 auto; padding: 2rem 40px; }
.wk-essay-title { font-family: 'Noto Serif TC', serif; font-size: 1.15rem; font-weight: 500; color: #2C2C2C; letter-spacing: 0.06em; line-height: 1.8; margin: 0 0 24px; }
.wk-essay-body { font-size: 0.95rem; line-height: 2.1; color: #3A3025; }
.wk-essay-body :deep(p) { text-indent: 2em; margin-bottom: 1em; }
.wk-essay-body :deep(p:last-child) { margin-bottom: 0; }

/* ── Day section ──────────────────────────────────────────── */
.wk-days-section { padding: 0; border-top: 1px solid #DDD8CF; }
.wk-days-inner { max-width: 1000px; margin: 0 auto; padding: 2rem 24px; }
.wk-day-tabs { display: flex; gap: 0; margin-bottom: 32px; border-bottom: 1px solid #E8E4DC; flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; }
.wk-day-tabs::-webkit-scrollbar { display: none; }
.wk-day-date { font-size: 0.78em; opacity: 0.75; }
.wk-day-tab {
  flex: 1;
  padding: 10px 4px;
  font-size: 0.78rem;
  font-weight: 300;
  color: #A09280;
  letter-spacing: 0.04em;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
  margin-bottom: -1px;
  font-family: 'Noto Sans TC', sans-serif;
  white-space: nowrap;
  text-align: center;
}
.wk-day-tab:hover { color: #3A3025; }
.wk-day-tab--active { color: #3A3025; font-weight: 500; border-bottom-color: #3A3025; }
.wk-day-tab--locked, .wk-day-tab:disabled { opacity: 0.28; cursor: not-allowed; }
.wk-day-tab--locked:hover { color: #A09280; }

/* ── Reading accordion ────────────────────────────────────── */
.wk-reading { border: 1px solid #E8E4DC; border-radius: 4px; margin-bottom: 8px; overflow: hidden; }
.wk-reading-head {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  position: relative;
  background: #fff;
  border: none;
  cursor: pointer;
  text-align: left;
  font-family: 'Noto Sans TC', sans-serif;
  transition: background-color 0.15s;
}
.wk-reading-head:hover { background-color: #FAF8F4; }
.wk-reading-head--open { background-color: #F5F2EC; }
.wk-reading-num { width: 22px; height: 22px; border-radius: 50%; background: #E8E4DC; color: #7A7268; font-size: 0.65rem; font-weight: 500; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.wk-reading-head--open .wk-reading-num { background: #3A3025; color: #fff; }
.wk-reading-ref { display: flex; align-items: baseline; gap: 6px; flex: 1; min-width: 0; }
.wk-reading-book { font-family: 'Noto Serif TC', serif; font-size: 0.9rem; font-weight: 500; color: #3A3025; letter-spacing: 0.04em; }
.wk-reading-passage { font-size: 0.75rem; font-weight: 300; color: #9A9080; }
.wk-reading-title { position: absolute; left: 50%; transform: translateX(-50%); font-size: 0.78rem; font-weight: 700; color: #5A5040; white-space: nowrap; pointer-events: none; }
.wk-reading-chevron { font-size: 1.2rem; color: #C0B8A8; transition: transform 0.2s; line-height: 1; flex-shrink: 0; }
.wk-reading-chevron.open { transform: rotate(90deg); }
.wk-reading-body { border-top: 1px solid #E8E4DC; padding: 24px 24px 28px; background: #FDFCFA; }

/* ── 讀/禱 section layout ────────────────────────────────────── */
.wk-rp-section { display: flex; gap: 14px; }
.wk-rp-section--read { padding-bottom: 20px; border-bottom: 1px solid #EDEAD5; margin-bottom: 20px; }
.wk-rp-label {
  flex-shrink: 0;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  font-family: 'Noto Serif TC', serif;
  font-size: 0.82rem;
  font-weight: 600;
  color: #C4B89A;
  letter-spacing: 0.2em;
  text-align: center;
  align-self: flex-start;
}
.wk-rp-content { flex: 1; min-width: 0; }

/* Scripture */
.wk-scripture :deep(.wk-verse) { font-family: 'Noto Serif TC', serif; font-size: 0.9rem; line-height: 1.95; color: #3A3025; margin: 0 0 0.35em; }

/* Meditation */
.wk-meditation { margin-bottom: 20px; }
.wk-meditation :deep(p) { font-size: 0.88rem; line-height: 2; color: #4A4030; margin-bottom: 0.6em; }

/* Key verse */
.wk-key-verse { padding: 16px 20px; background: #F5F2EC; border-left: 3px solid #C4B89A; border-radius: 2px; }
.wk-key-verse-label { font-size: 0.65rem; font-weight: 500; color: #9A9080; letter-spacing: 0.18em; text-transform: uppercase; display: block; margin-bottom: 8px; }
.wk-key-verse-text { font-family: 'Noto Serif TC', serif; font-size: 0.95rem; color: #3A3025; line-height: 2; margin: 0; }

/* ── Edit mode fields ────────────────────────────────────────── */
.wk-edit-area {
  width: 100%; box-sizing: border-box;
  border: none; border-bottom: 1px dashed #C8C0B0;
  background: #FDFCF4;
  font-family: 'Noto Serif TC', serif; font-size: 0.9rem; line-height: 2; color: #3A3025;
  padding: 6px 0; resize: vertical; outline: none;
  min-height: 80px;
}
.wk-edit-area--tall { min-height: 140px; }
.wk-edit-area--sm { min-height: 48px; }
.wk-edit-area:focus { border-bottom-color: #8A7A5A; background: #FFFEF8; }
.wk-edit-field-label { font-size: 0.62rem; font-weight: 600; color: #B0A89A; letter-spacing: 0.2em; text-transform: uppercase; margin: 14px 0 4px; }

/* ── Appendices (liturgical) ──────────────────────────────── */
.wk-appendices { background: #F2EFE9; padding: 0; margin: 0; border-top: 1px solid #DDD8CF; }
.wk-appendices-inner { max-width: 720px; margin: 0 auto; padding: 2rem 40px; }
.wk-appendix { margin-bottom: 48px; }
.wk-appendix:last-child { margin-bottom: 0; }
.wk-appendix-title {
  font-family: 'Noto Serif TC', serif;
  font-size: 1rem;
  font-weight: 500;
  color: #3A3025;
  letter-spacing: 0.1em;
  margin: 0 0 16px;
  text-align: center;
}
.wk-appendix-body { font-size: 0.9rem; line-height: 1.95; color: #3A3025; }
.wk-appendix-body :deep(p) { margin-bottom: 0.8em; }
.wk-appendix-body :deep(p:last-child) { margin-bottom: 0; }
.wk-appendix-body :deep(*:first-child) { margin-top: 0; }
.wk-appendix-body :deep(table) { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 0.85rem; }
.wk-appendix-body :deep(th) { background: #EAE5DC; padding: 8px 12px; font-weight: 500; border: 1px solid #DDD8CF; text-align: left; font-family: 'Noto Sans TC', sans-serif; }
.wk-appendix-body :deep(td) { padding: 8px 12px; border: 1px solid #DDD8CF; vertical-align: top; line-height: 1.7; }
.wk-appendix-body :deep(tr:nth-child(even) td) { background: #F8F5F0; }
.wk-appendix-body :deep(.wk-lit-week) { font-family: 'Noto Serif TC', serif; font-size: 0.95rem; font-weight: 600; color: #4A3580; margin: 1.6em 0 0.5em; }
.wk-appendix-body :deep(.wk-lit-action) { font-style: italic; color: #7A7268; margin: 0.3em 0; }
.wk-appendix-body :deep(.wk-lit-note) { font-size: 0.82rem; color: #8A8278; margin-top: 1.2em; border-top: 1px solid #DDD8CF; padding-top: 0.8em; }

/* ── Discussion section ───────────────────────────────────── */
.wk-discussion { background: #EEF0EB; padding: 0; margin: 0; border-top: 1px solid #DDD8CF; }
.wk-discussion-inner { max-width: 720px; margin: 0 auto; padding: 2rem 40px; }
.wk-discussion .wk-appendix-body :deep(.wk-disc-author) { color: #8A8278; font-size: 0.82rem; margin-bottom: 1.2em; text-align: right; }
.wk-discussion .wk-appendix-body :deep(.wk-disc-subtitle) { font-family: 'Noto Serif TC', serif; font-size: 0.95rem; font-weight: 600; color: #3A3025; margin: 1.8em 0 0.6em; }
.wk-discussion .wk-appendix-body :deep(*:first-child) { margin-top: 0; }
.wk-discussion .wk-appendix-body :deep(*:last-child) { margin-bottom: 0; }

/* ── Team credits ─────────────────────────────────────────── */
.wk-credits { background: #F2EFE9; border-top: 1px solid #DDD8CF; }
.wk-credits-inner { max-width: 720px; margin: 0 auto; padding: 2rem 40px; text-align: center; }
.wk-credits-grid { display: grid; grid-template-columns: auto auto; gap: 6px 20px; width: fit-content; margin: 0 auto 24px; text-align: left; }
.wk-credit-row { display: contents; }
.wk-credit-role { font-size: 0.7rem; font-weight: 500; color: #9A9080; letter-spacing: 0.12em; padding-top: 2px; white-space: nowrap; }
.wk-credit-names { font-family: 'Noto Serif TC', serif; font-size: 0.85rem; color: #5A5040; letter-spacing: 0.04em; line-height: 1.8; }
.wk-credits-site-label { font-size: 0.65rem; font-weight: 500; color: #9A9080; letter-spacing: 0.18em; text-transform: uppercase; margin: 0 0 6px; }
.wk-credits-link {
  display: inline-block;
  font-size: 0.78rem;
  color: #7A7268;
  letter-spacing: 0.1em;
  text-decoration: none;
  border-bottom: 1px solid #C8C0B0;
  padding-bottom: 1px;
  transition: color 0.2s, border-color 0.2s;
}
.wk-credits-link:hover { color: #3A3025; border-color: #3A3025; }

/* ── Responsive ───────────────────────────────────────────── */
@media (max-width: 640px) {
  .wk-topbar { padding: 16px 20px; }
  .wk-header { padding: 36px 20px 32px; }
  .wk-title-main { font-size: 1.4rem; }
  .wk-intro-inner, .wk-essay-inner { padding: 2rem 20px; }
  .wk-appendices-inner, .wk-discussion-inner { padding: 2rem 20px; }
  .wk-lectionary-inner { padding: 2rem 16px; }
  .wk-days-inner { padding: 12px 12px; }
  .wk-credits-inner { padding: 2px 20px; }
  .wk-days-inner { padding: 0 12px; }
  .wk-day-tab { padding: 8px 2px; font-size: 0.65rem; letter-spacing: 0; }
  .wk-day-date { display: none; }
  .wk-lec-table { font-size: 0.72rem; }
  .wk-lec-table th, .wk-lec-table td { padding: 6px 6px; }
  .wk-credits-grid { gap: 4px 14px; }
}
</style>
