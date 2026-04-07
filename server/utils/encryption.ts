import crypto from "crypto";

const ENCRYPTION_KEY =
  process.env.ENCRYPTION_KEY || "your-32-character-secret-key!!"; // 32 bytes
const ALGORITHM = "aes-256-cbc";

/**
 * 加密 API key
 */
export function encryptApiKey(apiKey: string): {
  encrypted: string;
  iv: string;
} {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(
    ALGORITHM,
    Buffer.from(ENCRYPTION_KEY, "utf-8").slice(0, 32),
    iv,
  );

  let encrypted = cipher.update(apiKey, "utf8", "hex");
  encrypted += cipher.final("hex");

  return {
    encrypted,
    iv: iv.toString("hex"),
  };
}

/**
 * 解密 API key
 */
export function decryptApiKey(encrypted: string, iv: string): string {
  const decipher = crypto.createDecipheriv(
    ALGORITHM,
    Buffer.from(ENCRYPTION_KEY, "utf-8").slice(0, 32),
    Buffer.from(iv, "hex"),
  );

  let decrypted = decipher.update(encrypted, "hex", "utf8");
  decrypted += decipher.final("utf8");

  return decrypted;
}
