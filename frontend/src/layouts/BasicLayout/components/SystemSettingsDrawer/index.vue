<script setup lang="ts">
import { computed } from 'vue'
import { NDrawer, NDrawerContent } from 'naive-ui'

import { useLocale } from '@/hooks'
import SystemSettingsPanel from './SystemSettingsPanel.vue'

defineOptions({ name: 'SystemSettingsDrawer' })

const props = defineProps<{
  show: boolean
}>()
const emit = defineEmits<{
  'update:show': [value: boolean]
}>()

const { t } = useLocale()
const drawerVisible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value),
})
</script>

<template>
  <NDrawer v-model:show="drawerVisible" placement="right" width="min(500px, 100vw)">
    <NDrawerContent :title="t('app.user.settings')" closable>
      <SystemSettingsPanel />
    </NDrawerContent>
  </NDrawer>
</template>
