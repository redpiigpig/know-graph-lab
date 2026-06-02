// @vitest-environment node
import { describe, it, expect, vi, afterEach } from "vitest";
import { getDeviceName } from "~/composables/useDevice";

function ua(s: string) {
  vi.stubGlobal("navigator", { userAgent: s });
}
afterEach(() => vi.unstubAllGlobals());

describe("getDeviceName 裝置名稱解析", () => {
  it("Windows Chrome", () => {
    ua("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36");
    expect(getDeviceName()).toBe("Windows · Chrome");
  });
  it("iPhone Safari", () => {
    ua("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605 Version/17 Safari/605");
    expect(getDeviceName()).toBe("iPhone · Safari");
  });
  it("Android Chrome", () => {
    ua("Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36");
    expect(getDeviceName()).toBe("Android · Chrome");
  });
  it("Mac Edge", () => {
    ua("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 Chrome/120 Safari/537.36 Edg/120");
    expect(getDeviceName()).toBe("Mac · Edge");
  });
});
