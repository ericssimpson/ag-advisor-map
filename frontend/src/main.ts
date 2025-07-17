// filepath: c:\Repository\ag-advisor-map\ag-advisor-map\frontend\src\main.ts
// Main entry point for the Vue application.
// Initializes Pinia for state management and mounts the root App component.
import { createPinia } from 'pinia'
import './index.css'
import { createApp } from 'vue'
import App from './App.vue'

// Import PrimeVue and required components
import PrimeVue from 'primevue/config'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Panel from 'primevue/panel'
import Calendar from 'primevue/calendar'

// Import PrimeVue styles
import 'primevue/resources/themes/lara-light-green/theme.css' // base theme
import 'primeicons/primeicons.css' // icons
import './assets/theme.css' // unified theme for the application

const pinia = createPinia()
const app = createApp(App)

// Register PrimeVue
app.use(PrimeVue, { ripple: true })

// Register PrimeVue components
app.component('PButton', Button)
app.component('PInputText', InputText)
app.component('PDropdown', Dropdown)
app.component('PPanel', Panel)
app.component('PCalendar', Calendar)

app.use(pinia)

app.mount('#app')
