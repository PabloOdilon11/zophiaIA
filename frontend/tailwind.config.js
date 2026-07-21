/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        zophia: {
          purple: "#8D3F9E",
          pink: "#ED4F9D",
          bg: "#FCF8F7",
          text: "#292331",
          card: "#FFFFFF",
          sidebar: "#FAF5F7",
          border: "#F3E6EA"
        }
      },
      fontFamily: {
        heading: ['Manrope', 'sans-serif'],
        body: ['DM Sans', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
