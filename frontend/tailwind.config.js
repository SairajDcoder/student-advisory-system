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
        brand: {
          DEFAULT: '#7B2D8E',
          dark: '#581C68',
          light: '#F6EEFA',
        },
        cta: {
          DEFAULT: '#FF6B4A',
          hover: '#F05336',
        },
        primary: {
          DEFAULT: '#7B2D8E',
          50: '#F9F1FC',
          100: '#F0DDF7',
          600: '#7B2D8E',
          700: '#5E206E',
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
