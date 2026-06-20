<template>
  <div class="holdings-view p-4">
    <a-row :gutter="[16, 16]" class="mb-6">
      <a-col :xs="12" :sm="8" :md="6">
        <a-card class="rounded-lg bg-blue-50/80">
          <a-statistic
            title="总市值"
            :value="store.totalMarketValue"
            :precision="2"
            prefix="¥"
            class="tabular-nums"
          />
        </a-card>
      </a-col>
      <a-col :xs="12" :sm="8" :md="6">
        <a-card class="rounded-lg" :class="store.totalFloatingPnl >= 0 ? 'bg-green-50/80' : 'bg-red-50/80'">
          <a-statistic
            title="浮动盈亏"
            :value="store.totalFloatingPnl"
            :precision="2"
            prefix="¥"
            :value-style="store.totalFloatingPnl >= 0 ? { color: '#52c41a' } : { color: '#ff4d4f' }"
            class="tabular-nums"
          />
        </a-card>
      </a-col>
      <a-col :xs="12" :sm="8" :md="6">
        <a-card class="rounded-lg" :class="store.totalFloatingPnlRatio >= 0 ? 'bg-green-50/80' : 'bg-red-50/80'">
          <a-statistic
            title="盈亏比例"
            :value="store.totalFloatingPnlRatio"
            :precision="2"
            suffix="%"
            :value-style="store.totalFloatingPnlRatio >= 0 ? { color: '#52c41a' } : { color: '#ff4d4f' }"
            class="tabular-nums"
          />
        </a-card>
      </a-col>
      <a-col :xs="12" :sm="8" :md="6">
        <a-card class="rounded-lg bg-purple-50/80">
          <a-statistic
            title="组合久期"
            :value="store.portfolioDuration"
            :precision="2"
            class="tabular-nums"
          >
            <template #suffix>
              <span class="text-sm text-gray-400">年</span>
            </template>
          </a-statistic>
        </a-card>
      </a-col>
    </a-row>

    <a-card class="rounded-lg">
      <template #title>
        <div class="flex items-center gap-2">
          <span>持仓明细</span>
          <a-tag v-if="store.holdings.length > 0" color="blue">{{ store.holdings.length }} 只</a-tag>
        </div>
      </template>
      <template #extra>
        <a-space>
          <a-switch
            v-model:checked="showDuration"
            checked-children="久期"
            un-checked-children="久期"
            size="small"
          />
          <a-button type="primary" @click="openModal()">
            <template #icon><PlusOutlined /></template>
            新增持仓
          </a-button>
        </a-space>
      </template>

      <a-empty v-if="store.holdings.length === 0" description="暂无持仓，请点击"新增持仓"添加" />

      <a-table
        v-else
        :data-source="store.holdingsWithMarket"
        :columns="visibleColumns"
        :pagination="false"
        :scroll="{ x: 'max-content' }"
        :row-key="(r) => r.id"
        size="small"
        :row-class-name="(record) => record.floatingPnl >= 0 ? 'row-profit' : 'row-loss'"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'code'">
            <span class="tabular-nums font-medium text-blue-600">{{ record.code }}</span>
          </template>
          <template v-else-if="column.key === 'quantity'">
            <span class="tabular-nums">{{ record.quantity.toLocaleString() }}</span>
          </template>
          <template v-else-if="column.key === 'costPrice'">
            <span class="tabular-nums">{{ record.costPrice.toFixed(4) }}</span>
          </template>
          <template v-else-if="column.key === 'buyDate'">
            <span class="tabular-nums">{{ record.buyDate }}</span>
          </template>
          <template v-else-if="column.key === 'latestPrice'">
            <span class="tabular-nums font-medium">{{ record.latestPrice.toFixed(4) }}</span>
          </template>
          <template v-else-if="column.key === 'marketValue'">
            <span class="tabular-nums">{{ record.marketValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
          </template>
          <template v-else-if="column.key === 'floatingPnl'">
            <span class="tabular-nums font-medium" :style="{ color: record.floatingPnl >= 0 ? '#52c41a' : '#ff4d4f' }">
              {{ record.floatingPnl >= 0 ? '+' : '' }}{{ record.floatingPnl.toFixed(2) }}
            </span>
          </template>
          <template v-else-if="column.key === 'floatingPnlRatio'">
            <span class="tabular-nums" :style="{ color: record.floatingPnlRatio >= 0 ? '#52c41a' : '#ff4d4f' }">
              {{ record.floatingPnlRatio >= 0 ? '+' : '' }}{{ record.floatingPnlRatio.toFixed(2) }}%
            </span>
          </template>
          <template v-else-if="column.key === 'durationContribution'">
            <span class="tabular-nums">{{ record.durationContribution.toFixed(4) }}</span>
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space size="small">
              <a-button type="link" size="small" @click="openModal(record)">编辑</a-button>
              <a-popconfirm
                title="确定删除该持仓吗？"
                ok-text="确定"
                cancel-text="取消"
                @confirm="handleDelete(record.id)"
              >
                <a-button type="link" danger size="small">删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑持仓' : '新增持仓'"
      :confirm-loading="submitting"
      @ok="handleSubmit"
      @cancel="resetForm"
      destroy-on-close
      width="520px"
    >
      <a-form
        ref="formRef"
        :model="formState"
        :rules="formRules"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 16 }"
        class="mt-4"
      >
        <a-form-item label="债券代码" name="code">
          <a-input v-model:value="formState.code" placeholder="如 230205" :disabled="isEdit" />
        </a-form-item>
        <a-form-item label="债券简称" name="name">
          <a-input v-model:value="formState.name" placeholder="如 23国开05" />
        </a-form-item>
        <a-form-item label="持仓数量(万)" name="quantity">
          <a-input-number
            v-model:value="formState.quantity"
            :min="0.01"
            :step="100"
            :precision="2"
            style="width: 100%"
            placeholder="单位：万元面值"
          />
        </a-form-item>
        <a-form-item label="成本净价" name="costPrice">
          <a-input-number
            v-model:value="formState.costPrice"
            :min="0"
            :step="0.01"
            :precision="4"
            style="width: 100%"
            placeholder="买入净价"
          />
        </a-form-item>
        <a-form-item label="买入日期" name="buyDate">
          <a-date-picker
            v-model:value="formState.buyDate"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </a-form-item>
        <a-form-item label="修正久期" name="modifiedDuration">
          <a-input-number
            v-model:value="formState.modifiedDuration"
            :min="0"
            :step="0.1"
            :precision="2"
            style="width: 100%"
            placeholder="选填，留空自动估算"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import type { FormInstance, Rule } from 'ant-design-vue/es/form'
import type { HoldingWithMarket } from '../stores/holdings'
import { useHoldingsStore } from '../stores/holdings'

const store = useHoldingsStore()

const showDuration = ref(false)

const baseColumns = [
  { title: '债券代码', key: 'code', dataIndex: 'code', width: 110, fixed: 'left' as const },
  { title: '简称', key: 'name', dataIndex: 'name', width: 140 },
  { title: '数量(万)', key: 'quantity', width: 100 },
  { title: '成本净价', key: 'costPrice', width: 100 },
  { title: '买入日期', key: 'buyDate', dataIndex: 'buyDate', width: 110 },
  { title: '最新市价', key: 'latestPrice', width: 100 },
  { title: '市值', key: 'marketValue', width: 120 },
  { title: '浮动盈亏', key: 'floatingPnl', width: 110 },
  { title: '盈亏比例', key: 'floatingPnlRatio', width: 100 },
  { title: '操作', key: 'action', width: 120, fixed: 'right' as const },
]

const durationColumns = [
  { title: '久期贡献', key: 'durationContribution', width: 100 },
]

const visibleColumns = computed(() => {
  if (showDuration.value) {
    const cols = [...baseColumns]
    cols.splice(cols.length - 1, 0, ...durationColumns)
    return cols
  }
  return baseColumns
})

const modalVisible = ref(false)
const isEdit = ref(false)
const editingId = ref<string | null>(null)
const submitting = ref(false)
const formRef = ref<FormInstance>()

interface FormState {
  code: string
  name: string
  quantity: number | null
  costPrice: number | null
  buyDate: string | null
  modifiedDuration: number | null
}

const defaultFormState = (): FormState => ({
  code: '',
  name: '',
  quantity: null,
  costPrice: null,
  buyDate: null,
  modifiedDuration: null,
})

const formState = ref<FormState>(defaultFormState())

const formRules: Record<string, Rule[]> = {
  code: [{ required: true, message: '请输入债券代码' }],
  name: [{ required: true, message: '请输入债券简称' }],
  quantity: [{ required: true, message: '请输入持仓数量' }],
  costPrice: [{ required: true, message: '请输入成本净价' }],
  buyDate: [{ required: true, message: '请选择买入日期' }],
}

function openModal(record?: HoldingWithMarket) {
  if (record) {
    isEdit.value = true
    editingId.value = record.id
    formState.value = {
      code: record.code,
      name: record.name,
      quantity: record.quantity,
      costPrice: record.costPrice,
      buyDate: record.buyDate,
      modifiedDuration: record.modifiedDuration,
    }
  } else {
    isEdit.value = false
    editingId.value = null
    formState.value = defaultFormState()
  }
  modalVisible.value = true
}

function resetForm() {
  formState.value = defaultFormState()
  formRef.value?.clearValidate()
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  submitting.value = true

  try {
    const data = {
      code: formState.value.code.trim(),
      name: formState.value.name.trim(),
      quantity: formState.value.quantity!,
      costPrice: formState.value.costPrice!,
      buyDate: formState.value.buyDate!,
      modifiedDuration: formState.value.modifiedDuration,
    }

    if (isEdit.value && editingId.value) {
      store.updateHolding(editingId.value, data)
      message.success('持仓已更新')
    } else {
      store.addHolding(data)
      message.success('持仓已添加')
    }

    modalVisible.value = false
    resetForm()
  } finally {
    submitting.value = false
  }
}

function handleDelete(id: string) {
  store.deleteHolding(id)
  message.success('持仓已删除')
}
</script>

<style scoped>
.holdings-view :deep(.row-profit) td {
  background: rgba(82, 196, 26, 0.04);
}

.holdings-view :deep(.row-loss) td {
  background: rgba(255, 77, 79, 0.04);
}
</style>
