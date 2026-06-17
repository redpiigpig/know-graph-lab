<template>
  <div v-if="creed" class="flex flex-col bg-stone-50 min-h-dvh">
    <AppHeader :title="creed.nameZh" :back="{ to: '/creeds', label: '信條對照' }" container-class="max-w-[1400px]">
      <template #actions>
        <span v-if="creed.nameLat" class="text-xs italic text-stone-400 truncate hidden sm:inline max-w-[16rem]">{{ creed.nameLat }}</span>
        <span class="text-xs text-stone-400 whitespace-nowrap">{{ creed.year }}</span>
      </template>
    </AppHeader>

    <div class="flex-1 max-w-[1400px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <header class="mb-8 pb-6 border-b border-stone-200">
        <div class="flex items-baseline flex-wrap gap-2 mb-3">
          <span v-if="creed.councilNo" class="font-mono text-xs px-2 py-0.5 rounded bg-stone-900 text-white">第 {{ creed.councilNo }} 次大公會議</span>
          <span v-if="creed.councilDocCode" class="font-mono text-xs px-2 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-200">{{ creed.councilDocCode }}</span>
          <span class="text-[11px] text-stone-400">{{ CATEGORY_LABEL_ZH[creed.category] }}</span>
        </div>
        <h1 class="text-3xl font-bold text-stone-900 leading-tight tracking-tight">{{ creed.nameZh }}</h1>
        <div class="mt-1.5 text-base text-stone-600">{{ creed.nameEn }}</div>
        <div v-if="creed.nameLat" class="text-sm italic text-stone-500 mt-0.5">{{ creed.nameLat }}</div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2 mt-6 text-sm">
          <div v-if="creed.location" class="flex gap-2"><span class="text-stone-400 shrink-0">地點：</span><span class="text-stone-800">{{ creed.location }}</span></div>
          <div class="flex gap-2"><span class="text-stone-400 shrink-0">年份：</span><span class="text-stone-800">{{ creed.year }}</span></div>
          <div v-if="creed.authors?.length" class="md:col-span-2 flex gap-2"><span class="text-stone-400 shrink-0">主筆／簽署：</span><span class="text-stone-800">{{ creed.authors.join('、') }}</span></div>
          <div class="md:col-span-2 flex gap-2"><span class="text-stone-400 shrink-0">主議題：</span><span class="text-stone-800 leading-relaxed">{{ creed.topic }}</span></div>
        </div>

        <!-- Traditions -->
        <div class="mt-6">
          <div class="text-[11px] uppercase tracking-wider text-stone-400 mb-2">接受傳統</div>
          <div class="flex flex-wrap gap-1.5">
            <span
              v-for="t in creed.acceptedBy"
              :key="t"
              class="text-xs px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200"
            >{{ TRADITION_LABEL_ZH[t] }}</span>
          </div>
          <div v-if="creed.rejectedBy?.length" class="mt-2">
            <div class="text-[11px] uppercase tracking-wider text-stone-400 mb-2">不接受</div>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="t in creed.rejectedBy"
                :key="t"
                class="text-xs px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200"
              >{{ TRADITION_LABEL_ZH[t] }}</span>
            </div>
          </div>
        </div>
      </header>

      <!-- Summary — lead paragraph + 文件名《》斜體 -->
      <section v-if="creed.summaryZh" class="mb-10">
        <div class="flex items-baseline gap-2 mb-3">
          <span class="text-base">📌</span>
          <h2 class="text-sm font-semibold tracking-wide text-stone-700">摘要</h2>
        </div>
        <div class="bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden">
          <div class="border-l-[3px] border-amber-400 px-6 py-5 prose-summary">
            <p
              v-for="(part, i) in summaryParagraphs"
              :key="i"
              :class="i === 0 ? 'lead text-[1.02rem] text-stone-900 font-medium leading-loose' : 'text-[0.95rem] text-stone-700 leading-loose mt-3'"
              style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif"
              v-html="renderRichText(part)"
            ></p>
          </div>
        </div>
      </section>

      <!-- ─── 逐段對照（梵二 / 有 textKey 的長文件） ─── -->
      <section v-if="paragraphMode" class="mb-8">
        <div class="flex items-baseline gap-2 mb-3 flex-wrap">
          <span class="text-base">📜</span>
          <h2 class="text-sm font-semibold tracking-wide text-stone-700">逐段對照</h2>
          <span class="text-[11px] text-stone-400">每段 一 row × 中／英／拉 三欄並列（vatican.va 段號）</span>
          <span v-if="paragraphRows.length > 0" class="text-[11px] text-stone-500 ml-auto">共 {{ paragraphRows.length }} 段</span>
        </div>

        <!-- 版本選擇 bar -->
        <div class="grid gap-3 mb-3" :style="{ gridTemplateColumns: '3rem 1fr 1fr 1fr' }">
          <div class="text-[10px] text-stone-400 uppercase tracking-wider self-center text-center">#</div>
          <div class="bg-white border border-stone-200 rounded-md px-3 py-1.5 flex items-center gap-2">
            <span class="text-[10px] uppercase tracking-wide text-stone-500">中文</span>
            <select v-if="zhVersions.length > 1" v-model="zhPickIdx" class="flex-1 text-xs text-stone-800 bg-transparent border-none focus:outline-none cursor-pointer">
              <option v-for="(v, i) in zhVersions" :key="i" :value="i">{{ v.shortLabel }}</option>
            </select>
            <span v-else class="flex-1 text-xs text-stone-700">{{ zhVersions[0]?.shortLabel || '—' }}</span>
          </div>
          <div class="bg-white border border-stone-200 rounded-md px-3 py-1.5 flex items-center gap-2">
            <span class="text-[10px] uppercase tracking-wide text-sky-700">EN</span>
            <select v-if="enVersions.length > 1" v-model="enPickIdx" class="flex-1 text-xs text-stone-800 bg-transparent border-none focus:outline-none cursor-pointer">
              <option v-for="(v, i) in enVersions" :key="i" :value="i">{{ v.shortLabel }}</option>
            </select>
            <span v-else class="flex-1 text-xs text-stone-700">{{ enVersions[0]?.shortLabel || '—' }}</span>
          </div>
          <div class="bg-white border border-stone-200 rounded-md px-3 py-1.5 flex items-center gap-2">
            <span class="text-[10px] uppercase tracking-wide text-amber-700">原文</span>
            <select v-if="origVersions.length > 1" v-model="origPickIdx" class="flex-1 text-xs text-stone-800 bg-transparent border-none focus:outline-none cursor-pointer">
              <option v-for="(v, i) in origVersions" :key="i" :value="i">{{ v.shortLabel }}</option>
            </select>
            <span v-else class="flex-1 text-xs text-stone-700">{{ origVersions[0]?.shortLabel || '—' }}</span>
          </div>
        </div>

        <div v-if="paragraphsLoading" class="text-center text-stone-400 py-12 text-sm">載入段落中…</div>
        <div v-else-if="docRows.length === 0" class="text-center text-stone-400 py-12 text-sm">⚠ 無法解析段落</div>

        <div v-else class="space-y-1.5">
          <template v-for="(row, ri) in docRows" :key="ri">
            <!-- Section heading: spans full width -->
            <div
              v-if="row.kind === 'heading'"
              class="bg-gradient-to-r from-amber-50 via-stone-50 to-white border-y border-amber-200 px-4 py-3 mt-5 first:mt-0"
            >
              <div class="text-[11px] font-semibold uppercase tracking-widest text-amber-800 mb-1">section</div>
              <div class="grid gap-4" :style="{ gridTemplateColumns: '1fr 1fr 1fr' }">
                <div class="text-[0.92rem] font-semibold text-stone-900"
                     style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif">
                  <template v-if="row.byLang.zh">{{ row.byLang.zh }}</template>
                  <span v-else class="text-stone-300 italic text-xs">—</span>
                </div>
                <div class="text-[0.88rem] font-semibold text-stone-900 font-sans italic">
                  <template v-if="row.byLang.en">{{ row.byLang.en }}</template>
                  <span v-else class="text-stone-300 italic text-xs">—</span>
                </div>
                <div class="text-[0.9rem] font-semibold text-stone-900 italic">
                  <template v-if="row.byLang.orig">{{ row.byLang.orig }}</template>
                  <span v-else class="text-stone-300 italic text-xs">—</span>
                </div>
              </div>
            </div>

            <!-- Paragraph row -->
            <article
              v-else
              :id="`para-${row.num}`"
              class="bg-white border border-stone-200 rounded-md overflow-hidden"
            >
              <div class="grid gap-px bg-stone-100" :style="{ gridTemplateColumns: '3rem 1fr 1fr 1fr' }">
                <div class="bg-stone-50 px-2 py-3 text-xs font-mono font-bold text-stone-700 flex items-start justify-center">
                  {{ row.num }}
                </div>
                <div class="bg-white px-3 py-3 text-[0.92rem] leading-loose text-stone-800 whitespace-pre-wrap"
                     style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif">
                  <span v-if="row.byLang.zh" v-html="renderBody(row.byLang.zh, 'zh')"></span>
                  <span v-else class="text-stone-300 italic text-xs">—</span>
                </div>
                <div class="bg-white px-3 py-3 text-[0.875rem] leading-relaxed text-stone-800 font-sans whitespace-pre-wrap">
                  <span v-if="row.byLang.en" v-html="renderBody(row.byLang.en, 'en')"></span>
                  <span v-else class="text-stone-300 italic text-xs">—</span>
                </div>
                <div class="bg-white px-3 py-3 text-[0.92rem] leading-relaxed text-stone-800 whitespace-pre-wrap"
                     :class="origActiveClass">
                  <span v-if="row.byLang.orig" v-html="renderBody(row.byLang.orig, 'orig')"></span>
                  <span v-else class="text-stone-300 italic text-xs">—</span>
                </div>
              </div>
            </article>
          </template>
        </div>

        <!-- Footnotes section -->
        <div v-if="hasFootnotes" class="mt-8 border-t-2 border-stone-300 pt-6">
          <div class="text-xs uppercase tracking-widest text-stone-500 font-semibold mb-3">📎 註腳對照</div>
          <div class="grid gap-4" :style="{ gridTemplateColumns: '3rem 1fr 1fr 1fr' }">
            <div></div>
            <div class="text-[10px] uppercase tracking-wider text-stone-400">中文</div>
            <div class="text-[10px] uppercase tracking-wider text-sky-700">English</div>
            <div class="text-[10px] uppercase tracking-wider text-amber-700">原文</div>

            <template v-for="num in footnoteNumbers" :key="num">
              <div :id="`fn-anchor-${num}`" class="text-xs font-mono font-bold text-stone-600 self-start pt-1 text-center">[{{ num }}]</div>
              <div :id="`fn-zh-${num}`" class="text-[0.85rem] text-stone-700 leading-relaxed scroll-mt-16"
                   style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif">
                <span v-if="footnoteOf('zh', num)" v-html="renderBody(footnoteOf('zh', num), 'zh')"></span>
                <span v-else class="text-stone-300 italic text-xs">—</span>
              </div>
              <div :id="`fn-en-${num}`" class="text-[0.82rem] text-stone-700 leading-relaxed font-sans scroll-mt-16">
                <span v-if="footnoteOf('en', num)" v-html="renderBody(footnoteOf('en', num), 'en')"></span>
                <span v-else class="text-stone-300 italic text-xs">—</span>
              </div>
              <div :id="`fn-orig-${num}`" class="text-[0.85rem] text-stone-700 leading-relaxed italic scroll-mt-16">
                <span v-if="footnoteOf('orig', num)" v-html="renderBody(footnoteOf('orig', num), 'orig')"></span>
                <span v-else class="text-stone-300 italic text-xs">—</span>
              </div>
            </template>
          </div>
        </div>

        <!-- 來源 footer -->
        <div class="mt-4 grid gap-2 text-[11px] text-stone-500 leading-relaxed" :style="{ gridTemplateColumns: '3rem 1fr 1fr 1fr' }">
          <div></div>
          <div>
            <div v-if="zhActive?.source">📖 {{ zhActive.source }}</div>
            <div v-if="zhActive?.translator">✍ {{ zhActive.translator }}</div>
            <div v-if="zhActive?.placeholder" class="text-amber-700">⏳ 中文版本為 placeholder</div>
          </div>
          <div>
            <div v-if="enActive?.source">📖 {{ enActive.source }}</div>
          </div>
          <div>
            <div v-if="origActive?.source">📖 {{ origActive.source }}</div>
          </div>
        </div>
      </section>

      <!-- ─── 三欄並列（短信經 — 無 textKey） ─── -->
      <section v-else class="mb-8">
        <div class="flex items-baseline gap-2 mb-3">
          <span class="text-base">📜</span>
          <h2 class="text-sm font-semibold tracking-wide text-stone-700">三欄對照</h2>
          <span class="text-[11px] text-stone-400">中文 ／ 英文 ／ 原文 — 各欄獨立捲動</span>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <!-- 中文欄 -->
          <div class="bg-white rounded-xl border border-stone-200 shadow-sm flex flex-col overflow-hidden">
            <div class="flex items-center gap-2 px-4 py-2.5 border-b border-stone-100 bg-gradient-to-r from-stone-50 to-white">
              <span class="text-base">🀄</span>
              <span class="text-xs font-semibold text-stone-700 uppercase tracking-wider">中文</span>
              <select
                v-if="zhVersions.length > 1"
                v-model="zhPickIdx"
                class="ml-auto text-xs bg-stone-50 border border-stone-200 rounded px-1.5 py-0.5 focus:outline-none focus:border-stone-400"
              >
                <option v-for="(v, i) in zhVersions" :key="i" :value="i">{{ v.shortLabel }}</option>
              </select>
              <span v-else class="ml-auto text-[11px] text-stone-400">{{ zhVersions[0]?.shortLabel || '—' }}</span>
            </div>
            <div class="flex-1 overflow-y-auto px-5 py-4 max-h-[78vh]" :class="zhActive?.placeholder ? 'bg-amber-50/30' : ''">
              <pre v-if="zhActive"
                   class="whitespace-pre-wrap break-words text-[0.9rem] leading-loose text-stone-800"
                   style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif"
              >{{ zhActive.text }}</pre>
              <div v-else class="text-sm text-stone-400 italic">尚無中文版本</div>
              <div v-if="zhActive?.placeholder" class="mt-3 text-[11px] text-amber-700 bg-amber-100/60 px-2 py-1 rounded inline-block">⏳ 待補正文</div>
            </div>
            <div v-if="zhActive?.source || zhActive?.translator" class="px-4 py-2 border-t border-stone-100 text-[11px] text-stone-500 leading-relaxed">
              <div v-if="zhActive.source">📖 {{ zhActive.source }}</div>
              <div v-if="zhActive.translator">✍ {{ zhActive.translator }}</div>
            </div>
          </div>

          <!-- 英文欄 -->
          <div class="bg-white rounded-xl border border-stone-200 shadow-sm flex flex-col overflow-hidden">
            <div class="flex items-center gap-2 px-4 py-2.5 border-b border-stone-100 bg-gradient-to-r from-sky-50 to-white">
              <span class="text-base">🇬🇧</span>
              <span class="text-xs font-semibold text-sky-800 uppercase tracking-wider">English</span>
              <select
                v-if="enVersions.length > 1"
                v-model="enPickIdx"
                class="ml-auto text-xs bg-sky-50 border border-sky-200 rounded px-1.5 py-0.5 focus:outline-none focus:border-sky-400"
              >
                <option v-for="(v, i) in enVersions" :key="i" :value="i">{{ v.shortLabel }}</option>
              </select>
              <span v-else class="ml-auto text-[11px] text-stone-400">{{ enVersions[0]?.shortLabel || '—' }}</span>
            </div>
            <div class="flex-1 overflow-y-auto px-5 py-4 max-h-[78vh]" :class="enActive?.placeholder ? 'bg-amber-50/30' : ''">
              <pre v-if="enActive"
                   class="whitespace-pre-wrap break-words text-[0.875rem] leading-relaxed text-stone-800 font-sans"
              >{{ enActive.text }}</pre>
              <div v-else class="text-sm text-stone-400 italic">No English version</div>
              <div v-if="enActive?.placeholder" class="mt-3 text-[11px] text-amber-700 bg-amber-100/60 px-2 py-1 rounded inline-block">⏳ pending</div>
            </div>
            <div v-if="enActive?.source" class="px-4 py-2 border-t border-stone-100 text-[11px] text-stone-500 leading-relaxed">
              📖 {{ enActive.source }}
            </div>
          </div>

          <!-- 原文欄 -->
          <div class="bg-white rounded-xl border border-stone-200 shadow-sm flex flex-col overflow-hidden">
            <div class="flex items-center gap-2 px-4 py-2.5 border-b border-stone-100 bg-gradient-to-r from-amber-50 to-white">
              <span class="text-base">📜</span>
              <span class="text-xs font-semibold text-amber-800 uppercase tracking-wider">原文</span>
              <select
                v-if="origVersions.length > 1"
                v-model="origPickIdx"
                class="ml-auto text-xs bg-amber-50 border border-amber-200 rounded px-1.5 py-0.5 focus:outline-none focus:border-amber-400"
              >
                <option v-for="(v, i) in origVersions" :key="i" :value="i">{{ v.shortLabel }}</option>
              </select>
              <span v-else class="ml-auto text-[11px] text-stone-400">{{ origVersions[0]?.shortLabel || '—' }}</span>
            </div>
            <div class="flex-1 overflow-y-auto px-5 py-4 max-h-[78vh]" :class="origActive?.placeholder ? 'bg-amber-50/30' : ''">
              <pre v-if="origActive"
                   class="whitespace-pre-wrap break-words text-[0.9rem] leading-relaxed text-stone-800"
                   :class="origActiveClass"
              >{{ origActive.text }}</pre>
              <div v-else class="text-sm text-stone-400 italic">尚無原文版本</div>
              <div v-if="origActive?.placeholder" class="mt-3 text-[11px] text-amber-700 bg-amber-100/60 px-2 py-1 rounded inline-block">⏳ 待補</div>
            </div>
            <div v-if="origActive?.source" class="px-4 py-2 border-t border-stone-100 text-[11px] text-stone-500 leading-relaxed">
              📖 {{ origActive.source }}
            </div>
          </div>
        </div>
      </section>

      <!-- Notes — bullet items + 文件名《》斜體 -->
      <section v-if="creed.notes" class="mb-10">
        <div class="flex items-baseline gap-2 mb-3">
          <span class="text-base">📝</span>
          <h2 class="text-sm font-semibold tracking-wide text-stone-700">歷史 Notes</h2>
        </div>
        <div class="bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden">
          <div class="border-l-[3px] border-stone-400 px-6 py-5">
            <template v-for="(block, i) in notesBlocks" :key="i">
              <ul v-if="block.kind === 'list'" class="space-y-2 text-[0.95rem] text-stone-700 leading-relaxed"
                  style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif">
                <li v-for="(item, j) in block.items" :key="j" class="pl-5 relative">
                  <span class="absolute left-0 top-[0.55em] w-1.5 h-1.5 rounded-full bg-stone-400"></span>
                  <span v-html="renderListItem(item)"></span>
                </li>
              </ul>
              <p v-else class="text-[0.95rem] text-stone-700 leading-loose mt-3 first:mt-0"
                 style="font-family: 'Noto Serif TC', 'Source Han Serif TC', 'Songti TC', serif"
                 v-html="renderRichText(block.text)"></p>
            </template>
          </div>
        </div>
      </section>

      <!-- Related -->
      <section v-if="relatedCreeds.length > 0" class="mb-8">
        <div class="flex items-baseline gap-2 mb-3">
          <span class="text-base">🔗</span>
          <h2 class="text-sm font-semibold tracking-wide text-stone-700">相關信條</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <NuxtLink
            v-for="r in relatedCreeds"
            :key="r.slug"
            :to="`/creeds/${r.slug}`"
            class="block bg-white border border-stone-200 rounded-lg px-4 py-3 hover:border-stone-400 hover:shadow-md transition-all duration-150"
          >
            <div class="flex items-baseline gap-1.5 mb-0.5">
              <span v-if="r.councilDocCode" class="text-[10px] font-mono font-semibold text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-100">{{ r.councilDocCode }}</span>
              <span class="text-[10px] text-stone-400">{{ r.year }}</span>
            </div>
            <div class="font-semibold text-stone-900 text-sm">{{ r.nameZh }}</div>
            <div class="text-xs text-stone-500 mt-0.5 line-clamp-1">{{ r.nameEn }}</div>
          </NuxtLink>
        </div>
      </section>
    </div>
  </div>

  <div v-else class="min-h-dvh flex items-center justify-center text-stone-400">
    找不到此信條：{{ route.params.slug }}
    <NuxtLink to="/creeds" class="ml-3 text-blue-500 underline">回信條列表</NuxtLink>
  </div>
</template>

<script setup lang="ts">
import { findCreed, ALL_CREEDS, CATEGORY_LABEL_ZH, TRADITION_LABEL_ZH, type CreedLanguage, type CreedVersion } from '~/data/creeds'
import { loadCreedText, loadCreedParagraphs, loadCreedDoc } from '~/data/creeds/textLoader'
import { alignParagraphs, alignDocs, type ParagraphRow, type DocRow, type FootnoteDef } from '~/data/creeds/paragraphParser'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const creed = computed(() => findCreed(route.params.slug as string))

useHead(() => ({
  title: creed.value ? `${creed.value.nameZh} — 信條對照` : '找不到信條',
}))

// Bucket CreedVersion -> zh / en / orig
// - zh: lang.startsWith('zh-')
// - en: lang === 'en'
// - orig: others (grc, lat, lat-filioque, hye, cop, syr-east, syr-west, gez, arc, hbo, de, fr)
type Bucket = 'zh' | 'en' | 'orig'
function bucketOf(lang: CreedLanguage): Bucket {
  if (lang.startsWith('zh-')) return 'zh'
  if (lang === 'en') return 'en'
  return 'orig'
}

/** 短 label — 給 dropdown 用，避免太長 */
const SHORT_LABEL: Partial<Record<CreedLanguage, string>> = {
  'zh-Hant-Joint2019': '五宗派合一',
  'zh-Hant-Catholic': '思高（天主教）',
  'zh-Hant-Anglican': '聖公會',
  'zh-Hant-Lutheran': '信義會',
  'zh-Hant-Orthodox': '東正教',
  'zh-Hant-Reformed': '改革宗',
  'zh-Hant-Methodist': '衛理宗',
  'zh-Hant-Baptist': '浸信宗',
  'zh-Hant-Protestant': '新教通用',
  'zh-Hant': '繁體中文',
  en: 'English',
  lat: 'Latin',
  'lat-filioque': 'Latin (filioque)',
  grc: 'Greek',
  hye: 'Armenian',
  cop: 'Coptic',
  'cop-sa': 'Coptic (Sahidic)',
  'syr-east': 'Syriac (East)',
  'syr-west': 'Syriac (West)',
  gez: "Ge'ez",
  hbo: 'Hebrew',
  arc: 'Aramaic',
  de: 'German',
  fr: 'French',
}

interface EnrichedVersion extends CreedVersion {
  shortLabel: string
}

function enrich(v: CreedVersion): EnrichedVersion {
  return { ...v, shortLabel: SHORT_LABEL[v.lang] || v.label }
}

/** Lazy text cache — reactive, keyed by textKey. */
const lazyTextCache = reactive<Record<string, string | 'loading' | undefined>>({})

function ensureText(version: EnrichedVersion | undefined): EnrichedVersion | undefined {
  if (!version) return undefined
  if (!version.textKey) return version  // already inline
  const cached = lazyTextCache[version.textKey]
  if (cached === undefined) {
    lazyTextCache[version.textKey] = 'loading'
    loadCreedText(version.textKey)
      .then(text => { lazyTextCache[version.textKey!] = text })
      .catch(err => { lazyTextCache[version.textKey!] = `[載入失敗：${err.message}]` })
    return { ...version, text: '載入中...' }
  }
  if (cached === 'loading') return { ...version, text: '載入中...' }
  return { ...version, text: cached }
}

/** 中文版本排序：合一 → 聖公 → 信義 → 天主教 → 東正 → 改革 → 衛理 → 浸信 → 通用 */
const ZH_ORDER: CreedLanguage[] = [
  'zh-Hant-Joint2019',
  'zh-Hant-Anglican',
  'zh-Hant-Lutheran',
  'zh-Hant-Catholic',
  'zh-Hant-Orthodox',
  'zh-Hant-Reformed',
  'zh-Hant-Methodist',
  'zh-Hant-Baptist',
  'zh-Hant-Protestant',
  'zh-Hant',
]
function zhSubOrder(lang: CreedLanguage): number {
  const i = ZH_ORDER.indexOf(lang)
  return i === -1 ? 999 : i
}

/** 原文版本排序：lat → lat-filioque → grc → hbo → 其他 */
const ORIG_ORDER: CreedLanguage[] = [
  'lat',
  'lat-filioque',
  'grc',
  'hbo',
  'arc',
  'syr-east',
  'syr-west',
  'hye',
  'cop',
  'cop-sa',
  'gez',
  'de',
  'fr',
]
function origSubOrder(lang: CreedLanguage): number {
  const i = ORIG_ORDER.indexOf(lang)
  return i === -1 ? 999 : i
}

const zhVersions = computed<EnrichedVersion[]>(() => {
  if (!creed.value) return []
  return [...creed.value.versions]
    .filter(v => bucketOf(v.lang) === 'zh')
    .sort((a, b) => zhSubOrder(a.lang) - zhSubOrder(b.lang))
    .map(enrich)
})
const enVersions = computed<EnrichedVersion[]>(() => {
  if (!creed.value) return []
  return [...creed.value.versions].filter(v => bucketOf(v.lang) === 'en').map(enrich)
})
const origVersions = computed<EnrichedVersion[]>(() => {
  if (!creed.value) return []
  return [...creed.value.versions]
    .filter(v => bucketOf(v.lang) === 'orig')
    .sort((a, b) => origSubOrder(a.lang) - origSubOrder(b.lang))
    .map(enrich)
})

const zhPickIdx = ref(0)
const enPickIdx = ref(0)
const origPickIdx = ref(0)

// 切換 creed 時重置
watch(() => creed.value?.slug, () => {
  zhPickIdx.value = 0
  enPickIdx.value = 0
  origPickIdx.value = 0
})

const zhActive = computed(() => ensureText(zhVersions.value[zhPickIdx.value]))
const enActive = computed(() => ensureText(enVersions.value[enPickIdx.value]))
const origActive = computed(() => ensureText(origVersions.value[origPickIdx.value]))

const origActiveClass = computed(() => {
  if (!origActive.value) return ''
  const lang = origActive.value.lang
  if (lang === 'lat' || lang === 'lat-filioque') return 'italic'
  if (lang === 'grc' || lang === 'cop' || lang === 'cop-sa') return ''
  return ''
})

const relatedCreeds = computed(() => {
  if (!creed.value?.related) return []
  return creed.value.related
    .map(slug => ALL_CREEDS.find(c => c.slug === slug))
    .filter((c): c is NonNullable<typeof c> => !!c)
})

// ── Rich-text helpers for summary / notes rendering ───────────────
function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

/**
 * Plain text -> escaped HTML with italic styling for:
 *   - 《文件名》  -> italic serif
 *   - (英文/拉丁 phrase) -> italic when content looks Latin/Western (>= 2 ASCII letter words)
 */
function renderRichText(text: string): string {
  if (!text) return ''
  let html = escapeHtml(text)
  // 《...》 italic 文件名稱
  html = html.replace(/《([^》]+)》/g, '<em class="italic font-medium text-stone-900">《$1》</em>')
  // 括號內 ≥2 字 ASCII 詞語視為拉丁/英文，italic
  html = html.replace(/（([A-Za-z][A-Za-z\s\-/.,;:]+[A-Za-z])）/g, '<span class="italic text-stone-600">（$1）</span>')
  return html
}

/**
 * Render paragraph body with:
 *   - inline footnote ref [^N] or (N) -> clickable <sup><a href="#fn-{lang}-N">[N]</a></sup>
 *   - biblical book+chapter ref (Rom 11:17-24) -> <span class="scripture-ref">
 */
function renderBody(body: string, lang: 'zh' | 'en' | 'orig'): string {
  if (!body) return ''
  let html = escapeHtml(body)
  // [^N] markdown footnote ref
  html = html.replace(/\[\^(\d{1,4})\]/g, (_, n) =>
    `<sup class="ml-0.5"><a class="text-stone-500 hover:text-stone-900 underline decoration-dotted font-semibold" href="#fn-${lang}-${n}">${n}</a></sup>`,
  )
  // (N) plain numeric in parens — conservative: surrounded by space/punct/start
  html = html.replace(/(^|[\s,;.])\((\d{1,3})\)(?=[\s,;.]|$)/g, (_, pre, n) =>
    `${pre}<sup class="ml-0.5"><a class="text-stone-500 hover:text-stone-900 underline decoration-dotted font-semibold" href="#fn-${lang}-${n}">${n}</a></sup>`,
  )
  // Biblical book reference (BookName Ch:V) — italic kai-ti styling
  html = html.replace(
    /\((([1-3]\s)?[A-Z][a-z]+\.?\s+\d+[:.]\d+(?:[-,–]\d+)?(?:f?\.?)?(?:\s*;\s*(?:[1-3]\s)?[A-Z][a-z]+\.?\s+\d+[:.]\d+(?:[-,–]\d+)?(?:f?\.?)?)*)\)/g,
    '<span class="scripture-ref">($1)</span>',
  )
  // Chinese biblical ref ⟨書N:M⟩ or （羅 11:17-24）— very conservative pattern
  html = html.replace(
    /（([一二三]?[一-鿿]{1,3}\s*\d+[:：.]\d+(?:[-－―]\d+)?)）/g,
    '<span class="scripture-ref">（$1）</span>',
  )
  return html
}

/** List item: `label：rest` -> bold label + rest. Falls back to renderRichText. */
function renderListItem(text: string): string {
  const idx = text.indexOf('：')
  if (idx > 0 && idx < 30) {
    const label = text.slice(0, idx)
    const rest = text.slice(idx + 1)
    return `<strong class="font-semibold text-stone-900">${escapeHtml(label)}</strong>：${renderRichText(rest)}`
  }
  return renderRichText(text)
}

const summaryParagraphs = computed<string[]>(() => {
  const t = creed.value?.summaryZh
  if (!t) return []
  return t.split(/\n{2,}/).map(s => s.trim()).filter(Boolean)
})

interface NotesBlock {
  kind: 'p' | 'list'
  text?: string
  items?: string[]
}

const notesBlocks = computed<NotesBlock[]>(() => {
  const t = creed.value?.notes
  if (!t) return []
  const lines = t.split('\n')
  const out: NotesBlock[] = []
  let listBuf: string[] | null = null
  for (const raw of lines) {
    const line = raw.trim()
    if (!line) {
      if (listBuf) { out.push({ kind: 'list', items: listBuf }); listBuf = null }
      continue
    }
    if (line.startsWith('- ') || line.startsWith('* ')) {
      if (!listBuf) listBuf = []
      listBuf.push(line.slice(2).trim())
    } else {
      if (listBuf) { out.push({ kind: 'list', items: listBuf }); listBuf = null }
      out.push({ kind: 'p', text: line })
    }
  }
  if (listBuf) out.push({ kind: 'list', items: listBuf })
  return out
})

// ── Paragraph mode（梵二 / 有 textKey 的長文件） ─────────────────
const paragraphMode = computed(() => {
  if (!creed.value) return false
  // 顯式 'simple' opt-out（如梵一 Dei Filius / Pastor Aeternus — 結構不適合段號對照）
  if (creed.value.displayMode === 'simple') return false
  return creed.value.versions.some(v => !!v.textKey)
})

const docRows = ref<DocRow[]>([])
const docFootnotes = ref<Record<string, FootnoteDef[]>>({})
const paragraphsLoading = ref(false)

async function recomputeParagraphs() {
  if (!paragraphMode.value) {
    docRows.value = []
    docFootnotes.value = {}
    return
  }
  const zh = zhActive.value
  const en = enActive.value
  const orig = origActive.value
  const tasks: Array<Promise<['zh' | 'en' | 'orig', Awaited<ReturnType<typeof loadCreedDoc>>]>> = []
  if (zh?.textKey) tasks.push(loadCreedDoc(zh.textKey).then(d => ['zh', d] as const))
  if (en?.textKey) tasks.push(loadCreedDoc(en.textKey).then(d => ['en', d] as const))
  if (orig?.textKey) tasks.push(loadCreedDoc(orig.textKey).then(d => ['orig', d] as const))

  if (tasks.length === 0) {
    docRows.value = []
    docFootnotes.value = {}
    return
  }

  paragraphsLoading.value = true
  try {
    const results = await Promise.all(tasks)
    const byLang: Record<string, Awaited<ReturnType<typeof loadCreedDoc>>> = {}
    for (const [k, d] of results) byLang[k] = d
    const aligned = alignDocs(byLang)
    docRows.value = aligned.rows
    docFootnotes.value = aligned.footnotesByLang
  } catch (err) {
    console.error('[creed paragraph load]', err)
    docRows.value = []
    docFootnotes.value = {}
  } finally {
    paragraphsLoading.value = false
  }
}

watch([paragraphMode, zhActive, enActive, origActive], () => {
  recomputeParagraphs()
}, { immediate: true })

// ── Footnote helpers ─────────────────────────────────────────────
const hasFootnotes = computed(() => {
  const all = Object.values(docFootnotes.value)
  return all.some(list => list && list.length > 0)
})

const footnoteNumbers = computed<string[]>(() => {
  const set = new Set<string>()
  for (const list of Object.values(docFootnotes.value)) {
    for (const f of list ?? []) set.add(f.num)
  }
  return Array.from(set).sort((a, b) => parseInt(a, 10) - parseInt(b, 10))
})

function footnoteOf(lang: 'zh' | 'en' | 'orig', num: string): string {
  return docFootnotes.value[lang]?.find(f => f.num === num)?.body ?? ''
}
</script>

<style>
/* Global (unscoped) so v-html inner spans also pick up the style. */
.scripture-ref {
  font-family: 'DFKai-SB', 'BiauKai', 'Kaiti TC', 'Kaiti SC', 'STKaiti', 'KaiTi', serif;
  font-style: italic;
  font-weight: 600;
  color: #92400e;  /* amber-800 */
}
</style>
