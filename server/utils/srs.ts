// ============================================================================
// SM-2 間隔複習演算法（SuperMemo-2）
// quality q：0–5；UI 簡化為 again(2) / hard(3) / good(4) / easy(5)
// ============================================================================

export interface SrsState {
  ease_factor: number;
  interval_days: number;
  repetitions: number;
}

export interface SrsResult extends SrsState {
  next_review: string; // YYYY-MM-DD
  mastery_level: number; // 0–5（給 UI/統計用，由 repetitions 推導）
}

export function sm2(prev: SrsState, q: number): SrsResult {
  let ease = prev.ease_factor || 2.5;
  let reps = prev.repetitions || 0;
  let interval = prev.interval_days || 0;

  if (q < 3) {
    // 答錯：重來
    reps = 0;
    interval = 1;
  } else {
    if (reps === 0) interval = 1;
    else if (reps === 1) interval = 6;
    else interval = Math.round(interval * ease);
    reps += 1;
  }

  // 更新 ease factor
  ease = ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02));
  if (ease < 1.3) ease = 1.3;

  const next = new Date(Date.now() + interval * 86400000).toISOString().slice(0, 10);
  const mastery = Math.min(5, reps);

  return {
    ease_factor: Math.round(ease * 100) / 100,
    interval_days: interval,
    repetitions: reps,
    next_review: next,
    mastery_level: mastery,
  };
}
