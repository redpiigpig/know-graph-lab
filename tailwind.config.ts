import type { Config } from "tailwindcss";

export default {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./data/**/*.{js,ts}",
    "./app.vue",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
          800: "#1e40af",
          900: "#1e3a8a",
        },
      },
    },
  },
  safelist: [
    // Dynamic color classes (/works writing_projects.color, 全集作家 color…)。
    // 🚨 pattern 一定要 ^…$ 錨定：不錨定時 Tailwind 會連 bg-amber-100/35 這類
    // 透明度組合全部生出來，CSS 曾因此膨脹到 400KB。
    {
      pattern:
        /^(bg|text|border)-(amber|blue|rose|emerald|violet|sky|indigo|cyan|orange|stone|purple|teal)-(50|100|200|300|500|600|700)$/,
    },
    {
      pattern:
        /^(bg-(amber|blue|rose|emerald|violet|sky|indigo|cyan|orange|stone|purple|teal)-100|border-(amber|blue|rose|emerald|violet|sky|indigo|cyan|orange|stone|purple|teal)-300|shadow-(amber|blue|rose|emerald|violet|sky|indigo|cyan|orange|stone|purple|teal)-100)$/,
      variants: ["hover"],
    },
  ],
  plugins: [],
} satisfies Config;
