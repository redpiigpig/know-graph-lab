/**
 * API: 生成圖表結構
 * 支援 Gemini API
 */

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig();
  const body = await readBody(event);

  const { prompt, chartType, apiProvider = "gemini" } = body;

  if (!prompt || !chartType) {
    throw createError({
      statusCode: 400,
      message: "Missing required parameters: prompt and chartType",
    });
  }

  try {
    let chartData;

    if (apiProvider === "gemini") {
      chartData = await generateWithGemini(
        prompt,
        chartType,
        config.geminiApiKey,
      );
    } else if (apiProvider === "claude") {
      chartData = await generateWithClaude(
        prompt,
        chartType,
        config.anthropicApiKey,
      );
    } else {
      throw new Error("Invalid API provider");
    }

    return {
      success: true,
      data: chartData,
    };
  } catch (error: any) {
    throw createError({
      statusCode: 500,
      message: error.message || "Failed to generate chart",
    });
  }
});

/**
 * 使用 Gemini API 生成圖表
 */
async function generateWithGemini(
  prompt: string,
  chartType: string,
  apiKey: string,
) {
  const systemPrompt = getSystemPrompt(chartType);

  const response = await fetch(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=" +
      apiKey,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        contents: [
          {
            parts: [
              {
                text: systemPrompt + "\n\n用戶需求：" + prompt,
              },
            ],
          },
        ],
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 2048,
          responseMimeType: "application/json",
        },
      }),
    },
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || "Gemini API request failed");
  }

  const data = await response.json();
  const content = data.candidates[0].content.parts[0].text;

  try {
    return JSON.parse(content);
  } catch (e) {
    console.error("Failed to parse Gemini response:", content);
    throw new Error("Invalid JSON response from Gemini");
  }
}

/**
 * 使用 Claude API 生成圖表（備用）
 */
async function generateWithClaude(
  prompt: string,
  chartType: string,
  apiKey: string,
) {
  const systemPrompt = getSystemPrompt(chartType);

  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 4000,
      messages: [{ role: "user", content: prompt }],
      system: systemPrompt,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || "Claude API request failed");
  }

  const data = await response.json();
  const content = data.content[0].text;

  try {
    const jsonText = content
      .replace(/```json\n?/g, "")
      .replace(/```\n?/g, "")
      .trim();
    return JSON.parse(jsonText);
  } catch (e) {
    console.error("Failed to parse Claude response:", content);
    throw new Error("Invalid JSON response from Claude");
  }
}

/**
 * 根據圖表類型獲取系統提示詞
 */
function getSystemPrompt(chartType: string): string {
  const prompts = {
    flowchart: `你是一個專業的流程圖設計師。根據用戶的描述，生成流程圖的結構化資料。

請以 JSON 格式回應，包含以下結構：
{
  "nodes": [
    {
      "id": "node_1",
      "label": "節點名稱",
      "type": "start" | "process" | "decision" | "end",
      "x": 100,
      "y": 100
    }
  ],
  "edges": [
    {
      "from": "node_1",
      "to": "node_2",
      "label": "連接標籤（可選）"
    }
  ]
}`,

    mindmap: `你是一個專業的心智圖設計師。根據用戶的描述，生成心智圖的結構化資料。

請以 JSON 格式回應，包含以下結構：
{
  "root": {
    "id": "root",
    "label": "中心主題",
    "children": [
      {
        "id": "child_1",
        "label": "分支主題",
        "children": []
      }
    ]
  }
}`,
  };

  return prompts[chartType as keyof typeof prompts] || prompts.flowchart;
}
