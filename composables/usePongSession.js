import { ref, computed } from 'vue'

const SESSION_KEY = 'pong_archive_session'
const SESSION_DAYS = 30

const session = ref(null)

export function usePongSession() {
  function loadSession() {
    if (import.meta.server) return
    try {
      const raw = localStorage.getItem(SESSION_KEY)
      if (!raw) { session.value = null; return }
      const data = JSON.parse(raw)
      if (data.expires && Date.now() > data.expires) {
        localStorage.removeItem(SESSION_KEY)
        session.value = null
        return
      }
      session.value = data
    } catch {
      session.value = null
    }
  }

  async function login(email, password) {
    const result = await $fetch('/api/pong-auth/login', {
      method: 'POST',
      body: { email, password },
    })
    const data = {
      ...result,
      expires: Date.now() + SESSION_DAYS * 24 * 60 * 60 * 1000,
    }
    if (import.meta.client) localStorage.setItem(SESSION_KEY, JSON.stringify(data))
    session.value = data
    return data
  }

  function logout() {
    if (import.meta.client) localStorage.removeItem(SESSION_KEY)
    session.value = null
  }

  const isLoggedIn = computed(() => !!session.value)
  const isChief = computed(() => session.value?.role === 'chief')

  return { session, isLoggedIn, isChief, login, logout, loadSession }
}
