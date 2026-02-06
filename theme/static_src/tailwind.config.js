// static_src/tailwind.config.js
module.exports = {
  content: [
    './templates/**/*.html',           // templates à la racine
    './../templates/**/*.html',        // templates dans l'app
    './../**/templates/**/*.html',     // tous les templates
    './src/**/*.js',                    // fichiers JS dans src
  ],
    safelist: [
    'bg-red-500',
    'text-white',
    'p-4',
    'table-auto',
    'border-2',
    'border-black',
    'min-w-full',
    'divide-y',
    'divide-gray-200',
    'bg-gray-50',
    'px-6',
    'py-3',
    'text-left',
    'text-xs',
    'font-medium',
    'text-gray-500',
    'uppercase',
    'tracking-wider',
    'bg-white',
    'whitespace-nowrap',
    'text-sm',
    'text-gray-900',
    'hover:bg-gray-50',
    'px-3',
    'py-1',
    'text-xs',
  ],
  theme: {
    extend: {
      fontFamily: {
        'inter': ['Inter', 'sans-serif'],
      },
      colors: {
        'purple': {
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
        },
      },
    },
  },
  plugins: [
    //require('daisyui'),
  ],
  daisyui: {
    themes: ["light"], 
  },
}