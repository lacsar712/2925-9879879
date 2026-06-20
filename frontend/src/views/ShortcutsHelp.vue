<template>
  <div class="shortcuts-help-page">
    <div class="page-header">
      <h1 class="text-2xl font-bold text-gray-800">快捷键说明</h1>
      <p class="text-gray-500 mt-1">掌握这些快捷键，提升你的操作效率</p>
    </div>

    <a-alert
      type="info"
      show-icon
      class="mb-6"
      :message="'提示：按 ? 键可随时呼出快捷键速查面板，Esc 关闭'"
    />

    <div class="category-blocks">
      <div v-for="category in categories" :key="category" class="category-block">
        <div class="category-header">
          <component :is="getCategoryIcon(category)" class="category-icon" />
          <h2 class="category-name">{{ CATEGORY_LABELS[category] }}</h2>
        </div>
        <a-table
          :columns="columns"
          :data-source="getHotkeysByCategory(category)"
          :pagination="false"
          size="middle"
          row-key="id"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'keys'">
              <div class="key-display">
                <template v-if="record.sequence && record.sequence.length > 0">
                  <span class="seq-hint">依次按下：</span>
                  <kbd v-for="(k, idx) in record.sequence" :key="idx" class="kbd">
                    {{ formatKeyDisplay(k) }}
                  </kbd>
                  <span v-if="record.sequence.length > 1" class="seq-arrow">→</span>
                </template>
                <template v-else>
                  <kbd v-for="(k, idx) in record.keys" :key="idx" class="kbd">
                    {{ formatKeyDisplay(k) }}
                  </kbd>
                  <span v-if="record.keys.length > 1" class="plus">+</span>
                </template>
              </div>
            </template>
            <template v-else-if="column.key === 'description'">
              <span class="desc-text">{{ record.description }}</span>
            </template>
            <template v-else-if="column.key === 'scope'">
              <a-tag :color="record.pauseOnInput ? 'blue' : 'green'">
                {{ record.pauseOnInput ? '输入框中暂停' : '全局可用' }}
              </a-tag>
            </template>
          </template>
        </a-table>
      </div>
    </div>

    <div class="tips-section">
      <h3 class="text-lg font-semibold text-gray-800 mb-3">使用技巧</h3>
      <ul class="tips-list">
        <li><strong>序列快捷键</strong>（如 G + D）：先按下并释放 G 键，然后在 1.5 秒内按下 D 键即可触发跳转。</li>
        <li><strong>组合快捷键</strong>（如 Ctrl + K）：按住修饰键（Ctrl/Alt/Shift）的同时按下主键。</li>
        <li><strong>输入框保护</strong>：当光标在输入框、文本域中时，导航类快捷键会自动暂停，避免与文字输入冲突。</li>
        <li><strong>随时速查</strong>：在任何页面按 <kbd class="kbd">?</kbd> 键都能弹出速查面板。</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import { SearchOutlined, CompassOutlined, QuestionCircleOutlined, ThunderboltOutlined } from '@ant-design/icons-vue'
import { HOTKEY_LIST, CATEGORY_LABELS, formatKeyDisplay, HotkeyCategory } from '../utils/hotkeys'

const columns = [
  {
    title: '快捷键',
    key: 'keys',
    width: 280,
  },
  {
    title: '功能说明',
    key: 'description',
  },
  {
    title: '作用范围',
    key: 'scope',
    width: 140,
  },
]

const categories = computed<HotkeyCategory[]>(() => {
  const set = new Set(HOTKEY_LIST.map(h => h.category))
  return Array.from(set)
})

function getHotkeysByCategory(category: HotkeyCategory) {
  return HOTKEY_LIST.filter(h => h.category === category)
}

function getCategoryIcon(category: HotkeyCategory) {
  const map: Record<HotkeyCategory, any> = {
    search: SearchOutlined,
    navigation: CompassOutlined,
    help: QuestionCircleOutlined,
    action: ThunderboltOutlined,
  }
  return map[category]
}
</script>

<style scoped>
.shortcuts-help-page {
  max-width: 960px;
}

.page-header {
  margin-bottom: 24px;
}

.category-blocks {
  display: flex;
  flex-direction: column;
  gap: 28px;
  margin-bottom: 32px;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.category-icon {
  font-size: 20px;
  color: #1890ff;
}

.category-name {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.key-display {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.seq-hint {
  font-size: 12px;
  color: #999;
  margin-right: 4px;
}

.seq-arrow {
  color: #999;
  font-size: 12px;
}

.plus {
  color: #999;
  font-size: 12px;
}

.kbd {
  display: inline-block;
  min-width: 28px;
  padding: 3px 10px;
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

.desc-text {
  font-size: 14px;
  color: #333;
}

.tips-section {
  background: #fafafa;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 20px 24px;
}

.tips-list {
  margin: 0;
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tips-list li {
  font-size: 14px;
  color: #595959;
  line-height: 1.7;
}

.tips-list :deep(.kbd) {
  margin: 0 2px;
}
</style>
