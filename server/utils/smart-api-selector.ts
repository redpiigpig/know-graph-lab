import { createClient } from "@supabase/supabase-js";

interface ApiKey {
  id: string;
  provider: string;
  encrypted_key: string;
  encryption_iv: string;
  key_type: "free" | "paid";
  priority: number;
  usage_limit: number | null;
  current_usage: number;
  is_active: boolean;
  is_exhausted: boolean;
}

/**
 * 智能選擇最佳 API Key
 */
export async function selectBestApiKey(
  userId: string,
  provider: string,
  supabaseUrl: string,
  supabaseKey: string,
): Promise<{ key: string; keyId: string } | null> {
  const supabase = createClient(supabaseUrl, supabaseKey);

  // 1. 取得所有符合條件的 keys（按優先級排序）
  const { data: keys } = await supabase
    .from("api_keys")
    .select("*")
    .eq("user_id", userId)
    .eq("provider", provider)
    .eq("is_active", true)
    .eq("is_exhausted", false)
    .order("priority", { ascending: true });

  if (!keys || keys.length === 0) {
    return null;
  }

  // 2. 篩選可用的 keys
  for (const key of keys as ApiKey[]) {
    // 檢查是否達到使用上限
    if (key.usage_limit && key.current_usage >= key.usage_limit) {
      // 標記為已用盡
      await supabase
        .from("api_keys")
        .update({ is_exhausted: true })
        .eq("id", key.id);
      continue;
    }

    // 解密並返回
    const decryptedKey = decryptApiKey(key.encrypted_key, key.encryption_iv);
    return {
      key: decryptedKey,
      keyId: key.id,
    };
  }

  return null;
}

/**
 * 記錄 API 使用
 */
export async function logApiUsage(
  keyId: string,
  userId: string,
  endpoint: string,
  tokensUsed: number,
  success: boolean,
  errorMessage: string | null,
  supabaseUrl: string,
  supabaseKey: string,
) {
  const supabase = createClient(supabaseUrl, supabaseKey);

  // 1. 記錄到 logs 表
  await supabase.from("api_usage_logs").insert({
    api_key_id: keyId,
    user_id: userId,
    endpoint,
    tokens_used: tokensUsed,
    success,
    error_message: errorMessage,
  });

  // 2. 更新使用計數
  const { data: key } = await supabase
    .from("api_keys")
    .select("current_usage, usage_reset_date")
    .eq("id", keyId)
    .single();

  if (key) {
    // 檢查是否需要重置（每月1號重置）
    const today = new Date();
    const resetDate = new Date(key.usage_reset_date);

    let newUsage = key.current_usage + 1;
    let newResetDate = key.usage_reset_date;

    if (
      today.getMonth() !== resetDate.getMonth() ||
      today.getFullYear() !== resetDate.getFullYear()
    ) {
      newUsage = 1;
      newResetDate = today.toISOString().split("T")[0];
    }

    await supabase
      .from("api_keys")
      .update({
        current_usage: newUsage,
        usage_reset_date: newResetDate,
        last_used_at: new Date().toISOString(),
      })
      .eq("id", keyId);
  }
}
