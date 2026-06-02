import { node, pc, sp, type FNode, type FEdge } from './helpers'

// SPINE_WAYPOINTS = ['阿丹','努哈','易卜拉欣','伊斯瑪儀','阿德南','穆罕默德']
// 穆罕默德 multi-wife (赫蒂徹 first per spouseField) + 法蒂瑪 (赫蒂徹所生 → 母系分組).

const N: FNode[] = [
  node('adam', '阿丹', 'male', 1),
  node('nuh', '努哈', 'male', 2),
  node('ibrahim', '易卜拉欣', 'male', 3),
  node('ismail', '伊斯瑪儀', 'male', 4),
  node('adnan', '阿德南', 'male', 5),
  node('muhammad', '穆罕默德', 'male', 6, { spouseField: '赫蒂徹、阿伊夏' }),
  node('khadija', '赫蒂徹', 'female', 6),
  node('aisha', '阿伊夏', 'female', 6),
  node('fatima', '法蒂瑪', 'female', 7),
]

const E: FEdge[] = [
  pc('adam', 'nuh'),
  pc('nuh', 'ibrahim'),
  pc('ibrahim', 'ismail'),
  pc('ismail', 'adnan'),
  pc('adnan', 'muhammad'),
  pc('muhammad', 'fatima'),
  pc('khadija', 'fatima'),          // 母系：法蒂瑪 = 赫蒂徹所生
  sp('muhammad', 'khadija'),
  sp('muhammad', 'aisha'),
]

export const islamicGood = { nodes: N, edges: E }

// Broken: drop 阿德南 waypoint → spine chain cannot resolve → hasSpine false.
export const islamicBroken = {
  nodes: N.filter(n => n.id !== 'adnan'),
  edges: E.filter(e => e.source !== 'adnan' && e.target !== 'adnan'),
}

export const allPersonIds = new Set(N.map(n => n.id))
