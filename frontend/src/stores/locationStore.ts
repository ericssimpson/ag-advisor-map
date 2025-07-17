/**
 * @file locationStore.ts
 * @description Pinia store for managing the target geographical location.
 */
import { defineStore } from 'pinia'

/**
 * Type definition for the target location.
 * It can be an object with longitude and latitude, or null if no location is set.
 */
export type TargetLocationType = {
  longitude: number
  latitude: number
} | null

/**
 * Interface for the location store's state.
 */
export interface LocationState {
  /** The current target location, or null if not set. */
  targetLocation: TargetLocationType
}

export const useLocationStore = defineStore('locationStore', {
  state: (): LocationState => ({
    targetLocation: null,
  }),

  actions: {
    /**
     * Sets the target geographical location.
     * @param {TargetLocationType} location - The location to set, or null to clear.
     */
    setTargetLocation(location: TargetLocationType) {
      this.targetLocation = location
    },
  },
})
