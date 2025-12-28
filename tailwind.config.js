/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",    // Ini bakal nge-scan semua file .html di app/templates dan sub-foldernya
    "./app/static/**/*.js",       // Scan file JS juga kalo lo pake class Tailwind di script
    "./app/templates/*.html"      // Backup buat file html yang ada di root templates
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
      },
    },
  },
  plugins: [],
}