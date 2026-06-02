// 裝置識別：在 localStorage 存一個 device_id，並產生易讀的裝置名稱
export function getDeviceId(): string {
  if (typeof window === "undefined") return "";
  let id = localStorage.getItem("kgl_device_id");
  if (!id) {
    id = (crypto as any).randomUUID ? crypto.randomUUID() : `dev-${Date.now()}-${Math.floor(Math.random() * 1e6)}`;
    localStorage.setItem("kgl_device_id", id);
  }
  return id;
}

export function getDeviceName(): string {
  if (typeof navigator === "undefined") return "未知裝置";
  const ua = navigator.userAgent;
  let os = "未知系統";
  if (/Windows/.test(ua)) os = "Windows";
  else if (/iPhone|iPad|iPod/.test(ua)) os = /iPad/.test(ua) ? "iPad" : "iPhone";
  else if (/Android/.test(ua)) os = "Android";
  else if (/Macintosh/.test(ua)) os = "Mac";
  else if (/Linux/.test(ua)) os = "Linux";
  let browser = "瀏覽器";
  if (/Edg\//.test(ua)) browser = "Edge";
  else if (/Chrome\//.test(ua)) browser = "Chrome";
  else if (/Firefox\//.test(ua)) browser = "Firefox";
  else if (/Safari\//.test(ua)) browser = "Safari";
  return `${os} · ${browser}`;
}
