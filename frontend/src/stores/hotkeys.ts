import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useHotkeysStore = defineStore('hotkeys', () => {
  const cheatsheetVisible = ref(false)
  const searchVisible = ref(false)
  const keySequence = ref<string[]>([])
  const isPaused = ref(false)

  function openCheatsheet() {
    cheatsheetVisible.value = true
  }

  function closeCheatsheet() {
    cheatsheetVisible.value = false
  }

  function toggleCheatsheet() {
    cheatsheetVisible.value = !cheatsheetVisible.value
  }

  function openSearch() {
    searchVisible.value = true
  }

  function closeSearch() {
    searchVisible.value = false
  }

  function toggleSearch() {
    searchVisible.value = !searchVisible.value
  }

  function pushKey(key: string) {
    keySequence.value.push(key)
  }

  function clearSequence() {
    keySequence.value = []
  }

  function pause() {
    isPaused.value = true
  }

  function resume() {
    isPaused.value = false
  }

  return {
    cheatsheetVisible,
    searchVisible,
    keySequence,
    isPaused,
    openCheatsheet,
    closeCheatsheet,
    toggleCheatsheet,
    openSearch,
    closeSearch,
    toggleSearch,
    pushKey,
    clearSequence,
    pause,
    resume,
  }
})
