<template>
  <div
    class="color-swatch flex flex-col items-center justify-center rounded-lg p-2 transition-transform hover:scale-105 cursor-pointer"
    :style="{ background: color }"
    :title="`${label}: ${color}`"
    @click="copyToClipboard"
  >
    <span class="text-xs font-medium mb-0.5" :style="{ color: textColor }">{{ label }}</span>
    <span class="text-[10px] opacity-80 font-mono" :style="{ color: textColor }">{{ color }}</span>
    <CopyOutlined
      v-if="copied"
      class="absolute top-1 right-1 text-xs animate-pulse"
      :style="{ color: textColor }"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import { CopyOutlined } from '@ant-design/icons-vue'

const props = defineProps<{
  label: string
  color: string
  textColor: string
}>()

const copied = ref(false)

async function copyToClipboard() {
  try {
    await navigator.clipboard.writeText(props.color)
    copied.value = true
    message.success(`已复制: ${props.color}`)
    setTimeout(() => {
      copied.value = false
    }, 1500)
  } catch {
    message.error('复制失败')
  }
}
</script>

<style scoped>
.color-swatch {
  min-height: 52px;
  position: relative;
  min-width: 80px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}
</style>
