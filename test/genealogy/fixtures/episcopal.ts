// GraphIn shape consumed by EpiscopalSpineTree (props.graph).
// One spine cluster (rome) + one east spine (antioch) + two branch sees
// (one 設立 / one 分裂) each attached to a distinct rome bishop so neither
// collapses into a "+N 被立" menu.

function bishop(
  id: string, name: string, succ: number | null,
  start: number | null, end: number | null,
) {
  return {
    id, name_zh: name, name_en: null,
    succession_number: succ, start_year: start, end_year: end,
    appointed_by: null, church: null, status: 'active', notes: null,
  }
}

export const episcopalGood = {
  jesus: { id: 'jesus', name_zh: '耶穌基督', name_en: 'Jesus Christ' },
  apostles: [
    { id: 'peter', name_zh: '彼得', name_en: 'Peter' },
    { id: 'andrew', name_zh: '安得烈', name_en: 'Andrew' },
  ],
  spines: [
    {
      key: 'rome',
      primaryApostleId: 'peter',
      secondaryApostleId: null,
      color: '#b91c1c',
      patriarchateYear: 380,
      see: {
        id: 'see-rome', see_zh: '羅馬', name_zh: '羅馬教座', name_en: 'Rome',
        church: '未分裂教會', tradition: 'catholic', founded_year: 33,
      },
      bishops: [
        bishop('b-peter', '彼得', 1, 33, 67),
        bishop('b-linus', '理諾', 2, 67, 76),
        bishop('b-gregory', '額我略一世', 64, 590, 604),
      ],
    },
    {
      key: 'antioch',
      primaryApostleId: 'andrew',
      secondaryApostleId: null,
      color: '#1d4ed8',
      patriarchateYear: 451,
      see: {
        id: 'see-antioch', see_zh: '安提阿', name_zh: '安提阿教座', name_en: 'Antioch',
        church: '東方教會', tradition: 'orthodox', founded_year: 34,
      },
      bishops: [
        bishop('a-evodius', '歐迪烏', 1, 53, 69),
        bishop('a-ignatius', '依納爵', 2, 70, 107),
      ],
    },
  ],
  branches: [
    {
      id: 'br-canterbury', see_zh: '坎特伯里', name_zh: '坎特伯里教座', name_en: 'Canterbury',
      church: '天主教', tradition: 'catholic', founded_year: 597,
      parent_see_id: 'see-rome', parent_spine_key: 'rome',
      parent_bishop_id: 'b-gregory', is_split: false,   // 設立（不同 see_zh）
      bishops: [bishop('c-augustine', '奧斯定', 1, 597, 604)],
    },
    {
      id: 'br-rome-rival', see_zh: '羅馬', name_zh: '羅馬（對立）', name_en: 'Rome (rival)',
      church: '對立教宗', tradition: 'catholic', founded_year: 70,
      parent_see_id: 'see-rome', parent_spine_key: 'rome',
      parent_bishop_id: 'b-linus', is_split: true,      // 分裂（同 see_zh）
      bishops: [bishop('r-rival', '對立者', 1, 70, 72)],
    },
  ],
  apostolicBranches: [],
  teachings: [],
}

export type EpiscopalGraph = typeof episcopalGood
