export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const { text } = await readBody(event)

  if (!text?.trim()) {
    throw createError({ statusCode: 400, message: '請提供譜系文字' })
  }

  const systemPrompt = `你是一位專業的族譜分析師。請分析以下文字，提取其中所有人物及其關係，輸出用於繪製族譜圖的 JSON 資料。

只輸出 JSON，不要任何說明。格式如下：
{
  "nodes": [
    {
      "id": "p1",
      "type": "person",
      "label": "姓名",
      "position": { "x": 0, "y": 0 },
      "data": {
        "name": "姓名",
        "gender": "male" | "female" | "unknown",
        "generation": "輩分或稱謂（如：祖父、父親、長子）",
        "birthYear": "出生年（如 1920，無則空字串）",
        "deathYear": "卒年（如 1985，無則空字串）",
        "notes": "備注（可選）",
        "shape": "rectangle"
      }
    }
  ],
  "edges": [
    {
      "id": "e1",
      "source": "p1",
      "target": "p2",
      "data": {
        "relationshipType": "parentChild" | "spouse" | "sibling",
        "label": "關係說明（可選）",
        "color": "#6b7280",
        "strokeWidth": 2,
        "strokeDasharray": ""
      }
    }
  ]
}

規則：
- parentChild：source 是父/母，target 是子女
- spouse：source 和 target 是配偶（用虛線）
- sibling：source 和 target 是兄弟姐妹
- id 唯一，用 p1, p2... 和 e1, e2...
- position 先全設 { x: 0, y: 0 }，前端會自動排版`

  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${config.geminiApiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: `${systemPrompt}\n\n文字內容：\n${text}` }] }],
          generationConfig: {
            temperature: 0.2,
            maxOutputTokens: 4096,
            responseMimeType: 'application/json',
          },
        }),
      }
    )

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.error?.message || 'Gemini API failed')
    }

    const result = await response.json()
    const content = result.candidates[0].content.parts[0].text
    return JSON.parse(content)
  } catch (e: any) {
    throw createError({ statusCode: 500, message: e.message || 'AI 解析失敗' })
  }
})
