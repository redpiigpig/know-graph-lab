<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-14">
          <div class="flex items-center gap-2 text-sm text-gray-500">
            <NuxtLink to="/excerpts" class="hover:text-blue-600 transition flex items-center gap-1.5">
              <img src="/logo_image.jpg" alt="logo" class="w-5 h-5 rounded object-cover" />
              <span>書摘庫</span>
            </NuxtLink>
            <span>›</span>
            <NuxtLink to="/excerpts/writing" class="hover:text-purple-600 transition">著作書摘</NuxtLink>
            <span>›</span>
            <span class="font-semibold text-gray-900 truncate max-w-xs">{{ overview?.project?.name ?? '載入中…' }}</span>
          </div>
          <div class="flex items-center gap-2">
            <button class="px-3 py-1.5 text-xs rounded-lg bg-purple-600 text-white hover:bg-purple-500" @click="showCreate = true">+ 新增文摘</button>
            <button class="px-3 py-1.5 text-xs rounded-lg border border-purple-300 text-purple-700 hover:bg-purple-50" @click="showOCR = true">上傳照片</button>
            <button class="px-3 py-1.5 text-xs rounded-lg border border-purple-300 text-purple-700 hover:bg-purple-50" @click="showCSV = true">上傳 CSV</button>
            <button @click="handleLogout" class="text-gray-500 hover:text-red-600 transition text-sm">登出</button>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      <!-- 載入骨架 -->
      <div v-if="loading" class="space-y-6 animate-pulse">
        <div class="bg-white rounded-2xl p-6 h-24"></div>
        <div class="flex gap-3">
          <div v-for="i in 6" :key="i" class="h-10 w-32 bg-white rounded-xl border border-gray-200"></div>
        </div>
      </div>

      <template v-else-if="overview">
        <!-- 書名標題 -->
        <div class="mb-6 flex items-center gap-4">
          <div class="w-14 h-14 bg-purple-100 rounded-2xl flex items-center justify-center text-3xl flex-shrink-0">📖</div>
          <div>
            <h1 class="text-3xl font-bold text-gray-900">{{ overview.project.name }}</h1>
            <p class="text-gray-500 text-sm mt-0.5">著作書摘 · {{ overview.total }} 筆素材</p>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-2 mb-4">
          <span class="text-xs text-gray-500 mr-1">檢視</span>
          <button
            type="button"
            :class="['px-3 py-1.5 rounded-lg text-xs font-medium border transition', layoutMode === 'tabs' ? 'bg-purple-600 text-white border-purple-600' : 'bg-white text-gray-600 border-gray-200 hover:border-purple-300']"
            @click="setLayoutMode('tabs')"
          >章節</button>
          <button
            type="button"
            :class="['px-3 py-1.5 rounded-lg text-xs font-medium border transition', layoutMode === 'scroll' ? 'bg-purple-600 text-white border-purple-600' : 'bg-white text-gray-600 border-gray-200 hover:border-purple-300']"
            @click="setLayoutMode('scroll')"
          >主題</button>
          <span class="w-px h-5 bg-gray-200 mx-1 hidden sm:block" />
          <template v-if="layoutMode === 'tabs'">
            <button type="button" class="px-3 py-1.5 rounded-lg text-xs font-medium border border-purple-200 text-purple-800 bg-purple-50 hover:bg-purple-100" @click="openAddNavRow('chapter')">+ 新增章節</button>
            <button type="button" class="px-3 py-1.5 rounded-lg text-xs font-medium border border-gray-200 text-gray-700 bg-white hover:bg-gray-50" @click="openManageNavRows('chapter')">管理章節順序／刪除</button>
            <button
              v-if="chapterNavItems.length"
              type="button"
              class="px-3 py-1.5 rounded-lg text-xs font-medium border border-amber-200 text-amber-900 bg-amber-50 hover:bg-amber-100"
              @click="openVolumeEditor"
            >章節分卷</button>
          </template>
          <template v-else>
            <button type="button" class="px-3 py-1.5 rounded-lg text-xs font-medium border border-purple-200 text-purple-800 bg-purple-50 hover:bg-purple-100" @click="openAddNavRow('topic')">+ 新增主題</button>
            <button type="button" class="px-3 py-1.5 rounded-lg text-xs font-medium border border-gray-200 text-gray-700 bg-white hover:bg-gray-50" @click="openManageNavRows('topic')">管理主題順序／刪除</button>
          </template>
        </div>

        <!-- 章節檢視：有分卷時先一排「卷」，點卷後第二排才出現「章」；無分卷則維持單排章 -->
        <template v-if="layoutMode === 'tabs' && chapterNavItems.length">
          <template v-if="usesVolumeChapterNav">
            <div class="mb-6">
            <div class="flex flex-wrap gap-2">
              <button
                v-for="(vol, vgi) in chapterNavVolumeGroups"
                :key="'vol-' + vgi"
                type="button"
                @click="selectVolumeNav(vgi)"
                :class="[
                  'px-4 py-2.5 rounded-xl text-xs font-semibold transition border text-left min-w-[108px] max-w-[220px]',
                  activeVolumeNavIndex === vgi
                    ? 'bg-purple-600 text-white border-purple-600 shadow-sm'
                    : 'bg-white text-gray-800 border-purple-200 hover:border-purple-400 hover:bg-purple-50'
                ]"
              >
                <span class="block leading-snug">{{ vol.title }}</span>
                <span
                  :class="activeVolumeNavIndex === vgi ? 'text-purple-200' : 'text-gray-500'"
                  class="text-[11px] font-normal mt-1 block"
                >{{ vol.chapters.reduce((s, c) => s + c.count, 0) }} 筆 · {{ vol.chapters.length }} 章</span>
              </button>
            </div>
            <div
              v-if="activeVolumeNavIndex !== null"
              class="flex flex-wrap gap-2 pt-4 mt-3 border-t border-purple-100"
            >
              <button
                v-for="ch in (chapterNavVolumeGroups[activeVolumeNavIndex]?.chapters ?? [])"
                :key="ch.name"
                type="button"
                @click="selectChapter(ch.name)"
                :class="[
                  'px-3 py-2 rounded-xl text-xs font-medium transition border text-left max-w-[220px]',
                  activeChapter === ch.name
                    ? 'bg-purple-600 text-white border-purple-600 shadow-sm'
                    : 'bg-white text-gray-700 border-gray-200 hover:border-purple-300 hover:text-purple-700'
                ]"
              >
                <span class="font-bold">{{ ch.name }}</span>
                <span v-if="ch.chapterName" :class="activeChapter === ch.name ? 'text-purple-200' : 'text-gray-400'" class="ml-1">·</span>
                <span v-if="ch.chapterName" :class="activeChapter === ch.name ? 'text-purple-100' : 'text-gray-500'" class="ml-1 line-clamp-1 block text-xs">{{ ch.chapterName }}</span>
                <span :class="activeChapter === ch.name ? 'text-purple-200' : 'text-gray-400'" class="text-xs">({{ ch.count }})</span>
              </button>
            </div>
            </div>
          </template>
          <div v-else class="flex flex-wrap gap-2 mb-6">
            <button
              v-for="ch in chapterNavItems"
              :key="ch.name"
              type="button"
              @click="selectChapter(ch.name)"
              :class="[
                'px-3 py-2 rounded-xl text-xs font-medium transition border text-left max-w-[220px]',
                activeChapter === ch.name
                  ? 'bg-purple-600 text-white border-purple-600 shadow-sm'
                  : 'bg-white text-gray-700 border-gray-200 hover:border-purple-300 hover:text-purple-700'
              ]"
            >
              <span class="font-bold">{{ ch.name }}</span>
              <span v-if="ch.chapterName" :class="activeChapter === ch.name ? 'text-purple-200' : 'text-gray-400'" class="ml-1">·</span>
              <span v-if="ch.chapterName" :class="activeChapter === ch.name ? 'text-purple-100' : 'text-gray-500'" class="ml-1 line-clamp-1 block text-xs">{{ ch.chapterName }}</span>
              <span :class="activeChapter === ch.name ? 'text-purple-200' : 'text-gray-400'" class="text-xs">({{ ch.count }})</span>
            </button>
          </div>
        </template>
        <p v-else-if="layoutMode === 'tabs'" class="text-sm text-gray-500 mb-6">
          目前沒有「第一章」形式的章節。若摘文是按主題分類，請切換到「主題」檢視；若要在此管理章節，請按「+ 新增章節」。
        </p>

        <!-- 章節檢視：單章內容 -->
        <div v-if="layoutMode === 'tabs' && chapLoading" class="space-y-3">
          <div v-for="i in 5" :key="i" class="bg-white rounded-xl border border-gray-200 p-5 animate-pulse">
            <div class="h-5 bg-gray-200 rounded w-1/3 mb-3"></div>
            <div class="space-y-2"><div class="h-3 bg-gray-200 rounded w-full"></div><div class="h-3 bg-gray-200 rounded w-4/5"></div></div>
          </div>
        </div>

        <template v-else-if="layoutMode === 'tabs' && activeChapter">
          <!-- 章節標題（可編輯） -->
          <div class="flex items-center gap-3 mb-6">
            <div class="flex items-center gap-2">
              <h2 class="text-2xl font-bold text-gray-900">{{ activeChapter }}</h2>
              <span class="text-gray-300">·</span>
              <InlineEdit
                :value="activeChapterName"
                placeholder="點此輸入章節名稱"
                class="text-2xl font-bold text-purple-700"
                @save="saveChapterName"
              />
            </div>
            <span class="text-gray-400 text-sm ml-auto">{{ excerpts.length }} 筆</span>
          </div>
          <div class="flex gap-2 mb-4 max-w-xl">
            <select v-model="searchField" class="px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white outline-none focus:ring-2 focus:ring-purple-400">
              <option value="all">全部</option>
              <option value="content">內容</option>
              <option value="title">標題</option>
              <option value="book">書名</option>
              <option value="author">作者</option>
            </select>
            <input
              v-model="searchQ"
              placeholder="搜尋此章節"
              class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-purple-400"
            />
          </div>

          <div v-if="listWritingEmpty" class="text-center py-20 text-gray-400">
            <p>{{ emptyWritingHint }}</p>
          </div>

          <div v-else class="space-y-0">
            <template v-for="sec in displayWritingSections" :key="sec.key">
              <div v-if="sec.sectionTitle" class="flex items-center gap-2 mt-8 mb-4 first:mt-0">
                <h2 class="text-lg font-bold text-purple-800">{{ sec.sectionTitle }}</h2>
                <span v-if="sec.sectionSubtitle" class="text-sm text-gray-500 truncate">{{ sec.sectionSubtitle }}</span>
              </div>
              <template v-for="group in sec.groups" :key="sec.key + ':' + (group.bookId ?? group.journalId ?? 'no')">
                <div class="flex items-center gap-3 py-3 mt-4 first:mt-0">
                  <NuxtLink
                    v-if="group.bookId"
                    :to="`/excerpts/library/${group.bookId}`"
                    class="text-sm font-semibold text-blue-700 hover:text-blue-900 hover:underline transition"
                  >{{ group.bookTitle }}</NuxtLink>
                  <NuxtLink
                    v-else-if="group.journalId"
                    :to="`/excerpts/journal/${group.journalId}`"
                    class="text-sm font-semibold text-amber-800 hover:text-amber-950 hover:underline transition"
                  >{{ group.bookTitle }}</NuxtLink>
                  <span v-else class="text-sm font-semibold text-gray-500">（無書目）</span>
                  <span v-if="group.bookAuthor" class="text-xs text-gray-400">{{ group.bookAuthor }}</span>
                  <span v-if="group.bookYear" class="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">{{ group.bookYear }}</span>
                  <div class="flex-1 h-px bg-purple-100"></div>
                </div>

                <div
                  v-for="excerpt in group.items"
                  :key="excerpt.id"
                  :data-excerpt-card-id="excerpt.id"
                  class="bg-white rounded-xl border border-gray-200 p-5 mb-2 hover:border-purple-200 transition-all duration-150 flex gap-3 items-stretch"
                >
                  <div class="flex-1 min-w-0 cursor-pointer" @click="toggleExpand(excerpt.id)">
                    <div class="flex items-start gap-3 mb-2">
                      <span class="text-xs font-mono text-purple-400 bg-purple-50 px-2 py-0.5 rounded mt-0.5 flex-shrink-0 select-none">
                        {{ chapterNumFromSection(sec.sectionTitle) }}-{{ excerpt.seq }}
                      </span>
                      <div class="flex-1 min-w-0">
                        <InlineEdit
                          :value="excerpt.title ?? ''"
                          placeholder="（無標題）"
                          class="font-semibold text-gray-900 text-base leading-snug"
                          @save="(v) => saveExcerptField(excerpt.id, 'title', v)"
                        />
                        <p v-if="searchQ.trim()" class="text-xs text-gray-700 mt-1" v-html="highlightText(excerpt.title || '（無標題）')"></p>
                      </div>
                    </div>
                    <p class="text-xs text-gray-400 mb-3 pl-12">
                      <template v-if="excerpt.book?.id">
                        <span v-if="excerpt.book.author">{{ excerpt.book.author }}</span>
                        <span v-if="excerpt.book.author && (excerpt.book.original_publish_year ?? excerpt.book.publish_year)">
                          （{{ excerpt.book.original_publish_year ?? excerpt.book.publish_year }}）
                        </span>
                        <span v-if="excerpt.book.title" class="mx-1">·</span>
                        <NuxtLink
                          :to="`/excerpts/library/${excerpt.book.id}`"
                          class="text-blue-500 hover:text-blue-700 hover:underline transition"
                        >《{{ excerpt.book.title }}》</NuxtLink>
                      </template>
                      <template v-else-if="excerpt.journalArticle?.id">
                        <span v-if="excerpt.journalArticle.author">{{ excerpt.journalArticle.author }}</span>
                        <span v-if="excerpt.journalArticle.publish_year" class="ml-1">（{{ excerpt.journalArticle.publish_year }}）</span>
                        <span v-if="excerpt.journalArticle.venue" class="mx-1">·</span>
                        <NuxtLink
                          :to="`/excerpts/journal/${excerpt.journalArticle.id}`"
                          class="text-amber-700 hover:text-amber-900 hover:underline transition"
                        >《{{ excerpt.journalArticle.venue }}》</NuxtLink>
                        <span v-if="excerpt.journalArticle.issue_label" class="ml-1">{{ excerpt.journalArticle.issue_label }}</span>
                      </template>
                      <span v-if="excerpt.page_number" class="ml-1">· {{ formatPageLabel(excerpt.page_number, excerpt.content || excerpt.title || '') }}</span>
                    </p>
                    <div class="pl-12">
                      <div
                        class="overflow-hidden transition-all duration-200 relative"
                        :class="expandedExcerptId === excerpt.id ? 'max-h-[1000px]' : 'max-h-[9.75rem]'"
                        :ref="(el) => setContentBoxRef(excerpt.id, el as HTMLElement | null)"
                      >
                        <InlineEdit
                          :value="excerpt.content"
                          placeholder="（無內容）"
                          multiline
                          class="text-sm text-gray-700 leading-relaxed [text-indent:2em]"
                          @save="(v) => saveExcerptField(excerpt.id, 'content', v)"
                        />
                        <div
                          v-if="expandedExcerptId !== excerpt.id && !!overflowById[excerpt.id]"
                          class="absolute bottom-0 left-0 right-0 h-6 bg-gradient-to-t from-white to-transparent pointer-events-none"
                        ></div>
                        <div
                          v-if="expandedExcerptId !== excerpt.id && !!overflowById[excerpt.id]"
                          class="absolute bottom-0 right-1 text-gray-400 text-sm pointer-events-none"
                        >...</div>
                      </div>
                      <p
                        v-if="searchQ.trim()"
                        class="text-sm text-gray-700 leading-relaxed mt-1 whitespace-pre-wrap [text-indent:2em]"
                        v-html="highlightText(excerpt.content || '')"
                      ></p>
                    </div>
                  </div>
                  <div
                    v-if="moveWritingTargets(excerpt).length"
                    class="relative shrink-0 flex flex-col items-center pt-0.5"
                    data-move-topic-root
                    @click.stop
                  >
                    <button
                      type="button"
                      class="w-9 h-9 rounded-xl border border-purple-200 bg-purple-50 text-lg leading-none hover:bg-purple-100 transition flex items-center justify-center"
                      title="轉到其他章節"
                      :disabled="moveBusyId === excerpt.id"
                      @click="toggleMoveChapterMenu(excerpt.id)"
                    >🏷️</button>
                    <div
                      v-if="moveMenuExcerptId === excerpt.id"
                      class="absolute right-0 top-full mt-1 z-30 w-56 rounded-xl border border-gray-200 bg-white py-1.5 shadow-lg"
                    >
                      <p class="px-3 py-1 text-[11px] text-gray-500">轉到章節</p>
                      <button
                        v-for="ch in moveWritingTargets(excerpt)"
                        :key="ch.name"
                        type="button"
                        class="w-full text-left px-3 py-2 text-sm text-gray-800 hover:bg-purple-50"
                        @click="moveExcerptToChapter(excerpt, ch.name)"
                      >{{ ch.name }} <span class="text-gray-400 text-xs">({{ ch.count }})</span></button>
                      <p v-if="!moveWritingTargets(excerpt).length" class="px-3 py-2 text-xs text-gray-400">沒有其他分類</p>
                    </div>
                  </div>
                </div>
              </template>
            </template>
          </div>
        </template>

        <div v-else-if="layoutMode === 'scroll' && scrollLoading" class="space-y-3">
          <div v-for="i in 5" :key="i" class="bg-white rounded-xl border border-gray-200 p-5 animate-pulse">
            <div class="h-5 bg-gray-200 rounded w-1/3 mb-3"></div>
            <div class="space-y-2"><div class="h-3 bg-gray-200 rounded w-full"></div><div class="h-3 bg-gray-200 rounded w-4/5"></div></div>
          </div>
        </div>

        <div
          v-else-if="layoutMode === 'scroll' && !topicNavItems.length"
          class="rounded-xl border border-purple-100 bg-purple-50/80 px-5 py-6 text-sm text-gray-700 mb-4"
        >
          <p class="font-medium text-purple-900">目前沒有「主題」分類列</p>
          <p class="mt-2 text-gray-600 leading-relaxed">
            此著作的摘文若都標在「第一章」這類章名底下，主題檢視會是空的，這是預期行為。
            若要依自訂主題（例如人間佛教、某思想家）瀏覽，請留在本頁按「+ 新增主題」建立主題列，再把摘文歸到該主題。
          </p>
        </div>

        <template v-else-if="layoutMode === 'scroll'">
          <div class="flex gap-2 mb-4 max-w-xl">
            <select v-model="searchField" class="px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white outline-none focus:ring-2 focus:ring-purple-400">
              <option value="all">全部</option>
              <option value="content">內容</option>
              <option value="title">標題</option>
              <option value="book">書名</option>
              <option value="author">作者</option>
            </select>
            <input
              v-model="searchQ"
              placeholder="搜尋全書摘文"
              class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-purple-400"
            />
          </div>
          <div v-if="listWritingEmpty" class="text-center py-20 text-gray-400">
            <p>{{ searchQ.trim() ? '找不到符合的摘文' : '尚無摘文' }}</p>
          </div>
          <div v-else class="space-y-0">
            <template v-for="sec in displayWritingSections" :key="sec.key">
              <div class="flex items-center gap-2 mt-8 mb-4 first:mt-0">
                <h2 class="text-lg font-bold text-purple-800">{{ sec.sectionTitle }}</h2>
                <span v-if="sec.sectionSubtitle" class="text-sm text-gray-500 truncate">{{ sec.sectionSubtitle }}</span>
              </div>
              <template v-for="group in sec.groups" :key="sec.key + ':' + (group.bookId ?? group.journalId ?? 'no')">
                <div class="flex items-center gap-3 py-3 mt-4 first:mt-0">
                  <NuxtLink
                    v-if="group.bookId"
                    :to="`/excerpts/library/${group.bookId}`"
                    class="text-sm font-semibold text-blue-700 hover:text-blue-900 hover:underline transition"
                  >{{ group.bookTitle }}</NuxtLink>
                  <NuxtLink
                    v-else-if="group.journalId"
                    :to="`/excerpts/journal/${group.journalId}`"
                    class="text-sm font-semibold text-amber-800 hover:text-amber-950 hover:underline transition"
                  >{{ group.bookTitle }}</NuxtLink>
                  <span v-else class="text-sm font-semibold text-gray-500">（無書目）</span>
                  <span v-if="group.bookAuthor" class="text-xs text-gray-400">{{ group.bookAuthor }}</span>
                  <span v-if="group.bookYear" class="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">{{ group.bookYear }}</span>
                  <div class="flex-1 h-px bg-purple-100"></div>
                </div>
                <div
                  v-for="excerpt in group.items"
                  :key="excerpt.id"
                  :data-excerpt-card-id="excerpt.id"
                  class="bg-white rounded-xl border border-gray-200 p-5 mb-2 hover:border-purple-200 transition-all duration-150 flex gap-3 items-stretch"
                >
                  <div class="flex-1 min-w-0 cursor-pointer" @click="toggleExpand(excerpt.id)">
                    <div class="flex items-start gap-3 mb-2">
                      <span class="text-xs font-mono text-purple-400 bg-purple-50 px-2 py-0.5 rounded mt-0.5 flex-shrink-0 select-none">
                        {{ chapterNumFromSection(sec.sectionTitle) }}-{{ excerpt.seq }}
                      </span>
                      <div class="flex-1 min-w-0">
                        <InlineEdit
                          :value="excerpt.title ?? ''"
                          placeholder="（無標題）"
                          class="font-semibold text-gray-900 text-base leading-snug"
                          @save="(v) => saveExcerptField(excerpt.id, 'title', v)"
                        />
                        <p v-if="searchQ.trim()" class="text-xs text-gray-700 mt-1" v-html="highlightText(excerpt.title || '（無標題）')"></p>
                      </div>
                    </div>
                    <p class="text-xs text-gray-400 mb-3 pl-12">
                      <template v-if="excerpt.book?.id">
                        <span v-if="excerpt.book.author">{{ excerpt.book.author }}</span>
                        <span v-if="excerpt.book.author && (excerpt.book.original_publish_year ?? excerpt.book.publish_year)">
                          （{{ excerpt.book.original_publish_year ?? excerpt.book.publish_year }}）
                        </span>
                        <span v-if="excerpt.book.title" class="mx-1">·</span>
                        <NuxtLink
                          :to="`/excerpts/library/${excerpt.book.id}`"
                          class="text-blue-500 hover:text-blue-700 hover:underline transition"
                        >《{{ excerpt.book.title }}》</NuxtLink>
                      </template>
                      <template v-else-if="excerpt.journalArticle?.id">
                        <span v-if="excerpt.journalArticle.author">{{ excerpt.journalArticle.author }}</span>
                        <span v-if="excerpt.journalArticle.publish_year" class="ml-1">（{{ excerpt.journalArticle.publish_year }}）</span>
                        <span v-if="excerpt.journalArticle.venue" class="mx-1">·</span>
                        <NuxtLink
                          :to="`/excerpts/journal/${excerpt.journalArticle.id}`"
                          class="text-amber-700 hover:text-amber-900 hover:underline transition"
                        >《{{ excerpt.journalArticle.venue }}》</NuxtLink>
                        <span v-if="excerpt.journalArticle.issue_label" class="ml-1">{{ excerpt.journalArticle.issue_label }}</span>
                      </template>
                      <span v-if="excerpt.page_number" class="ml-1">· {{ formatPageLabel(excerpt.page_number, excerpt.content || excerpt.title || '') }}</span>
                    </p>
                    <div class="pl-12">
                      <div
                        class="overflow-hidden transition-all duration-200 relative"
                        :class="expandedExcerptId === excerpt.id ? 'max-h-[1000px]' : 'max-h-[9.75rem]'"
                        :ref="(el) => setContentBoxRef(excerpt.id, el as HTMLElement | null)"
                      >
                        <InlineEdit
                          :value="excerpt.content"
                          placeholder="（無內容）"
                          multiline
                          class="text-sm text-gray-700 leading-relaxed [text-indent:2em]"
                          @save="(v) => saveExcerptField(excerpt.id, 'content', v)"
                        />
                        <div
                          v-if="expandedExcerptId !== excerpt.id && !!overflowById[excerpt.id]"
                          class="absolute bottom-0 left-0 right-0 h-6 bg-gradient-to-t from-white to-transparent pointer-events-none"
                        ></div>
                        <div
                          v-if="expandedExcerptId !== excerpt.id && !!overflowById[excerpt.id]"
                          class="absolute bottom-0 right-1 text-gray-400 text-sm pointer-events-none"
                        >...</div>
                      </div>
                      <p
                        v-if="searchQ.trim()"
                        class="text-sm text-gray-700 leading-relaxed mt-1 whitespace-pre-wrap [text-indent:2em]"
                        v-html="highlightText(excerpt.content || '')"
                      ></p>
                    </div>
                  </div>
                  <div
                    v-if="moveWritingTargets(excerpt).length"
                    class="relative shrink-0 flex flex-col items-center pt-0.5"
                    data-move-topic-root
                    @click.stop
                  >
                    <button
                      type="button"
                      class="w-9 h-9 rounded-xl border border-purple-200 bg-purple-50 text-lg leading-none hover:bg-purple-100 transition flex items-center justify-center"
                      title="轉到其他章節"
                      :disabled="moveBusyId === excerpt.id"
                      @click="toggleMoveChapterMenu(excerpt.id)"
                    >🏷️</button>
                    <div
                      v-if="moveMenuExcerptId === excerpt.id"
                      class="absolute right-0 top-full mt-1 z-30 w-56 rounded-xl border border-gray-200 bg-white py-1.5 shadow-lg"
                    >
                      <p class="px-3 py-1 text-[11px] text-gray-500">轉到章節</p>
                      <button
                        v-for="ch in moveWritingTargets(excerpt)"
                        :key="ch.name"
                        type="button"
                        class="w-full text-left px-3 py-2 text-sm text-gray-800 hover:bg-purple-50"
                        @click="moveExcerptToChapter(excerpt, ch.name)"
                      >{{ ch.name }} <span class="text-gray-400 text-xs">({{ ch.count }})</span></button>
                      <p v-if="!moveWritingTargets(excerpt).length" class="px-3 py-2 text-xs text-gray-400">沒有其他分類</p>
                    </div>
                  </div>
                </div>
              </template>
            </template>
          </div>
        </template>
      </template>

      <div v-else class="text-center py-20 text-gray-400">找不到此著作項目</div>
    </div>

    <div v-if="showCreate" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="w-full max-w-xl bg-white rounded-2xl border border-gray-200 p-5">
        <h3 class="text-lg font-bold mb-3">新增文摘</h3>
        <input v-model="form.bookQuery" placeholder="搜尋書名/作者（可空白）" class="w-full px-3 py-2 border rounded-lg text-sm mb-2" />
        <div v-if="bookCandidates.length" class="max-h-28 overflow-auto border rounded-lg mb-2">
          <button v-for="b in bookCandidates" :key="b.id" @click="pickBook(b)" class="w-full text-left px-3 py-1.5 text-sm hover:bg-gray-50">{{ b.title }} · {{ b.author || '未知作者' }}</button>
        </div>
        <input v-model="form.title" placeholder="標題" class="w-full px-3 py-2 border rounded-lg text-sm mb-2" />
        <div class="grid grid-cols-2 gap-2 mb-2">
          <input v-model="form.chapter" placeholder="章節（預設帶入目前章）" class="px-3 py-2 border rounded-lg text-sm" />
          <input v-model="form.page_number" placeholder="頁碼" class="px-3 py-2 border rounded-lg text-sm" />
        </div>
        <textarea v-model="form.content" rows="6" placeholder="內文" class="w-full px-3 py-2 border rounded-lg text-sm mb-3" />
        <div class="flex justify-end gap-2">
          <button class="px-3 py-1.5 text-sm text-gray-500" @click="showCreate=false">取消</button>
          <button class="px-3 py-1.5 text-sm bg-purple-600 text-white rounded-lg" @click="createExcerpt">建立</button>
        </div>
      </div>
    </div>

    <div v-if="showOCR" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="w-full max-w-md bg-white rounded-2xl border border-gray-200 p-5">
        <h3 class="text-lg font-bold mb-3">上傳照片 OCR</h3>
        <input type="file" accept="image/*" @change="onPickImage" class="w-full text-sm mb-2" />
        <input v-model="ocrStartPage" placeholder="起始頁碼（預設1）" class="w-full px-3 py-2 border rounded-lg text-sm mb-3" />
        <div class="flex justify-end gap-2">
          <button class="px-3 py-1.5 text-sm text-gray-500" @click="showOCR=false">取消</button>
          <button class="px-3 py-1.5 text-sm bg-purple-600 text-white rounded-lg" @click="uploadOCR">送出</button>
        </div>
      </div>
    </div>

    <div v-if="showCSV" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="w-full max-w-md bg-white rounded-2xl border border-gray-200 p-5">
        <h3 class="text-lg font-bold mb-3">上傳 CSV 匯入文摘</h3>
        <input type="file" accept=".csv,text/csv" @change="onPickCSV" class="w-full text-sm mb-3" />
        <div class="flex justify-end gap-2">
          <button class="px-3 py-1.5 text-sm text-gray-500" @click="showCSV=false">取消</button>
          <button class="px-3 py-1.5 text-sm bg-purple-600 text-white rounded-lg" @click="uploadCSV">送出</button>
        </div>
      </div>
    </div>

    <div v-if="showAddChapter" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="w-full max-w-md bg-white rounded-2xl border border-gray-200 p-5">
        <h3 class="text-lg font-bold text-gray-900 mb-2">新增章節</h3>
        <p class="text-xs text-gray-500 mb-3">章節代碼須與摘文欄位一致（通常為「第一章」格式）；勿與現有章節重複。</p>
        <input v-model="newChapterName" class="w-full px-3 py-2 border rounded-lg text-sm mb-3" placeholder="例：第十一章" />
        <div class="flex justify-end gap-2">
          <button class="px-3 py-1.5 text-sm text-gray-500" @click="showAddChapter = false">取消</button>
          <button class="px-3 py-1.5 text-sm bg-purple-600 text-white rounded-lg" :disabled="chapterBusy" @click="submitNewChapter">建立</button>
        </div>
      </div>
    </div>

    <div v-if="showVolumeEditor" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="w-full max-w-md bg-white rounded-2xl border border-gray-200 p-5 max-h-[90vh] overflow-auto shadow-xl">
        <h3 class="text-lg font-bold text-gray-900 mb-2">章節分卷顯示</h3>
        <p class="text-xs text-gray-500 mb-4 leading-relaxed">
          依「第…章」的章序分卷後，章節檢視會先顯示<strong>一排卷</strong>，點卷後第二排才出現該卷的章。設定寫入專案說明欄位，不會改動摘文。
        </p>
        <label class="block text-xs font-medium text-gray-600 mb-1">每卷幾章</label>
        <input
          v-model.number="volumeEditorChapterSize"
          type="number"
          min="1"
          max="50"
          class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm mb-3 outline-none focus:ring-2 focus:ring-purple-400"
        />
        <label class="block text-xs font-medium text-gray-600 mb-1">卷名（每行一個：第 1 行＝第 1 卷…）</label>
        <textarea
          v-model="volumeEditorLabelsText"
          rows="8"
          class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm mb-2 outline-none focus:ring-2 focus:ring-purple-400"
          placeholder="遠古時代卷&#10;古風時代卷&#10;…"
        />
        <button
          type="button"
          class="text-xs text-purple-700 hover:underline mb-3 block text-left"
          @click="fillThousandFacesVolumePreset"
        >一鍵套用《千面上帝》範例（7 卷 × 每卷 4 章）</button>
        <label class="block text-xs font-medium text-gray-600 mb-1">備註（選填；文章書摘專案會顯示在標題下方）</label>
        <input
          v-model="volumeEditorPublicNote"
          type="text"
          class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm mb-4 outline-none focus:ring-2 focus:ring-purple-400"
        />
        <div class="flex flex-wrap gap-2 justify-end">
          <button type="button" class="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-800" @click="showVolumeEditor = false">關閉</button>
          <button
            type="button"
            class="px-3 py-1.5 text-sm text-red-600 border border-red-200 rounded-lg hover:bg-red-50"
            :disabled="volumeLayoutBusy"
            @click="clearVolumeLayout"
          >取消分卷</button>
          <button
            type="button"
            class="px-3 py-1.5 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-500 disabled:opacity-40"
            :disabled="volumeLayoutBusy"
            @click="saveVolumeLayout"
          >儲存</button>
        </div>
      </div>
    </div>

    <div v-if="showManageChapters" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div class="w-full max-w-lg bg-white rounded-2xl border border-gray-200 p-5 max-h-[85vh] overflow-auto">
        <h3 class="text-lg font-bold text-gray-900 mb-2">管理章節</h3>
        <p class="text-xs text-gray-500 mb-3">↑↓ 調整順序；刪除會將該章摘文改為未分章。</p>
        <ul class="space-y-2 mb-4">
          <li
            v-for="(ch, idx) in manageOrder"
            :key="ch.name"
            class="flex items-center gap-2 rounded-lg border border-gray-100 px-3 py-2 bg-gray-50"
          >
            <div class="flex flex-col gap-0.5">
              <button type="button" class="text-gray-500 hover:text-purple-700 disabled:opacity-30 text-xs" :disabled="idx === 0" @click="moveManageOrder(idx, -1)">↑</button>
              <button type="button" class="text-gray-500 hover:text-purple-700 disabled:opacity-30 text-xs" :disabled="idx === manageOrder.length - 1" @click="moveManageOrder(idx, 1)">↓</button>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-gray-900 text-sm truncate">{{ ch.name }}</p>
              <p v-if="ch.chapterName" class="text-xs text-gray-500 truncate">{{ ch.chapterName }}</p>
            </div>
            <span class="text-xs text-gray-400">{{ ch.count }} 筆</span>
            <button
              v-if="ch.name !== '（未分章）'"
              type="button"
              class="text-xs text-red-600 hover:underline px-1"
              :disabled="chapterBusy"
              @click="deleteChapterRow(ch.name)"
            >刪除</button>
          </li>
        </ul>
        <div class="flex justify-end gap-2">
          <button class="px-3 py-1.5 text-sm text-gray-500" @click="showManageChapters = false">關閉</button>
          <button class="px-3 py-1.5 text-sm bg-purple-600 text-white rounded-lg" :disabled="chapterBusy" @click="saveManageOrder">儲存順序</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const supabase = useSupabaseClient();
const router = useRouter();
const route = useRoute();
const projectId = route.params.id as string;

type ExcerptItem = {
  id: string;
  title: string | null;
  content: string;
  chapter: string | null;
  page_number: string | null;
  seq: number;
  created_at?: string;
  book: {
    id: string;
    title: string;
    author: string;
    publish_year: number | null;
    original_publish_year: number | null;
    sort_year: number;
  } | null;
  journalArticle: {
    id: string;
    title: string;
    venue: string | null;
    author: string | null;
    publish_year: number | null;
    issue_label: string | null;
    sort_year: number;
  } | null;
};

type ChapterInfo = { name: string; count: number; chapterName?: string };
type Overview = {
  project: { id: string; name: string; type: string; description: string | null };
  total: number;
  chapters: ChapterInfo[];
};

type WritingGroup = {
  bookId: string | null;
  journalId: string | null;
  bookTitle: string;
  bookAuthor: string;
  bookYear: number | null;
  items: ExcerptItem[];
};

const loading = ref(true);
const chapLoading = ref(false);
const scrollLoading = ref(false);
const overview = ref<Overview | null>(null);
const activeChapter = ref<string | null>(null);
const activeChapterName = ref("");
const excerpts = ref<ExcerptItem[]>([]);
const allExcerptsAllChapters = ref<ExcerptItem[]>([]);
const layoutMode = ref<"tabs" | "scroll">("tabs");
const books = ref<any[]>([]);
const moveMenuExcerptId = ref<string | null>(null);
const moveBusyId = ref<string | null>(null);
const showAddChapter = ref(false);
const showManageChapters = ref(false);
const newChapterName = ref("");
const manageOrder = ref<{ name: string; count: number; chapterName?: string }[]>([]);
const chapterBusy = ref(false);
const showVolumeEditor = ref(false);
const volumeEditorChapterSize = ref(4);
const volumeEditorLabelsText = ref("");
const volumeEditorPublicNote = ref("");
const volumeLayoutBusy = ref(false);
const addNavKind = ref<"chapter" | "topic">("topic");
const manageNavKind = ref<"chapter" | "topic">("topic");
const chapterNavItems = computed(() => chapterNavRows(overview.value?.chapters ?? []));
const topicNavItems = computed(() => topicNavRows(overview.value?.chapters ?? []));
const excerptLayoutMeta = computed(() => parseExcerptLayoutMeta(overview.value?.project?.description ?? null));
const resolvedExcerptLayoutMeta = computed(() =>
  resolveExcerptLayoutMeta(overview.value?.project?.description ?? null, overview.value?.project?.name ?? null)
);
const chapterNavVolumeGroups = computed(() =>
  groupChaptersByVolume(chapterNavItems.value, resolvedExcerptLayoutMeta.value)
);
const usesVolumeChapterNav = computed(() => chapterNavVolumeGroups.value.some((g) => !!g.title));
const activeVolumeNavIndex = ref<number | null>(null);

watch(usesVolumeChapterNav, (on) => {
  if (!on) activeVolumeNavIndex.value = null;
});

async function selectVolumeNav(idx: number) {
  const group = chapterNavVolumeGroups.value[idx];
  const first = group?.chapters[0]?.name;
  if (!first) return;
  activeVolumeNavIndex.value = idx;
  await selectChapter(first);
}
const searchQ = ref("");
const searchField = ref<"all" | "content" | "title" | "book" | "author">("all");
const showCreate = ref(false);
const showOCR = ref(false);
const showCSV = ref(false);
const ocrFile = ref<File | null>(null);
const csvFile = ref<File | null>(null);
const ocrStartPage = ref("1");
const expandedExcerptId = ref<string | null>(null);
const overflowById = ref<Record<string, boolean>>({});
const contentBoxRefs = new Map<string, HTMLElement>();
const form = ref({
  book_id: "",
  bookQuery: "",
  title: "",
  chapter: "",
  page_number: "",
  content: "",
});
const bookCandidates = computed(() => {
  const q = form.value.bookQuery.trim().toLowerCase();
  if (!q) return books.value.slice(0, 8);
  return books.value.filter((b: any) =>
    (b.title || "").toLowerCase().includes(q) || (b.author || "").toLowerCase().includes(q)
  ).slice(0, 8);
});

// Chapter number (1, 2, 3...) extracted from activeChapter string
const chapterNum = computed(() => {
  if (!activeChapter.value) return "?";
  const nums: Record<string, string> = {
    一:"1",二:"2",三:"3",四:"4",五:"5",六:"6",七:"7",八:"8",九:"9",十:"10",
    十一:"11",十二:"12",十三:"13",十四:"14",十五:"15",十六:"16",十七:"17",十八:"18",
    十九:"19",二十:"20",二十一:"21",二十二:"22",二十三:"23",二十四:"24",
    二十五:"25",二十六:"26",二十七:"27",二十八:"28",二十九:"29",三十:"30",
  };
  const m = activeChapter.value.match(/第(.+)章/);
  return m ? (nums[m[1]] ?? m[1]) : "?";
});

function excerptInWritingChapter(e: ExcerptItem, chapterName: string) {
  if (chapterName === "（未分章）") {
    return e.chapter == null || String(e.chapter).trim() === "" || e.chapter === "（未分章）";
  }
  return e.chapter === chapterName;
}

function writingMatchesSearch(e: ExcerptItem, q: string): boolean {
  if (!q) return true;
  return (
    searchField.value === "title"
      ? !!(e.title || "").toLowerCase().includes(q)
      : searchField.value === "content"
      ? !!(e.content || "").toLowerCase().includes(q)
      : searchField.value === "book"
      ? !!(e.book?.title || "").toLowerCase().includes(q) ||
        !!(e.journalArticle?.title || "").toLowerCase().includes(q) ||
        !!(e.journalArticle?.venue || "").toLowerCase().includes(q)
      : searchField.value === "author"
      ? !!(e.book?.author || "").toLowerCase().includes(q) ||
        !!(e.journalArticle?.author || "").toLowerCase().includes(q)
      : !!(e.title || "").toLowerCase().includes(q) ||
        !!(e.content || "").toLowerCase().includes(q) ||
        !!(e.book?.title || "").toLowerCase().includes(q) ||
        !!(e.book?.author || "").toLowerCase().includes(q) ||
        !!(e.journalArticle?.title || "").toLowerCase().includes(q) ||
        !!(e.journalArticle?.venue || "").toLowerCase().includes(q) ||
        !!(e.journalArticle?.author || "").toLowerCase().includes(q)
  );
}

function pageSortValue(raw: string | null | undefined): number {
  const s = (raw || "").trim().toLowerCase();
  if (!s) return Number.MAX_SAFE_INTEGER;
  const cleaned = s
    .replace(/^p(?:age)?\.?\s*/i, "")
    .replace(/^頁\s*/i, "");
  const m = cleaned.match(/\d+/);
  return m ? Number(m[0]) : Number.MAX_SAFE_INTEGER;
}

function compareExcerptByPage(a: ExcerptItem, b: ExcerptItem): number {
  const pa = pageSortValue(a.page_number);
  const pb = pageSortValue(b.page_number);
  if (pa !== pb) return pa - pb;
  const ta = new Date(a.created_at || 0).getTime();
  const tb = new Date(b.created_at || 0).getTime();
  if (ta !== tb) return ta - tb;
  return a.id.localeCompare(b.id);
}

/** 依書籍／期刊年代 → 同書內依頁碼，最後整章重新編 1、2、3…（搜尋篩選時只對可見列編號） */
function buildWritingBookGroups(exList: ExcerptItem[]): WritingGroup[] {
  const map = new Map<string, WritingGroup>();
  for (const ex of exList) {
    const key = ex.book?.id ?? ex.journalArticle?.id ?? "__none__";
    if (!map.has(key)) {
      const isJ = !!ex.journalArticle?.id;
      map.set(key, {
        bookId: isJ ? null : (ex.book?.id ?? null),
        journalId: isJ ? ex.journalArticle!.id : null,
        bookTitle: isJ
          ? `《${ex.journalArticle!.venue || "期刊"}》${ex.journalArticle!.issue_label ? ` ${ex.journalArticle!.issue_label}` : ""}`.trim()
          : (ex.book?.title ?? "（無書目）"),
        bookAuthor: isJ ? (ex.journalArticle!.author ?? "") : (ex.book?.author ?? ""),
        bookYear: isJ
          ? (ex.journalArticle!.publish_year ?? null)
          : (ex.book?.original_publish_year ?? ex.book?.publish_year ?? null),
        items: [],
      });
    }
    map.get(key)!.items.push(ex);
  }
  const sortYear = (g: WritingGroup) => g.bookYear ?? 9999;
  const sortedGroups = [...map.values()]
    .sort((a, b) => sortYear(a) - sortYear(b))
    .map((g) => ({
      ...g,
      items: [...g.items].sort(compareExcerptByPage),
    }));
  let seq = 1;
  return sortedGroups.map((g) => ({
    ...g,
    items: g.items.map((item) => ({ ...item, seq: seq++ })),
  }));
}

const filteredExcerpts = computed(() => {
  const q = searchQ.value.trim().toLowerCase();
  if (!q) return excerpts.value;
  return excerpts.value.filter((e) =>
    searchField.value === "title"
      ? (e.title || "").toLowerCase().includes(q)
      : searchField.value === "content"
      ? (e.content || "").toLowerCase().includes(q)
      : searchField.value === "book"
      ? (e.book?.title || "").toLowerCase().includes(q) ||
        (e.journalArticle?.title || "").toLowerCase().includes(q) ||
        (e.journalArticle?.venue || "").toLowerCase().includes(q)
      : searchField.value === "author"
      ? (e.book?.author || "").toLowerCase().includes(q) ||
        (e.journalArticle?.author || "").toLowerCase().includes(q)
      : (e.title || "").toLowerCase().includes(q) ||
        (e.content || "").toLowerCase().includes(q) ||
        (e.book?.title || "").toLowerCase().includes(q) ||
        (e.book?.author || "").toLowerCase().includes(q) ||
        (e.journalArticle?.title || "").toLowerCase().includes(q) ||
        (e.journalArticle?.venue || "").toLowerCase().includes(q) ||
        (e.journalArticle?.author || "").toLowerCase().includes(q)
  );
});

const bookGroups = computed(() => buildWritingBookGroups(filteredExcerpts.value));

const globalWritingPool = computed(() => {
  const q = searchQ.value.trim().toLowerCase();
  if (!q) return allExcerptsAllChapters.value;
  return allExcerptsAllChapters.value.filter((e) => writingMatchesSearch(e, q));
});

const scrollWritingSections = computed(() => {
  if (layoutMode.value !== "scroll") return [];
  const pool = globalWritingPool.value;
  return topicNavItems.value.map((ch) => ({
    name: ch.name,
    chapterName: ch.chapterName ?? "",
    groups: buildWritingBookGroups(pool.filter((e) => excerptInWritingChapter(e, ch.name))),
  }));
});

const displayWritingSections = computed(() => {
  if (layoutMode.value === "scroll") {
    return scrollWritingSections.value.map((s) => ({
      key: `s:${s.name}`,
      sectionTitle: s.name,
      sectionSubtitle: s.chapterName,
      groups: s.groups,
    }));
  }
  return [
    {
      key: `t:${activeChapter.value ?? "all"}`,
      sectionTitle: null as string | null,
      sectionSubtitle: null as string | null,
      groups: bookGroups.value,
    },
  ];
});

const scrollHasAnyWriting = computed(() =>
  scrollWritingSections.value.some((s) => s.groups.some((g) => g.items.length))
);

const listWritingEmpty = computed(() => {
  if (layoutMode.value === "tabs") {
    if (!chapterNavItems.value.length) return true;
    return !filteredExcerpts.value.length;
  }
  if (!topicNavItems.value.length) return false;
  return !scrollHasAnyWriting.value;
});

const emptyWritingHint = computed(() => {
  if (searchQ.value.trim()) return "找不到符合的摘文";
  if (layoutMode.value === "tabs" && !chapterNavItems.value.length) {
    return "尚無「第…章」章節；請新增章節，或切換到「主題」檢視以瀏覽主題摘文。";
  }
  if (layoutMode.value === "tabs") return "此章節尚無摘文";
  return "尚無摘文";
});

async function getToken() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) { router.push("/login"); return null; }
  return session.access_token;
}

async function loadAllChaptersExcerpts() {
  const token = await getToken();
  if (!token || !overview.value?.chapters?.length) return;
  scrollLoading.value = true;
  try {
    const acc: ExcerptItem[] = [];
    for (const ch of overview.value.chapters) {
      const data = await $fetch<{ excerpts: ExcerptItem[] }>(
        `/api/projects/${projectId}?chapter=${encodeURIComponent(ch.name)}`,
        { headers: { Authorization: `Bearer ${token}` } }
      ).catch(() => null);
      if (data?.excerpts?.length) acc.push(...data.excerpts);
    }
    allExcerptsAllChapters.value = acc;
  } finally {
    scrollLoading.value = false;
  }
}

function openVolumeEditor() {
  const stored = parseExcerptLayoutMeta(overview.value?.project?.description ?? null);
  const base =
    stored?.volumeLabels?.length
      ? stored
      : resolveExcerptLayoutMeta(overview.value?.project?.description ?? null, overview.value?.project?.name ?? null);
  volumeEditorChapterSize.value = base?.volumeChapterSize ?? 4;
  volumeEditorLabelsText.value = (base?.volumeLabels ?? []).join("\n");
  volumeEditorPublicNote.value = stored?.publicNote ?? "";
  showVolumeEditor.value = true;
}

function fillThousandFacesVolumePreset() {
  volumeEditorChapterSize.value = 4;
  volumeEditorLabelsText.value = PRESET_THOUSAND_FACES_VOLUMES.join("\n");
}

async function saveVolumeLayout() {
  const size = Math.max(1, Math.min(50, Number(volumeEditorChapterSize.value) || 4));
  const labels = volumeEditorLabelsText.value.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
  if (!labels.length) {
    window.alert("請至少輸入一行卷名，或改按「取消分卷」。");
    return;
  }
  const meta: { volumeChapterSize: number; volumeLabels: string[]; publicNote?: string } = {
    volumeChapterSize: size,
    volumeLabels: labels,
  };
  const note = volumeEditorPublicNote.value.trim();
  if (note) meta.publicNote = note;
  const token = await getToken();
  if (!token) return;
  volumeLayoutBusy.value = true;
  try {
    await $fetch(`/api/projects/${projectId}`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}` },
      body: { description: JSON.stringify(meta) },
    });
    showVolumeEditor.value = false;
    await fetchOverview();
  } catch (e: any) {
    window.alert(e?.data?.message || e?.message || "儲存失敗");
  } finally {
    volumeLayoutBusy.value = false;
  }
}

async function clearVolumeLayout() {
  if (!window.confirm("確定取消分卷？章節按鈕會恢復成平鋪一欄。")) return;
  const token = await getToken();
  if (!token) return;
  volumeLayoutBusy.value = true;
  try {
    await $fetch(`/api/projects/${projectId}`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}` },
      body: { description: JSON.stringify({ flatChapters: true }) },
    });
    showVolumeEditor.value = false;
    await fetchOverview();
  } catch (e: any) {
    window.alert(e?.data?.message || e?.message || "更新失敗");
  } finally {
    volumeLayoutBusy.value = false;
  }
}

async function fetchOverview() {
  const token = await getToken(); if (!token) return;
  books.value = await $fetch<any[]>("/api/books", {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => []);
  overview.value = await $fetch<Overview>(`/api/projects/${projectId}`, {
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => null);
  loading.value = false;
  const layoutSaved = localStorage.getItem("excerpts-writing-layout");
  if (layoutSaved === "scroll" || layoutSaved === "tabs") {
    layoutMode.value = layoutSaved;
  }
  if (!overview.value?.chapters?.length) return;
  if (layoutMode.value === "scroll") {
    await loadAllChaptersExcerpts();
  } else {
    const chNav = chapterNavItems.value;
    if (chNav.length) {
      const volMeta = resolveExcerptLayoutMeta(
        overview.value?.project?.description ?? null,
        overview.value?.project?.name ?? null
      );
      if (volMeta?.volumeLabels?.length) {
        const groups = chapterNavVolumeGroups.value;
        const cur = activeChapter.value;
        const curValid = !!(cur && chNav.some((c) => c.name === cur));
        if (curValid && cur) {
          const vgi = volumeGroupIndexForChapter(groups, cur);
          if (vgi != null) {
            activeVolumeNavIndex.value = vgi;
            await selectChapter(cur);
          } else {
            const firstCh = groups[0]?.chapters[0]?.name;
            if (firstCh) {
              activeVolumeNavIndex.value = 0;
              await selectChapter(firstCh);
            } else {
              activeVolumeNavIndex.value = null;
              activeChapter.value = null;
              excerpts.value = [];
            }
          }
        } else {
          const firstCh = groups[0]?.chapters[0]?.name;
          if (firstCh) {
            activeVolumeNavIndex.value = 0;
            await selectChapter(firstCh);
          } else {
            activeVolumeNavIndex.value = null;
            activeChapter.value = null;
            excerpts.value = [];
          }
        }
      } else {
        const first = chNav[0].name;
        if (!activeChapter.value || !chNav.some((c) => c.name === activeChapter.value)) {
          await selectChapter(first);
        } else {
          await selectChapter(activeChapter.value);
        }
      }
    } else {
      activeChapter.value = null;
      excerpts.value = [];
    }
  }
}

async function setLayoutMode(mode: "tabs" | "scroll") {
  layoutMode.value = mode;
  moveMenuExcerptId.value = null;
  localStorage.setItem("excerpts-writing-layout", mode);
  if (!overview.value?.chapters?.length) return;
  if (mode === "scroll") {
    await loadAllChaptersExcerpts();
  } else {
    const chNav = chapterNavItems.value;
    if (chNav.length) {
      const volMeta = resolveExcerptLayoutMeta(
        overview.value?.project?.description ?? null,
        overview.value?.project?.name ?? null
      );
      if (volMeta?.volumeLabels?.length) {
        const groups = chapterNavVolumeGroups.value;
        const cur = activeChapter.value;
        const curValid = !!(cur && chNav.some((c) => c.name === cur));
        if (curValid && cur) {
          const vgi = volumeGroupIndexForChapter(groups, cur);
          if (vgi != null) {
            activeVolumeNavIndex.value = vgi;
            await selectChapter(cur);
          } else {
            const firstCh = groups[0]?.chapters[0]?.name;
            if (firstCh) {
              activeVolumeNavIndex.value = 0;
              await selectChapter(firstCh);
            } else {
              activeVolumeNavIndex.value = null;
              activeChapter.value = null;
              excerpts.value = [];
            }
          }
        } else {
          const firstCh = groups[0]?.chapters[0]?.name;
          if (firstCh) {
            activeVolumeNavIndex.value = 0;
            await selectChapter(firstCh);
          } else {
            activeVolumeNavIndex.value = null;
            activeChapter.value = null;
            excerpts.value = [];
          }
        }
      } else {
        await selectChapter(activeChapter.value && chNav.some((c) => c.name === activeChapter.value)
          ? activeChapter.value
          : chNav[0].name);
      }
    } else {
      activeChapter.value = null;
      excerpts.value = [];
    }
  }
}

function chapterNumFromSection(sectionTitle: string | null): string {
  if (!sectionTitle) return chapterNum.value;
  const nums: Record<string, string> = {
    一:"1",二:"2",三:"3",四:"4",五:"5",六:"6",七:"7",八:"8",九:"9",十:"10",
    十一:"11",十二:"12",十三:"13",十四:"14",十五:"15",十六:"16",十七:"17",十八:"18",
    十九:"19",二十:"20",二十一:"21",二十二:"22",二十三:"23",二十四:"24",
    二十五:"25",二十六:"26",二十七:"27",二十八:"28",二十九:"29",三十:"30",
  };
  const m = sectionTitle.match(/第(.+)章/);
  return m ? (nums[m[1]] ?? m[1]) : "?";
}

function openAddNavRow(kind: "chapter" | "topic") {
  addNavKind.value = kind;
  newChapterName.value = "";
  showAddChapter.value = true;
}

async function submitNewChapter() {
  const name = newChapterName.value.trim();
  if (!name) return;
  if (addNavKind.value === "chapter" && !isChapterNavName(name)) {
    window.alert("章節請使用「第一章」「第二章」這類格式（第…章）。");
    return;
  }
  if (addNavKind.value === "topic" && isChapterNavName(name)) {
    window.alert("主題名稱請勿使用「第…章」格式；若要新增章節請切換到「章節」檢視。");
    return;
  }
  const token = await getToken();
  if (!token) return;
  chapterBusy.value = true;
  try {
    await $fetch(`/api/projects/chapters/${projectId}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: { chapter_code: name, chapter_name: name },
    });
    showAddChapter.value = false;
    newChapterName.value = "";
    await fetchOverview();
    if (addNavKind.value === "chapter" && layoutMode.value === "tabs") {
      await selectChapter(name);
    }
  } catch (e: any) {
    window.alert(e?.data?.message || e?.message || "建立失敗");
  } finally {
    chapterBusy.value = false;
  }
}

function openManageNavRows(kind: "chapter" | "topic") {
  manageNavKind.value = kind;
  manageOrder.value = [...(kind === "chapter" ? chapterNavItems.value : topicNavItems.value)];
  showManageChapters.value = true;
}

function moveManageOrder(i: number, dir: number) {
  const j = i + dir;
  if (j < 0 || j >= manageOrder.value.length) return;
  const arr = [...manageOrder.value];
  [arr[i], arr[j]] = [arr[j], arr[i]];
  manageOrder.value = arr;
}

async function saveManageOrder() {
  const token = await getToken();
  if (!token) return;
  const allCh = overview.value?.chapters ?? [];
  const chaptersOrderedOverview = allCh.filter((c) => isChapterNavName(c.name));
  const topicsOrderedOverview = allCh.filter((c) => !isChapterNavName(c.name));
  const merged =
    manageNavKind.value === "chapter"
      ? [...manageOrder.value, ...topicsOrderedOverview]
      : [...chaptersOrderedOverview, ...manageOrder.value];
  const items = merged
    .filter((c) => c.name !== "（未分章）")
    .map((c) => ({
      chapter_code: c.name,
      chapter_name: (c.chapterName || c.name).trim(),
    }));
  if (!items.length) {
    showManageChapters.value = false;
    return;
  }
  chapterBusy.value = true;
  try {
    await $fetch(`/api/projects/chapters/${projectId}/reorder`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}` },
      body: { items },
    });
    showManageChapters.value = false;
    await fetchOverview();
  } catch (e: any) {
    window.alert(e?.data?.message || e?.message || "儲存失敗");
  } finally {
    chapterBusy.value = false;
  }
}

async function deleteChapterRow(name: string) {
  if (name === "（未分章）") return;
  if (!window.confirm(`確定刪除章節「${name}」？該章摘文將改為未分章。`)) return;
  const token = await getToken();
  if (!token) return;
  chapterBusy.value = true;
  try {
    await $fetch(`/api/projects/chapters/${projectId}?chapter_code=${encodeURIComponent(name)}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    showManageChapters.value = false;
    await fetchOverview();
  } catch (e: any) {
    window.alert(e?.data?.message || e?.message || "刪除失敗");
  } finally {
    chapterBusy.value = false;
  }
}

function writingNavBucket(excerpt: ExcerptItem): string {
  return excerpt.chapter == null || String(excerpt.chapter).trim() === "" || excerpt.chapter === "（未分章）"
    ? "（未分章）"
    : excerpt.chapter!;
}

function moveWritingTargets(excerpt: ExcerptItem) {
  const cur = writingNavBucket(excerpt);
  if (layoutMode.value === "tabs") {
    const others = chapterNavItems.value.filter((c) => c.name !== cur);
    const ua = (overview.value?.chapters ?? []).find((c) => c.name === "（未分章）");
    const out = [...others];
    if (ua && cur !== "（未分章）") out.push(ua);
    return out.filter((c) => c.name !== cur);
  }
  return topicNavItems.value.filter((c) => c.name !== cur);
}

function toggleMoveChapterMenu(excerptId: string) {
  moveMenuExcerptId.value = moveMenuExcerptId.value === excerptId ? null : excerptId;
}

async function moveExcerptToChapter(excerpt: ExcerptItem, newChapter: string) {
  const cur =
    excerpt.chapter == null || String(excerpt.chapter).trim() === "" || excerpt.chapter === "（未分章）"
      ? "（未分章）"
      : excerpt.chapter!;
  if (newChapter === cur) {
    moveMenuExcerptId.value = null;
    return;
  }
  const token = await getToken();
  if (!token) return;
  moveBusyId.value = excerpt.id;
  try {
    await $fetch(`/api/excerpts/${excerpt.id}`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}` },
      body: { chapter: newChapter === "（未分章）" ? null : newChapter },
    });
    moveMenuExcerptId.value = null;
    expandedExcerptId.value = null;
    await fetchOverview();
  } finally {
    moveBusyId.value = null;
  }
}

async function selectChapter(name: string) {
  const token = await getToken(); if (!token) return;
  moveMenuExcerptId.value = null;
  activeChapter.value = name;
  searchQ.value = "";
  const ch = overview.value?.chapters.find((c) => c.name === name);
  activeChapterName.value = ch?.chapterName ?? "";
  chapLoading.value = true;
  const data = await $fetch<{ project: any; chapterName: string; excerpts: ExcerptItem[] }>(
    `/api/projects/${projectId}?chapter=${encodeURIComponent(name)}`,
    { headers: { Authorization: `Bearer ${token}` } }
  ).catch(() => null);
  excerpts.value = data?.excerpts ?? [];
  if (data?.chapterName) activeChapterName.value = data.chapterName;
  chapLoading.value = false;
  if (usesVolumeChapterNav.value) {
    const vgi = volumeGroupIndexForChapter(chapterNavVolumeGroups.value, name);
    if (vgi != null) activeVolumeNavIndex.value = vgi;
  }
}
function pickBook(b: any) {
  form.value.book_id = b.id;
  form.value.bookQuery = `${b.title} · ${b.author || "未知作者"}`;
}
function onPickImage(e: Event) {
  ocrFile.value = (e.target as HTMLInputElement).files?.[0] || null;
}
function onPickCSV(e: Event) {
  csvFile.value = (e.target as HTMLInputElement).files?.[0] || null;
}
async function createExcerpt() {
  const token = await getToken(); if (!token || !form.value.content.trim()) return;
  let bookId = form.value.book_id || null;
  if (!bookId && form.value.bookQuery.trim()) {
    const createdBook = await $fetch<any>("/api/books", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: { title: form.value.bookQuery.trim() },
    }).catch(() => null);
    if (createdBook?.id) {
      bookId = createdBook.id;
      books.value = [createdBook, ...books.value];
    }
  }
  const created = await $fetch<any>("/api/excerpts", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: {
      title: form.value.title,
      content: form.value.content,
      chapter: form.value.chapter || activeChapter.value,
      page_number: form.value.page_number,
      book_id: bookId,
    },
  }).catch(() => null);
  if (!created?.id) return;
  await $fetch(`/api/projects/${projectId}/attach`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: { excerptIds: [created.id] },
  }).catch(() => null);
  showCreate.value = false;
  form.value = { book_id: "", bookQuery: "", title: "", chapter: activeChapter.value || "", page_number: "", content: "" };
  if (layoutMode.value === "scroll") await loadAllChaptersExcerpts();
  else if (activeChapter.value) await selectChapter(activeChapter.value);
}
async function uploadOCR() {
  const token = await getToken(); if (!token || !ocrFile.value) return;
  const fd = new FormData();
  fd.append("image", ocrFile.value);
  if (form.value.book_id) fd.append("bookId", form.value.book_id);
  fd.append("startPage", ocrStartPage.value || "1");
  const r = await $fetch<any>("/api/ai/ocr", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: fd,
  }).catch(() => null);
  const ids = (r?.excerpts ?? []).map((x: any) => x.id).filter(Boolean);
  if (ids.length) {
    await $fetch(`/api/projects/${projectId}/attach`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: { excerptIds: ids },
    }).catch(() => null);
  }
  showOCR.value = false;
  ocrFile.value = null;
  if (layoutMode.value === "scroll") await loadAllChaptersExcerpts();
  else if (activeChapter.value) await selectChapter(activeChapter.value);
}
async function uploadCSV() {
  const token = await getToken(); if (!token || !csvFile.value) return;
  const fd = new FormData();
  fd.append("file", csvFile.value);
  fd.append("projectId", projectId);
  if (form.value.book_id) fd.append("bookId", form.value.book_id);
  await $fetch("/api/excerpts/import-csv", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: fd,
  }).catch(() => null);
  showCSV.value = false;
  csvFile.value = null;
  if (layoutMode.value === "scroll") await loadAllChaptersExcerpts();
  else if (activeChapter.value) await selectChapter(activeChapter.value);
}
function highlightText(text: string): string {
  const q = searchQ.value.trim();
  if (!q) return escapeHtml(text);
  const escaped = q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const reg = new RegExp(`(${escaped})`, "gi");
  return escapeHtml(text).replace(reg, '<mark class="bg-yellow-200 rounded px-0.5">$1</mark>');
}
function toggleExpand(id: string) {
  expandedExcerptId.value = expandedExcerptId.value === id ? null : id;
  nextTick(recomputeOverflow);
}
function setContentBoxRef(id: string, el: HTMLElement | null) {
  if (!el) {
    contentBoxRefs.delete(id);
    return;
  }
  contentBoxRefs.set(id, el);
}
function recomputeOverflow() {
  const next: Record<string, boolean> = {};
  for (const [id, el] of contentBoxRefs.entries()) {
    next[id] = el.scrollHeight > el.clientHeight + 1;
  }
  overflowById.value = next;
}
function onGlobalClick(e: MouseEvent) {
  const target = e.target as HTMLElement | null;
  if (!target) return;
  if (!target.closest("[data-move-topic-root]")) {
    moveMenuExcerptId.value = null;
  }
  if (target.closest("[data-excerpt-card-id]")) return;
  expandedExcerptId.value = null;
  nextTick(recomputeOverflow);
}
function escapeHtml(text: string): string {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}
function formatPageLabel(rawPage: string, contextText: string): string {
  const raw = (rawPage || "").trim();
  if (!raw) return "";
  const cleaned = raw
    .replace(/^p\.?\s*/i, "")
    .replace(/^page\s*/i, "")
    .replace(/^頁\s*/i, "")
    .trim();
  const isChinese = /[\u4E00-\u9FFF]/.test(contextText);
  return isChinese ? `頁${cleaned}` : `p. ${cleaned}`;
}

async function saveExcerptField(id: string, field: "title" | "content", value: string) {
  const token = await getToken(); if (!token) return;
  await $fetch(`/api/excerpts/${id}`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}` },
    body: { [field]: value },
  }).catch(console.error);
  const ex = excerpts.value.find((e) => e.id === id);
  if (ex) (ex as any)[field] = value;
  const ex2 = allExcerptsAllChapters.value.find((e) => e.id === id);
  if (ex2) (ex2 as any)[field] = value;
}

async function saveChapterName(value: string) {
  if (!activeChapter.value) return;
  const token = await getToken(); if (!token) return;
  activeChapterName.value = value;
  await $fetch(`/api/projects/chapters/${projectId}`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}` },
    body: { chapter_code: activeChapter.value, chapter_name: value },
  }).catch(console.error);
  // Update in overview too
  const ch = overview.value?.chapters.find((c) => c.name === activeChapter.value);
  if (ch) ch.chapterName = value;
}

async function handleLogout() { await supabase.auth.signOut(); router.push("/login"); }

onMounted(() => {
  const saved = localStorage.getItem("excerpts-writing-search-field");
  if (saved && ["all", "content", "title", "book", "author"].includes(saved)) {
    searchField.value = saved as any;
  }
  fetchOverview();
  document.addEventListener("click", onGlobalClick);
  window.addEventListener("resize", recomputeOverflow);
  nextTick(recomputeOverflow);
});
onBeforeUnmount(() => {
  document.removeEventListener("click", onGlobalClick);
  window.removeEventListener("resize", recomputeOverflow);
});
watch([displayWritingSections, expandedExcerptId], () => nextTick(recomputeOverflow));
watch(searchField, (v) => {
  localStorage.setItem("excerpts-writing-search-field", v);
});
useHead({ title: computed(() => overview.value ? `${overview.value.project.name} — 著作書摘` : "著作書摘") });
</script>
