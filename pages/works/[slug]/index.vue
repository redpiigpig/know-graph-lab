<template>
  <div class="min-h-screen bg-slate-50">
    <AppHeader :title="project?.title ?? '載入中…'" :back="{ to: '/works', label: '寫作計畫' }" container-class="max-w-5xl" />

    <div v-if="notFound" class="max-w-5xl mx-auto px-6 py-24 text-center">
      <div class="text-4xl mb-4">📭</div>
      <h1 class="text-lg font-semibold text-gray-700 mb-1">找不到此寫作計畫</h1>
      <p class="text-sm text-gray-400 mb-6">slug：{{ slug }}</p>
      <NuxtLink to="/works" class="text-sm text-amber-600 hover:underline">← 回寫作計畫列表</NuxtLink>
    </div>

    <template v-else>
      <!-- 封面 -->
      <div class="bg-white border-b border-gray-100">
        <div class="max-w-5xl mx-auto px-6 py-10">
          <div v-if="!project" class="text-gray-400 text-sm">載入中⋯</div>
          <template v-else>
            <div class="flex items-center gap-2 mb-3">
              <span class="text-xs font-medium px-2.5 py-1 rounded-full" :class="`bg-${project.color}-100 text-${project.color}-700`">寫作計畫</span>
              <WorksInlineEdit
                tag="span"
                :model-value="project.status"
                :editable="editMode && !!user"
                placeholder-hint="（點擊設定狀態）"
                display-class="text-xs text-gray-400"
                @save="patch({ status: $event })"
              />
            </div>

            <div class="flex items-center gap-3 mb-1">
              <WorksInlineEdit
                tag="span"
                :model-value="project.emoji"
                :editable="editMode && !!user"
                placeholder="📝"
                display-class="text-2xl"
                @save="patch({ emoji: $event })"
              />
              <WorksInlineEdit
                tag="h1"
                :model-value="project.title"
                :editable="editMode && !!user"
                placeholder="標題"
                display-class="text-xl font-bold text-gray-900 leading-snug flex-1"
                @save="patch({ title: $event })"
              />
            </div>

            <WorksInlineEdit
              tag="p"
              :model-value="project.subtitle"
              :editable="editMode && !!user"
              placeholder="副標 / 英文書名"
              display-class="text-sm text-gray-400 italic mb-4 block"
              @save="patch({ subtitle: $event })"
            />

            <WorksInlineEdit
              tag="p"
              :model-value="project.description"
              :editable="editMode && !!user"
              multiline
              :rows="3"
              placeholder="描述"
              display-class="text-sm text-gray-600 leading-relaxed max-w-2xl block"
              @save="patch({ description: $event })"
            />
          </template>
        </div>
      </div>

      <!-- 每日對話 — 先選月份，再選日期（仿聖經 卷→章；私人，登入者限定） -->
      <div v-if="dialogueDays.length" class="max-w-5xl mx-auto px-6 py-8">
        <!-- 序（楔子）：整條對話錄的開篇引言，渲染在月份格之上 -->
        <section v-if="prefaceHtml" class="dialogue-frame mb-8" v-html="prefaceHtml"></section>

        <div class="mb-4">
          <h2 class="text-base font-semibold text-gray-900">每日對話</h2>
          <p class="text-xs text-gray-500 mt-0.5">
            共 {{ dialogueDays.length }} 天 · {{ totalTurns }} 則 · 選擇月份，再挑一天查閱
          </p>
        </div>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <NuxtLink v-for="grp in dayGroups" :key="grp.month"
            :to="`/works/${slug}/month/${grp.month}`"
            class="no-underline flex flex-col items-center justify-center gap-1 py-7 rounded-2xl bg-white border-2 border-violet-100 hover:border-violet-300 hover:shadow-lg hover:shadow-violet-100 transition">
            <div class="text-3xl">🪈</div>
            <div class="text-base font-bold text-gray-900">{{ grp.label }}</div>
            <div class="text-xs text-gray-400">{{ grp.items.length }} 天 · {{ grp.turns }} 則</div>
          </NuxtLink>
        </div>

        <!-- 跋（收束）：整條對話錄的終篇，渲染在月份格之下 -->
        <section v-if="codaHtml" class="dialogue-frame dialogue-frame--coda mt-10" v-html="codaHtml"></section>
      </div>

      <div v-else-if="hasDialogueDays && !user" class="max-w-5xl mx-auto px-6 py-24 text-center text-gray-400 text-sm">
        <div class="text-3xl mb-3">🔒</div>
        此為私人對話，登入後可逐日查閱。
      </div>

      <!-- 書摘與構思 — 登入者限定（書籍計畫；論文計畫改放分頁內；含 manifest 的書改走下方分頁） -->
      <div v-if="user && !dialogueDays.length && project?.kind !== 'paper' && !materialsAvailable" class="max-w-5xl mx-auto px-6 py-8">
        <div class="mb-3 flex items-center justify-between">
          <div>
            <h2 class="text-base font-semibold text-gray-900">書摘與構思</h2>
            <p class="text-xs text-gray-500 mt-0.5">章節草稿 · 引用筆記 · 此分頁僅登入者可見</p>
          </div>
          <div class="flex items-center gap-2">
            <button
              v-if="editMode"
              class="px-3 py-1.5 text-xs rounded-lg border border-blue-300 text-blue-700 hover:bg-blue-50"
              @click="showPicker = true"
            >📎 插入引用</button>
            <button
              class="px-3 py-1.5 text-xs rounded-lg border border-purple-300 text-purple-700 hover:bg-purple-50"
              @click="showExport = true"
            >📄 預覽 + 書目</button>
            <span class="text-xs text-gray-400 ml-2">{{ editMode ? notesStatus : '檢視中（按右上「編輯」可修改）' }}</span>
          </div>
        </div>

        <p v-if="pickerToast" class="text-xs text-emerald-600 mb-2">{{ pickerToast }}</p>
        <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden" style="min-height: 400px;">
          <ClientOnly>
            <GenealogyRichTextEditor
              v-if="editMode"
              :key="editorKey"
              v-model="notesHtml"
              @update:model-value="onNotesUpdate"
            />
            <div v-else-if="notesHtml" class="prose-notes px-6 py-5" v-html="notesHtml"></div>
            <div v-else class="px-6 py-12 text-center text-gray-400 text-sm">
              <div class="text-3xl mb-2">📝</div>
              <p>尚無筆記。按右上「編輯」開始撰寫。</p>
            </div>
          </ClientOnly>
        </div>
      </div>

      <div v-else-if="project?.kind !== 'paper' && !hasDialogueDays && !materialsAvailable" class="max-w-5xl mx-auto px-6 py-24 text-center text-gray-400 text-sm">
        登入後可看到「書摘與構思」筆記分頁
      </div>

      <!-- 書籍計畫（含研究資料 manifest）：分頁（研究資料 / 口述訪談 / 書摘與構思） -->
      <template v-if="useBookTabs">
        <!-- tab 列 -->
        <div class="max-w-5xl mx-auto px-6 border-t border-gray-100">
          <div class="flex items-center gap-1 overflow-x-auto">
            <button v-for="t in bookTabs" :key="t.key" @click="bookTab = t.key"
              class="px-4 py-3 text-sm font-medium border-b-2 -mb-px whitespace-nowrap transition"
              :class="bookTab === t.key ? 'border-rose-500 text-rose-700' : 'border-transparent text-gray-500 hover:text-gray-800'">
              {{ t.label }}<span v-if="t.badge" class="ml-1.5 text-xs" :class="bookTab === t.key ? 'text-rose-500' : 'text-gray-400'">{{ t.badge }}</span>
            </button>
          </div>
        </div>

        <div class="max-w-5xl mx-auto px-6 py-8">
          <!-- ── 研究資料 ── -->
          <div v-show="bookTab === 'materials'">
            <div class="mb-4">
              <h2 class="text-base font-semibold text-gray-900">研究資料</h2>
              <p class="text-xs text-gray-500 mt-0.5">
                共 {{ materials?.totalFiles }} 件 · 依碩士論文原始分類整理
              </p>
              <p v-if="materials?.note" class="mt-2 text-xs text-gray-400 leading-relaxed max-w-2xl">{{ materials.note }}</p>
              <p v-if="materials?.source" class="mt-1 text-[11px] text-gray-300 font-mono break-all">{{ materials.source }}</p>
            </div>

            <div class="space-y-6">
              <section v-for="cat in materials?.categories" :key="cat.key" class="bg-white rounded-2xl border border-gray-100 p-5">
                <div class="flex items-baseline gap-2 mb-1">
                  <span class="text-lg leading-none">{{ cat.icon }}</span>
                  <h3 class="text-sm font-bold text-gray-800">{{ cat.label }}</h3>
                  <span class="text-xs text-gray-400">{{ cat.groups.length }} 類</span>
                </div>
                <p v-if="cat.desc" class="text-xs text-gray-500 mb-3 leading-relaxed">{{ cat.desc }}</p>

                <div class="space-y-1.5">
                  <details v-for="(g, gi) in cat.groups" :key="gi" class="group rounded-lg border border-gray-100 overflow-hidden">
                    <summary class="flex items-center gap-2 px-3 py-2 cursor-pointer select-none hover:bg-gray-50 text-sm">
                      <span class="text-gray-400 text-xs group-open:rotate-90 transition-transform">▶</span>
                      <span class="font-medium text-gray-800">{{ g.label }}</span>
                      <span v-if="g.tag" class="text-[10px] font-medium px-1.5 py-0.5 rounded-full bg-rose-50 text-rose-600">{{ g.tag }}</span>
                      <span class="ml-auto text-xs text-gray-400">{{ g.count }} 件</span>
                    </summary>
                    <div class="px-3 pb-3 pt-1 border-t border-gray-50">
                      <ul v-if="g.files?.length" class="space-y-0.5">
                        <li v-for="(f, fi) in g.files" :key="fi">
                          <div class="flex items-baseline gap-2 text-xs leading-relaxed rounded px-1 py-0.5 -mx-1 hover:bg-rose-50/60 group/file">
                            <span class="inline-block w-9 flex-shrink-0 text-[10px] font-mono uppercase text-gray-300 text-right">{{ fileExt(f.name) }}</span>
                            <span class="flex-1 text-gray-700">{{ f.name.replace(/\.[a-z0-9]+$/i, '') }}</span>
                            <button @click="toggleText(f)" class="flex-shrink-0 text-gray-400 hover:text-rose-600">
                              {{ textStates[f.key]?.open ? '收合' : '全文' }}
                            </button>
                            <a :href="`/api/works/material?key=${encodeURIComponent(f.key)}`"
                              class="flex-shrink-0 text-gray-300 hover:text-rose-500 no-underline">{{ fmtSize(f.size) }} ↓</a>
                          </div>
                          <!-- 全文面板 -->
                          <div v-if="textStates[f.key]?.open" class="ml-11 mt-1 mb-2 rounded-lg border border-gray-100 bg-gray-50/70">
                            <div v-if="textStates[f.key].loading" class="px-3 py-3 text-[11px] text-gray-400">載入全文⋯</div>
                            <template v-else-if="textStates[f.key].available">
                              <div v-if="textStates[f.key].zh" class="flex items-center gap-1 px-2 pt-2">
                                <button v-for="v in (['zh','orig'] as const)" :key="v" @click="textStates[f.key].view = v"
                                  class="text-[10px] px-2 py-0.5 rounded-full"
                                  :class="textStates[f.key].view === v ? 'bg-rose-100 text-rose-700' : 'text-gray-400 hover:text-gray-600'">
                                  {{ v === 'zh' ? '繁中' : '原文' }}
                                </button>
                              </div>
                              <pre class="px-3 py-2 text-[11px] leading-relaxed text-gray-700 whitespace-pre-wrap font-sans max-h-80 overflow-auto">{{ textStates[f.key].view === 'zh' && textStates[f.key].zh ? textStates[f.key].zh : textStates[f.key].text }}</pre>
                            </template>
                            <div v-else class="px-3 py-3 text-[11px] text-gray-400">全文尚未轉錄（OCR 進行中）。</div>
                          </div>
                        </li>
                      </ul>
                    </div>
                  </details>
                </div>
              </section>
            </div>
          </div>

          <!-- ── 碩士文稿正文 ── -->
          <div v-show="bookTab === 'thesis'">
            <div class="mb-4 flex items-start justify-between gap-3 flex-wrap">
              <div>
                <h2 class="text-base font-semibold text-gray-900">碩士文稿正文</h2>
                <p class="text-xs text-gray-500 mt-0.5">{{ thesisConf?.note || '本專書改寫底稿' }}</p>
              </div>
              <div class="flex items-center gap-2">
                <a v-if="thesisConf?.pdfKey" :href="`/api/works/material?key=${encodeURIComponent(thesisConf.pdfKey)}`"
                  class="text-xs font-medium px-3 py-1.5 rounded-lg border border-rose-300 text-rose-700 hover:bg-rose-50 no-underline">⬇ 下載論文 PDF</a>
                <NuxtLink to="/thesis" class="text-xs font-medium px-3 py-1.5 rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-50">論文閱讀器 →</NuxtLink>
              </div>
            </div>
            <div class="flex gap-6">
              <aside class="w-44 flex-shrink-0 hidden md:block">
                <div class="sticky top-4 space-y-0.5">
                  <button v-for="ch in thesisConf?.chapters" :key="ch.id" @click="selectThesisChapter(ch.id)"
                    :class="['w-full text-left px-3 py-2 rounded-lg text-xs transition-colors leading-snug', activeThesisChapter === ch.id ? 'bg-rose-100 text-rose-700 font-medium' : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700']">
                    {{ ch.title }}
                  </button>
                </div>
              </aside>
              <div class="flex-1 min-w-0">
                <div class="md:hidden mb-3">
                  <select v-model="activeThesisChapter" @change="loadThesisChapter(activeThesisChapter)" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
                    <option v-for="ch in thesisConf?.chapters" :key="ch.id" :value="ch.id">{{ ch.title }}</option>
                  </select>
                </div>
                <div v-if="thesisLoading" class="text-gray-400 text-sm py-8 text-center">載入中⋯</div>
                <div v-else-if="thesisHtml" class="thesis-prose bg-white rounded-2xl border border-gray-100 px-6 py-8 sm:px-10" v-html="thesisHtml"></div>
                <div v-else class="text-gray-400 text-sm py-8 text-center">找不到此章節文字。</div>
              </div>
            </div>
          </div>

          <!-- ── 口述訪談 ── -->
          <div v-show="bookTab === 'interviews'">
            <div class="mb-5 flex items-center justify-between flex-wrap gap-3">
              <div>
                <h2 class="text-base font-semibold text-gray-900">口述訪談紀錄</h2>
                <p class="text-xs text-gray-500 mt-0.5">共 {{ interviewsStore.published.length }} 位受訪者，2023–2025 年間完成</p>
              </div>
              <div class="flex gap-2 flex-wrap">
                <button v-for="cat in interviewCategories" :key="cat" @click="activeIvCat = cat"
                  :class="['text-xs px-3 py-1.5 rounded-full border transition-colors', activeIvCat === cat ? 'bg-rose-600 text-white border-rose-600' : 'border-gray-200 text-gray-500 hover:border-gray-400']">
                  {{ cat }}
                </button>
              </div>
            </div>
            <div class="grid gap-3 sm:grid-cols-2">
              <NuxtLink v-for="iv in filteredInterviews" :key="iv.id"
                :to="`/works/${slug}/interview/${encodeURIComponent(iv.filename)}`"
                class="bg-white rounded-xl border border-gray-100 p-4 hover:border-rose-200 hover:shadow-sm transition-all no-underline">
                <div class="flex items-start gap-3">
                  <div :class="['w-9 h-9 rounded-full flex items-center justify-center text-sm flex-shrink-0', ivCatStyle(iv.category)]">
                    {{ ivCatIcon(iv.category) }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-baseline justify-between gap-2">
                      <h3 class="text-sm font-semibold text-gray-900 truncate">{{ iv.name }}</h3>
                      <span class="text-xs text-gray-400 flex-shrink-0">{{ iv.date }}</span>
                    </div>
                    <p class="text-xs text-gray-500 mt-0.5">{{ iv.role }}</p>
                    <p class="text-xs text-rose-500 mt-1.5">閱讀全文 →</p>
                  </div>
                </div>
              </NuxtLink>
            </div>
          </div>

          <!-- ── 書摘與構思（登入者限定） ── -->
          <div v-show="bookTab === 'notes'">
            <div class="mb-3 flex items-center justify-between">
              <div>
                <h2 class="text-base font-semibold text-gray-900">書摘與構思</h2>
                <p class="text-xs text-gray-500 mt-0.5">章節草稿 · 引用筆記 · 此分頁僅登入者可見</p>
              </div>
              <div class="flex items-center gap-2">
                <button v-if="editMode" class="px-3 py-1.5 text-xs rounded-lg border border-blue-300 text-blue-700 hover:bg-blue-50" @click="showPicker = true">📎 插入引用</button>
                <button class="px-3 py-1.5 text-xs rounded-lg border border-purple-300 text-purple-700 hover:bg-purple-50" @click="showExport = true">📄 預覽 + 書目</button>
                <span class="text-xs text-gray-400 ml-2">{{ editMode ? notesStatus : '檢視中（按右上「編輯」可修改）' }}</span>
              </div>
            </div>
            <p v-if="pickerToast" class="text-xs text-emerald-600 mb-2">{{ pickerToast }}</p>
            <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden" style="min-height: 400px;">
              <ClientOnly>
                <GenealogyRichTextEditor v-if="editMode" :key="editorKey" v-model="notesHtml" @update:model-value="onNotesUpdate" />
                <div v-else-if="notesHtml" class="prose-notes px-6 py-5" v-html="notesHtml"></div>
                <div v-else class="px-6 py-12 text-center text-gray-400 text-sm">
                  <div class="text-3xl mb-2">📝</div>
                  <p>尚無筆記。按右上「編輯」開始撰寫。</p>
                </div>
              </ClientOnly>
            </div>
          </div>
        </div>
      </template>

      <!-- 論文計畫：分頁（研究回顧 / 修改建議 / 原文 / 書摘與構思） -->
      <template v-if="project?.kind === 'paper'">
        <!-- tab 列 -->
        <div class="max-w-5xl mx-auto px-6 border-t border-gray-100">
          <div class="flex items-center gap-1 overflow-x-auto">
            <button v-for="t in paperTabs" :key="t.key" @click="activeTab = t.key"
              class="px-4 py-3 text-sm font-medium border-b-2 -mb-px whitespace-nowrap transition"
              :class="activeTab === t.key ? 'border-teal-500 text-teal-700' : 'border-transparent text-gray-500 hover:text-gray-800'">
              {{ t.label }}<span v-if="t.badge" class="ml-1.5 text-xs" :class="activeTab === t.key ? 'text-teal-500' : 'text-gray-400'">{{ t.badge }}</span>
            </button>
          </div>
        </div>

        <div class="max-w-5xl mx-auto px-6 py-8">
          <!-- ── 研究回顧 ── -->
          <div v-show="activeTab === 'review'">
            <div class="mb-4">
              <h2 class="text-base font-semibold text-gray-900">研究回顧</h2>
              <p class="text-xs text-gray-500 mt-0.5">
                文獻綜述 · 共 {{ litEntries.length }} 筆
                <span v-if="litEntries.length"> · 開放取用外文文獻提供 <span class="text-teal-600">原文／逐段中譯</span> 兩欄對照</span>
              </p>
            </div>
            <div v-if="litLoading" class="text-gray-400 text-sm py-8 text-center">載入中⋯</div>
            <div v-else-if="litEntries.length === 0" class="text-gray-400 text-sm py-8 text-center">尚無文獻綜述。</div>
            <div v-else class="space-y-8">
              <section v-for="grp in litGroups" :key="grp.theme">
                <div v-if="grp.firstBiblio" class="border-t border-dashed border-gray-200 pt-6 mb-4">
                  <h3 class="text-sm font-semibold text-gray-700">論文參考文獻</h3>
                  <p class="text-xs text-gray-400 mt-0.5">本文實際引用之書目，依文獻類型分類（以上為八敬法主題綜述）</p>
                </div>
                <h3 v-if="grp.theme" class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">{{ grp.theme }}</h3>
                <div class="space-y-3">
                  <div v-for="e in grp.items" :key="e.id"
                    class="bg-white rounded-2xl border border-gray-100 p-5 transition-all"
                    :class="e.has_fulltext ? 'cursor-pointer hover:border-teal-200 hover:shadow-sm' : ''"
                    @click="() => e.has_fulltext && navigateTo(`/works/${slug}/review/${e.ref_key}`)">
                    <div class="flex flex-wrap items-center gap-1.5 mb-2">
                      <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">{{ langLabel(e.language) }}</span>
                      <span v-if="e.dimension" class="text-xs font-medium px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600">{{ e.dimension }}</span>
                      <span v-if="e.stance" class="text-xs font-medium px-2 py-0.5 rounded-full bg-rose-50 text-rose-600">立場：{{ e.stance }}</span>
                      <span v-if="e.has_fulltext" class="text-xs font-medium px-2 py-0.5 rounded-full bg-teal-50 text-teal-700">原文／中譯對照</span>
                    </div>
                    <h4 class="text-sm font-semibold text-gray-900 leading-snug mb-1">
                      {{ e.authors }}<span v-if="e.year"> （{{ e.year }}）</span>　{{ e.title }}
                    </h4>
                    <p v-if="e.venue" class="text-xs text-gray-500 mb-2">{{ e.venue }}</p>
                    <p v-if="e.abstract_zh" class="text-sm text-gray-700 leading-relaxed">{{ e.abstract_zh }}</p>
                    <div class="mt-2 flex items-center gap-3 text-xs">
                      <NuxtLink v-if="e.has_fulltext" :to="`/works/${slug}/review/${e.ref_key}`" @click.stop
                        class="text-teal-700 hover:underline font-medium">閱讀全文（原文／中譯）→</NuxtLink>
                      <a v-if="e.fulltext_url" :href="e.fulltext_url" target="_blank" rel="noopener" @click.stop
                        class="text-blue-600 hover:underline">原始連結 ↗</a>
                      <span v-if="!e.has_fulltext && !e.fulltext_url" class="text-gray-300 italic">無線上全文</span>
                    </div>
                  </div>
                </div>
              </section>
            </div>
          </div>

          <!-- ── 修改建議 ── -->
          <div v-show="activeTab === 'memo'">
            <div class="mb-4">
              <h2 class="text-base font-semibold text-gray-900">修改建議</h2>
              <p class="text-xs text-gray-500 mt-0.5">改寫為英文期刊論文的學術修改建議書（顧問意見，未更動論文原文）</p>
            </div>
            <div v-if="memoLoading" class="text-gray-400 text-sm py-8 text-center">載入中⋯</div>
            <div v-else-if="memoHtml" class="doc-prose bg-white rounded-2xl border border-gray-100 px-6 py-6 sm:px-10" v-html="memoHtml"></div>
            <div v-else class="text-gray-400 text-sm py-8 text-center">尚無修改建議。</div>
          </div>

          <!-- ── 修改草稿 ── -->
          <div v-show="activeTab === 'draft'">
            <div class="mb-4">
              <h2 class="text-base font-semibold text-gray-900">修改草稿</h2>
              <p class="text-xs text-gray-500 mt-0.5">依修改建議改寫的中文草稿（英文期刊版工作底稿，待逐段英譯）</p>
            </div>
            <div v-if="draftLoading" class="text-gray-400 text-sm py-8 text-center">載入中⋯</div>
            <div v-else-if="draftHtml" class="doc-prose bg-white rounded-2xl border border-gray-100 px-6 py-6 sm:px-10" v-html="draftHtml"></div>
            <div v-else class="text-gray-400 text-sm py-8 text-center">尚無草稿。</div>
          </div>

          <!-- ── 原文 ── -->
          <div v-show="activeTab === 'original'">
            <div class="mb-4 flex items-start justify-between gap-3">
              <div>
                <h2 class="text-base font-semibold text-gray-900">論文原文</h2>
                <p class="text-xs text-gray-500 mt-0.5">研討會論文全文（改寫底稿，原樣保留）</p>
              </div>
              <NuxtLink v-if="project.paper_ref" :to="`/papers/${project.paper_ref}`"
                class="flex-shrink-0 text-xs font-medium px-3 py-1.5 rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-50">在閱讀器開啟 →</NuxtLink>
            </div>
            <div v-if="paperLoading" class="text-gray-400 text-sm py-8 text-center">載入中⋯</div>
            <div v-else-if="paperHtml" class="doc-prose paper-prose bg-white rounded-2xl border border-gray-100 px-6 py-8 sm:px-12" v-html="paperHtml"></div>
            <div v-else class="text-gray-400 text-sm py-8 text-center">找不到原文檔。</div>
          </div>

          <!-- ── 書摘與構思（登入者限定） ── -->
          <div v-show="activeTab === 'notes'">
            <div class="mb-3 flex items-center justify-between">
              <div>
                <h2 class="text-base font-semibold text-gray-900">書摘與構思</h2>
                <p class="text-xs text-gray-500 mt-0.5">章節草稿 · 引用筆記 · 此分頁僅登入者可見</p>
              </div>
              <div class="flex items-center gap-2">
                <button v-if="editMode" class="px-3 py-1.5 text-xs rounded-lg border border-blue-300 text-blue-700 hover:bg-blue-50" @click="showPicker = true">📎 插入引用</button>
                <button class="px-3 py-1.5 text-xs rounded-lg border border-purple-300 text-purple-700 hover:bg-purple-50" @click="showExport = true">📄 預覽 + 書目</button>
                <span class="text-xs text-gray-400 ml-2">{{ editMode ? notesStatus : '檢視中（按右上「編輯」可修改）' }}</span>
              </div>
            </div>
            <p v-if="pickerToast" class="text-xs text-emerald-600 mb-2">{{ pickerToast }}</p>
            <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden" style="min-height: 400px;">
              <ClientOnly>
                <GenealogyRichTextEditor v-if="editMode" :key="editorKey" v-model="notesHtml" @update:model-value="onNotesUpdate" />
                <div v-else-if="notesHtml" class="prose-notes px-6 py-5" v-html="notesHtml"></div>
                <div v-else class="px-6 py-12 text-center text-gray-400 text-sm">
                  <div class="text-3xl mb-2">📝</div>
                  <p>尚無筆記。按右上「編輯」開始撰寫。</p>
                </div>
              </ClientOnly>
            </div>
          </div>
        </div>
      </template>
    </template>

    <ExcerptPicker
      :open="showPicker"
      @close="showPicker = false"
      @picked="onPicked"
    />
    <DocumentExportModal
      :open="showExport"
      :source-html="notesHtml"
      @close="showExport = false"
    />
  </div>
</template>

<script setup lang="ts">
import { useDebounceFn } from '@vueuse/core'

const route = useRoute()
const slug = computed(() => String(route.params.slug ?? ''))
const user = useSupabaseUser()
const supabase = useSupabaseClient()
const editMode = useEditMode()

interface Project {
  id: string
  slug: string
  title: string
  subtitle: string | null
  description: string | null
  emoji: string
  color: string
  status: string | null
  content_json: string | null
  kind: 'book' | 'paper'
  paper_ref: string | null
}

interface LitEntry {
  id: number
  ref_key: string
  authors: string
  year: number | null
  title: string
  venue: string | null
  language: string | null
  theme: string | null
  dimension: string | null
  stance: string | null
  abstract_zh: string | null
  fulltext_url: string | null
  fulltext_status: string
  has_fulltext: boolean
}

const LANG_LABELS: Record<string, string> = {
  en: '英文', zh: '中文', de: '德文', fr: '法文', ja: '日文',
  la: '拉丁文', grc: '希臘文', es: '西班牙文', it: '義大利文', other: '其他',
}
function langLabel(code: string | null) {
  return LANG_LABELS[code ?? ''] ?? (code || '—')
}

const project = ref<Project | null>(null)
const notFound = ref(false)
const notesHtml = ref('')
const editorKey = ref(0)
const notesStatus = ref('')
const lastSavedHtml = ref('')
const showPicker = ref(false)
const showExport = ref(false)
const pickerToast = ref('')

function onPicked(payload: { id: string; marker: string; toastMsg: string }) {
  pickerToast.value = payload.toastMsg
  setTimeout(() => { pickerToast.value = '' }, 3500)
}

useHead(() => ({ title: project.value ? `${project.value.title} — 寫作計畫` : '寫作計畫' }))

async function loadProject() {
  let token = ''
  if (user.value) {
    const { data: { session } } = await supabase.auth.getSession()
    token = session?.access_token ?? ''
  }
  try {
    const data = await $fetch<{ project: Project }>(`/api/works/projects/${slug.value}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    project.value = data.project
    notesHtml.value = (typeof data.project.content_json === 'string' ? data.project.content_json : '') || ''
    editorKey.value++
  } catch (err: any) {
    if (err?.statusCode === 404) notFound.value = true
    else console.error(err)
  }
}

onMounted(loadProject)
watch(() => user.value, loadProject)

// ── 每日對話（一條對話串拆成每天一頁）─────────────────────────────
interface DialogueDay { day_date: string; weekday: string; day_title: string; n_turns: number }
const dialogueDays = ref<DialogueDay[]>([])
const hasDialogueDays = ref(false)

async function loadDialogueDays() {
  let token = ''
  if (user.value) {
    const { data: { session } } = await supabase.auth.getSession()
    token = session?.access_token ?? ''
  }
  try {
    const res = await $fetch<{ days: DialogueDay[]; hasDays: boolean }>('/api/works/dialogue-days', {
      query: { slug: slug.value },
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    dialogueDays.value = res.days ?? []
    hasDialogueDays.value = !!res.hasDays
  } catch { dialogueDays.value = []; hasDialogueDays.value = false }
}
onMounted(loadDialogueDays)
watch(() => user.value, loadDialogueDays)

const totalTurns = computed(() => dialogueDays.value.reduce((s, d) => s + (d.n_turns || 0), 0))

// 對話錄的序／跋（楔子／收束）放在主卡 content_json，以 <!--CODA--> 分隔：
// 前半＝序（渲染在月份格之上），後半＝跋（之下）。只在有 dialogue_days（私人）時顯示。
const prefaceHtml = computed(() => {
  if (!dialogueDays.value.length) return ''
  return (project.value?.content_json ?? '').split('<!--CODA-->')[0] || ''
})
const codaHtml = computed(() => {
  if (!dialogueDays.value.length) return ''
  return (project.value?.content_json ?? '').split('<!--CODA-->')[1] || ''
})
const MONTH_ZH = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
function dayNum(date: string) { return Number(date.split('-')[2]) }
const dayGroups = computed(() => {
  const groups: { month: string; label: string; items: DialogueDay[]; turns: number }[] = []
  for (const d of dialogueDays.value) {
    const [y, m] = d.day_date.split('-')
    const month = `${y}-${m}`
    let g = groups.find(x => x.month === month)
    if (!g) { g = { month, label: `${y}年${MONTH_ZH[Number(m) - 1]}`, items: [], turns: 0 }; groups.push(g) }
    g.items.push(d); g.turns += d.n_turns || 0
  }
  return groups
})

// ── 書籍計畫：研究資料 manifest + 口述訪談 ─────────────────────────────
interface MaterialFile { name: string; key: string; size: number }
interface MaterialGroup { label: string; count?: number; size?: number; tag?: string; files?: MaterialFile[] }
interface MaterialCategory { key: string; label: string; icon?: string; desc?: string; groups: MaterialGroup[] }
interface ThesisChapter { id: string; title: string }
interface ThesisConf { title?: string; note?: string; pdfKey?: string; contentBase?: string; chapters: ThesisChapter[] }
interface Materials { book?: string; subtitle?: string; source?: string; note?: string; interviews?: boolean; thesis?: ThesisConf; totalFiles?: number; totalBytes?: number; categories: MaterialCategory[] }

const materials = ref<Materials | null>(null)
const materialsAvailable = ref(false)

async function loadMaterials() {
  if (project.value?.kind === 'paper') { materialsAvailable.value = false; return }
  try {
    const data = await $fetch<Materials>(`/content/works/${slug.value}-materials.json`, { responseType: 'json' })
    if (data && Array.isArray(data.categories) && data.categories.length) { materials.value = data; materialsAvailable.value = true }
    else materialsAvailable.value = false
  } catch { materialsAvailable.value = false }
}
watch(() => project.value?.kind, loadMaterials)

// 口述訪談（沿用碩士論文 store 的已發佈清單）
const interviewsStore = useThesisInterviewsStore()
const showInterviews = computed(() => materialsAvailable.value && !!materials.value?.interviews)
const interviewCategories = ['全部', '法師', '學者', '宗教對話', '社運界', '其他']
const activeIvCat = ref('全部')
const filteredInterviews = computed(() =>
  activeIvCat.value === '全部'
    ? interviewsStore.published
    : interviewsStore.published.filter((iv) => iv.category === activeIvCat.value)
)
function ivCatStyle(cat: string) {
  const m: Record<string, string> = { '法師': 'bg-amber-100 text-amber-700', '學者': 'bg-blue-100 text-blue-700', '宗教對話': 'bg-green-100 text-green-700', '社運界': 'bg-rose-100 text-rose-700', '其他': 'bg-gray-100 text-gray-600' }
  return m[cat] ?? 'bg-gray-100 text-gray-600'
}
function ivCatIcon(cat: string) {
  const m: Record<string, string> = { '法師': '🪷', '學者': '📚', '宗教對話': '🕊️', '社運界': '✊', '其他': '👤' }
  return m[cat] ?? '👤'
}
function fileExt(name: string) {
  const m = name.match(/\.([a-z0-9]+)$/i)
  return m ? m[1].toLowerCase() : ''
}
function fmtSize(bytes?: number) {
  if (!bytes) return ''
  if (bytes >= 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`
  return `${Math.max(1, Math.round(bytes / 1024))} KB`
}

// 研究資料全文（轉錄文字；外文另有 .zh 繁中翻譯）lazy-load
interface TextState { open: boolean; loading: boolean; loaded: boolean; available: boolean; text: string | null; zh: string | null; view: 'orig' | 'zh' }
const textStates = reactive<Record<string, TextState>>({})
async function toggleText(f: MaterialFile) {
  let st = textStates[f.key]
  if (!st) { st = textStates[f.key] = { open: false, loading: false, loaded: false, available: false, text: null, zh: null, view: 'orig' } }
  st.open = !st.open
  if (st.open && !st.loaded && !st.loading) {
    st.loading = true
    try {
      const r = await $fetch<{ available: boolean; text: string | null; zh: string | null }>(
        '/api/works/material-text', { query: { key: f.key } })
      st.available = r.available
      st.text = r.text ?? null
      st.zh = r.zh ?? null
      st.view = r.zh ? 'zh' : 'orig'
    } catch {
      st.available = false
    } finally {
      st.loading = false
      st.loaded = true
    }
  }
}

// 碩士文稿正文（改寫底稿）
const thesisConf = computed(() => materials.value?.thesis ?? null)
const activeThesisChapter = ref('abstract')
const thesisHtml = ref('')
const thesisLoading = ref(false)
async function loadThesisChapter(id: string) {
  const base = thesisConf.value?.contentBase ?? '/content/thesis'
  thesisLoading.value = true
  try {
    const txt = await $fetch<string>(`${base}/${id}.txt`, { responseType: 'text' })
    thesisHtml.value = renderThesisText(txt || '')
  } catch { thesisHtml.value = '' } finally { thesisLoading.value = false }
}
function selectThesisChapter(id: string) { activeThesisChapter.value = id; loadThesisChapter(id) }
// 碩士論文段落判讀（章/節/小節/摘要/關鍵字/腳註）
function renderThesisText(txt: string): string {
  const sup = (s: string) => esc(s).replace(/\[(\d+)\]/g, '<sup>[$1]</sup>')
  const out: string[] = []
  let inEn = false
  for (const raw of txt.replace(/\r\n/g, '\n').split('\n')) {
    const t = raw.trim()
    if (!t) continue
    if (/^\d{1,3}$/.test(t)) continue // 目錄頁碼
    if (t === '摘要') { inEn = false; out.push(`<h3 class="ttl">${esc(t)}</h3>`); continue }
    if (t === 'Abstract') { inEn = true; out.push(`<h3 class="ttl">${esc(t)}</h3>`); continue }
    if (/^第[一二三四五六七八九十百]+章/.test(t)) { inEn = false; out.push(`<h2>${esc(t)}</h2>`); continue }
    if (/^第[一二三四五六七八九十百]+節/.test(t)) { out.push(`<h3>${esc(t)}</h3>`); continue }
    if (/^附錄[一二三四五六七八九十]+/.test(t)) { out.push(`<h3>${esc(t)}</h3>`); continue }
    if (/^[一二三四五六七八九十]+、/.test(t)) { out.push(`<h4>${esc(t)}</h4>`); continue }
    if (/^（[一二三四五六七八九十]+）/.test(t)) { out.push(`<h5>${esc(t)}</h5>`); continue }
    if (/^關鍵字[：:]/.test(t) || /^Keywords/.test(t)) { out.push(`<p class="kw">${esc(t)}</p>`); continue }
    if (/^\[\d+\]/.test(t)) { out.push(`<p class="ref">${sup(t)}</p>`); continue }
    out.push(`<p${inEn ? ' class="en"' : ''}>${sup(t)}</p>`)
  }
  return out.join('\n')
}

// 書籍計畫分頁（研究資料 / 碩士文稿 / 口述訪談 / 書摘與構思）
type BookTab = 'materials' | 'thesis' | 'interviews' | 'notes'
const bookTab = ref<BookTab>('materials')
const useBookTabs = computed(() => project.value?.kind !== 'paper' && !dialogueDays.value.length && materialsAvailable.value)
const bookTabs = computed(() => {
  const tabs: { key: BookTab; label: string; badge?: string }[] = [
    { key: 'materials', label: '研究資料', badge: materials.value?.totalFiles ? String(materials.value.totalFiles) : undefined },
  ]
  if (thesisConf.value) tabs.push({ key: 'thesis', label: '碩士文稿' })
  if (showInterviews.value) tabs.push({ key: 'interviews', label: '口述訪談', badge: String(interviewsStore.published.length) })
  if (user.value) tabs.push({ key: 'notes', label: '書摘與構思' })
  return tabs
})
watch(bookTabs, (tabs) => { if (!tabs.some((t) => t.key === bookTab.value)) bookTab.value = 'materials' })
watch(bookTab, (t) => { if (t === 'thesis' && !thesisHtml.value && !thesisLoading.value) loadThesisChapter(activeThesisChapter.value) })

// ── 研究回顧（文獻綜述）─────────────────────────────────────────────
const litEntries = ref<LitEntry[]>([])
const litLoading = ref(false)

async function loadLitReview() {
  if (project.value?.kind !== 'paper') { litEntries.value = []; return }
  litLoading.value = true
  try {
    const res = await $fetch<{ entries: LitEntry[] }>('/api/lit-review/entries', { query: { slug: slug.value } })
    litEntries.value = res.entries ?? []
  } catch { litEntries.value = [] } finally { litLoading.value = false }
}
watch(() => project.value?.kind, loadLitReview)

// A paper's real 參考文獻 is grouped by document type (mirrors DOC_TYPE_THEMES in
// scripts/lit_review.py); everything else is the thematic 文獻綜述 survey.
const DOC_TYPE_LABELS = new Set([
  '佛典與檔案', '專書著作', '期刊文章', '研討會與專書論文',
  '學位論文', '報刊與雜誌', '網路文章',
])

// Group entries by theme, preserving server order (display_order encodes theme grouping).
// `firstBiblio` marks the first works-cited group so the reader can divide the
// thematic survey from the paper's actual references with a single heading.
const litGroups = computed(() => {
  const groups: { theme: string; items: LitEntry[]; firstBiblio?: boolean }[] = []
  for (const e of litEntries.value) {
    const theme = e.theme ?? ''
    let g = groups.find(x => x.theme === theme)
    if (!g) { g = { theme, items: [] }; groups.push(g) }
    g.items.push(e)
  }
  const firstBiblio = groups.find(g => DOC_TYPE_LABELS.has(g.theme))
  if (firstBiblio) firstBiblio.firstBiblio = true
  return groups
})

// ── 論文計畫分頁（研究回顧 / 修改建議 / 原文 / 書摘）─────────────────────
type PaperTab = 'review' | 'memo' | 'draft' | 'original' | 'notes'
const activeTab = ref<PaperTab>('review')

const memoHtml = ref('')
const memoLoading = ref(false)
const memoAvailable = ref(false)
const draftHtml = ref('')
const draftLoading = ref(false)
const draftAvailable = ref(false)
const paperHtml = ref('')
const paperLoading = ref(false)

const paperTabs = computed(() => {
  const tabs: { key: PaperTab; label: string; badge?: string }[] = [
    { key: 'review', label: '研究回顧', badge: litEntries.value.length ? String(litEntries.value.length) : undefined },
  ]
  if (memoAvailable.value) tabs.push({ key: 'memo', label: '修改建議' })
  if (draftAvailable.value) tabs.push({ key: 'draft', label: '修改草稿' })
  if (project.value?.paper_ref) tabs.push({ key: 'original', label: '原文' })
  if (user.value) tabs.push({ key: 'notes', label: '書摘與構思' })
  return tabs
})
// If the active tab disappears (e.g. logout hides 書摘), fall back to 研究回顧.
watch(paperTabs, (tabs) => {
  if (!tabs.some(t => t.key === activeTab.value)) activeTab.value = 'review'
})

// 修改建議：抓 public/content/works/<ref>-revision-memo.md → 迷你 markdown 渲染
async function loadMemo() {
  const ref = project.value?.paper_ref
  if (!ref) { memoAvailable.value = false; return }
  memoLoading.value = true
  try {
    const md = await $fetch<string>(`/content/works/${ref}-revision-memo.md`, { responseType: 'text' })
    if (md && md.trim()) { memoHtml.value = renderMarkdown(md); memoAvailable.value = true }
    else { memoAvailable.value = false }
  } catch { memoAvailable.value = false } finally { memoLoading.value = false }
}

// 修改草稿：抓 public/content/works/<ref>-revision-draft.md → 迷你 markdown 渲染
async function loadDraft() {
  const ref = project.value?.paper_ref
  if (!ref) { draftAvailable.value = false; return }
  draftLoading.value = true
  try {
    const md = await $fetch<string>(`/content/works/${ref}-revision-draft.md`, { responseType: 'text' })
    if (md && md.trim()) { draftHtml.value = renderMarkdown(md); draftAvailable.value = true }
    else { draftAvailable.value = false }
  } catch { draftAvailable.value = false } finally { draftLoading.value = false }
}

// 原文：抓 public/content/papers/<ref>.txt → 內嵌渲染
async function loadPaperText() {
  const ref = project.value?.paper_ref
  if (!ref) { paperHtml.value = ''; return }
  paperLoading.value = true
  try {
    const txt = await $fetch<string>(`/content/papers/${ref}.txt`, { responseType: 'text' })
    paperHtml.value = renderPaperText(txt || '')
  } catch { paperHtml.value = '' } finally { paperLoading.value = false }
}

watch(() => project.value?.paper_ref, (r) => { if (r) { loadMemo(); loadDraft(); loadPaperText() } }, { immediate: true })

// ── 迷你 markdown 渲染（無外部依賴；夠用於修改建議書：標題/粗體/清單/引用/表格/連結/分隔線）──
function esc(s: string) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;') }
function inlineMd(s: string) {
  return esc(s)
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
}
function renderMarkdown(md: string): string {
  const lines = md.replace(/\r\n/g, '\n').split('\n')
  const out: string[] = []
  let i = 0
  let list: 'ul' | 'ol' | null = null
  const closeList = () => { if (list) { out.push(`</${list}>`); list = null } }
  while (i < lines.length) {
    const t = lines[i].trim()
    if (!t) { closeList(); i++; continue }
    if (/^---+$/.test(t)) { closeList(); out.push('<hr>'); i++; continue }
    // 表格：本行以 | 起，下一行為分隔列
    if (t.startsWith('|') && i + 1 < lines.length && /^\|[\s:|-]+\|?\s*$/.test(lines[i + 1].trim())) {
      closeList()
      const cells = (s: string) => s.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(c => c.trim())
      const head = cells(t); i += 2
      const rows: string[][] = []
      while (i < lines.length && lines[i].trim().startsWith('|')) { rows.push(cells(lines[i])); i++ }
      let tbl = '<table><thead><tr>' + head.map(h => `<th>${inlineMd(h)}</th>`).join('') + '</tr></thead><tbody>'
      for (const r of rows) tbl += '<tr>' + r.map(c => `<td>${inlineMd(c)}</td>`).join('') + '</tr>'
      out.push(tbl + '</tbody></table>'); continue
    }
    const h = t.match(/^(#{1,6})\s+(.*)$/)
    if (h) { closeList(); const lvl = Math.min(h[1].length + 1, 6); out.push(`<h${lvl}>${inlineMd(h[2])}</h${lvl}>`); i++; continue }
    if (t.startsWith('>')) {
      closeList(); const buf: string[] = []
      while (i < lines.length && lines[i].trim().startsWith('>')) { buf.push(lines[i].trim().replace(/^>\s?/, '')); i++ }
      out.push(`<blockquote>${inlineMd(buf.join(' '))}</blockquote>`); continue
    }
    const ul = t.match(/^[-*]\s+(.*)$/)
    if (ul) { if (list !== 'ul') { closeList(); out.push('<ul>'); list = 'ul' } out.push(`<li>${inlineMd(ul[1])}</li>`); i++; continue }
    const ol = t.match(/^\d+[.)]\s+(.*)$/)
    if (ol) { if (list !== 'ol') { closeList(); out.push('<ol>'); list = 'ol' } out.push(`<li>${inlineMd(ol[1])}</li>`); i++; continue }
    closeList(); out.push(`<p>${inlineMd(t)}</p>`); i++
  }
  closeList()
  return out.join('\n')
}

// ── 論文原文（.txt）內嵌渲染：沿用 /papers reader 的段落判讀（標題/小節/引用/腳註上標）──
function renderPaperText(txt: string): string {
  const sup = (s: string) => esc(s).replace(/\[(\d+)\]/g, '<sup>[$1]</sup>')
  const out: string[] = []
  let inRef = false
  for (const raw of txt.replace(/\r\n/g, '\n').split('\n')) {
    const t = raw.trim()
    if (!t) continue
    if (t === '參考文獻' || t === '參考資料' || t === '注釋' || t === '注解') { inRef = t === '注釋' || t === '注解'; out.push(`<h3>${esc(t)}</h3>`); continue }
    if (/^[一二三四五六七八九十百]+、/.test(t)) { out.push(`<h3>${esc(t)}</h3>`); continue }
    if (/^（[一二三四五六七八九十]+）/.test(t)) { out.push(`<h4>${esc(t)}</h4>`); continue }
    if (t === '摘要' || t === 'Abstract') { out.push(`<h3>${esc(t)}</h3>`); continue }
    if (/^關鍵字[：:]/.test(t) || /^Keywords[：:]/.test(t)) { out.push(`<p class="kw">${esc(t)}</p>`); continue }
    if (/^　　　/.test(raw)) { out.push(`<blockquote>${sup(t)}</blockquote>`); continue }
    if (inRef) { out.push(`<p class="ref">${sup(t)}</p>`); continue }
    out.push(`<p>${sup(t.replace(/^　+/, ''))}</p>`)
  }
  return out.join('\n')
}

async function patch(updates: Record<string, unknown>) {
  if (!project.value) return
  try {
    const res = await authedFetch<{ project: Project }>(`/api/works/projects/${project.value.slug}`, {
      method: 'PATCH',
      body: updates,
    })
    const slugChanged = res.project.slug !== project.value.slug
    project.value = { ...project.value, ...res.project }
    if (slugChanged) navigateTo(`/works/${res.project.slug}`)
  } catch (err: any) {
    alert(`儲存失敗：${err?.data?.message ?? err?.message ?? err}`)
  }
}

const saveNotes = useDebounceFn(async (html: string) => {
  if (!project.value || !user.value) return
  if (html === lastSavedHtml.value) return
  notesStatus.value = '儲存中⋯'
  try {
    await authedFetch(`/api/works/projects/${project.value.slug}`, {
      method: 'PATCH',
      body: { content_json: html },
    })
    lastSavedHtml.value = html
    notesStatus.value = '已儲存'
    setTimeout(() => { if (notesStatus.value === '已儲存') notesStatus.value = '' }, 1500)
  } catch (err: any) {
    notesStatus.value = `儲存失敗：${err?.data?.message ?? err?.message ?? err}`
  }
}, 800)

function onNotesUpdate(html: string) {
  notesHtml.value = html
  saveNotes(html)
}
</script>

<style scoped>
/* 對話錄的序／跋（楔子／收束）— 居中、襯線、留白，與下方月份格形成框架感 */
.dialogue-frame { max-width: 42rem; margin-left: auto; margin-right: auto; }
.dialogue-frame :deep(p) {
  font-family: '楷体', 'KaiTi', 'STKaiti', Georgia, serif;
  font-size: 16px; line-height: 2.05; color: #4b5563;
  text-align: justify; text-indent: 2em; margin: 0 0 0.7em;
}
.dialogue-frame :deep(p:first-child::first-letter) { color: #7c3aed; font-weight: 700; }
.dialogue-frame--coda { border-top: 1px solid #ede9fe; padding-top: 1.6em; }
.dialogue-frame--coda :deep(p) { color: #6b7280; font-size: 15px; }
/* 題詞（楔子前的引文）— 標題與序之間 */
.dialogue-frame :deep(.dialogue-epigraph) {
  border: 0; margin: 0 0 2.4em; padding: 0; text-align: center;
}
.dialogue-frame :deep(.dialogue-epigraph p) {
  font-family: '楷体', 'KaiTi', 'STKaiti', serif; font-style: normal;
  text-indent: 0; text-align: center; color: #6d5b8f;
  font-size: 15.5px; line-height: 2.1; letter-spacing: 0.03em;
}
.dialogue-frame :deep(.dialogue-epigraph cite) {
  display: block; margin-top: 0.9em; font-style: normal;
  font-size: 12.5px; color: #a78bba; letter-spacing: 0.02em;
}

.prose-notes :deep(p)   { margin: 0 0 0.4em; line-height: 1.75; color: #374151; font-size: 14px; }
.prose-notes :deep(h1)  { font-size: 1.5rem; font-weight: 700; margin: 0.6em 0 0.3em; color: #111827; }
.prose-notes :deep(h2)  { font-size: 1.2rem; font-weight: 600; margin: 0.5em 0 0.25em; color: #1f2937; }
.prose-notes :deep(h3)  { font-size: 1.05rem; font-weight: 600; margin: 0.4em 0 0.2em; color: #374151; }
.prose-notes :deep(ul)  { list-style: disc; padding-left: 1.4em; margin: 0.3em 0; }
.prose-notes :deep(ol)  { list-style: decimal; padding-left: 1.4em; margin: 0.3em 0; }
.prose-notes :deep(blockquote) { border-left: 3px solid #f59e0b; padding-left: 0.8em; color: #6b7280; margin: 0.4em 0; }

/* 修改建議書（迷你 markdown）+ 原文 共用排版 */
.doc-prose :deep(h2) { font-size: 1.25rem; font-weight: 700; color: #0f172a; margin: 1.4em 0 0.5em; }
.doc-prose :deep(h3) { font-size: 1.05rem; font-weight: 700; color: #1f2937; margin: 1.2em 0 0.4em; }
.doc-prose :deep(h4) { font-size: 0.95rem; font-weight: 600; color: #334155; margin: 1em 0 0.3em; }
.doc-prose :deep(h5), .doc-prose :deep(h6) { font-size: 0.9rem; font-weight: 600; color: #475569; margin: 0.8em 0 0.3em; }
.doc-prose :deep(p) { font-size: 0.9rem; line-height: 1.85; color: #374151; margin: 0 0 0.7em; }
.doc-prose :deep(ul) { list-style: disc; padding-left: 1.5em; margin: 0.4em 0 0.8em; }
.doc-prose :deep(ol) { list-style: decimal; padding-left: 1.6em; margin: 0.4em 0 0.8em; }
.doc-prose :deep(li) { font-size: 0.9rem; line-height: 1.8; color: #374151; margin: 0.15em 0; }
.doc-prose :deep(strong) { font-weight: 700; color: #0f172a; }
.doc-prose :deep(code) { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.82em; background: #f1f5f9; color: #be123c; padding: 0.1em 0.35em; border-radius: 4px; }
.doc-prose :deep(a) { color: #0d9488; text-decoration: underline; }
.doc-prose :deep(blockquote) { border-left: 3px solid #14b8a6; background: #f0fdfa; padding: 0.5em 0.9em; color: #475569; margin: 0.6em 0; border-radius: 0 6px 6px 0; font-size: 0.88rem; }
.doc-prose :deep(hr) { border: 0; border-top: 1px solid #e5e7eb; margin: 1.6em 0; }
.doc-prose :deep(table) { width: 100%; border-collapse: collapse; margin: 0.6em 0 1em; font-size: 0.85rem; }
.doc-prose :deep(th) { text-align: left; background: #f8fafc; border: 1px solid #e2e8f0; padding: 0.45em 0.7em; font-weight: 600; color: #334155; }
.doc-prose :deep(td) { border: 1px solid #e2e8f0; padding: 0.45em 0.7em; color: #475569; vertical-align: top; }

/* 碩士文稿正文 */
.thesis-prose { font-family: 'Georgia', 'Noto Serif TC', 'Source Han Serif TC', serif; }
.thesis-prose :deep(h2) { font-size: 1.25rem; font-weight: 700; text-align: center; margin: 2.2em 0 1.2em; letter-spacing: 0.06em; color: #111827; }
.thesis-prose :deep(h3) { font-size: 1.05rem; font-weight: 700; margin: 1.8em 0 0.8em; color: #1f2937; }
.thesis-prose :deep(h3.ttl) { text-align: center; }
.thesis-prose :deep(h4) { font-size: 0.95rem; font-weight: 600; margin: 1.3em 0 0.6em; color: #374151; }
.thesis-prose :deep(h5) { font-size: 0.9rem; font-weight: 600; margin: 1em 0 0.4em; color: #4b5563; }
.thesis-prose :deep(p) { font-size: 0.9rem; line-height: 2.1; text-indent: 2em; margin-bottom: 0.55rem; color: #1f2937; }
.thesis-prose :deep(p.en) { text-indent: 0; line-height: 1.9; font-family: 'Georgia', serif; }
.thesis-prose :deep(p.kw) { text-indent: 0; border-left: 3px solid #fda4af; padding-left: 1rem; margin: 1.2em 0; color: #374151; line-height: 1.8; }
.thesis-prose :deep(p.ref) { text-indent: 0; padding-left: 2em; font-size: 0.78rem; color: #64748b; line-height: 1.8; }
.thesis-prose :deep(sup) { font-size: 0.65em; color: #be123c; vertical-align: super; }

.paper-prose :deep(h3) { text-align: center; margin-top: 2em; }
.paper-prose :deep(p) { text-indent: 2em; line-height: 1.95; }
.paper-prose :deep(p.kw) { text-indent: 0; text-align: center; font-style: italic; color: #94a3b8; font-size: 0.8rem; }
.paper-prose :deep(p.ref) { text-indent: 0; padding-left: 1.4em; font-size: 0.82rem; color: #64748b; }
.paper-prose :deep(blockquote) { font-family: '標楷體', 'DFKai-SB', 'BiauKai', 'KaiTi', serif; }
.paper-prose :deep(sup) { font-size: 0.65em; color: #0d9488; vertical-align: super; }
</style>
