// @vitest-environment node
import { describe, expect, it } from 'vitest'
import { computeAbstinenceProgress } from '~/data/soldierDiaryConfig'

describe('大兵日記禁慾挑戰進度', () => {
  it('計算已進行日數與成功回報天數', () => {
    const logs = [
      { log_date: '2026-07-02', payload: { abstinence: { targetDays: 7, startDate: '2026-07-01', result: 'success' as const } } },
      { log_date: '2026-07-01', payload: { abstinence: { targetDays: 7, startDate: '2026-07-01', result: 'success' as const } } },
    ]
    expect(computeAbstinenceProgress(logs, '2026-07-03')).toEqual({
      targetDays: 7,
      startDate: '2026-07-01',
      elapsedDays: 3,
      successDays: 2,
      status: 'active',
    })
  })

  it('失敗回報會結束該輪挑戰', () => {
    const logs = [
      { log_date: '2026-07-02', payload: { abstinence: { targetDays: 7, startDate: '2026-07-01', result: 'failure' as const } } },
      { log_date: '2026-07-01', payload: { abstinence: { targetDays: 7, startDate: '2026-07-01', result: 'success' as const } } },
    ]
    expect(computeAbstinenceProgress(logs, '2026-07-02')?.status).toBe('failed')
  })

  it('成功天數達標即完成', () => {
    const logs = [
      { log_date: '2026-07-02', payload: { abstinence: { targetDays: 2, startDate: '2026-07-01', result: 'success' as const } } },
      { log_date: '2026-07-01', payload: { abstinence: { targetDays: 2, startDate: '2026-07-01', result: 'success' as const } } },
    ]
    expect(computeAbstinenceProgress(logs, '2026-07-02')?.status).toBe('completed')
  })
})
