/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // enables dark mode with class strategy
  content: [
    '../templates/**/*.html',   // Django templates
    '../../templates/**/*.html', // project-level templates
    '../../**/templates/**/*.html',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
  
