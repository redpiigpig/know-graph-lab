// 龐君華會督數位典藏 — 內嵌編輯模式
// 模組層級的單例 ref，讓 layout 和各頁面共用同一個開關
import { ref } from 'vue'

const isEditing = ref(false)
const saveStatus = ref('idle') // 'idle' | 'saving' | 'saved' | 'error'

const timers = {}

export function usePongEditor() {
  function toggleEdit() {
    isEditing.value = !isEditing.value
    if (!isEditing.value) saveStatus.value = 'idle'
  }

  // 單一欄位延遲存檔
  function autosave(key, fn, delay = 700) {
    clearTimeout(timers[key])
    saveStatus.value = 'pending'
    timers[key] = setTimeout(async () => {
      saveStatus.value = 'saving'
      try {
        await fn()
        saveStatus.value = 'saved'
        setTimeout(() => {
          if (saveStatus.value === 'saved') saveStatus.value = 'idle'
        }, 2000)
      } catch (e) {
        saveStatus.value = 'error'
        console.error('[pong-editor] save error:', e)
      }
    }, delay)
  }

  // 批次存多個欄位
  async function saveFields(table, id, fields) {
    saveStatus.value = 'saving'
    try {
      await $fetch('/api/pong-save', {
        method: 'POST',
        body: { table, id, fields },
      })
      saveStatus.value = 'saved'
      setTimeout(() => {
        if (saveStatus.value === 'saved') saveStatus.value = 'idle'
      }, 2000)
    } catch (e) {
      saveStatus.value = 'error'
      console.error('[pong-editor] save error:', e)
    }
  }

  // 便捷：單欄位直接存
  function saveField(table, id, field, value) {
    autosave(`${table}.${id}.${field}`, () =>
      saveFields(table, id, { [field]: value })
    )
  }

  return { isEditing, saveStatus, toggleEdit, saveField, saveFields, autosave }
}
