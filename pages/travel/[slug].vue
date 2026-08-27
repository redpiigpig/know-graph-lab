<template>
  <div class="min-h-screen bg-[#f7f6f1] text-slate-900">
    <AppHeader :title="trip.title" :back="{ to: '/travel', label: '旅遊日誌' }">
      <template #actions>
        <a
          :href="trip.originalPlanUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="hidden text-xs text-slate-400 transition hover:text-emerald-700 sm:inline"
        >原始規劃 ↗</a>
      </template>
    </AppHeader>

    <main>
      <section class="relative overflow-hidden bg-[#103a34] text-white">
        <div class="absolute inset-0 overflow-hidden" aria-hidden="true">
          <div class="absolute -right-20 top-[-110px] h-[330px] w-[330px] rounded-full border-[62px] border-emerald-300/10" />
          <div class="absolute -bottom-48 left-[20%] h-96 w-96 rounded-full bg-amber-200/10 blur-3xl" />
          <svg viewBox="0 0 1200 440" class="absolute inset-0 h-full w-full" preserveAspectRatio="none">
            <path d="M-40 410 C 160 245, 260 350, 420 210 S 760 110, 1240 25" fill="none" stroke="rgba(255,255,255,.11)" stroke-width="2" stroke-dasharray="9 10" />
          </svg>
        </div>

        <div class="relative mx-auto max-w-6xl px-5 py-12 sm:px-8 sm:py-16">
          <div class="grid gap-10 lg:grid-cols-[1fr_360px] lg:items-end">
            <div>
              <p class="text-[11px] font-semibold uppercase tracking-[0.28em] text-emerald-200/70">{{ trip.eyebrow }}</p>
              <h1 class="mt-4 max-w-3xl font-serif text-4xl font-semibold tracking-tight sm:text-6xl">{{ trip.title }}</h1>
              <div class="mt-6 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-emerald-50/75">
                <span>{{ trip.dateLabel }}</span>
                <span class="h-3 w-px bg-white/20" />
                <span>{{ trip.duration }}</span>
                <span class="h-3 w-px bg-white/20" />
                <span>{{ progressLabel }}</span>
              </div>
            </div>

            <div class="rounded-2xl border border-white/15 bg-white/[0.07] p-5 backdrop-blur-sm">
              <div class="mb-4 text-[10px] font-semibold uppercase tracking-[0.22em] text-emerald-100/55">Flight path</div>
              <div class="flex items-center justify-between gap-1">
                <template v-for="(stop, index) in routeStops" :key="`${stop.code}-${index}`">
                  <div class="text-center">
                    <div class="text-lg">{{ stop.flag }}</div>
                    <div class="mt-1 text-[11px] font-semibold tracking-wide text-white/85">{{ stop.code }}</div>
                  </div>
                  <div v-if="index < routeStops.length - 1" class="h-px flex-1 bg-white/20">
                    <span class="block -translate-y-[7px] text-center text-[9px] text-white/35">✦</span>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div class="sticky top-14 z-30 border-b border-stone-200 bg-[#f7f6f1]/95 backdrop-blur">
        <div class="mx-auto flex max-w-6xl gap-1 overflow-x-auto px-4 sm:px-8">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            type="button"
            :class="[
              'whitespace-nowrap border-b-2 px-4 py-4 text-sm font-medium transition',
              activeTab === tab.id
                ? 'border-emerald-700 text-emerald-800'
                : 'border-transparent text-slate-400 hover:text-slate-700',
            ]"
            @click="activeTab = tab.id"
          >{{ tab.label }}</button>
        </div>
      </div>

      <div class="mx-auto max-w-6xl px-5 py-8 sm:px-8 sm:py-12">
        <section v-if="activeTab === 'days'">
          <div class="mb-7 flex gap-2 overflow-x-auto pb-2">
            <button
              v-for="(day, index) in trip.days"
              :key="day.date"
              type="button"
              class="min-w-[82px] rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-left transition hover:-translate-y-0.5 hover:border-emerald-300 hover:shadow-sm"
              @click="scrollToDay(index)"
            >
              <span class="block text-[10px] font-semibold uppercase tracking-wide text-slate-400">Day {{ index + 1 }}</span>
              <span class="mt-0.5 block text-sm font-semibold text-slate-700">{{ day.date }}</span>
              <span class="mt-0.5 block truncate text-[10px] text-slate-400">{{ day.city }}</span>
            </button>
          </div>

          <div class="space-y-7">
            <article
              v-for="(day, index) in trip.days"
              :id="`day-${index + 1}`"
              :key="day.date"
              class="scroll-mt-36 overflow-hidden rounded-[24px] border border-stone-200/80 bg-white shadow-sm"
            >
              <header :class="['border-b px-5 py-5 sm:px-7', accentClasses[day.accent].header]">
                <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div class="flex items-center gap-4">
                    <div :class="['flex h-12 w-12 flex-col items-center justify-center rounded-2xl text-center', accentClasses[day.accent].date]">
                      <span class="text-[9px] font-semibold uppercase tracking-wide">Day</span>
                      <span class="text-lg font-bold leading-none">{{ index + 1 }}</span>
                    </div>
                    <div>
                      <div class="flex flex-wrap items-center gap-2">
                        <h2 class="text-lg font-bold text-slate-900">{{ day.date }} · {{ day.weekday }}</h2>
                        <span class="text-lg" aria-hidden="true">{{ day.flag }}</span>
                      </div>
                      <p class="mt-0.5 text-sm text-slate-500">{{ day.city }}｜{{ day.theme }}</p>
                    </div>
                  </div>
                  <span :class="['w-fit rounded-full px-3 py-1 text-[11px] font-semibold', accentClasses[day.accent].badge]">
                    {{ day.country }}
                  </span>
                </div>
              </header>

              <div class="grid lg:grid-cols-[1fr_280px]">
                <div class="px-5 py-6 sm:px-7">
                  <ol class="relative ml-2 border-l border-stone-200">
                    <li v-for="activity in day.activities" :key="`${activity.time}-${activity.title}`" class="relative pb-7 pl-7 last:pb-0">
                      <span :class="['absolute -left-[7px] top-1 h-3 w-3 rounded-full border-2 border-white ring-1', accentClasses[day.accent].dot]" />
                      <div class="mb-1 flex flex-wrap items-baseline gap-x-3 gap-y-1">
                        <time class="min-w-[48px] text-xs font-bold tabular-nums text-slate-400">{{ activity.time }}</time>
                        <h3 class="font-semibold text-slate-800">{{ activityIcon(activity.kind) }} {{ activity.title }}</h3>
                      </div>
                      <p class="ml-0 text-sm leading-6 text-slate-500 sm:ml-[60px]">{{ activity.detail }}</p>
                      <a
                        v-if="activity.mapQuery"
                        :href="mapHref(activity.mapQuery)"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="ml-0 mt-2 inline-flex text-xs font-medium text-emerald-700 hover:underline sm:ml-[60px]"
                      >地圖導航 ↗</a>
                    </li>
                  </ol>
                </div>

                <aside class="border-t border-stone-100 bg-stone-50/65 px-5 py-6 sm:px-7 lg:border-l lg:border-t-0">
                  <div v-if="day.highlights.length" class="mb-6">
                    <h3 class="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">大型景點</h3>
                    <div class="mt-3 flex flex-wrap gap-2">
                      <span v-for="highlight in day.highlights" :key="highlight" class="rounded-full bg-white px-2.5 py-1 text-[11px] text-slate-600 ring-1 ring-stone-200">{{ highlight }}</span>
                    </div>
                  </div>
                  <h3 class="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">當日交通</h3>
                  <ol class="mt-4 space-y-3">
                    <li v-for="(transport, transportIndex) in day.transport" :key="transport" class="flex gap-3 text-sm leading-5 text-slate-600">
                      <span class="flex h-5 w-5 flex-none items-center justify-center rounded-full bg-white text-[10px] font-bold text-slate-400 ring-1 ring-stone-200">
                        {{ transportIndex + 1 }}
                      </span>
                      <span>{{ transport }}</span>
                    </li>
                  </ol>

                  <div v-if="day.reminder" class="mt-6 rounded-xl border border-amber-100 bg-amber-50/80 p-3.5 text-xs leading-5 text-amber-900/75">
                    <span class="mr-1" aria-hidden="true">☂️</span>{{ day.reminder }}
                  </div>

                  <div class="mt-4 rounded-xl border border-emerald-100 bg-emerald-50/70 p-3.5 text-xs leading-5 text-emerald-900/75">
                    <span class="font-semibold text-emerald-900">當日預算</span><br>
                    {{ day.budgetTwd }}
                  </div>

                  <div class="mt-6 border-t border-dashed border-stone-200 pt-4 text-xs leading-5 text-slate-400">
                    <span class="font-semibold text-slate-500">旅行後記</span><br>
                    照片、今日一句與實際花費，旅途中再補上。
                  </div>
                </aside>
              </div>
            </article>
          </div>

          <section class="mt-10">
            <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">Recommended by friends</p>
            <h2 class="mt-1 font-serif text-3xl font-semibold">朋友推薦景點</h2>
            <div class="mt-5 grid gap-4 lg:grid-cols-3">
              <article v-for="place in trip.friendRecommendations" :key="place.place" class="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
                <div class="flex flex-wrap items-center justify-between gap-2">
                  <span class="text-xs font-semibold text-emerald-700">{{ place.timing }}</span>
                  <span :class="['rounded-full px-2.5 py-1 text-[11px] font-semibold', friendStatusClass(place.status)]">{{ place.status }}</span>
                </div>
                <h3 class="mt-4 font-semibold text-slate-900">{{ place.place }}</h3>
                <p class="mt-3 text-xs leading-5 text-slate-500">{{ place.detail }}</p>
                <p class="mt-3 rounded-xl bg-amber-50 p-3 text-xs leading-5 text-amber-900/75">{{ place.tradeoff }}</p>
                <div class="mt-4 flex gap-3 text-xs font-semibold">
                  <a :href="mapHref(place.mapQuery)" target="_blank" rel="noopener noreferrer" class="text-emerald-700 hover:underline">地圖 ↗</a>
                  <a :href="place.href" target="_blank" rel="noopener noreferrer" class="text-slate-400 hover:text-slate-700 hover:underline">資料 ↗</a>
                </div>
              </article>
            </div>
          </section>

          <section class="mt-16 border-t border-stone-200 pt-12">
            <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-rose-500">Second phase · INEB continuing program</p>
                <h2 class="mt-1 font-serif text-3xl font-semibold text-slate-900">第二階段｜INEB 後續行程</h2>
                <p class="mt-2 text-sm font-medium text-slate-700">{{ trip.inebProgram.titleZh }}</p>
                <p class="mt-1 text-sm text-slate-400">{{ trip.inebProgram.titleEn }}</p>
              </div>
              <div class="flex flex-wrap items-center gap-3">
                <span class="rounded-full bg-rose-50 px-3 py-1.5 text-xs font-semibold text-rose-700">{{ trip.inebProgram.dateLabel }}</span>
                <a :href="trip.inebProgram.sourceUrl" target="_blank" rel="noopener noreferrer" class="text-xs font-semibold text-emerald-700 hover:underline">原始課表 ↗</a>
              </div>
            </div>

            <div class="mt-6 overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm">
              <div class="grid md:grid-cols-2">
                <div class="border-b border-stone-100 p-5 md:border-b-0 md:border-r">
                  <p class="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">中文</p>
                  <p class="mt-3 text-sm font-semibold leading-6 text-slate-800">{{ trip.inebProgram.subtitleZh }}</p>
                  <p class="mt-3 text-xs leading-6 text-slate-500">{{ trip.inebProgram.summaryZh }}</p>
                </div>
                <div class="p-5">
                  <p class="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">English</p>
                  <p class="mt-3 text-sm font-semibold leading-6 text-slate-800">{{ trip.inebProgram.subtitleEn }}</p>
                  <p class="mt-3 text-xs leading-6 text-slate-500">{{ trip.inebProgram.summaryEn }}</p>
                </div>
              </div>
              <div class="grid border-t border-stone-100 md:grid-cols-2">
                <div class="border-b border-stone-100 bg-stone-50/60 p-5 md:border-b-0 md:border-r">
                  <p class="text-xs font-semibold text-slate-700">住宿與衛浴</p>
                  <p class="mt-2 text-xs leading-6 text-slate-500">{{ trip.inebProgram.accommodationZh }}</p>
                </div>
                <div class="bg-stone-50/60 p-5">
                  <p class="text-xs font-semibold text-slate-700">Accommodation</p>
                  <p class="mt-2 text-xs leading-6 text-slate-500">{{ trip.inebProgram.accommodationEn }}</p>
                </div>
              </div>
            </div>

            <div class="mt-6 grid gap-4 lg:grid-cols-3">
              <article v-for="notice in trip.inebProgram.notices" :key="notice.titleEn" :class="['rounded-2xl border p-5', programNoticeClass(notice.level)]">
                <p class="text-sm font-semibold text-slate-900">{{ notice.titleZh }}</p>
                <p class="mt-1 text-xs font-medium text-slate-500">{{ notice.titleEn }}</p>
                <p class="mt-3 text-xs leading-6 text-slate-600">{{ notice.detailZh }}</p>
                <p class="mt-2 text-xs leading-5 text-slate-400">{{ notice.detailEn }}</p>
              </article>
            </div>

            <div class="mt-7 rounded-2xl border border-emerald-100 bg-emerald-50/65 p-5">
              <div class="grid gap-5 md:grid-cols-2">
                <div>
                  <p class="text-sm font-semibold text-emerald-950">個人階段費用</p>
                  <p class="mt-2 text-xs leading-6 text-emerald-900/75">{{ trip.inebProgram.costZh }}</p>
                </div>
                <div>
                  <p class="text-sm font-semibold text-emerald-950">Personal-phase cost</p>
                  <p class="mt-2 text-xs leading-6 text-emerald-900/65">{{ trip.inebProgram.costEn }}</p>
                </div>
              </div>
            </div>

            <div class="mt-8 space-y-5">
              <article v-for="programDay in trip.inebProgram.days" :key="programDay.date" class="overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm">
                <header class="border-b border-stone-100 bg-slate-50 px-5 py-4 sm:px-6">
                  <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <p class="text-xs font-bold tabular-nums text-rose-600">{{ programDay.date }} · {{ programDay.weekdayZh }} / {{ programDay.weekdayEn }}</p>
                      <h3 class="mt-1 text-lg font-semibold text-slate-900">{{ programDay.themeZh }}</h3>
                      <p class="mt-0.5 text-sm text-slate-500">{{ programDay.themeEn }}</p>
                    </div>
                    <div class="text-left text-xs leading-5 text-slate-400 sm:text-right">
                      <div>{{ programDay.locationZh }}</div>
                      <div>{{ programDay.locationEn }}</div>
                    </div>
                  </div>
                </header>

                <div class="hidden grid-cols-[110px_1fr_1fr] border-b border-stone-100 bg-stone-50/50 px-5 py-2 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400 sm:grid sm:px-6">
                  <span>Time</span><span>中文</span><span>English</span>
                </div>
                <div>
                  <div v-for="item in programDay.items" :key="`${programDay.date}-${item.time}-${item.en}`" class="grid gap-2 border-b border-stone-100 px-5 py-3 last:border-b-0 sm:grid-cols-[110px_1fr_1fr] sm:gap-4 sm:px-6">
                    <div class="text-xs font-bold tabular-nums text-rose-600">{{ item.time }}</div>
                    <div class="text-sm leading-5 text-slate-700">{{ item.zh }}</div>
                    <div class="text-sm leading-5 text-slate-400">{{ item.en }}</div>
                  </div>
                </div>

                <div v-if="programDay.personalNoteZh" class="grid gap-3 border-t border-amber-100 bg-amber-50/70 px-5 py-4 text-xs leading-5 sm:grid-cols-2 sm:px-6">
                  <p class="text-amber-900/80"><span class="font-semibold text-amber-900">個人提醒：</span>{{ programDay.personalNoteZh }}</p>
                  <p class="text-amber-900/55"><span class="font-semibold text-amber-900/70">Personal note: </span>{{ programDay.personalNoteEn }}</p>
                </div>
              </article>
            </div>
          </section>
        </section>

        <section v-else-if="activeTab === 'bookings'" class="space-y-10">
          <div class="grid gap-3">
            <div v-for="alert in trip.bookingAlerts" :key="alert" class="rounded-2xl border border-amber-200 bg-amber-50 px-5 py-4 text-sm leading-6 text-amber-900">
              {{ alert }}
            </div>
          </div>
          <div>
            <div class="mb-5 flex items-end justify-between gap-4">
              <div>
                <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">Flights</p>
                <h2 class="mt-1 font-serif text-3xl font-semibold">四段航班</h2>
              </div>
              <span class="text-xs text-slate-400">時間均為當地時間</span>
            </div>
            <div class="grid gap-4 md:grid-cols-2">
              <article v-for="flight in trip.flights" :key="flight.flightNo" class="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
                <div class="flex items-center justify-between gap-4">
                  <div class="text-sm font-semibold text-slate-800">{{ flight.route }}</div>
                  <span class="rounded-full bg-sky-50 px-2.5 py-1 text-xs font-bold text-sky-700">{{ flight.flightNo }}</span>
                </div>
                <div class="mt-1 text-xs text-slate-400">{{ flight.airline }} · 經濟艙</div>
                <div class="mt-5 grid grid-cols-[1fr_auto_1fr] items-center gap-3">
                  <div>
                    <div class="text-lg font-bold tabular-nums text-slate-900">{{ flight.depart }}</div>
                    <div class="mt-1 text-xs text-slate-500">{{ flight.departAirport }}</div>
                  </div>
                  <div class="flex items-center gap-1 text-slate-300"><span>—</span><span>✈</span><span>—</span></div>
                  <div class="text-right">
                    <div class="text-lg font-bold tabular-nums text-slate-900">{{ flight.arrive }}</div>
                    <div class="mt-1 text-xs text-slate-500">{{ flight.arriveAirport }}</div>
                  </div>
                </div>
              </article>
            </div>
          </div>

          <div>
            <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">Hotels</p>
            <h2 class="mt-1 font-serif text-3xl font-semibold">三間住宿</h2>
            <div class="mt-5 grid gap-4 lg:grid-cols-3">
              <article v-for="hotel in trip.hotels" :key="hotel.nameLocal" class="flex flex-col rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
                <div class="flex items-center justify-between gap-3 text-xs">
                  <span class="font-semibold text-emerald-700">{{ hotel.city }}</span>
                  <span class="text-slate-400">{{ hotel.nights }}</span>
                </div>
                <h3 class="mt-4 font-semibold leading-6 text-slate-900">{{ hotel.nameZh }}</h3>
                <p class="mt-0.5 text-xs text-slate-400">{{ hotel.nameLocal }}</p>
                <p class="mt-4 flex-1 text-xs leading-5 text-slate-500">{{ hotel.address }}</p>
                <p class="mt-3 text-sm font-bold tabular-nums text-slate-800">實付 {{ formatTwd(hotel.paidTwd) }}</p>
                <div class="mt-5 flex gap-2 border-t border-stone-100 pt-4">
                  <a :href="`tel:${hotel.phone.replace(/\s/g, '')}`" class="rounded-lg bg-stone-100 px-3 py-2 text-xs font-medium text-slate-600 hover:bg-stone-200">撥電話</a>
                  <a :href="mapHref(hotel.mapQuery)" target="_blank" rel="noopener noreferrer" class="rounded-lg bg-emerald-50 px-3 py-2 text-xs font-medium text-emerald-700 hover:bg-emerald-100">開地圖 ↗</a>
                </div>
              </article>
            </div>
          </div>

          <div class="rounded-2xl border border-sky-100 bg-sky-50/70 p-5 text-sm leading-6 text-sky-900/75">
            <strong class="text-sky-900">機場交通重點：</strong>
            新加坡以 MRT 為主；吉隆坡優先用 KLIA Ekspres 連接 KL Sentral；曼谷抵達時可用 Airport Rail Link＋Grab，回程深夜則建議由飯店直接叫車。
          </div>

          <div>
            <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">Transit tickets</p>
            <h2 class="mt-1 font-serif text-3xl font-semibold">三城市交通與買票方式</h2>
            <div class="mt-5 grid gap-4 lg:grid-cols-3">
              <article v-for="guide in trip.transitGuides" :key="guide.city" class="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
                <div class="flex items-center gap-3">
                  <span class="text-2xl">{{ guide.flag }}</span>
                  <div>
                    <h3 class="font-semibold text-slate-900">{{ guide.city }}</h3>
                    <p class="text-xs text-slate-400">{{ guide.modes }}</p>
                  </div>
                </div>
                <dl class="mt-5 space-y-4 text-xs leading-5">
                  <div><dt class="font-semibold text-slate-700">行程怎麼搭</dt><dd class="mt-1 text-slate-500">{{ guide.itineraryUse }}</dd></div>
                  <div><dt class="font-semibold text-slate-700">現場怎麼付</dt><dd class="mt-1 text-slate-500">{{ guide.payment }}</dd></div>
                  <div><dt class="font-semibold text-emerald-700">建議方案</dt><dd class="mt-1 text-slate-600">{{ guide.recommendation }}</dd></div>
                </dl>
                <div class="mt-4 rounded-xl bg-amber-50 p-3 text-xs leading-5 text-amber-900/75">{{ guide.caution }}</div>
                <a :href="guide.href" target="_blank" rel="noopener noreferrer" class="mt-4 inline-flex text-xs font-semibold text-emerald-700 hover:underline">官方票務資訊 ↗</a>
              </article>
            </div>
          </div>
        </section>

        <section v-else-if="activeTab === 'costs'" class="space-y-8">
          <div>
            <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">Budget for three adults</p>
            <h2 class="mt-1 font-serif text-3xl font-semibold">三位成人費用</h2>
          </div>

          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div class="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
              <p class="text-xs text-slate-400">機票實付</p>
              <p class="mt-2 text-2xl font-bold tabular-nums">{{ formatTwd(trip.costs.flightTotalTwd) }}</p>
            </div>
            <div class="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
              <p class="text-xs text-slate-400">飯店實付</p>
              <p class="mt-2 text-2xl font-bold tabular-nums">{{ formatTwd(trip.costs.hotelTotalTwd) }}</p>
            </div>
            <div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-5 shadow-sm">
              <p class="text-xs text-emerald-700">已付固定支出</p>
              <p class="mt-2 text-2xl font-bold tabular-nums text-emerald-900">{{ formatTwd(trip.costs.fixedTotalTwd) }}</p>
              <p class="mt-1 text-xs text-emerald-700">平均約 {{ formatTwd(Math.round(trip.costs.fixedTotalTwd / 3)) }}／人</p>
            </div>
            <div class="rounded-2xl bg-[#173f39] p-5 text-white shadow-sm">
              <p class="text-xs text-emerald-100/70">家庭旅行總預算</p>
              <p class="mt-2 text-xl font-bold tabular-nums">{{ formatTwd(trip.costs.projectedMinTwd) }}</p>
              <p class="text-xs text-emerald-100/65">至</p>
              <p class="text-xl font-bold tabular-nums">{{ formatTwd(trip.costs.projectedMaxTwd) }}</p>
            </div>
          </div>

          <div class="grid gap-6 lg:grid-cols-[1fr_340px]">
            <div class="overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm">
              <div class="border-b border-stone-100 px-5 py-4"><h3 class="font-semibold">Trip.com 訂單明細</h3></div>
              <div class="divide-y divide-stone-100">
                <div v-for="item in trip.costs.items" :key="item.label" class="grid gap-2 px-5 py-4 sm:grid-cols-[1fr_auto] sm:items-center">
                  <div>
                    <p class="text-sm font-semibold text-slate-800">{{ item.label }}</p>
                    <p class="mt-1 text-xs leading-5 text-slate-400">{{ item.detail }}</p>
                  </div>
                  <div class="sm:text-right">
                    <p class="font-bold tabular-nums text-slate-900">{{ formatTwd(item.totalTwd) }}</p>
                    <p class="text-[11px] text-slate-400">每人 {{ formatTwd(item.perPersonTwd) }}</p>
                  </div>
                </div>
              </div>
            </div>

            <aside class="rounded-2xl border border-sky-100 bg-sky-50/70 p-6 text-sm leading-6 text-sky-900/75">
              <h3 class="font-semibold text-sky-950">當地活動預算</h3>
              <p class="mt-3 text-2xl font-bold tabular-nums text-sky-950">{{ formatTwd(trip.costs.localBudgetMinTwd) }}–{{ formatTwd(trip.costs.localBudgetMaxTwd).replace('NT$', '') }}</p>
              <p class="mt-3">含三人餐飲、門票、市區交通、包車與 10% 機動金；不含購物、保險、eSIM，以及 07/24 後的 INEB 費用。</p>
            </aside>
          </div>
        </section>

        <section v-else-if="activeTab === 'movies'" class="space-y-8">
          <div>
            <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">Screen locations</p>
            <h2 class="mt-1 font-serif text-3xl font-semibold">電影・動漫拍照地圖</h2>
            <p class="mt-3 max-w-3xl text-sm leading-6 text-slate-500">主行程與順路短停已嵌入每日時間表；備選場景只有在不犧牲休息與主要文化景點時才加排。</p>
          </div>

          <div class="grid gap-4 md:grid-cols-2">
            <article v-for="spot in trip.movieSpots" :key="`${spot.work}-${spot.location}`" class="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <span class="text-xs font-semibold text-emerald-700">{{ spot.city }} · {{ spot.day }}</span>
                <span :class="['rounded-full px-2.5 py-1 text-[11px] font-semibold', movieStatusClass(spot.status)]">{{ spot.status }}</span>
              </div>
              <h3 class="mt-4 font-semibold leading-6 text-slate-900">{{ spot.work }}</h3>
              <p class="mt-1 text-sm font-medium text-slate-600">{{ spot.location }}</p>
              <p class="mt-3 text-xs leading-5 text-slate-500">{{ spot.photoTip }}</p>
              <div class="mt-4 flex gap-3 border-t border-stone-100 pt-4 text-xs font-semibold">
                <a :href="mapHref(spot.mapQuery)" target="_blank" rel="noopener noreferrer" class="text-emerald-700 hover:underline">開啟地圖 ↗</a>
                <a :href="spot.href" target="_blank" rel="noopener noreferrer" class="text-slate-400 hover:text-slate-700 hover:underline">場景資料 ↗</a>
              </div>
            </article>
          </div>
        </section>

        <section v-else class="space-y-10">
          <div class="rounded-2xl border border-red-100 bg-white p-6 shadow-sm">
            <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-red-500">Sensitive insurance data</p>
                <h2 class="mt-1 font-serif text-3xl font-semibold">保險投保資料</h2>
                <p class="mt-3 max-w-2xl text-sm leading-6 text-slate-500">網站只顯示遮罩資料；完整身分證、手機與信箱保存在私人 Notion 子頁。投保表生日統一使用西元，民國日期保留供核對。</p>
              </div>
              <a :href="trip.insuranceSummary.notionUrl" target="_blank" rel="noopener noreferrer" class="inline-flex w-fit rounded-xl bg-red-50 px-4 py-2.5 text-sm font-semibold text-red-700 hover:bg-red-100">開啟完整投保資料 🔒</a>
            </div>

            <div class="mt-6 grid gap-4 lg:grid-cols-3">
              <article v-for="person in trip.insuranceSummary.people" :key="person.name" class="rounded-xl bg-stone-50 p-4">
                <div class="text-[10px] font-semibold uppercase tracking-wide text-slate-400">{{ person.role }}</div>
                <h3 class="mt-2 font-semibold text-slate-900">{{ person.name }}</h3>
                <p class="text-xs text-slate-400">{{ person.englishName }}</p>
                <dl class="mt-4 space-y-2 text-xs leading-5 text-slate-600">
                  <div class="flex justify-between gap-4"><dt>西元生日</dt><dd class="font-medium">{{ person.birth }}</dd></div>
                  <div class="flex justify-between gap-4"><dt>民國對照</dt><dd>{{ person.rocBirth }}</dd></div>
                  <div class="flex justify-between gap-4"><dt>身分證</dt><dd class="font-mono">{{ person.idMasked }}</dd></div>
                </dl>
              </article>
            </div>

            <div class="mt-5 overflow-hidden rounded-xl border border-stone-200">
              <div v-for="flight in trip.insuranceSummary.flights" :key="flight.label" class="grid gap-2 border-b border-stone-100 bg-white px-4 py-3 text-xs last:border-b-0 sm:grid-cols-[120px_1fr_1fr_1fr]">
                <span class="font-semibold text-slate-700">{{ flight.label }}</span>
                <span>{{ flight.flight }}</span>
                <span class="text-slate-500">{{ flight.route }}</span>
                <span class="font-medium tabular-nums text-slate-700">{{ flight.time }}</span>
              </div>
            </div>
          </div>

          <div>
            <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">Before departure</p>
            <h2 class="mt-1 font-serif text-3xl font-semibold">三國入境資料</h2>
            <p class="mt-3 max-w-2xl text-sm leading-6 text-slate-500">只從政府官方網站填寫；旅行社或搜尋廣告可能收取不必要費用。</p>

            <div class="mt-6 grid gap-4 lg:grid-cols-3">
              <a
                v-for="task in trip.entryTasks"
                :key="task.title"
                :href="task.href"
                target="_blank"
                rel="noopener noreferrer"
                class="group rounded-2xl border border-stone-200 bg-white p-5 text-inherit no-underline shadow-sm transition hover:-translate-y-0.5 hover:border-emerald-300 hover:shadow-md"
              >
                <div class="flex items-center justify-between gap-3">
                  <span class="text-2xl">{{ task.flag }}</span>
                  <span class="rounded-full bg-amber-50 px-2.5 py-1 text-[11px] font-semibold text-amber-700">{{ task.openDate }}</span>
                </div>
                <div class="mt-4 text-xs font-semibold text-slate-400">{{ task.country }}</div>
                <h3 class="mt-1 font-semibold text-slate-900">{{ task.title }}</h3>
                <p class="mt-3 text-xs leading-5 text-slate-500">{{ task.note }}</p>
                <span class="mt-4 inline-flex text-xs font-semibold text-emerald-700 group-hover:underline">前往官方網站 ↗</span>
              </a>
            </div>
          </div>

          <div class="grid gap-6 lg:grid-cols-[1fr_340px]">
            <div class="space-y-5">
              <section v-for="group in trip.checklistGroups" :key="group.id" class="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm">
                <div class="flex flex-wrap items-end justify-between gap-3">
                  <div>
                    <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-700">{{ group.owner }}</p>
                    <h2 class="mt-1 font-serif text-2xl font-semibold">{{ group.title }}</h2>
                  </div>
                  <span class="text-xs text-slate-400">{{ completedCount(group.id, group.items) }}／{{ group.items.length }} 完成</span>
                </div>
                <div class="mt-5 grid gap-3 sm:grid-cols-2">
                  <label v-for="item in group.items" :key="item" class="flex cursor-pointer items-start gap-3 rounded-xl bg-stone-50 px-4 py-3 text-sm leading-5 text-slate-600 transition hover:bg-stone-100">
                    <input v-model="checkedItems[checkKey(group.id, item)]" type="checkbox" class="mt-0.5 h-4 w-4 rounded border-stone-300 text-emerald-700 focus:ring-emerald-600">
                    <span :class="checkedItems[checkKey(group.id, item)] ? 'text-slate-400 line-through' : ''">{{ item }}</span>
                  </label>
                </div>
              </section>
            </div>

            <aside class="rounded-2xl bg-[#173f39] p-6 text-white shadow-sm">
              <div class="text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-200/65">Family travel notes</div>
              <h2 class="mt-2 font-serif text-2xl font-semibold">全家移動原則</h2>
              <ul class="mt-5 space-y-4 text-sm leading-6 text-emerald-50/75">
                <li>• 行李多或下雨時，短程 Grab 通常比多次轉乘更省體力。</li>
                <li>• 國際線以起飛前 3 小時抵達航廈為目標。</li>
                <li>• 每天保留一個可刪景點；午後雷雨時先進商場或飯店休息。</li>
                <li>• 護照、保險、登機證與三國入境卡各存一份離線截圖。</li>
              </ul>
            </aside>
          </div>

          <div>
            <h2 class="font-serif text-2xl font-semibold">資料來源與即時確認</h2>
            <div class="mt-4 flex flex-wrap gap-2">
              <a
                v-for="link in trip.officialLinks"
                :key="link.href"
                :href="link.href"
                target="_blank"
                rel="noopener noreferrer"
                class="rounded-full border border-stone-200 bg-white px-3.5 py-2 text-xs font-medium text-slate-600 transition hover:border-emerald-300 hover:text-emerald-700"
              >{{ link.label }} ↗</a>
            </div>
            <p class="mt-4 text-xs leading-5 text-slate-400">交通時刻、票價、景點開放與入境規定可能臨時調整；請在前一晚再點官方連結確認。</p>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { southeastAsiaTrip2026 as trip } from '~/data/travel'
import type { TravelActivity } from '~/data/travel'

definePageMeta({ middleware: 'auth' })
useHead({ title: `${trip.title} — 旅遊日誌` })

const route = useRoute()
if (route.params.slug !== trip.slug) {
  throw createError({ statusCode: 404, statusMessage: '找不到這趟旅程' })
}

const tabs = [
  { id: 'days', label: '每日行程' },
  { id: 'bookings', label: '航班住宿' },
  { id: 'costs', label: '費用估算' },
  { id: 'movies', label: '電影場景' },
  { id: 'prepare', label: '行前資訊' },
] as const
type TabId = (typeof tabs)[number]['id']
const activeTab = ref<TabId>('days')

const routeStops = [
  { code: 'TPE', flag: '🇹🇼' },
  { code: 'SIN', flag: '🇸🇬' },
  { code: 'KUL', flag: '🇲🇾' },
  { code: 'BKK', flag: '🇹🇭' },
  { code: 'TPE', flag: '🇹🇼' },
]

const checklistStorageKey = 'travel:singapore-malaysia-thailand-2026:checklist'
const checkedItems = ref<Record<string, boolean>>({})

onMounted(() => {
  try {
    checkedItems.value = JSON.parse(localStorage.getItem(checklistStorageKey) || '{}')
  }
  catch {
    checkedItems.value = {}
  }
})

watch(checkedItems, (value) => {
  localStorage.setItem(checklistStorageKey, JSON.stringify(value))
}, { deep: true })

function checkKey(groupId: string, item: string) {
  return `${groupId}:${item}`
}

function completedCount(groupId: string, items: string[]) {
  return items.filter(item => checkedItems.value[checkKey(groupId, item)]).length
}

const accentClasses = {
  emerald: {
    header: 'border-emerald-100 bg-emerald-50/70',
    date: 'bg-emerald-700 text-white',
    badge: 'bg-emerald-100 text-emerald-700',
    dot: 'bg-emerald-600 ring-emerald-200',
  },
  amber: {
    header: 'border-amber-100 bg-amber-50/70',
    date: 'bg-amber-600 text-white',
    badge: 'bg-amber-100 text-amber-700',
    dot: 'bg-amber-500 ring-amber-200',
  },
  rose: {
    header: 'border-rose-100 bg-rose-50/70',
    date: 'bg-rose-600 text-white',
    badge: 'bg-rose-100 text-rose-700',
    dot: 'bg-rose-500 ring-rose-200',
  },
  slate: {
    header: 'border-slate-100 bg-slate-50',
    date: 'bg-slate-700 text-white',
    badge: 'bg-slate-100 text-slate-600',
    dot: 'bg-slate-500 ring-slate-200',
  },
}

const progressLabel = computed(() => {
  const now = new Date()
  const start = new Date(`${trip.startDate}T00:00:00+08:00`)
  const end = new Date(`${trip.endDate}T23:59:59+08:00`)
  if (now > end) return '旅程完成，待補日誌'
  if (now >= start) return '旅途中'
  const days = Math.ceil((start.getTime() - now.getTime()) / 86_400_000)
  return `距離出發 ${days} 天`
})

function activityIcon(kind: TravelActivity['kind']) {
  return {
    flight: '✈️',
    food: '🍜',
    sight: '📍',
    hotel: '🛏️',
    transfer: '🚉',
    free: '✦',
  }[kind]
}

function programNoticeClass(level: 'duplicate' | 'conflict' | 'budget') {
  return {
    duplicate: 'border-amber-200 bg-amber-50/70',
    conflict: 'border-rose-200 bg-rose-50/70',
    budget: 'border-sky-200 bg-sky-50/70',
  }[level]
}

function mapHref(query: string) {
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`
}

function formatTwd(value: number) {
  return `NT$${new Intl.NumberFormat('zh-TW').format(value)}`
}

function movieStatusClass(status: '主行程' | '順路短停' | '備選') {
  return {
    主行程: 'bg-emerald-100 text-emerald-700',
    順路短停: 'bg-sky-100 text-sky-700',
    備選: 'bg-stone-100 text-slate-500',
  }[status]
}

function friendStatusClass(status: '已排入' | '原本已有' | '半日備選') {
  return {
    已排入: 'bg-emerald-100 text-emerald-700',
    原本已有: 'bg-sky-100 text-sky-700',
    半日備選: 'bg-amber-100 text-amber-700',
  }[status]
}

function scrollToDay(index: number) {
  document.getElementById(`day-${index + 1}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>
