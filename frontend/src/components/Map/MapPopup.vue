<script setup lang="ts">
import { useProductStore } from '@/stores/productStore'
import { computed } from 'vue'

const productStore = useProductStore()

/**
 * Computed property for the absolute X position of the popup.
 * Appends 'px' to the x-coordinate from the productStore.
 */
const absX = computed<string>(() => `${productStore.clickedPoint.x}px`)

/**
 * Computed property for the absolute Y position of the popup.
 * Appends 'px' to the y-coordinate from the productStore.
 */
const absY = computed<string>(() => `${productStore.clickedPoint.y}px`)

/**
 * Computed property for the value to be displayed in the popup.
 * Formats the number to two decimal places or shows 'No Data' if the value is NaN.
 */
const value = computed<string>(() => {
  const pointValue = productStore.clickedPoint.value
  return isNaN(pointValue) ? 'No Data' : pointValue.toFixed(2)
})

/**
 * Hides the popup by setting the 'show' property in the productStore to false.
 */
function hidePopup(): void {
  productStore.clickedPoint.show = false
}
</script>

<template>
  <div
    v-if="
      productStore.clickedPoint.show && !isNaN(productStore.clickedPoint.value)
    "
    class="
      absolute
      font-bold
      text-lg
      p-2
      rounded-xl
      flex flex-row
      space-x-3
      items-center
      bg-white
      shadow-lg
    "
    :style="{ left: absX, top: absY, zIndex: 1001 }"
  >
    <p>{{ value }}</p>
    <button
      type="button"
      aria-label="Close popup"
      class="
        text-gray-600
        hover:text-gray-800
        text-xs
        cursor-pointer
        focus:outline-none
      "
      @click="hidePopup"
    >
      X
    </button>
  </div>
</template>

<style scoped>
/* Scoped styles for MapPopup if needed */
.bg-white {
  background-color: white;
}
.p-2 {
  padding: 0.5rem; /* 8px */
}
.rounded-xl {
  border-radius: 0.75rem; /* 12px */
}
.space-x-3 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-x-reverse: 0;
  margin-right: calc(0.75rem * var(--tw-space-x-reverse)); /* 12px */
  margin-left: calc(0.75rem * calc(1 - var(--tw-space-x-reverse)));
}
.items-center {
  align-items: center;
}
.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
    0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
.text-gray-600 {
  color: #4b5563; /* Tailwind gray-600 */
}
.hover\:text-gray-800:hover {
  color: #1f2937; /* Tailwind gray-800 */
}
.focus\:outline-none:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
}
</style>
