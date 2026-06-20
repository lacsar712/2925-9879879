<template>
  <a-modal
    :open="visible"
    :footer="null"
    :centered="true"
    :width="720"
    :closable="true"
    @cancel="handleClose"
    class="hotkey-cheatsheet"
  >
    <div class="cheatsheet-header">
      <h2 class="text-xl font-semibold text-gray-800 mb-1">快捷键速查</h2>
      <p class="text-sm text-gray-500">按 <kbd class="kbd">Esc</kbd> 关闭，或按 <kbd class="kbd">?</kbd> 随时打开</p>
    </div>

    <div class="cheatsheet-body">
      <div v-for="category in categories" :key="category" class="category-section">
        <h3 class="category-title">{{ CATEGORY_LABELS[category] }}</h3>
        <div class="hotkey-grid">
          <div v-for="hotkey in getHotkeysByCategory(category)" :key="hotkey.id" class="hotkey-item">
            <span class="hotkey-desc">{{ hotkey.description }}</span>
            <div class="hotkey-keys">
              <template v-if="hotkey.sequence && hotkey.sequence.length > 0">
                <kbd v-for="(k, idx) in hotkey.sequence" :key="idx" class="kbd">
                  {{ formatKeyDisplay(k) }}
                </kbd>
                <span v-if="hotkey.sequence.length > 1" class="seq-then">然后</span>
              </template>
              <template v-else>
                <kbd v-for="(k, idx) in hotkey.keys" :key="idx" class="kbd">
                  {{ formatKeyDisplay(k) }}
                </kbd>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="cheatsheet-footer">
      <a-button type="primary" ghost @click="goToHelpPage">
        查看完整说明页
      </a-button>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useHotkeysStore } from '../../stores/hotkeys'
import { HOTKEY_LIST, CATEGORY_LABELS, formatKeyDisplay, HotkeyCategory } from '../../utils/hotkeys'

const router = useRouter()
const hotkeysStore = useHotkeysStore()

const visible = computed(() => hotkeysStore.cheatsheetVisible)

const categories = computed<HotkeyCategory[]>(() => {
  const set = new Set(HOTKEY_LIST.map(h => h.category))
  return Array.from(set)
})

function getHotkeysByCategory(category: HotkeyCategory) {
  return HOTKEY_LIST.filter(h => h.category === category)
}

function handleClose() {
  hotkeysStore.closeCheatsheet()
}

function goToHelpPage() {
  hotkeysStore.closeCheatsheet()
  router.push('/shortcuts')
}
</script>

<style scoped>
.hotkey-cheatsheet :deep(.ant-modal-content) {
  border-radius: 12px;
  overflow: hidden;
}

.cheatsheet-header {
  padding: 8px 0 16px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 16px;
}

.category-section {
  margin-bottom: 20px;
}

.category-title {
  font-size: 13px;
  font-weight: 600;
  color: #1890ff;
  margin: 0 0 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.hotkey-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 24px;
}

.hotkey-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 0;
}

.hotkey-desc {
  font-size: 14px;
  color: #333;
}

.hotkey-keys {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.kbd {
  display: inline-block;
  min-width: 28px;
  padding: 2px 8px;
  font-size: 12px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  color: #374151;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-bottom-width: 2px;
  border-radius: 4px;
  text-align: center;
  line-height: 1.4;
}

.seq-then {
  font-size: 12px;
  color: #9ca3af;
  margin: 0 2px;
}

.cheatsheet-footer {
  margin-top: 8px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
}
</style>
