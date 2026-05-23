<template>
  <div class="min-h-screen bg-stone-50 text-stone-900 flex flex-col">
    <!-- Topbar -->
    <nav class="border-b border-stone-200 bg-white sticky top-0 z-40 flex-shrink-0">
      <div class="px-4 h-14 flex items-center justify-between gap-4">
        <div class="flex items-center gap-3 min-w-0 flex-1">
          <NuxtLink to="/ebook" class="text-stone-500 hover:text-stone-900 text-sm transition flex-shrink-0">← 書架</NuxtLink>
          <span class="text-stone-300">·</span>
          <!-- Always-visible TOC button (on lg+ it still toggles a slide-over;
               on narrow screens it's the only way to see the TOC). -->
          <button @click="tocDrawerOpen = !tocDrawerOpen"
            :class="['flex items-center gap-1 px-2 py-1 rounded-md text-xs transition border flex-shrink-0',
              tocDrawerOpen ? 'bg-stone-900 text-white border-stone-900' : 'bg-white text-stone-700 border-stone-200 hover:border-stone-400']"
            title="目錄">
            <span>📑</span><span class="hidden sm:inline">目錄</span>
          </button>
          <span class="text-sm font-medium text-stone-900 truncate">{{ ebook?.title }}</span>
          <span v-if="ebook?.author" class="text-stone-400 text-sm hidden md:inline truncate">／{{ ebook.author }}</span>
        </div>

        <div class="flex items-center gap-2 flex-shrink-0">
          <button @click="goPage(currentPage - 1)" :disabled="currentPage <= 1"
            class="w-8 h-8 flex items-center justify-center rounded-lg bg-stone-100 hover:bg-stone-200 disabled:opacity-30 transition">‹</button>
          <input v-model.number="jumpPage" @keyup.enter="goPage(jumpPage)" type="number" :min="1" :max="ebook?.total_pages ?? 1"
            class="w-14 bg-white border border-stone-200 rounded-lg px-2 py-1 text-center text-sm focus:outline-none focus:border-blue-500" />
          <span class="text-xs text-stone-400">/ {{ ebook?.total_pages }}</span>
          <button @click="goPage(currentPage + 1)" :disabled="currentPage >= (ebook?.total_pages ?? 1)"
            class="w-8 h-8 flex items-center justify-center rounded-lg bg-stone-100 hover:bg-stone-200 disabled:opacity-30 transition">›</button>
        </div>

        <div class="flex items-center gap-2 flex-1 justify-end">
          <!-- 中 / 對照 / 英 切換（僅在 chunk 有原文時顯示） -->
          <div v-if="pageSourceText" class="inline-flex bg-stone-100 rounded-lg p-0.5 text-xs gap-0.5">
            <button @click="setViewMode('zh')"
              :class="['px-2.5 py-1 rounded-md transition',
                viewMode==='zh' ? 'bg-white shadow-sm text-stone-900 font-medium' : 'text-stone-500 hover:text-stone-900']">中</button>
            <button @click="setViewMode('bi')"
              :class="['px-2.5 py-1 rounded-md transition',
                viewMode==='bi' ? 'bg-white shadow-sm text-stone-900 font-medium' : 'text-stone-500 hover:text-stone-900']">中英</button>
            <button @click="setViewMode('en')"
              :class="['px-2.5 py-1 rounded-md transition',
                viewMode==='en' ? 'bg-white shadow-sm text-stone-900 font-medium' : 'text-stone-500 hover:text-stone-900']">英</button>
          </div>
          <input v-model="pageSearch" type="text" placeholder="頁內搜尋…"
            class="hidden sm:block bg-white border border-stone-200 rounded-lg px-3 py-1.5 text-sm w-40 focus:outline-none focus:border-blue-500" />
          <button @click="cycleReadingStatus"
            :title="readingStatus === 'reading' ? '點擊：標記已讀'
                  : readingStatus === 'read'    ? '點擊：從書櫃移除'
                  :                                '點擊：加入閱讀中'"
            :class="['hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition border',
              readingStatus === 'reading' ? 'bg-blue-100 border-blue-300 text-blue-800'
              : readingStatus === 'read'  ? 'bg-emerald-100 border-emerald-300 text-emerald-800'
              :                              'bg-white border-stone-200 hover:border-blue-300 text-stone-600']">
            <span>{{ readingStatus === 'reading' ? '📖' : readingStatus === 'read' ? '✅' : '📚' }}</span>
            <span>{{ readingStatus === 'reading' ? '閱讀中' : readingStatus === 'read' ? '已讀' : '加入書櫃' }}</span>
          </button>
          <button v-if="readingStatus === 'reading'" @click="addTodayBookmark"
            title="標記今日讀到這裡"
            class="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition border bg-white border-stone-200 hover:border-purple-400 text-stone-600">
            <span>📅</span><span>今日讀到這裡</span>
          </button>
          <button @click="annotationsPanelOpen = !annotationsPanelOpen"
            :class="['hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition border',
              annotationsPanelOpen ? 'bg-amber-100 border-amber-300 text-amber-800' : 'bg-white border-stone-200 hover:border-amber-300 text-stone-600']">
            <span>📝</span><span>標記 {{ bookAnnotations.length }}</span>
          </button>
        </div>
      </div>
    </nav>

    <div class="flex flex-1 overflow-hidden relative">
      <!-- TOC backdrop (only on narrow screens when drawer open) -->
      <div v-if="tocDrawerOpen" @click="tocDrawerOpen = false"
        class="lg:hidden fixed inset-0 bg-stone-900/40 z-30 transition-opacity"></div>

      <!-- Left TOC sidebar — slide-over on narrow, in-flow on lg+ when open -->
      <aside :class="['border-r border-stone-200 bg-white overflow-y-auto flex-shrink-0 transition-transform duration-200',
          tocDrawerOpen
            ? 'fixed lg:relative inset-y-0 left-0 top-14 lg:top-0 w-72 lg:w-64 z-40 translate-x-0 shadow-xl lg:shadow-none'
            : 'fixed lg:relative -translate-x-full w-0 lg:w-0 lg:opacity-0 lg:overflow-hidden']">
        <div class="p-3">
          <div class="text-xs uppercase text-stone-400 mb-2 px-2 tracking-wider">目錄</div>
          <div v-if="!toc.length && pageLoading" class="text-stone-400 text-sm px-2 py-2">載入中…</div>

          <!-- Front matter (no volume). For books where the standardize step
               failed to extract volumes, ALL chapters land here — so we
               still need to show the nested section anchors under the
               current chapter.
               TOC items use real <a href> so right-click → 開新分頁 works. -->
          <div v-if="frontMatter.length" class="space-y-0.5 mb-3">
            <template v-for="entry in frontMatter" :key="entry.chunk_index">
              <div class="group relative">
                <a :href="`?page=${entry.chunk_index + 1}`"
                  @click.prevent="goPage(entry.chunk_index + 1)"
                  :title="entry.title"
                  :class="[tocBtnCls(entry), 'w-full flex items-center gap-1.5 no-underline']">
                  <span class="flex-1 text-left truncate">{{ entry.title }}</span>
                  <span v-if="bookmarkByChunk.get(entry.chunk_index)"
                    class="text-[10px] px-1 py-px rounded bg-purple-100 text-purple-700 font-medium flex-shrink-0">
                    📅 {{ fmtBookmarkDate(bookmarkByChunk.get(entry.chunk_index)!.created_at) }}
                  </span>
                </a>
                <button v-if="bookmarkByChunk.get(entry.chunk_index)"
                  @click.stop="deleteBookmark(bookmarkByChunk.get(entry.chunk_index)!.id)"
                  title="移除書籤"
                  class="absolute right-1 top-1/2 -translate-y-1/2 hidden group-hover:flex w-4 h-4 items-center justify-center rounded text-purple-700 hover:bg-purple-200 text-xs">×</button>
              </div>
              <!-- Section anchors for the currently-open chapter -->
              <div v-if="entry.chunk_index === currentPage - 1 && entry.sections?.length"
                class="space-y-px ml-1 border-l border-stone-200 pl-2 pb-1 mb-1">
                <a v-for="sec in entry.sections" :key="sec.anchor_id"
                  :href="`#${sec.anchor_id}`"
                  @click.prevent="scrollToSection(sec.anchor_id)"
                  :title="sec.title"
                  :class="['block w-full text-left py-1 rounded text-xs text-stone-500 hover:bg-stone-50 hover:text-stone-900 truncate no-underline',
                    sec.level === 3 ? 'pl-2' : 'pl-5 text-[11px] text-stone-400']">
                  <span class="text-stone-300 mr-1">›</span>{{ sec.title }}
                </a>
              </div>
            </template>
          </div>

          <!-- Volumes (collapsible). For volumes with a single page the
               whole volume row becomes the link (no expansion, no
               redundant child entry that would just duplicate the
               volume name). Multi-page volumes keep the expand/toggle
               behavior and show their pages as children. -->
          <div v-for="v in volumes" :key="v.name" class="mb-1">
            <a v-if="v.entries.length === 1"
              :href="`?page=${v.entries[0].chunk_index + 1}`"
              @click.prevent="goPage(v.entries[0].chunk_index + 1)"
              :title="v.name"
              :class="[
                'w-full flex items-center gap-1 px-2 py-2 rounded text-sm font-medium hover:bg-stone-50 transition no-underline',
                currentPage - 1 === v.entries[0].chunk_index
                  ? 'bg-blue-50 text-blue-700' : 'text-stone-900'
              ]">
              <span class="text-stone-300 text-xs w-3 inline-block">·</span>
              <span class="flex-1 text-left truncate">{{ shortVolumeName(v.name) }}</span>
            </a>
            <button v-else @click="toggleVolume(v.name)"
              class="w-full flex items-center gap-1 px-2 py-2 rounded text-sm font-medium text-stone-900 hover:bg-stone-50 transition">
              <span class="text-stone-400 text-xs w-3 inline-block">{{ expandedVolumes.has(v.name) ? '▾' : '▸' }}</span>
              <span class="flex-1 text-left truncate">{{ shortVolumeName(v.name) }}</span>
              <span class="text-xs text-stone-400">{{ v.entries.length }}</span>
            </button>
            <div v-if="v.entries.length > 1 && expandedVolumes.has(v.name)" class="space-y-0.5 mt-0.5">
              <template v-for="entry in v.entries" :key="entry.chunk_index">
                <div class="group relative">
                  <a :href="`?page=${entry.chunk_index + 1}`"
                    @click.prevent="goPage(entry.chunk_index + 1)"
                    :title="entry.title"
                    :class="[tocBtnCls(entry), 'w-full flex items-center gap-1.5 no-underline']">
                    <span class="flex-1 text-left truncate">{{ stripVolumePrefix(entry.title, v.name) }}</span>
                    <span v-if="bookmarkByChunk.get(entry.chunk_index)"
                      class="text-[10px] px-1 py-px rounded bg-purple-100 text-purple-700 font-medium flex-shrink-0">
                      📅 {{ fmtBookmarkDate(bookmarkByChunk.get(entry.chunk_index)!.created_at) }}
                    </span>
                  </a>
                  <button v-if="bookmarkByChunk.get(entry.chunk_index)"
                    @click.stop="deleteBookmark(bookmarkByChunk.get(entry.chunk_index)!.id)"
                    title="移除書籤"
                    class="absolute right-1 top-1/2 -translate-y-1/2 hidden group-hover:flex w-4 h-4 items-center justify-center rounded text-purple-700 hover:bg-purple-200 text-xs">×</button>
                </div>
                <!-- Nested section anchors, only for current chapter -->
                <div v-if="entry.chunk_index === currentPage - 1 && entry.sections?.length"
                  class="space-y-px ml-1 border-l border-stone-200 pl-2 pb-1">
                  <a v-for="sec in entry.sections" :key="sec.anchor_id"
                    :href="`#${sec.anchor_id}`"
                    @click.prevent="scrollToSection(sec.anchor_id)"
                    :class="['block w-full text-left py-1 rounded text-xs text-stone-500 hover:bg-stone-50 hover:text-stone-900 truncate no-underline',
                      sec.level === 3 ? 'pl-2' : 'pl-5 text-[11px] text-stone-400']">
                    <span class="text-stone-300 mr-1">›</span>{{ sec.title }}
                  </a>
                </div>
              </template>
            </div>
          </div>
        </div>
      </aside>

      <!-- Reading area -->
      <div class="flex-1 overflow-y-auto bg-stone-50" ref="scrollEl">
        <article :class="['ebook-article mx-auto px-12 py-14 shadow-sm rounded-lg my-8 border border-stone-200',
          viewMode === 'bi' && pageSourceText ? 'max-w-7xl' : 'max-w-4xl']">
          <div v-if="pageLoading" class="space-y-3 animate-pulse">
            <div v-for="i in 8" :key="i" :class="['h-4 bg-stone-200 rounded', i % 3 === 0 ? 'w-3/4' : 'w-full']"></div>
          </div>

          <template v-else-if="pageContent || pageSourceText">
            <!-- ── COVER PAGE (chunk 0 / chapter_path == 封面) ──
                 Replaces the markdown chunk content with a curated layout:
                 image + title + subtitle + author + translator + publisher.
                 The bare `## 封面 / 基督教要義 / 加爾文` content is hidden
                 since the structured layout already shows everything. -->
            <div v-if="isCoverPage" class="cover-hero group/cover">
              <div v-if="ebook?.cover_url && !coverEditOpen" class="cover-image-wrap">
                <img :src="ebook.cover_url" :alt="ebook?.title" class="cover-image" />
                <button @click="openCoverEdit" title="換封面" class="cover-edit-btn">✏</button>
              </div>
              <div v-else-if="!ebook?.cover_url && !coverEditOpen"
                class="cover-placeholder" @click="openCoverEdit">
                <div class="cover-placeholder-icon">📕</div>
                <div class="cover-placeholder-title">封面圖片</div>
                <div class="cover-placeholder-sub">點此貼上網址</div>
              </div>
              <div v-if="coverEditOpen" class="cover-editor">
                <div class="text-sm text-stone-700 font-medium mb-1">封面圖片網址</div>
                <input v-model="coverUrlDraft" type="url" placeholder="https://..."
                  class="w-full text-sm border border-stone-300 rounded-md px-3 py-2 focus:outline-none focus:border-blue-500"
                  @keyup.enter="saveCoverUrl"
                  @keyup.escape="coverEditOpen = false" />
                <div class="flex gap-2 mt-2">
                  <button @click="saveCoverUrl" :disabled="coverSaving"
                    class="flex-1 px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-500 disabled:opacity-50">
                    {{ coverSaving ? '儲存中…' : '儲存' }}
                  </button>
                  <button @click="coverEditOpen = false"
                    class="px-3 py-1.5 text-sm bg-stone-100 text-stone-600 rounded-md hover:bg-stone-200">取消</button>
                  <button v-if="ebook?.cover_url" @click="clearCoverUrl"
                    class="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-md">清除</button>
                </div>
                <p class="text-xs text-stone-400 mt-2">到博客來/校園書房/誠品 → 右鍵封面 → 複製圖片網址 → 貼上</p>
              </div>

              <!-- Decorative diamond -->
              <div class="cover-divider"><span>❦</span></div>

              <h1 class="cover-title">{{ ebook?.title }}</h1>
              <p v-if="ebook?.subtitle" class="cover-subtitle">{{ ebook.subtitle }}</p>
              <p v-if="ebook?.original_title" class="cover-original-title">
                <em>{{ ebook.original_title }}</em>
              </p>

              <div class="cover-author-block">
                <p class="cover-author">
                  <span class="cover-author-label">著</span>
                  {{ ebook?.original_author || ebook?.author }}
                  <span v-if="ebook?.author_en" class="cover-author-en"> ({{ ebook.author_en }})</span>
                </p>
                <p v-if="ebook?.translator" class="cover-translator">
                  <span class="cover-author-label">譯</span>
                  {{ ebook.translator }}
                </p>
              </div>

              <div v-if="ebook?.publisher || ebook?.publication_year || ebook?.original_publish_year" class="cover-imprint">
                <span v-if="ebook?.publisher">{{ ebook.publisher }}</span>
                <span v-if="ebook?.publisher && ebook?.publication_year"> · </span>
                <span v-if="ebook?.publication_year">{{ ebook.publication_year }}</span>
                <span v-if="ebook?.original_publish_year && ebook?.original_publish_year !== ebook?.publication_year">
                  （原著 {{ ebook.original_publish_year }}）
                </span>
              </div>
            </div>

            <!-- ── NORMAL PAGE (any chunk that isn't the cover) ──
                 Breadcrumb shows the parent work (volume) as primary
                 context; chapter title sits secondary. Book title is
                 dropped — it's already in the topbar. -->
            <template v-else>
              <div class="text-stone-400 mb-10 flex items-baseline gap-2">
                <span v-if="pageVolume" class="text-sm font-medium text-stone-700 tracking-tight">{{ pageVolume }}</span>
                <span v-if="pageVolume && pageChapter" class="text-stone-300">›</span>
                <span class="text-xs uppercase tracking-wider">
                  {{ cleanChapterLabel || `第 ${currentPage} 段` }}
                </span>
              </div>
            </template>

            <!-- View-mode-specific content — fully suppressed on cover page. -->
            <template v-if="!isCoverPage">
              <!-- 中文（單欄）-->
              <div v-if="effectiveViewMode === 'zh'"
                ref="contentEl"
                class="ebook-prose"
                v-html="markdownHtml"
                @mouseup="onTextSelectionEnd"
                @click="onContentClick"></div>

              <!-- 英文原文（單欄，無標註功能）-->
              <div v-else-if="effectiveViewMode === 'en'"
                class="ebook-prose ebook-prose-en"
                v-html="sourceHtml"></div>

              <!-- 中英對照（逐段對齊雙欄）-->
              <div v-else ref="contentEl"
                class="bilingual-rows"
                @mouseup="onTextSelectionEnd"
                @click="onContentClick">
                <div v-for="(pair, idx) in paragraphPairs" :key="idx"
                  class="grid grid-cols-1 lg:grid-cols-[2fr_3fr] gap-x-8 gap-y-1 py-1">
                  <div class="ebook-prose" v-html="pair.zh"></div>
                  <div class="ebook-prose ebook-prose-en lg:border-l lg:border-stone-100 lg:pl-8"
                    v-html="pair.en"></div>
                </div>
              </div>
            </template>

            <div class="flex justify-between mt-16 pt-6 border-t border-stone-200">
              <button @click="goPage(currentPage - 1)" :disabled="currentPage <= 1"
                class="px-5 py-2 bg-white border border-stone-200 hover:border-blue-400 hover:text-blue-700 disabled:opacity-30 rounded-lg text-sm transition">← 上一段</button>
              <button @click="goPage(currentPage + 1)" :disabled="currentPage >= (ebook?.total_pages ?? 1)"
                class="px-5 py-2 bg-white border border-stone-200 hover:border-blue-400 hover:text-blue-700 disabled:opacity-30 rounded-lg text-sm transition">下一段 →</button>
            </div>
          </template>

          <div v-else class="text-center py-20 text-stone-400">此段無內容</div>
        </article>
      </div>

      <!-- Right annotations panel -->
      <aside v-if="annotationsPanelOpen"
        class="w-80 border-l border-stone-200 bg-white overflow-y-auto flex-shrink-0 hidden lg:block">
        <div class="p-4">
          <div class="flex items-center justify-between mb-3">
            <div class="text-sm font-semibold text-stone-900">📝 我的標記</div>
            <span class="text-xs text-stone-400">{{ bookAnnotations.length }} 條</span>
          </div>
          <p v-if="!bookAnnotations.length" class="text-stone-400 text-sm py-8 text-center">
            選一段文字標螢光，就會出現在這裡
          </p>
          <div class="space-y-2.5">
            <div v-for="a in sortedBookAnnotations" :key="a.id"
              class="group bg-stone-50 hover:bg-amber-50 border border-stone-200 hover:border-amber-300 rounded-lg p-3 transition">
              <button @click="jumpToAnnotation(a)"
                class="w-full text-left">
                <div class="flex items-start gap-2 mb-1.5">
                  <span class="w-3 h-3 rounded-full mt-1 flex-shrink-0 border border-stone-300"
                    :style="{ background: COLOR_BG[a.color] || COLOR_BG.yellow }"></span>
                  <p class="text-sm text-stone-800 leading-snug line-clamp-3 flex-1">{{ a.selected_text }}</p>
                </div>
                <p v-if="a.note" class="text-xs text-stone-600 italic mb-1.5 pl-5">📌 {{ a.note }}</p>
                <p class="text-xs text-stone-400 pl-5">{{ chunkLabel(a.chunk_index) }}<span v-if="a.excerpt_id" class="text-blue-500">　·　已存書摘</span></p>
              </button>
              <div class="flex gap-1 mt-2 pt-2 border-t border-stone-100 opacity-0 group-hover:opacity-100 transition">
                <button @click="openNoteEditor(a)" class="text-xs px-2 py-1 hover:bg-stone-200 rounded text-stone-600">註記</button>
                <button @click="deleteAnnotation(a.id)" class="text-xs px-2 py-1 hover:bg-red-100 text-red-600 rounded">刪除</button>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>

    <!-- Selection popup (when text selected in reader) -->
    <div v-if="selectionPopup.show"
      data-selection-popup
      class="fixed bg-white shadow-xl border border-stone-200 rounded-xl px-2 py-2 flex items-center gap-1 z-50"
      :style="{ top: selectionPopup.y + 'px', left: selectionPopup.x + 'px' }">
      <button v-for="c in HIGHLIGHT_COLORS" :key="c.name"
        @click="saveAnnotationFromSelection(c.name)"
        :title="c.label"
        class="w-7 h-7 rounded-full border border-stone-300 hover:scale-110 transition"
        :style="{ background: c.bg }"></button>
      <div class="w-px h-6 bg-stone-200 mx-1"></div>
      <button @click="openNewNoteFromSelection"
        class="px-2.5 py-1.5 text-xs bg-stone-100 hover:bg-stone-200 rounded-lg transition whitespace-nowrap">+ 註記</button>
      <button @click="openExcerptModalFromSelection"
        class="px-2.5 py-1.5 text-xs bg-blue-600 text-white hover:bg-blue-500 rounded-lg transition whitespace-nowrap">+ 書摘</button>
    </div>

    <!-- Mark click popup (when clicking an existing highlight) -->
    <div v-if="markPopup.show"
      data-mark-popup
      class="fixed bg-white shadow-xl border border-stone-200 rounded-xl px-2 py-2 flex items-center gap-1 z-50"
      :style="{ top: markPopup.y + 'px', left: markPopup.x + 'px' }">
      <button v-for="c in HIGHLIGHT_COLORS" :key="c.name"
        @click="changeAnnotationColor(c.name)"
        :title="`改為${c.label}`"
        class="w-6 h-6 rounded-full border border-stone-300 hover:scale-110 transition"
        :style="{ background: c.bg }"></button>
      <div class="w-px h-5 bg-stone-200 mx-1"></div>
      <button @click="openNoteEditorForMark" class="px-2.5 py-1 text-xs hover:bg-stone-100 rounded">註記</button>
      <button @click="deleteCurrentMark" class="px-2.5 py-1 text-xs text-red-600 hover:bg-red-50 rounded">刪除</button>
    </div>

    <!-- Note editor modal (auto-save) -->
    <div v-if="noteEditor.show" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md space-y-4 border border-stone-200 shadow-xl">
        <div class="flex items-center justify-between">
          <h3 class="font-semibold text-lg text-stone-900">{{ noteEditor.editingExisting ? '編輯註記' : '新增註記' }}</h3>
          <span class="text-xs flex items-center gap-1.5"
            :class="{
              'text-stone-400': noteEditor.status === '' || noteEditor.status === 'saved',
              'text-blue-600': noteEditor.status === 'saving',
              'text-red-600': noteEditor.status === 'error',
            }">
            <span v-if="noteEditor.status === 'saving'">● 儲存中…</span>
            <span v-else-if="noteEditor.status === 'saved'">✓ 已儲存</span>
            <span v-else-if="noteEditor.status === 'error'">⚠ {{ noteEditor.errorMsg || '儲存失敗' }}</span>
            <span v-else class="text-stone-300">未變更</span>
          </span>
        </div>
        <div class="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-stone-700 max-h-32 overflow-y-auto whitespace-pre-wrap leading-relaxed">{{ noteEditor.text }}</div>
        <textarea v-model="noteEditor.note" placeholder="寫下你的想法…（自動儲存）" rows="4"
          class="w-full border border-stone-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500 resize-none"></textarea>
        <div class="flex justify-end">
          <button @click="closeNoteEditor"
            class="px-5 py-2 bg-stone-900 hover:bg-stone-700 text-white rounded-lg text-sm transition">完成</button>
        </div>
      </div>
    </div>

    <!-- Toast (errors / status) -->
    <Transition name="fade">
      <div v-if="toast.show" class="fixed bottom-6 left-1/2 -translate-x-1/2 z-[60] pointer-events-none">
        <div :class="['px-4 py-3 rounded-lg shadow-xl text-sm font-medium pointer-events-auto',
          toast.type === 'error' ? 'bg-red-600 text-white' : 'bg-stone-900 text-white']">
          {{ toast.message }}
        </div>
      </div>
    </Transition>

    <!-- Save excerpt modal -->
    <div v-if="excerptModal.show" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-2xl p-6 w-full max-w-lg space-y-4 border border-stone-200 shadow-xl">
        <h3 class="font-semibold text-lg text-stone-900">存到書摘圖書館</h3>
        <div class="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-stone-700 max-h-32 overflow-y-auto whitespace-pre-wrap leading-relaxed">{{ excerptModal.content }}</div>
        <input v-model="excerptModal.title" placeholder="為這段書摘命名（必填）"
          class="w-full border border-stone-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500" />
        <div class="flex items-center gap-2">
          <span class="text-xs text-stone-500">螢光顏色：</span>
          <button v-for="c in HIGHLIGHT_COLORS" :key="c.name"
            @click="excerptModal.color = c.name"
            :class="['w-6 h-6 rounded-full border-2 transition',
              excerptModal.color === c.name ? 'border-stone-700 scale-110' : 'border-stone-300 hover:scale-110']"
            :style="{ background: c.bg }" :title="c.label"></button>
        </div>
        <p class="text-xs text-stone-400">將連結至《{{ ebook?.title }}》· {{ pageChapter || `第 ${currentPage} 段` }}</p>
        <div class="flex gap-3">
          <button @click="confirmSaveExcerpt"
            :disabled="!excerptModal.title.trim() || excerptModal.saving"
            class="flex-1 py-2.5 bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-40 rounded-xl text-sm font-medium transition">
            {{ excerptModal.saving ? '儲存中…' : '儲存到書摘圖書館' }}
          </button>
          <button @click="excerptModal.show = false"
            class="px-4 py-2.5 bg-stone-100 hover:bg-stone-200 rounded-xl text-sm transition">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });

interface TocSection { anchor_id: string; title: string; level: number }
interface TocEntry {
  chunk_index: number;
  title: string;
  level: number;
  volume?: string | null;
  sections?: TocSection[];
}
interface VolumeGroup { name: string; entries: TocEntry[] }
interface Annotation {
  id: string;
  ebook_id: string;
  chunk_index: number;
  selected_text: string;
  context_before?: string | null;
  context_after?: string | null;
  note?: string | null;
  color: string;
  excerpt_id?: string | null;
  created_at?: string;
}
interface Bookmark { id: string; chunk_index: number; created_at: string }
type ReadingStatus = "reading" | "read" | null;

const HIGHLIGHT_COLORS = [
  { name: "yellow", label: "黃", bg: "#FEF08A" },
  { name: "green",  label: "綠", bg: "#BBF7D0" },
  { name: "blue",   label: "藍", bg: "#BFDBFE" },
  { name: "pink",   label: "粉", bg: "#FBCFE8" },
];
const COLOR_BG: Record<string, string> = Object.fromEntries(HIGHLIGHT_COLORS.map(c => [c.name, c.bg]));

const supabase = useSupabaseClient();
const router = useRouter();
const route = useRoute();
const ebookId = route.params.id as string;

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) { router.push("/login"); return null; }
  return session.access_token;
}

// ── State ──
const ebook = ref<any>(null);
const toc = ref<TocEntry[]>([]);
const currentPage = ref(parseInt(route.query.page as string ?? "1") || 1);
const jumpPage = ref(currentPage.value);
const pageContent = ref("");
const pageSourceText = ref<string | null>(null);
const pageChapter = ref<string | null>(null);
const pageLoading = ref(false);

// View mode for bilingual books. "zh" = 中譯, "bi" = 對照, "en" = 原文.
// Persisted across pages + reloads; gracefully degrades to "zh" if a chunk
// has no source_text (e.g. mid-book transition between bilingual and
// monolingual books, or a chunk that pre-dates the source-text schema).
type ViewMode = "zh" | "bi" | "en";
const viewMode = ref<ViewMode>("zh");
// Tracks whether localStorage had an explicit preference at load time.
// When false (first visit to any ebook), we auto-default to 'bi' the first
// time we see a chunk with source_text — so AI-translated books open in
// side-by-side mode by default. User clicking the toggle locks in their
// choice via localStorage and disables auto-switching.
const viewModeUserChosen = ref(false);
const effectiveViewMode = computed<ViewMode>(() =>
  !pageSourceText.value ? "zh" : viewMode.value
);
function setViewMode(m: ViewMode) {
  viewMode.value = m;
  viewModeUserChosen.value = true;
  try { localStorage.setItem("ebook-viewMode", m); } catch { /* private mode */ }
}
// Auto-default to bilingual when first bilingual chunk loads (until user
// explicitly picks a mode via the toggle).
watch(pageSourceText, (src) => {
  if (src && !viewModeUserChosen.value && viewMode.value === "zh") {
    viewMode.value = "bi";
  }
});
const pageSearch = ref("");
const annotations = ref<Annotation[]>([]);
const bookAnnotations = ref<Annotation[]>([]);
const expandedVolumes = ref<Set<string>>(new Set());
const annotationsPanelOpen = ref(false);
// TOC drawer: defaults open on desktop (lg+), can be toggled via topbar
// 📑 button on any screen. We start open and let the user close it.
const tocDrawerOpen = ref(true);
const lastUsedColor = ref<string>("yellow");
const contentEl = ref<HTMLDivElement | null>(null);
const scrollEl = ref<HTMLElement | null>(null);

// Bookshelf state — user's reading status for this book + their date bookmarks.
const readingStatus = ref<ReadingStatus>(null);
const bookmarks = ref<Bookmark[]>([]);
// Quick chunk_index → date map for the TOC sidebar badges.
const bookmarkByChunk = computed(() => {
  const m = new Map<number, Bookmark>();
  // bookmarks are pre-sorted desc by created_at server-side; keep latest per chunk.
  for (const b of bookmarks.value) {
    if (!m.has(b.chunk_index)) m.set(b.chunk_index, b);
  }
  return m;
});
function fmtBookmarkDate(iso: string): string {
  const d = new Date(iso);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

// ── Toast for errors / status ──
const toast = ref({ show: false, message: "", type: "info" as "info" | "error" });
let toastTimer: any = null;
function showToast(message: string, type: "info" | "error" = "info") {
  toast.value = { show: true, message, type };
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.value.show = false; }, type === "error" ? 5000 : 2500);
}

// Clean chapter label for breadcrumb — strip `[^N]` markdown footnote
// refs that bled into the chapter heading during standardize.
const cleanChapterLabel = computed(() =>
  (pageChapter.value || "").replace(/\[\^\d+\]/g, "").trim()
);
// Volume (parent work) the current chunk belongs to — populated by polish
// step (`volume` field on chunks). Used as the primary breadcrumb label
// since it gives reader-relevant context (which letter/treatise they're in)
// vs the duplicated book title.
const pageVolume = computed<string | null>(() => {
  const here = toc.value.find(e => e.chunk_index === currentPage.value - 1);
  return here?.volume ?? null;
});

// ── TOC grouping ──
const frontMatter = computed(() => toc.value.filter(e => !e.volume));
const volumes = computed<VolumeGroup[]>(() => {
  const map = new Map<string, TocEntry[]>();
  for (const e of toc.value) {
    if (!e.volume) continue;
    if (!map.has(e.volume)) map.set(e.volume, []);
    map.get(e.volume)!.push(e);
  }
  return [...map].map(([name, entries]) => ({ name, entries }));
});

function shortVolumeName(name: string): string {
  // Strip the book title prefix from volume name for compact display
  const t = ebook.value?.title;
  if (t && name.startsWith(t + "：")) return name.slice(t.length + 1);
  if (t && name.startsWith(t + ":")) return name.slice(t.length + 1);
  return name;
}
// Strip the volume-name prefix from an entry title so multi-page entries
// under a volume read「第1-10章」instead of「致丟格那妥書 第1-10章」(redundant
// because the volume name sits in the parent row right above).
function stripVolumePrefix(entryTitle: string, volumeName: string): string {
  if (entryTitle.startsWith(volumeName)) {
    return entryTitle.slice(volumeName.length).trim().replace(/^[—－·,，:：]+\s*/, "");
  }
  return entryTitle;
}

function toggleVolume(name: string) {
  const next = new Set(expandedVolumes.value);
  if (next.has(name)) next.delete(name);
  else next.add(name);
  expandedVolumes.value = next;
}

function tocBtnCls(entry: TocEntry) {
  const isActive = entry.chunk_index === currentPage.value - 1;
  return [
    "w-full text-left py-1.5 rounded text-sm transition truncate block",
    isActive ? "bg-blue-50 text-blue-700 font-medium" : "text-stone-600 hover:bg-stone-50",
    entry.level === 2 ? "pl-3" : entry.level === 3 ? "pl-7" : "pl-11 text-xs",
  ];
}

// ── Markdown render ──
function escapeHtml(s: string) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
// Inline markdown formatter. `chunkIdx` (when provided) is used to mint
// per-chunk footnote ref anchors so each `[^N]` becomes a clickable sup
// linked to the chunk's footnote section, with a back-link from the
// footnote body to here.
function inlineFmt(s: string, chunkIdx: number | null = null) {
  let out = s.replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>")
          // *italic* — split by Latin presence:
          //   - Latin-containing → Georgia italic (English book titles,
          //     Latin/German terms, foreign-language quotes)
          //   - Pure CJK         → regular <em> (rare but possible)
          .replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, (_, lead, inner) =>
            /[A-Za-z]/.test(inner)
              ? `${lead}<em class="book-title-en">${inner}</em>`
              : `${lead}<em>${inner}</em>`
          )
          // <u>X</u> survives escapeHtml as &lt;u&gt;X&lt;/u&gt; — restore the tag here
          .replace(/&lt;u&gt;([^<]+?)&lt;\/u&gt;/g, "<u>$1</u>")
          // English book titles 《Some Title》 → italic Latin serif. Pure-CJK
          // titles like 《創世記》 stay upright.
          .replace(/《([^《》]*[A-Za-z][^《》]*)》/g, "<em class=\"book-title-en\">《$1》</em>");

  // Footnote refs `[^N]` → clickable superscript with bidirectional anchor.
  // Each inline ref gets `id="fnref-{chunk}-{N}"`, links to `#fn-{chunk}-{N}`.
  // Footnote body in `renderMarkdown` adds the matching id + back-link.
  if (chunkIdx !== null) {
    out = out.replace(/\[\^(\d+)\]/g, (_, n) =>
      `<sup class="footnote-ref" id="fnref-${chunkIdx}-${n}">` +
      `<a href="#fn-${chunkIdx}-${n}" title="跳到註 ${n}">${n}</a></sup>`
    );
  }
  // Print page markers `{{p:N}}` (injected by extract_epub_extras.py).
  // Rendered as tiny inline pill that doesn't disrupt the prose but lets
  // citation generation pick up the original page number under the cursor.
  out = out.replace(/\{\{p:(\d+)\}\}/g, (_, n) =>
    `<span class="page-marker" data-page="${n}" title="原書頁碼 ${n}">[頁${n}]</span>`
  );
  return out;
}
// Render markdown to HTML. `chunkIndex` (when provided) is used to mint
// stable anchor ids on h3/h4 — these match what `loadToc` emits, so the
// TOC sidebar can scrollIntoView to a section within the current chapter.
//
// Footnote detection: a paragraph that's just 15+ em-dashes / hyphens
// (`————————————————…`) marks the start of the chunk's footnote section.
// Everything after is rendered inside <section class="footnotes"> with
// smaller font, and each `(N) text...` paragraph gets `id="fn-{chunk}-{N}"`
// so URL hashes and TOC refs can link directly.
function renderMarkdown(md: string, chunkIndex: number | null = null): string {
  const blocks = md.split(/\n{2,}/);
  const out: string[] = [];
  let subSeq = 0;
  let inFootnotes = false;
  for (let block of blocks) {
    block = block.trim();
    if (!block) continue;
    // Footnote separator — long horizontal run of em-dashes / hyphens.
    if (/^[—－\-]{15,}$/.test(block)) {
      if (!inFootnotes) {
        out.push('<section class="footnotes" aria-label="註釋">');
        out.push('<div class="footnotes-label">註　釋</div>');
        inFootnotes = true;
      } else {
        out.push('<hr class="footnote-divider">');
      }
      continue;
    }
    if (/^-{3,}$/.test(block)) { out.push("<hr>"); continue; }
    const escaped = escapeHtml(block);
    let h: RegExpMatchArray | null;
    // Heading detection — match HEADING LINE separately from the rest of
    // the block. CCEL EPUBs wrap long headings across multiple lines with
    // single \n (e.g. `#### Chapter I.—After the salutation, the\nwriter
    // declares...`), so `.+$` without /m fails to match and the whole
    // block falls through to <p>{escaped}</p> showing raw `####`.
    // The fix: capture (heading first-line, rest-of-block) and emit both.
    if ((h = escaped.match(/^####\s+([^\n]+)(?:\n([\s\S]*))?$/))) {
      const id = chunkIndex !== null ? ` id="sec-${chunkIndex}-${subSeq}"` : "";
      subSeq++;
      out.push(`<h4${id}>${inlineFmt(h[1].trim(), chunkIndex)}</h4>`);
      if (h[2]?.trim()) {
        out.push(`<p>${inlineFmt(h[2].trim(), chunkIndex).replace(/\n/g, " ")}</p>`);
      }
    }
    else if ((h = escaped.match(/^###\s+([^\n]+)(?:\n([\s\S]*))?$/))) {
      const id = chunkIndex !== null ? ` id="sec-${chunkIndex}-${subSeq}"` : "";
      subSeq++;
      out.push(`<h3${id}>${inlineFmt(h[1].trim(), chunkIndex)}</h3>`);
      if (h[2]?.trim()) {
        out.push(`<p>${inlineFmt(h[2].trim(), chunkIndex).replace(/\n/g, " ")}</p>`);
      }
    }
    else if ((h = escaped.match(/^##\s+([^\n]+)(?:\n([\s\S]*))?$/))) {
      out.push(`<h2>${inlineFmt(h[1].trim(), chunkIndex)}</h2>`);
      if (h[2]?.trim()) {
        out.push(`<p>${inlineFmt(h[2].trim(), chunkIndex).replace(/\n/g, " ")}</p>`);
      }
    }
    else if ((h = escaped.match(/^#\s+([^\n]+)(?:\n([\s\S]*))?$/))) {
      out.push(`<h1>${inlineFmt(h[1].trim(), chunkIndex)}</h1>`);
      if (h[2]?.trim()) {
        out.push(`<p>${inlineFmt(h[2].trim(), chunkIndex).replace(/\n/g, " ")}</p>`);
      }
    }
    else if (/^&gt;\s/.test(escaped)) {
      const lines = escaped.split(/\n/).map(ln => ln.replace(/^&gt;\s?/, "")).join("<br>");
      out.push(`<blockquote>${inlineFmt(lines, chunkIndex)}</blockquote>`);
    } else {
      // Footnote body paragraph — both the leading (N) label AND the
      // trailing ↩ navigate back to the inline ref in the body. The
      // paragraph itself has id="fn-{chunk}-{N}" for URL-hash addressing
      // (right-click → 複製連結 still works on the paragraph background).
      const fn = inFootnotes ? escaped.match(/^\((\d+)\)\s*(.*)$/s) : null;
      if (fn && chunkIndex !== null) {
        const num = fn[1];
        const rest = inlineFmt(fn[2], chunkIndex).replace(/\n/g, "<br>");
        out.push(
          `<p class="footnote-item" id="fn-${chunkIndex}-${num}">` +
          `<a href="#fnref-${chunkIndex}-${num}" class="footnote-num" title="回到正文">(${num})</a> ` +
          `${rest} ` +
          `<a href="#fnref-${chunkIndex}-${num}" class="footnote-back" title="回到正文">↩</a></p>`
        );
      } else {
        // CCEL EPUBs word-wrap paragraphs with single `\n` between lines.
        // Replacing each \n with <br> created jagged forced-break columns
        // (worse in the English bilingual column). Collapse single \n to a
        // space so the browser reflows naturally; only `\n\n` (paragraph
        // break) is honored upstream via the block split.
        out.push(`<p>${inlineFmt(escaped, chunkIndex).replace(/\n/g, " ").replace(/  +/g, " ")}</p>`);
      }
    }
  }
  if (inFootnotes) out.push("</section>");
  return out.join("\n");
}

// Detect 目錄 (table-of-contents) page — special render: each chapter
// becomes a hyperlink to its reader page; sub-section lines indent
// under their parent chapter.
const isTocPage = computed(() =>
  pageChapter.value === "目錄" || pageChapter.value === "目　錄" || pageChapter.value === "目　　錄"
);

// Build a lookup map from cleaned chapter title → chunk_index so each
// `**第N章 …**` line in the 目錄 source can resolve to `?page=N+1`.
function normChapterKey(s: string): string {
  return s.replace(/\[\^\d+\]/g, "").replace(/\s+/g, "").trim();
}
const chapterIndexByTitle = computed(() => {
  const m = new Map<string, number>();
  for (const e of toc.value) {
    m.set(normChapterKey(e.title), e.chunk_index);
  }
  return m;
});

// Render the 目錄 chunk content as a properly-indented + hyperlinked list.
// Lines fall into four shapes:
//   `## 目錄`                  → page heading (h2)
//   `**第N卷**`                 → volume label (display-only)
//   `**第N章　Chapter Title**`  → clickable link to that chapter's page
//   plain text (other)         → section title, indented under its chapter
function renderTocPage(md: string): string {
  const lines = md.split(/\n+/).map(l => l.trim()).filter(Boolean);
  const out: string[] = [];
  for (let raw of lines) {
    const line = raw;
    // h2 目錄 heading
    let m = line.match(/^##\s+(?:<u>)?目[　 ]*錄(?:<\/u>)?$/);
    if (m) { out.push('<h2 class="toc-page-title">目　錄</h2>'); continue; }
    // **第N卷** volume label
    m = line.match(/^\*\*(第[一二三四五六七八九十百千]+[卷編冊集篇部])\*\*$/);
    if (m) { out.push(`<div class="toc-volume">${m[1]}</div>`); continue; }
    // **第N章　Title** chapter link
    m = line.match(/^\*\*(第[一二三四五六七八九十百千]+章)([　 ]+)(.+?)\*\*$/);
    if (m) {
      const chNum = m[1];
      const title = m[3].trim();
      const cleanTitle = title.replace(/\[\^\d+\]/g, "").trim();
      const fullKey = normChapterKey(`${chNum}${title}`);
      const idx = chapterIndexByTitle.value.get(fullKey);
      if (idx !== undefined) {
        out.push(
          `<div class="toc-chapter"><a href="?page=${idx + 1}" data-toc-chapter="${idx + 1}">` +
          `<span class="toc-ch-num">${chNum}</span>` +
          `<span class="toc-ch-title">${escapeHtml(cleanTitle)}</span>` +
          `</a></div>`
        );
      } else {
        // No match in TOC — render as plain (rare, defensive)
        out.push(`<div class="toc-chapter toc-chapter-orphan">${escapeHtml(chNum)} ${escapeHtml(cleanTitle)}</div>`);
      }
      continue;
    }
    // Other **bold** lines — back-matter labels (參考書目 / 英漢譯名對照表 /
    // 修訂後記 etc.) or front-matter (前言, 致法王書...). If we can resolve
    // them to a chunk index they become hyperlinks like chapters.
    m = line.match(/^\*\*(.+?)\*\*$/);
    if (m) {
      const title = m[1].trim();
      const idx = chapterIndexByTitle.value.get(normChapterKey(title));
      if (idx !== undefined) {
        out.push(
          `<div class="toc-chapter"><a href="?page=${idx + 1}" data-toc-chapter="${idx + 1}">` +
          `<span class="toc-ch-title toc-ch-title-solo">${escapeHtml(title)}</span>` +
          `</a></div>`
        );
      } else {
        out.push(`<div class="toc-chapter toc-chapter-orphan">${escapeHtml(title)}</div>`);
      }
      continue;
    }
    // Plain section line — indent under chapter
    out.push(`<div class="toc-section">${escapeHtml(line)}</div>`);
  }
  return out.join("\n");
}

const markdownHtml = computed(() =>
  isTocPage.value
    ? renderTocPage(pageContent.value)
    : renderMarkdown(pageContent.value, currentPage.value - 1)
);
const sourceHtml = computed(() => pageSourceText.value ? renderMarkdown(pageSourceText.value) : "");

// Paragraph-level alignment for bilingual mode. Each paragraph (split on
// blank line in source markdown) pairs with the matching translated
// paragraph. If counts differ (LLM occasionally splits or merges), pad with
// empty cells so the surviving paragraphs stay on the correct row.
function splitParagraphs(md: string): string[] {
  return md.split(/\n{2,}/).map(p => p.trim()).filter(Boolean);
}
const paragraphPairs = computed<{ zh: string; en: string }[]>(() => {
  if (!pageContent.value || !pageSourceText.value) return [];
  const zh = splitParagraphs(pageContent.value);
  const en = splitParagraphs(pageSourceText.value);
  const n = Math.max(zh.length, en.length);
  const out: { zh: string; en: string }[] = [];
  for (let i = 0; i < n; i++) {
    out.push({
      zh: zh[i] ? renderMarkdown(zh[i]) : "",
      en: en[i] ? renderMarkdown(en[i]) : "",
    });
  }
  return out;
});

// ── DOM-based highlight applier (handles cross-paragraph + multi-occurrence) ──
function isInsideMark(node: Node, container: HTMLElement): boolean {
  let p: Node | null = node.parentNode;
  while (p && p !== container) {
    if ((p as Element).tagName === "MARK") return true;
    p = p.parentNode;
  }
  return false;
}

function gatherTextNodes(container: HTMLElement): { node: Text; start: number; end: number }[] {
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, {
    acceptNode: (n) => isInsideMark(n, container) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT,
  });
  const nodes: { node: Text; start: number; end: number }[] = [];
  let total = 0;
  let n = walker.nextNode() as Text | null;
  while (n) {
    const t = n.textContent || "";
    nodes.push({ node: n, start: total, end: total + t.length });
    total += t.length;
    n = walker.nextNode() as Text | null;
  }
  return nodes;
}

function wrapTextNodeSlice(node: Text, startOff: number, endOff: number, attrs: Record<string, string>): HTMLElement {
  const text = node.textContent || "";
  const before = text.slice(0, startOff);
  const middle = text.slice(startOff, endOff);
  const after = text.slice(endOff);

  const mark = document.createElement("mark");
  mark.textContent = middle;
  for (const [k, v] of Object.entries(attrs)) mark.setAttribute(k, v);

  const parent = node.parentNode;
  if (!parent) return mark;
  if (before) parent.insertBefore(document.createTextNode(before), node);
  parent.insertBefore(mark, node);
  if (after) parent.insertBefore(document.createTextNode(after), node);
  parent.removeChild(node);
  return mark;
}

function highlightOne(container: HTMLElement, text: string, attrs: Record<string, string>): number {
  if (!text || text.length < 2) return 0;
  let wrapped = 0;
  // Cap iterations defensively in case mark filter fails to advance.
  for (let iter = 0; iter < 200; iter++) {
    const nodes = gatherTextNodes(container);
    let total = "";
    for (const n of nodes) total += n.node.textContent || "";
    const idx = total.indexOf(text);
    if (idx === -1) break;
    const matchEnd = idx + text.length;
    let didWrap = false;
    // Wrap each text node touched by this match (handles cross-paragraph).
    for (const np of nodes) {
      if (matchEnd <= np.start || idx >= np.end) continue;
      const localStart = Math.max(0, idx - np.start);
      const localEnd = Math.min(np.end - np.start, matchEnd - np.start);
      if (localEnd > localStart) {
        wrapTextNodeSlice(np.node, localStart, localEnd, attrs);
        didWrap = true;
      }
    }
    if (!didWrap) break;
    wrapped++;
  }
  return wrapped;
}

function applyHighlights() {
  if (!contentEl.value) return;
  // Apply each annotation. acceptNode rejects already-marked text, so this is
  // idempotent — calling twice doesn't double-wrap.
  for (const a of annotations.value) {
    const bg = COLOR_BG[a.color] || COLOR_BG.yellow;
    const style = `background:${bg};padding:0 2px;border-radius:2px;cursor:pointer;`;
    const noteAttr = a.note ? `; box-shadow: 0 0 0 1px ${bg}; outline: 1px dashed #f59e0b; outline-offset: 1px;` : "";
    highlightOne(contentEl.value, a.selected_text, {
      "data-anno-id": a.id,
      "style": style + noteAttr,
      "title": a.note ? `📌 ${a.note}` : "",
    });
  }
  // Apply page search (separate styling, not persistent)
  if (pageSearch.value.trim()) {
    highlightOne(contentEl.value, pageSearch.value.trim(), {
      "data-search": "1",
      "style": "background:#FCD34D;padding:0 2px;border-radius:2px;",
    });
  }
}

function unwrapMarksByAnnoId(annoId: string) {
  if (!contentEl.value) return;
  const marks = contentEl.value.querySelectorAll(`mark[data-anno-id="${annoId}"]`);
  for (const m of marks) {
    const parent = m.parentNode;
    if (!parent) continue;
    while (m.firstChild) parent.insertBefore(m.firstChild, m);
    parent.removeChild(m);
    parent.normalize();
  }
}

// Re-apply highlights whenever the rendered HTML or annotations change.
watch([markdownHtml, annotations], async () => {
  await nextTick();
  applyHighlights();
});

// Re-apply when the user switches view mode — contentEl mounts/unmounts as
// the v-if/v-else branches swap, so highlights must be re-attached.
watch(effectiveViewMode, async () => {
  await nextTick();
  applyHighlights();
});

// ── Loaders ──
async function loadPage(page: number) {
  pageLoading.value = true;
  const token = await getToken(); if (!token) return;
  const isFirstLoad = !ebook.value;
  const url = `/api/ebooks/${ebookId}?page=${page}${isFirstLoad ? "&includeToc=1" : ""}`;
  const data = await $fetch<any>(url, { headers: { Authorization: `Bearer ${token}` } }).catch(() => null);

  if (data) {
    if (!ebook.value) ebook.value = data;
    if (data.toc) toc.value = data.toc;
  }
  pageContent.value = data?.currentPage?.content ?? "";
  pageSourceText.value = data?.currentPage?.source_text ?? null;
  pageChapter.value = data?.currentPage?.chapter_path ?? null;
  pageLoading.value = false;
  jumpPage.value = page;

  // Auto-expand the volume containing the current chunk
  const here = toc.value.find(e => e.chunk_index === page - 1);
  if (here?.volume) expandedVolumes.value = new Set([...expandedVolumes.value, here.volume]);

  await loadAnnotations(page - 1);

  await nextTick();
  // Scroll reading area to top. Also call window.scrollTo defensively in
  // case the scroll container changed or the browser is honoring a stale
  // URL hash from a prior in-page anchor click.
  scrollEl.value?.scrollTo({ top: 0, behavior: "auto" });
  window.scrollTo({ top: 0, behavior: "auto" });
}

async function loadAnnotations(chunkIndex: number) {
  const token = await getToken(); if (!token) return;
  annotations.value = await $fetch<Annotation[]>(
    `/api/annotations?ebookId=${ebookId}&chunkIndex=${chunkIndex}`,
    { headers: { Authorization: `Bearer ${token}` } }
  ).catch(() => []);
}

async function loadBookAnnotations() {
  const token = await getToken(); if (!token) return;
  bookAnnotations.value = await $fetch<Annotation[]>(
    `/api/annotations?ebookId=${ebookId}`,
    { headers: { Authorization: `Bearer ${token}` } }
  ).catch(() => []);
}

// ── Bookshelf + bookmarks ──
async function loadReadingStatus() {
  const token = await getToken(); if (!token) return;
  const data = await $fetch<{ status: ReadingStatus }>(
    `/api/ebooks/${ebookId}/reading-status`,
    { headers: { Authorization: `Bearer ${token}` } }
  ).catch(() => ({ status: null }));
  readingStatus.value = data?.status ?? null;
}

async function loadBookmarks() {
  const token = await getToken(); if (!token) return;
  bookmarks.value = await $fetch<Bookmark[]>(
    `/api/ebooks/${ebookId}/bookmarks`,
    { headers: { Authorization: `Bearer ${token}` } }
  ).catch(() => []);
}

// Cycle: null → reading → read → null. Each transition is a single PUT.
async function cycleReadingStatus() {
  const next: ReadingStatus =
    readingStatus.value === null ? "reading" :
    readingStatus.value === "reading" ? "read" : null;
  const token = await getToken(); if (!token) return;
  try {
    await $fetch(`/api/ebooks/${ebookId}/reading-status`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: { status: next },
    });
    readingStatus.value = next;
    showToast(
      next === "reading" ? "已加入閱讀中"
      : next === "read"  ? "已標記為已讀"
      :                    "已從書櫃移除"
    );
  } catch (e: any) {
    showToast(`狀態更新失敗：${e?.data?.message ?? e?.message ?? ""}`, "error");
  }
}

async function addTodayBookmark() {
  const token = await getToken(); if (!token) return;
  try {
    const created = await $fetch<Bookmark>(`/api/ebooks/${ebookId}/bookmarks`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: { chunk_index: currentPage.value - 1 },
    });
    // newest-first ordering matches server response
    bookmarks.value = [created, ...bookmarks.value];
    showToast(`已標記今日讀到第 ${currentPage.value} 段`);
  } catch (e: any) {
    showToast(`書籤建立失敗：${e?.data?.message ?? e?.message ?? ""}`, "error");
  }
}

async function deleteBookmark(id: string) {
  const token = await getToken(); if (!token) return;
  try {
    await $fetch(`/api/bookmarks/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    bookmarks.value = bookmarks.value.filter(b => b.id !== id);
    showToast("已移除書籤");
  } catch (e: any) {
    showToast(`刪除失敗：${e?.data?.message ?? e?.message ?? ""}`, "error");
  }
}

const sortedBookAnnotations = computed(() =>
  [...bookAnnotations.value].sort((a, b) => a.chunk_index - b.chunk_index ||
    (a.created_at ?? "").localeCompare(b.created_at ?? ""))
);

function chunkLabel(idx: number): string {
  const e = toc.value.find(t => t.chunk_index === idx);
  if (!e) return `第 ${idx + 1} 段`;
  return e.volume ? `${shortVolumeName(e.volume)} · ${e.title}` : e.title;
}

function goPage(p: number) {
  if (!ebook.value) return;
  const clamped = Math.max(1, Math.min(p, ebook.value.total_pages));
  if (clamped === currentPage.value) return;
  currentPage.value = clamped;
  // hash: "" strips any stale `#fnref-…` / `#sec-…` hash from prior in-page
  // anchor navigation, so the next page lands at the top instead of trying
  // to scroll to a now-stale element.
  router.replace({ query: { page: String(clamped) }, hash: "" });
  loadPage(clamped);
}

// Scroll to a section anchor inside the currently-rendered chapter. Anchor
// ids are minted by renderMarkdown to match what loadToc reports — clicking
// 節 X in the TOC sidebar lands on the corresponding heading.
async function scrollToSection(anchorId: string) {
  await nextTick();
  const el = document.getElementById(anchorId);
  if (!el) return;
  el.scrollIntoView({ behavior: "smooth", block: "start" });
  // brief flash for visual feedback
  el.animate(
    [{ background: "#fef3c7" }, { background: "transparent" }],
    { duration: 1200 }
  );
}

// ── Cover image paste / edit ──
// The cover image appears on the book's 封面 page only — typically chunk 0
// (page=1) or any chunk whose `chapter_path` is "封面". This keeps the
// reader UI clean: chapters look like text, cover page looks like a book
// cover. Other reader pages don't show the cover.
const isCoverPage = computed(() =>
  currentPage.value === 1 || pageChapter.value === "封面"
);
const coverEditOpen = ref(false);
const coverUrlDraft = ref("");
const coverSaving = ref(false);
function openCoverEdit() {
  coverUrlDraft.value = ebook.value?.cover_url ?? "";
  coverEditOpen.value = true;
}
async function saveCoverUrl() {
  const token = await getToken(); if (!token) return;
  const url = coverUrlDraft.value.trim();
  if (url && !/^https?:\/\//i.test(url)) {
    showToast("封面網址必須 http 或 https 開頭", "error");
    return;
  }
  coverSaving.value = true;
  try {
    const result = await $fetch<{ id: string; cover_url: string | null }>(
      `/api/ebooks/${ebookId}/cover`,
      {
        method: "PUT",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: { cover_url: url || null },
      }
    );
    if (ebook.value) ebook.value.cover_url = result.cover_url;
    coverEditOpen.value = false;
    showToast(url ? "封面已更新" : "封面已清除");
  } catch (e: any) {
    showToast(`封面儲存失敗：${e?.data?.message || e?.message || ""}`, "error");
  } finally {
    coverSaving.value = false;
  }
}
async function clearCoverUrl() {
  coverUrlDraft.value = "";
  await saveCoverUrl();
}

async function jumpToAnnotation(a: Annotation) {
  if (a.chunk_index !== currentPage.value - 1) {
    goPage(a.chunk_index + 1);
    // Wait for content + highlights to render, then scroll to mark.
    await new Promise(r => setTimeout(r, 400));
  }
  await nextTick();
  const mark = contentEl.value?.querySelector(`mark[data-anno-id="${a.id}"]`);
  if (mark) {
    (mark as HTMLElement).scrollIntoView({ behavior: "smooth", block: "center" });
    // brief flash
    (mark as HTMLElement).animate(
      [{ filter: "brightness(1.5)" }, { filter: "brightness(1)" }],
      { duration: 800 }
    );
  }
}

// ── Selection toolbar ──
const selectionPopup = ref({ show: false, x: 0, y: 0 });
const lastSelection = ref<{ text: string; before: string; after: string } | null>(null);

function captureSelection() {
  const sel = window.getSelection?.();
  if (!sel || sel.rangeCount === 0) return null;
  const text = sel.toString().trim();
  if (text.length < 2) return null;
  const range = sel.getRangeAt(0);
  if (!contentEl.value || !contentEl.value.contains(range.commonAncestorContainer)) return null;
  // Bilingual mode: ignore selections inside the English source column —
  // annotations are scoped to the Chinese translation only.
  const startEl = range.commonAncestorContainer.nodeType === 1
    ? (range.commonAncestorContainer as Element)
    : range.commonAncestorContainer.parentElement;
  if (startEl?.closest(".ebook-prose-en")) return null;
  const containerText = contentEl.value.innerText || "";
  const idx = containerText.indexOf(text);
  const before = idx > 0 ? containerText.slice(Math.max(0, idx - 30), idx) : "";
  const after = idx >= 0 ? containerText.slice(idx + text.length, idx + text.length + 30) : "";
  return { text, before, after, range };
}

function onTextSelectionEnd() {
  setTimeout(() => {
    const captured = captureSelection();
    if (!captured) {
      selectionPopup.value.show = false;
      return;
    }
    lastSelection.value = { text: captured.text, before: captured.before, after: captured.after };
    const rect = captured.range.getBoundingClientRect();
    const popupWidth = 340;
    selectionPopup.value = {
      show: true,
      x: Math.max(8, Math.min(window.innerWidth - popupWidth - 8, rect.left + rect.width / 2 - popupWidth / 2)),
      y: Math.max(8, rect.top - 56),
    };
    markPopup.value.show = false;
  }, 1);
}

// ── Click on existing mark ──
const markPopup = ref({ show: false, x: 0, y: 0, annoId: "" });

function onContentClick(e: MouseEvent) {
  const target = e.target as HTMLElement;

  // Cross-page link rendered inside the 目錄 chunk content. Use the SPA
  // router (`goPage`) instead of letting the browser do a full reload.
  const pageLink = target.closest("a[data-toc-chapter]") as HTMLAnchorElement | null;
  if (pageLink) {
    const p = parseInt(pageLink.dataset.tocChapter || "0", 10);
    if (p > 0) {
      e.preventDefault();
      e.stopPropagation();
      goPage(p);
      return;
    }
  }

  // Intra-chunk anchor link (footnote ref ↔ footnote body, section anchor).
  // We hijack the navigation to do smooth scroll + flash highlight, since
  // the sticky topbar otherwise covers the target and bare :target CSS is
  // too subtle on inline superscript.
  const anchor = target.closest("a[href^='#']") as HTMLAnchorElement | null;
  if (anchor) {
    const href = anchor.getAttribute("href")!;
    const id = href.slice(1);
    const el = document.getElementById(id);
    if (el) {
      e.preventDefault();
      e.stopPropagation();
      // Update URL hash so :target still applies, without page jump.
      history.replaceState(null, "", `${location.pathname}${location.search}${href}`);
      el.scrollIntoView({ behavior: "smooth", block: "center" });
      el.animate(
        [
          { background: "#fde68a", outline: "2px solid #f59e0b", outlineOffset: "2px" },
          { background: "transparent", outline: "2px solid transparent", outlineOffset: "2px" },
        ],
        { duration: 1500 }
      );
      return;
    }
  }

  const mark = target.closest("mark[data-anno-id]") as HTMLElement | null;
  if (!mark) {
    markPopup.value.show = false;
    return;
  }
  e.stopPropagation();
  const annoId = mark.dataset.annoId!;
  const rect = mark.getBoundingClientRect();
  markPopup.value = {
    show: true,
    x: Math.max(8, Math.min(window.innerWidth - 280, rect.left)),
    y: Math.max(8, rect.bottom + 6),
    annoId,
  };
  selectionPopup.value.show = false;
}

function hidePopupsOnOutsideClick(e: MouseEvent) {
  const t = e.target as HTMLElement;
  if (t.closest("[data-selection-popup]") || t.closest("[data-mark-popup]")) return;
  if (t.closest("mark[data-anno-id]")) return;
  if (t.closest(".ebook-prose")) return;
  selectionPopup.value.show = false;
  markPopup.value.show = false;
}

// ── Save annotation from selection ──
async function postAnnotation(body: any): Promise<Annotation | null> {
  const token = await getToken(); if (!token) return null;
  try {
    return await $fetch<Annotation>("/api/annotations", {
      method: "POST", body,
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch (e: any) {
    showToast(`儲存失敗：${e?.data?.message || e?.message || "請檢查網路"}`, "error");
    return null;
  }
}

async function saveAnnotationFromSelection(color: string) {
  const sel = lastSelection.value;
  if (!sel) return;
  selectionPopup.value.show = false;
  const newAnno = await postAnnotation({
    ebook_id: ebookId,
    chunk_index: currentPage.value - 1,
    selected_text: sel.text,
    context_before: sel.before,
    context_after: sel.after,
    color,
  });
  // Only push to UI state if save succeeded — avoids the "looks saved but isn't" trap.
  if (newAnno) {
    lastUsedColor.value = color;
    annotations.value = [...annotations.value, newAnno];
    bookAnnotations.value = [...bookAnnotations.value, newAnno];
    window.getSelection?.()?.removeAllRanges();
  }
}

// ── Note editor (auto-save with 1s debounce) ──
const noteEditor = ref({
  show: false,
  annoId: "",            // empty until first save creates the annotation
  editingExisting: false,
  text: "",
  note: "",
  color: "yellow",
  status: "" as "" | "saving" | "saved" | "error",
  errorMsg: "",
  // Snapshot the selection at open time so it survives loss of window selection.
  pendingSel: null as { text: string; before: string; after: string } | null,
});
let noteSaveTimer: any = null;

async function openNewNoteFromSelection() {
  const sel = lastSelection.value;
  if (!sel) return;
  selectionPopup.value.show = false;
  // Create the annotation up front (with empty note + last color) so the
  // highlight appears immediately. Note edits then PATCH this row.
  const newAnno = await postAnnotation({
    ebook_id: ebookId,
    chunk_index: currentPage.value - 1,
    selected_text: sel.text,
    context_before: sel.before,
    context_after: sel.after,
    color: lastUsedColor.value,
    note: null,
  });
  if (!newAnno) return;  // toast already shown by postAnnotation
  annotations.value = [...annotations.value, newAnno];
  bookAnnotations.value = [...bookAnnotations.value, newAnno];
  noteEditor.value = {
    show: true, annoId: newAnno.id, editingExisting: false,
    text: newAnno.selected_text, note: "",
    color: newAnno.color, status: "saved", errorMsg: "",
    pendingSel: null,
  };
  window.getSelection?.()?.removeAllRanges();
}

function openNoteEditor(a: Annotation) {
  noteEditor.value = {
    show: true, annoId: a.id, editingExisting: true,
    text: a.selected_text, note: a.note ?? "",
    color: a.color, status: a.note ? "saved" : "", errorMsg: "",
    pendingSel: null,
  };
}

function openNoteEditorForMark() {
  const a = bookAnnotations.value.find(x => x.id === markPopup.value.annoId);
  if (!a) return;
  openNoteEditor(a);
  markPopup.value.show = false;
}

function closeNoteEditor() {
  // If a save is in flight, let it finish. Otherwise just close.
  if (noteSaveTimer) {
    clearTimeout(noteSaveTimer);
    noteSaveTimer = null;
    // Flush a final save synchronously so closing doesn't lose the last keystroke.
    autoSaveNote();
  }
  noteEditor.value.show = false;
}

async function autoSaveNote() {
  if (!noteEditor.value.annoId) return;  // nothing to PATCH
  const token = await getToken();
  if (!token) {
    noteEditor.value.status = "error";
    noteEditor.value.errorMsg = "未登入";
    return;
  }
  noteEditor.value.status = "saving";
  try {
    const updated = await $fetch<Annotation>(`/api/annotations/${noteEditor.value.annoId}`, {
      method: "PATCH",
      body: { note: noteEditor.value.note || null },
      headers: { Authorization: `Bearer ${token}` },
    });
    annotations.value = annotations.value.map(a => a.id === updated.id ? { ...a, note: updated.note } : a);
    bookAnnotations.value = bookAnnotations.value.map(a => a.id === updated.id ? { ...a, note: updated.note } : a);
    unwrapMarksByAnnoId(updated.id);
    await nextTick();
    applyHighlights();
    noteEditor.value.status = "saved";
    noteEditor.value.errorMsg = "";
  } catch (e: any) {
    noteEditor.value.status = "error";
    noteEditor.value.errorMsg = e?.data?.message || e?.message || "網路錯誤";
    showToast(`註記儲存失敗：${noteEditor.value.errorMsg}`, "error");
  }
}

// Watch the note text and auto-save with 1s debounce.
watch(() => noteEditor.value.note, (newV, oldV) => {
  if (!noteEditor.value.show) return;
  if (newV === oldV) return;
  noteEditor.value.status = "";
  if (noteSaveTimer) clearTimeout(noteSaveTimer);
  noteSaveTimer = setTimeout(() => {
    noteSaveTimer = null;
    autoSaveNote();
  }, 1000);
});

// ── Delete / change color ──
async function deleteAnnotation(id: string) {
  const token = await getToken(); if (!token) return;
  try {
    await $fetch<{ ok: boolean }>(`/api/annotations/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch (e: any) {
    showToast(`刪除失敗：${e?.data?.message || e?.message || "請檢查網路"}`, "error");
    return;
  }
  annotations.value = annotations.value.filter(a => a.id !== id);
  bookAnnotations.value = bookAnnotations.value.filter(a => a.id !== id);
  unwrapMarksByAnnoId(id);
}

function deleteCurrentMark() {
  const id = markPopup.value.annoId;
  markPopup.value.show = false;
  if (id) deleteAnnotation(id);
}

async function changeAnnotationColor(color: string) {
  const id = markPopup.value.annoId;
  markPopup.value.show = false;
  if (!id) return;
  const token = await getToken(); if (!token) return;
  try {
    await $fetch<Annotation>(`/api/annotations/${id}`, {
      method: "PATCH",
      body: { color },
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch (e: any) {
    showToast(`換色失敗：${e?.data?.message || e?.message || "請檢查網路"}`, "error");
    return;
  }
  lastUsedColor.value = color;
  annotations.value = annotations.value.map(a => a.id === id ? { ...a, color } : a);
  bookAnnotations.value = bookAnnotations.value.map(a => a.id === id ? { ...a, color } : a);
  unwrapMarksByAnnoId(id);
  await nextTick();
  applyHighlights();
}

// ── Save excerpt ──
const excerptModal = ref({ show: false, title: "", content: "", color: "yellow", saving: false });

function openExcerptModalFromSelection() {
  const sel = lastSelection.value;
  if (!sel) return;
  excerptModal.value = {
    show: true, title: "", content: sel.text,
    color: lastUsedColor.value, saving: false,
  };
  selectionPopup.value.show = false;
}

async function confirmSaveExcerpt() {
  const sel = lastSelection.value;
  if (!sel || !excerptModal.value.title.trim()) return;
  excerptModal.value.saving = true;
  const newAnno = await postAnnotation({
    ebook_id: ebookId,
    chunk_index: currentPage.value - 1,
    selected_text: sel.text,
    context_before: sel.before,
    context_after: sel.after,
    color: excerptModal.value.color,
    save_as_excerpt: true,
    excerpt_title: excerptModal.value.title.trim(),
    // chapter goes to excerpts.chapter so the book page groups by it;
    // page_label is human-readable section reference for the citation line.
    chapter: pageChapter.value ?? null,
    page_label: `第 ${currentPage.value} 段`,
  });
  excerptModal.value.saving = false;
  if (newAnno) {
    lastUsedColor.value = newAnno.color;
    annotations.value = [...annotations.value, newAnno];
    bookAnnotations.value = [...bookAnnotations.value, newAnno];
    excerptModal.value.show = false;
    window.getSelection?.()?.removeAllRanges();
    showToast("已存到書摘圖書館");
  }
  // On error, postAnnotation showed the toast and modal stays open so user can retry.
}

// ── Lifecycle ──
// ── Copy → auto-append Chicago citation ──
// When user copies text from the reader area, append a Chicago-format
// citation (with the nearest preceding {{p:N}} page marker as the source
// page). Works in both single-column and bilingual modes. The user gets
// raw selection (no citation) by holding Shift+Cmd/Ctrl-C — too far in
// the weeds for v1; default copy is always augmented.
function findNearestPageBeforeNode(startNode: Node | null): number | null {
  if (!startNode) return null;
  // Walk backwards in document order from startNode looking for a
  // .page-marker element. We scope to the article container so we don't
  // pick up markers from a different chunk.
  const article = (startNode as Element).closest?.("article") || document.querySelector("article");
  if (!article) return null;
  const markers = Array.from(article.querySelectorAll<HTMLElement>(".page-marker"));
  if (!markers.length) return null;
  // Find the LAST marker that's positioned <= startNode in document order.
  let best: HTMLElement | null = null;
  for (const m of markers) {
    // compareDocumentPosition: returns DOCUMENT_POSITION_PRECEDING (2) if
    // m comes BEFORE startNode in the document.
    const pos = startNode.compareDocumentPosition(m);
    if (pos & Node.DOCUMENT_POSITION_PRECEDING) {
      best = m;  // keep updating; later in iteration = later in document
    } else if (pos & Node.DOCUMENT_POSITION_FOLLOWING) {
      break;  // marker is after selection; we've passed our target
    }
  }
  if (!best) {
    // Fall back: use the FIRST marker on the page (selection might be
    // before any marker in the chunk, but the chunk does contain one).
    best = markers[0];
  }
  const n = parseInt(best.dataset.page || "", 10);
  return Number.isFinite(n) ? n : null;
}

function buildChicagoCitation(pageNum: number | null): string {
  const b = ebook.value;
  if (!b) return "";
  const parts: string[] = [];
  // Author (Chinese if present, else English)
  const author = b.author || b.author_en;
  if (author) parts.push(author);
  // Title (chinese) + original title in parens
  const title = b.title?.replace(/（[^）]+）$/, "").trim() || "";
  if (title) parts.push(`《${title}》`);
  // Editor / translator
  if (b.translator) parts.push(`${b.translator}`);
  // Publisher (Location: Publisher, Year)
  const pubBits: string[] = [];
  if (b.publisher_location) pubBits.push(b.publisher_location);
  if (b.publisher) pubBits.push(b.publisher);
  if (b.publication_year) pubBits.push(b.publication_year);
  if (pubBits.length) parts.push(`（${pubBits.join("：")}）`);
  // Page
  if (pageNum !== null) parts.push(`頁 ${pageNum}`);
  // Chapter context — helps readers who want chunk-level, not page-level, ref
  const chap = pageVolume.value || cleanChapterLabel.value;
  if (chap && !title.includes(chap)) parts.push(chap);
  return parts.join("，") + "。";
}

function onReaderCopy(e: ClipboardEvent) {
  const sel = window.getSelection();
  if (!sel || sel.isCollapsed) return;
  const selText = sel.toString().trim();
  if (!selText) return;
  // Only intercept selections that ORIGINATE in the reader article. Anchors
  // outside (sidebar, toolbar) keep native copy behavior.
  const anchor = sel.anchorNode;
  const article = (anchor as Element)?.closest?.("article")
                  || (anchor?.parentElement?.closest("article"));
  if (!article) return;

  const pageNum = findNearestPageBeforeNode(anchor);
  const citation = buildChicagoCitation(pageNum);
  if (!citation) return;

  // Compose. Use a newline + em-dash + citation for clear visual separation.
  const augmented = `${selText}\n\n—— ${citation}`;
  e.clipboardData?.setData("text/plain", augmented);
  e.preventDefault();
  showToast(pageNum ? `已複製 + 自動帶入頁 ${pageNum} 引用` : "已複製 + 自動帶入引用", "info");
}

onMounted(async () => {
  document.addEventListener("mousedown", hidePopupsOnOutsideClick);
  document.addEventListener("copy", onReaderCopy);

  // Restore view mode from previous session. If user has explicitly chosen
  // a mode before, honor it; otherwise the watcher on pageSourceText will
  // auto-default to 'bi' once a bilingual chunk loads.
  try {
    const saved = localStorage.getItem("ebook-viewMode") as ViewMode | null;
    if (saved === "zh" || saved === "bi" || saved === "en") {
      viewMode.value = saved;
      viewModeUserChosen.value = true;
    }
  } catch { /* private mode */ }

  // Fetch shelf state + bookmarks first so we can decide whether to auto-jump.
  await Promise.all([loadReadingStatus(), loadBookmarks()]);

  // Auto-jump rule: only when (a) status === 'reading', (b) at least one
  // bookmark exists, and (c) the user did NOT explicitly request a page via
  // ?page= in the URL. 'read' books and ad-hoc visits behave normally.
  const hasExplicitPage = !!route.query.page;
  if (!hasExplicitPage && readingStatus.value === "reading" && bookmarks.value.length > 0) {
    const target = bookmarks.value[0].chunk_index + 1;
    currentPage.value = target;
    jumpPage.value = target;
    router.replace({ query: { page: String(target) } });
    showToast(`接續 ${fmtBookmarkDate(bookmarks.value[0].created_at)} 閱讀進度，第 ${target} 段`);
  }

  loadPage(currentPage.value);
  loadBookAnnotations();
});
onBeforeUnmount(() => {
  document.removeEventListener("mousedown", hidePopupsOnOutsideClick);
  document.removeEventListener("copy", onReaderCopy);
});
useHead({ title: computed(() => ebook.value ? `${ebook.value.title} — 閱讀` : "閱讀") });
</script>

<style>
/* Google Fonts — loaded ONCE globally (not scoped, so <head> picks it up).
   - Noto Serif TC: body 正文宋體 (already requested via fontface-stack but
     explicit load keeps render consistent across machines)
   - ZCOOL XiaoWei: 楷書風格的繁中字體，作為 blockquote 引用字體 (近似標楷體) */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;500;600;700&family=ZCOOL+XiaoWei&display=swap');
</style>

<style scoped>
/* ── COVER HERO ──
   Curated title-page layout: image + decorative divider + display title
   + author + publisher imprint. Replaces the bare markdown content of
   chunk 0 (`## 封面 / 書名 / 作者`). */
.cover-hero {
  text-align: center;
  padding: 2.5rem 1rem 1rem;
  font-family: "Noto Serif TC", "Source Han Serif TC", "PingFang TC", "Microsoft JhengHei", Georgia, serif;
}
.cover-image-wrap {
  display: inline-block;
  position: relative;
  margin-bottom: 2rem;
  /* Lock to typical book aspect ratio so we can crop the publisher
     image's white padding via object-fit: cover. */
  width: min(320px, 60vw);
  aspect-ratio: 2 / 3;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #d6d3d1;
  box-shadow: 0 14px 40px -10px rgba(0, 0, 0, 0.28), 0 4px 14px -4px rgba(0, 0, 0, 0.16);
}
.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;          /* fills container; crops outer whitespace */
  object-position: center;
  display: block;
}
.cover-edit-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid #d6d3d1;
  color: #78716c;
  font-size: 14px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  opacity: 0;
  transition: opacity 0.15s, transform 0.15s, color 0.15s;
  cursor: pointer;
}
.cover-edit-btn:hover { color: #1c1917; transform: scale(1.08); }
.group\/cover:hover .cover-edit-btn { opacity: 1; }
.cover-placeholder {
  display: inline-block;
  padding: 4rem 4.5rem;
  border-radius: 8px;
  border: 2px dashed #d6d3d1;
  background: #fafaf9;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  margin-bottom: 2rem;
  text-align: center;
}
.cover-placeholder:hover { border-color: #60a5fa; background: rgba(219, 234, 254, 0.3); }
.cover-placeholder-icon { font-size: 3rem; color: #d6d3d1; margin-bottom: 0.75rem; }
.cover-placeholder-title { color: #78716c; font-size: 0.95rem; margin-bottom: 0.25rem; }
.cover-placeholder-sub { color: #a8a29e; font-size: 0.8rem; }
.cover-editor {
  max-width: 28rem;
  margin: 0 auto 2rem;
  background: #fafaf9;
  border: 1px solid #d6d3d1;
  border-radius: 8px;
  padding: 1rem 1.25rem;
  text-align: left;
}
.cover-divider {
  margin: 0.5rem auto 1.5rem;
  color: #a8a29e;
  font-size: 1.5rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.25rem;
}
.cover-divider::before,
.cover-divider::after {
  content: "";
  display: block;
  flex: 0 0 4rem;
  height: 1px;
  background: #d6d3d1;
}
.cover-title {
  font-family: "Noto Serif TC", "Source Han Serif TC", serif;
  font-size: 2.6rem;
  font-weight: 700;
  color: #0c0a09;
  letter-spacing: 0.12em;
  margin: 0 0 0.5rem;
  line-height: 1.35;
}
.cover-subtitle {
  font-size: 1.1rem;
  color: #44403c;
  margin: 0.5rem 0 0;
  letter-spacing: 0.05em;
}
.cover-original-title {
  margin: 0.6rem 0 1.25rem;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.05rem;
  color: #78716c;
}
.cover-original-title em { font-style: italic; }
.cover-author-block {
  margin: 1.75rem 0 1rem;
  color: #292524;
}
.cover-author,
.cover-translator {
  margin: 0.4rem 0;
  font-size: 1.05rem;
  letter-spacing: 0.08em;
}
.cover-author-label {
  display: inline-block;
  padding: 0.1rem 0.45rem;
  background: #e7e5e4;
  color: #57534e;
  font-size: 0.7rem;
  font-weight: 600;
  border-radius: 3px;
  margin-right: 0.5rem;
  letter-spacing: 0;
  vertical-align: middle;
}
.cover-author-en {
  font-family: Georgia, serif;
  font-style: italic;
  color: #78716c;
  font-size: 0.95em;
}
.cover-imprint {
  margin-top: 2.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e7e5e4;
  color: #a8a29e;
  font-size: 0.85rem;
  letter-spacing: 0.06em;
}

/* Article container — warm parchment tint instead of clinical white. */
.ebook-article {
  background: #fdfcf7;
  position: relative;
}
.ebook-article::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(to bottom, rgba(255,255,255,0) 0, rgba(255,250,235,0.25) 100%);
  border-radius: inherit;
}

.ebook-prose {
  color: #1c1917;
  font-size: 17px;
  line-height: 2;
  font-family: "Noto Serif TC", "Source Han Serif TC", "PingFang TC", "Microsoft JhengHei", Georgia, serif;
}
.ebook-prose :deep(h1) {
  font-size: 2.2rem;
  font-weight: 700;
  margin: 3rem 0 1.75rem;
  color: #0c0a09;
  letter-spacing: 0.02em;
  text-align: center;
}
/* h2 = 章 (chapter heading inside the chunk, mirrors chapter_path)
   Biggest, most prominent; ornamental double-rule + centered.         */
.ebook-prose :deep(h2) {
  font-size: 1.85rem;
  font-weight: 700;
  margin: 1rem 0 2.5rem;
  color: #0c0a09;
  padding: 1.25rem 0 1rem;
  border-top: 1px solid #d6d3d1;
  border-bottom: 3px double #78716c;
  text-align: center;
  letter-spacing: 0.06em;
  line-height: 1.55;
}
/* h3 = 節 (section). Medium-large; left-aligned with a left accent bar. */
.ebook-prose :deep(h3) {
  font-size: 1.4rem;
  font-weight: 600;
  margin: 2.5rem 0 1rem;
  color: #1c1917;
  padding-left: 0.75rem;
  border-left: 4px solid #78716c;
  letter-spacing: 0.02em;
  scroll-margin-top: 4rem;
}
/* h4 = 子節 / numbered sub-items. Smaller but still distinct.          */
.ebook-prose :deep(h4) {
  font-size: 1.15rem;
  font-weight: 600;
  margin: 1.75rem 0 0.75rem;
  color: #44403c;
  letter-spacing: 0.02em;
  scroll-margin-top: 4rem;
}
.ebook-prose :deep(p) {
  margin: 1.1rem 0;
  text-indent: 2em;
  text-align: justify;
}
.ebook-prose :deep(strong) { font-weight: 700; color: #0c0a09; }
.ebook-prose :deep(em) { font-style: italic; }
/* English book titles 《...》 — render in italicized Latin serif. The
   regex in inlineFmt wraps them in <em class="book-title-en">.        */
.ebook-prose :deep(em.book-title-en) {
  font-family: Georgia, "Times New Roman", serif;
  font-style: italic;
  font-weight: 500;
  color: #1c1917;
}
/* Blockquote 引用 — 標楷體 (ZCOOL XiaoWei web font + system 標楷體 fallback).
   No italic on CJK (italic looks bad on Chinese); use the kai script font
   itself to signal "quoted material". */
.ebook-prose :deep(blockquote) {
  border-left: 3px solid #c4a35a;
  padding: 0.75rem 1rem 0.75rem 1.5rem;
  margin: 1.75rem 0;
  color: #44403c;
  background: #fefce8;
  border-radius: 0 4px 4px 0;
  font-family: "ZCOOL XiaoWei", "DFKai-SB", "BiauKai", "標楷體", "Noto Serif TC", serif;
  font-size: 16.5px;
  line-height: 1.95;
  font-style: normal;
}
.ebook-prose :deep(blockquote p) {
  text-indent: 0;
}
.ebook-prose :deep(hr) {
  margin: 2rem 0;
  border: 0;
  border-top: 1px solid #e7e5e4;
}
/* Footnote section —章末註釋區。Smaller font, ornamental separator,
   each entry's (N) label is a clickable anchor (URL hash) so users can
   right-click → copy link to a specific note. */
.ebook-prose :deep(section.footnotes) {
  margin-top: 4rem;
  padding-top: 0;
  font-size: 13.5px;
  line-height: 1.9;
  color: #57534e;
  position: relative;
}
.ebook-prose :deep(.footnotes-label) {
  font-size: 11px;
  letter-spacing: 0.4em;
  color: #a8a29e;
  text-align: center;
  margin: 0 auto 1.5rem;
  text-indent: 0.4em;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  font-weight: 500;
}
.ebook-prose :deep(.footnotes-label)::before,
.ebook-prose :deep(.footnotes-label)::after {
  content: "";
  flex: 0 0 5rem;
  height: 1px;
  background: #d6d3d1;
}
.ebook-prose :deep(.footnote-item) {
  margin: 0.6rem 0;
  text-indent: -2.2em;
  padding-left: 2.2em;
  text-align: justify;
}
.ebook-prose :deep(.footnote-item:target) {
  background: #fef3c7;
  border-left: 3px solid #f59e0b;
  padding-left: 2em;
  margin-left: -0.5rem;
  padding-right: 0.5rem;
  border-radius: 0 4px 4px 0;
  scroll-margin-top: 4rem;
}
.ebook-prose :deep(a.footnote-num) {
  color: #2563eb;
  font-weight: 500;
  text-decoration: none;
  font-variant-numeric: tabular-nums;
}
.ebook-prose :deep(a.footnote-num:hover) {
  text-decoration: underline;
}
/* Inline footnote reference — small superscript, blue, clickable. */
.ebook-prose :deep(sup.footnote-ref) {
  font-size: 0.7em;
  line-height: 0;
  margin: 0 1px 0 2px;
  vertical-align: super;
  scroll-margin-top: 6rem;     /* clear of sticky topbar when scrolled to */
  scroll-margin-bottom: 4rem;
}
.ebook-prose :deep(sup.footnote-ref a) {
  color: #2563eb;
  text-decoration: none;
  padding: 1px 4px;
  border-radius: 3px;
  font-weight: 600;
  background: rgba(219, 234, 254, 0.45);
}
.ebook-prose :deep(sup.footnote-ref a:hover) {
  background: #93c5fd;
  color: #fff;
}
/* When :target is active, persistent highlight on the footnote ref the
   user just navigated back to. Stays until they click somewhere else. */
.ebook-prose :deep(sup.footnote-ref:target a) {
  background: #fbbf24;
  color: #0c0a09;
  outline: 2px solid #d97706;
  outline-offset: 1px;
}
/* Back-link arrow on each footnote body paragraph. */
.ebook-prose :deep(a.footnote-back) {
  color: #94a3b8;
  text-decoration: none;
  margin-left: 0.25rem;
  font-size: 0.95em;
}
.ebook-prose :deep(a.footnote-back:hover) {
  color: #2563eb;
}
.ebook-prose :deep(mark) {
  cursor: pointer;
  transition: filter 0.15s;
}
.ebook-prose :deep(mark:hover) { filter: brightness(0.95); }

/* Print-edition page marker — tiny gray pill from `{{p:N}}` extracted by
   extract_epub_extras.py. Doesn't disrupt prose but discoverable on hover
   and consumed by copy-handler for Chicago citation. */
.ebook-prose :deep(.page-marker) {
  font-size: 0.65em;
  color: #a8a29e;
  background: #f5f5f4;
  padding: 1px 5px;
  border-radius: 3px;
  margin: 0 3px;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.5px;
  vertical-align: 1px;
  white-space: nowrap;
  cursor: help;
  user-select: none;
}
.ebook-prose :deep(.page-marker:hover) {
  background: #e7e5e4;
  color: #57534e;
}

/* ── 目錄 page styling ──
   Each 章 line becomes a hyperlink. 節 lines (plain non-bold) indent 2
   levels deeper than chapters and stay as muted display-only text. */
.ebook-prose :deep(.toc-page-title) {
  font-size: 1.85rem;
  font-weight: 700;
  margin: 1rem 0 2rem;
  text-align: center;
  letter-spacing: 0.6em;
  text-indent: 0.6em;
  color: #0c0a09;
  padding: 1rem 0;
  border-top: 1px solid #d6d3d1;
  border-bottom: 3px double #78716c;
}
.ebook-prose :deep(.toc-volume) {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0c0a09;
  margin: 2rem 0 0.5rem;
  letter-spacing: 0.15em;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid #d6d3d1;
}
.ebook-prose :deep(.toc-chapter) {
  margin: 0.4rem 0;
  padding-left: 1.5rem;     /* base indent under volume */
  line-height: 1.7;
}
.ebook-prose :deep(.toc-chapter a) {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  color: #1c1917;
  text-decoration: none;
  padding: 0.3rem 0.5rem;
  border-radius: 4px;
  transition: background 0.15s, color 0.15s;
}
.ebook-prose :deep(.toc-chapter a:hover) {
  background: #fef3c7;
  color: #0c0a09;
}
.ebook-prose :deep(.toc-ch-num) {
  flex: 0 0 4em;
  font-weight: 600;
  color: #57534e;
  font-variant-numeric: tabular-nums;
}
.ebook-prose :deep(.toc-ch-title) {
  flex: 1;
  font-weight: 500;
}
/* Back-matter / front-matter entry without 第N章 prefix (e.g. 參考書目,
   英漢譯名對照表, 修訂後記). Left-align without reserving num column. */
.ebook-prose :deep(.toc-ch-title-solo) {
  flex: 1;
  font-weight: 600;
  color: #1c1917;
  margin-left: 0;
}
.ebook-prose :deep(.toc-chapter-orphan) {
  color: #a8a29e;     /* greyed-out — couldn't resolve to a real chunk */
}
.ebook-prose :deep(.toc-section) {
  padding-left: 4.5rem;     /* chapter base 1.5em + chapter内 num 4em ≈ +2 more */
  margin: 0.15rem 0;
  font-size: 0.92em;
  color: #78716c;
  line-height: 1.6;
}

/* English source column overrides — Latin typography */
.ebook-prose-en {
  font-family: Georgia, "Times New Roman", "Source Serif Pro", serif;
  font-size: 16px;
  line-height: 1.75;
}
.ebook-prose-en :deep(p) {
  text-indent: 0;
  margin: 0.9rem 0;
}
.ebook-prose-en :deep(h1),
.ebook-prose-en :deep(h2),
.ebook-prose-en :deep(h3),
.ebook-prose-en :deep(h4) {
  letter-spacing: 0;
}
.ebook-prose-en :deep(blockquote) {
  font-style: italic;
  font-family: Georgia, "Times New Roman", serif;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s, transform 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(8px); }
</style>
