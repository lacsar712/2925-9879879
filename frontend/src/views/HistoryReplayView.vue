<template>
  <div class="history-replay-view p-4">
    <HistoryReplay @snapshot-change="handleSnapshotChange" />
  </div>
</template>

<script setup lang="ts">
import HistoryReplay from '../components/market/HistoryReplay.vue'
import type { QuoteSnapshot } from '../mock/historyReplay'

function handleSnapshotChange(snapshot: QuoteSnapshot) {
  console.log('Snapshot changed:', snapshot.snapshot_time, snapshot.bond.code)
}
</script>
