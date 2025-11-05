/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",    // Ищем классы в HTML-шаблонах Django
    "./**/*.py",                // Иногда классы могут быть в Python-коде (редко, но можно добавить)
    "./static_src/**/*.js",     // Если будешь использовать JS с Tailwind-классами
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/line-clamp')
  ],
}