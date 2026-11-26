/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'Poppins', 'system-ui', 'sans-serif'],
      },
      colors: {
        primary: {
          DEFAULT: '#4F46E5',
          50: '#EEF2FF',
          100: '#E0E7FF',
          600: '#4F46E5',
          700: '#4338CA',
        },
        tealaccent: {
          DEFAULT: '#14B8A6',
          50: '#F0FDFA',
          600: '#0D9488',
        },
      },
      borderRadius: {
        card: '16px',
      },
    },
  },
  plugins: [],
}
