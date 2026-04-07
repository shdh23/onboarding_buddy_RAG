/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg:      "#F3EDE5",
        surface: "#FAF8F5",
        border:  "#E5DED4",
        borderl: "#D4CCC0",
        text:    "#1A1915",
        muted:   "#8B8580",
        accent:  "#D97757",
        danger:  "#C4453A",
        agent:   "#D97757",
        success: "#5B9A6F",
      },
      fontFamily: {
        sans: ['"Söhne"', "Inter", "system-ui", "-apple-system", "sans-serif"],
      },
      borderRadius: {
        "2xl": "16px",
        "xl":  "12px",
        "lg":  "10px",
      },
      boxShadow: {
        soft:  "0 1px 3px rgba(26,25,21,0.05), 0 1px 2px rgba(26,25,21,0.04)",
        card:  "0 2px 8px rgba(26,25,21,0.06), 0 4px 16px rgba(26,25,21,0.04)",
        hover: "0 4px 12px rgba(26,25,21,0.08), 0 8px 24px rgba(26,25,21,0.06)",
        input: "0 0 0 2px rgba(217, 119, 87, 0.25)",
      },
    },
  },
  plugins: [],
}
