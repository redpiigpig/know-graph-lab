import type { Config } from "tailwindcss";

export default {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
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
    {
      // Dynamic color classes used in /works (writing_projects.color)
      pattern:
        /(bg|text|border|hover:bg|hover:border|hover:shadow)-(amber|blue|rose|emerald|violet|sky|indigo|cyan|orange|stone|purple)-(50|100|200|300|500|600|700)/,
    },
  ],
  plugins: [],
} satisfies Config;
