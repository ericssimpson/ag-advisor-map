module.exports = {
  plugins: {
    'postcss-import': {},
    '@tailwindcss/postcss': {},
    autoprefixer: {},
    ...(process.env.NODE_ENV === 'production'
      ? {
          '@fullhuman/postcss-purgecss': {
            content: [
              './index.html',
              './src/**/*.vue',
              './src/**/*.ts',
              './src/**/*.js',
            ],
            safelist: {
              // Add any classes that are added dynamically and might be missed by the scanner
              // For example, from PrimeVue or other libraries
              standard: [
                /p-\w+/, // PrimeVue components
                /pi-\w+/, // PrimeIcons
                /mapboxgl-\w+/, // Mapbox GL JS
              ],
              deep: [],
              greedy: [],
              keyframes: [],
              variables: [],
            },
          },
        }
      : {}),
  },
}
