import { node, pc, sp, type FNode, type FEdge } from './helpers'

// Minimal graph that resolves BOTH dual-spine waypoint chains:
//   A: 亞當→…→大衛→所羅門→雅各(馬但)→約瑟→耶穌
//   B: 亞當→…→大衛→拿單→瑪塔→約亞敬→馬利亞→耶穌
// 大衛 is the branch point (所羅門 / 拿單). 耶穌 has two parents (約瑟 legal, 馬利亞 bio).
// Extras: 以撒 + wife 利百加 (no own children → effectiveChildIds inheritance);
//         雅各 + wives 利亞/拉結 (multi-wife single-row placement).

const N: FNode[] = [
  node('adam', '亞當', 'male', 1),
  node('seth', '塞特', 'male', 2),
  node('noah', '挪亞', 'male', 3),
  node('shem', '閃', 'male', 4),
  node('abr', '亞伯拉罕', 'male', 5),
  node('isaac', '以撒', 'male', 6),
  node('rebekah', '利百加', 'female', 6),       // 以撒之妻，無自身 children
  node('jacob', '雅各', 'male', 7),
  node('leah', '利亞', 'female', 7),
  node('rachel', '拉結', 'female', 7),
  node('judah', '猶大', 'male', 8),
  node('levi', '利未', 'male', 8),               // 猶大的兄弟（非脊柱）
  node('david', '大衛（耶西之子）', 'male', 9),
  // A line
  node('solomon', '所羅門（大衛之子）', 'male', 10),
  node('jacobMatthan', '雅各（馬但之子）', 'male', 11),
  node('joseph', '約瑟（馬利亞之夫）', 'male', 12),
  // B line
  node('nathan', '拿單（大衛之子）', 'male', 10),
  node('mattatha', '瑪塔（路加 3:24）', 'male', 11),
  node('joachim', '約亞敬（聖母之父）', 'male', 12),
  node('mary', '馬利亞（耶穌之母）', 'female', 13),
  // Convergence
  node('jesus', '耶穌（拿撒勒人）', 'male', 14),
]

const E: FEdge[] = [
  pc('adam', 'seth'),
  pc('seth', 'noah'),
  pc('noah', 'shem'),
  pc('shem', 'abr'),
  pc('abr', 'isaac'),
  pc('isaac', 'jacob'),
  pc('jacob', 'judah'),
  pc('jacob', 'levi'),
  pc('judah', 'david'),
  // A
  pc('david', 'solomon'),
  pc('solomon', 'jacobMatthan'),
  pc('jacobMatthan', 'joseph'),
  pc('joseph', 'jesus', 'legal'),
  // B
  pc('david', 'nathan'),
  pc('nathan', 'mattatha'),
  pc('mattatha', 'joachim'),
  pc('joachim', 'mary'),
  pc('mary', 'jesus', 'biological'),
  // marriages
  sp('isaac', 'rebekah'),
  sp('jacob', 'leah'),
  sp('jacob', 'rachel'),
]

export const biblicalGood = { nodes: N, edges: E }

// Broken: drop one B-line waypoint person (瑪塔) → spineFromWaypoints returns []
// for B because bfsPath can't reach it → hasSpine false → whole tree disappears.
export const biblicalBroken = {
  nodes: N.filter(n => n.id !== 'mattatha'),
  edges: E.filter(e => e.source !== 'mattatha' && e.target !== 'mattatha'),
}

export const allPersonIds = new Set(N.map(n => n.id))
