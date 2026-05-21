<template>
  <video
    v-if="shouldLoad"
    ref="videoEl"
    :src="`${src}#t=0.1`"
    preload="metadata"
    muted
    playsinline
    :class="cls"
  />
  <div
    v-else
    ref="placeholderEl"
    :class="cls"
    class="bg-stone-200 flex items-center justify-center"
  >
    <span class="text-stone-400 text-2xl">🎬</span>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  src: string;
  cls?: string;
}>();

const shouldLoad = ref(false);
const placeholderEl = ref<HTMLElement | null>(null);
const videoEl = ref<HTMLVideoElement | null>(null);

let observer: IntersectionObserver | null = null;

onMounted(() => {
  if (typeof IntersectionObserver === "undefined") {
    shouldLoad.value = true;
    return;
  }
  observer = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (e.isIntersecting) {
          shouldLoad.value = true;
          observer?.disconnect();
          observer = null;
          break;
        }
      }
    },
    { rootMargin: "200px 0px", threshold: 0.01 },
  );
  if (placeholderEl.value) observer.observe(placeholderEl.value);
});

onBeforeUnmount(() => {
  observer?.disconnect();
  observer = null;
});
</script>
