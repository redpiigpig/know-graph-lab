/**
 * 大兵日記 登入 session（localStorage，30 天）＋帶 token 的 $fetch 包裝。
 * chief（教官）與 recruit（兵員）共用同一 session 物件，以 role 區分。
 */
import { ref, computed } from 'vue'

const SESSION_KEY = 'soldier_diary_session'
const SESSION_DAYS = 30

export interface SoldierSession {
  token: string
  id: number
  role: 'chief' | 'recruit'
  callsign: string
  name: string
  expires: number
}

const session = ref<SoldierSession | null>(null)
let loaded = false

export function useSoldierSession() {
  function loadSession() {
    if (import.meta.server) return
    loaded = true
    try {
      const raw = localStorage.getItem(SESSION_KEY)
      if (!raw) { session.value = null; return }
      const data = JSON.parse(raw) as SoldierSession
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

  if (import.meta.client && !loaded) loadSession()

  async function login(callsign: string, code: string) {
    const result = await $fetch<any>('/api/soldier-diary/login', {
      method: 'POST',
      body: { callsign, code },
    })
    const data: SoldierSession = {
      token: result.token,
      id: result.id,
      role: result.role,
      callsign: result.callsign,
      name: result.name,
      expires: Date.now() + SESSION_DAYS * 86400000,
    }
    if (import.meta.client) localStorage.setItem(SESSION_KEY, JSON.stringify(data))
    session.value = data
    return data
  }

  function logout() {
    if (import.meta.client) localStorage.removeItem(SESSION_KEY)
    session.value = null
  }

  /** 帶 Authorization token 的 $fetch */
  function authedFetch<T = any>(url: string, opts: any = {}): Promise<T> {
    const token = session.value?.token
    return $fetch<T>(url, {
      ...opts,
      headers: { ...(opts.headers || {}), Authorization: token ? `Bearer ${token}` : '' },
    })
  }

  const isLoggedIn = computed(() => !!session.value)
  const isChief = computed(() => session.value?.role === 'chief')
  const isRecruit = computed(() => session.value?.role === 'recruit')

  return { session, isLoggedIn, isChief, isRecruit, login, logout, loadSession, authedFetch }
}
