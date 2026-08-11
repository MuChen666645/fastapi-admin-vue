<script setup lang="ts">
import { computed } from 'vue'
import { NTag } from 'naive-ui'

import type { DictTagProps } from '@/types'

defineOptions({ name: 'DictTag' })

const props = withDefaults(defineProps<DictTagProps>(), {
  options: () => [],
  type: 'default',
  size: 'small',
  bordered: true,
  round: false,
  showValue: true,
})

const normalizedValues = computed<string[]>(() => {
  const sourceValues = Array.isArray(props.value) ? props.value : [props.value]
  return [
    ...new Set(
      sourceValues
        .filter((value) => value !== null && value !== undefined && value !== '')
        .map(String),
    ),
  ]
})

const matchedOptions = computed(() =>
  props.options.filter((option) => normalizedValues.value.includes(option.dict_value)),
)

const unmatchedValues = computed(() => {
  const matchedValues = new Set(matchedOptions.value.map((option) => option.dict_value))
  return normalizedValues.value.filter((value) => !matchedValues.has(value))
})
</script>

<template>
  <span
    v-if="matchedOptions.length || (props.showValue && unmatchedValues.length)"
    class="inline-flex flex-wrap items-center gap-1"
  >
    <NTag
      v-for="option in matchedOptions"
      :key="option.dict_code"
      :type="props.type"
      :size="props.size"
      :bordered="props.bordered"
      :round="props.round"
    >
      {{ option.dict_label }}
    </NTag>
    <span
      v-if="props.showValue && unmatchedValues.length"
      class="text-sm text-[var(--app-color-text-muted)]"
    >
      {{ unmatchedValues.join(', ') }}
    </span>
  </span>
</template>
