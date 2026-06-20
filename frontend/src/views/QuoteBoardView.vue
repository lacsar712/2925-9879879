<template>
  <div class="quote-board-view p-4">
    <BrokerQuoteBoard :bond-limit="20" />
  </div>
</template>

<script setup lang="ts">
import BrokerQuoteBoard from '../components/market/BrokerQuoteBoard.vue'
</script>

<style scoped>
.quote-board-view {
  min-height: 100%;
}
</style>
