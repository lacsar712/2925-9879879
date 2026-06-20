import { onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useHotkeysStore } from '../stores/hotkeys'
import { HOTKEY_LIST, normalizeKey, isInputElement } from '../utils/hotkeys'

const SEQUENCE_TIMEOUT = 1500

export function useHotkeys() {
  const router = useRouter()
  const hotkeysStore = useHotkeysStore()

  let sequenceTimer: number | null = null
  let boundHandler: ((e: KeyboardEvent) => void) | null = null

  function startSequenceTimer() {
    if (sequenceTimer) window.clearTimeout(sequenceTimer)
    sequenceTimer = window.setTimeout(() => {
      hotkeysStore.clearSequence()
    }, SEQUENCE_TIMEOUT)
  }

  function matchCombination(e: KeyboardEvent, keys: string[]): boolean {
    const hasCtrl = e.ctrlKey || e.metaKey
    const hasAlt = e.altKey
    const hasShift = e.shiftKey
    const normalizedKey = normalizeKey(e)

    const needCtrl = keys.includes('ctrl')
    const needAlt = keys.includes('alt')
    const needShift = keys.includes('shift')

    if (needCtrl !== hasCtrl) return false
    if (needAlt !== hasAlt) return false
    if (needShift !== hasShift) return false

    const nonModifierKeys = keys.filter(k => !['ctrl', 'alt', 'shift'].includes(k))
    if (nonModifierKeys.length !== 1) return false

    return nonModifierKeys[0] === normalizedKey
  }

  function matchSequence(sequence: string[]): boolean {
    if (hotkeysStore.keySequence.length !== sequence.length) return false
    return hotkeysStore.keySequence.every((k, i) => k === sequence[i])
  }

  function handleKeyDown(e: KeyboardEvent) {
    if (hotkeysStore.cheatsheetVisible && e.key === 'Escape') {
      hotkeysStore.closeCheatsheet()
      return
    }
    if (hotkeysStore.searchVisible && e.key === 'Escape') {
      hotkeysStore.closeSearch()
      return
    }

    const normalizedKey = normalizeKey(e)
    const targetIsInput = isInputElement(e.target)

    for (const hotkey of HOTKEY_LIST) {
      const skipBecauseInput = targetIsInput && hotkey.pauseOnInput

      if (hotkey.sequence && hotkey.sequence.length > 0) {
        if (skipBecauseInput) continue

        if (!e.ctrlKey && !e.altKey && !e.metaKey) {
          hotkeysStore.pushKey(normalizedKey)
          startSequenceTimer()

          if (matchSequence(hotkey.sequence)) {
            e.preventDefault()
            hotkeysStore.clearSequence()
            if (sequenceTimer) {
              window.clearTimeout(sequenceTimer)
              sequenceTimer = null
            }
            if (hotkey.route) {
              router.push(hotkey.route)
            }
            return
          }
        }
      } else {
        if (skipBecauseInput) continue

        if (matchCombination(e, hotkey.keys)) {
          e.preventDefault()
          if (hotkey.id === 'show-cheatsheet') {
            hotkeysStore.toggleCheatsheet()
          } else if (hotkey.id === 'global-search') {
            hotkeysStore.toggleSearch()
          } else if (hotkey.route) {
            router.push(hotkey.route)
          }
          return
        }
      }
    }
  }

  function setupListeners() {
    boundHandler = handleKeyDown
    window.addEventListener('keydown', boundHandler)
  }

  function cleanupListeners() {
    if (boundHandler) {
      window.removeEventListener('keydown', boundHandler)
      boundHandler = null
    }
    if (sequenceTimer) {
      window.clearTimeout(sequenceTimer)
      sequenceTimer = null
    }
  }

  onMounted(() => {
    setupListeners()
  })

  onBeforeUnmount(() => {
    cleanupListeners()
  })

  return {
    hotkeysStore,
  }
}
