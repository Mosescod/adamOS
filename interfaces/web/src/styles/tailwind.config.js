module.exports = {
    content: [
      "./pages/**/*.{js,ts,jsx,tsx}",
      "./components/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        fontFamily: {
          sans: ['Inter', 'sans-serif'],
          mono: ['"Space Mono"', 'monospace']
        },
        colors: {
          cyan: {
            400: '#22d3ee',
            500: '#06b6d4',
            600: '#0891b2',
          },
          gray: {
            700: '#374151',
            800: '#1f2937',
            900: '#111827',
          }
        }
      },
    },
    plugins: [],
  }