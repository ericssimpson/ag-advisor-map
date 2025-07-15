const purgecss = require('@fullhuman/postcss-purgecss')

module.exports = {
  plugins: [
    require('postcss-import'),
    require('@tailwindcss/postcss'),
    require('autoprefixer'),
    ...(process.env.NODE_ENV === 'production'
      ? [
          purgecss({
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
          }),
        ]
      : []),
  ],
}
