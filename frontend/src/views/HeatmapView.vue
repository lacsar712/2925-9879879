<template>
  <div class="heatmap-view p-4">
    <a-card class="rounded-lg">
      <template #title>
        <div class="flex items-center gap-2">
          <FireOutlined class="text-orange-500" />
          <span>市场热力图</span>
        </div>
      </template>
      <template #extra>
        <a-tag color="blue">
          横轴：剩余期限 &nbsp;|&nbsp; 纵轴：债券品种
        </a-tag>
      </template>
      <MarketHeatmap @cell-click="handleCellClick" />
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { FireOutlined } from '@ant-design/icons-vue'
import MarketHeatmap from '../components/market/MarketHeatmap.vue'

interface HeatmapCell {
  bond_type: string
  term_bucket: string
  avg_change: number
  total_volume: number
  trade_count: number
}

function handleCellClick(data: HeatmapCell) {
  console.log('热力图格子点击:', data)
}
</script>

<style scoped>
.heatmap-view {
  width: 100%;
}
</style>
