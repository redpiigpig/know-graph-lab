/**
 * 大兵日記（A Soldier's Diary）後端共用工具 — service-role Supabase client、
 * 無狀態 HMAC session token、以及 chief / recruit 身分守衛。
 *
 * token 格式：base64url(JSON payload) + "." + HMAC-SHA256（截 32 hex）。
 * secret 用 ENCRYPTION_KEY（既有）＋固定 salt；無狀態、免存 DB。
 */
import { createClient, type SupabaseClient } from '@supabase/supabase-js'
import { createHmac } from 'node:crypto'

export function sdSupabase(): SupabaseClient {
  return createClient(
    process.env.SUPABASE_URL as string,
    process.env.SUPABASE_SERVICE_ROLE_KEY as string,
    { auth: { persistSession: false } },
  )
}

export interface SdAuth {
  id: number // chief 為 0
  role: 'chief' | 'recruit'
  callsign: string
  name: string
}

function secret(): string {
  return (process.env.ENCRYPTION_KEY || 'soldier-diary-dev-secret') + '::soldier-diary'
}

function b64url(s: string): string {
  return Buffer.from(s, 'utf-8').toString('base64url')
}

export function sdSignToken(auth: SdAuth): string {
  const body = b64url(JSON.stringify(auth))
  const sig = createHmac('sha256', secret()).update(body).digest('hex').slice(0, 32)
  return `${body}.${sig}`
}

export function sdVerifyToken(token: string | undefined | null): SdAuth | null {
  if (!token || typeof token !== 'string' || !token.includes('.')) return null
  const [body, sig] = token.split('.')
  const expect = createHmac('sha256', secret()).update(body).digest('hex').slice(0, 32)
  if (sig !== expect) return null
  try {
    const auth = JSON.parse(Buffer.from(body, 'base64url').toString('utf-8'))
    if (auth && (auth.role === 'chief' || auth.role === 'recruit')) return auth as SdAuth
    return null
  } catch {
    return null
  }
}

/** 從 Authorization: Bearer <token> 取出身分，無效則 401 */
export function sdRequireAuth(event: Parameters<typeof defineEventHandler>[0]): SdAuth {
  const token = getHeader(event, 'authorization')?.replace('Bearer ', '')
  const auth = sdVerifyToken(token)
  if (!auth) throw createError({ statusCode: 401, message: '請先登入' })
  return auth
}

/** 僅限長官（chief） */
export function sdRequireChief(event: Parameters<typeof defineEventHandler>[0]): SdAuth {
  const auth = sdRequireAuth(event)
  if (auth.role !== 'chief') throw createError({ statusCode: 403, message: '此操作僅限長官' })
  return auth
}

export const SD_CHIEF_CALLSIGN = '教官'
