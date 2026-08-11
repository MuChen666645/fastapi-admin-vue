<script setup lang="ts">
import { RefreshOutline } from '@vicons/ionicons5'
import { NButton, NIcon, NRadioButton, NRadioGroup } from 'naive-ui'
import { computed } from 'vue'

import { useLocale } from '@/hooks'
import type { LogPageHeaderProps, LogType } from '@/types'

defineOptions({ name: 'LogPageHeader' })

const props = defineProps<LogPageHeaderProps>()
const emit = defineEmits<{
  'update:activeType': [value: LogType]
  refresh: []
}>()

const { t } = useLocale()

const listPermissionByType: Readonly<Record<LogType, string>> = {
  login: 'monitor:login:list',
  operation: 'monitor:operation:list',
  exception: 'monitor:exception:list',
}

const activeListPermission = computed(() => listPermissionByType[props.activeType])

const handleActiveTypeChange = (value: string | number): void => {
  if (value === 'login' || value === 'operation' || value === 'exception') {
    emit('update:activeType', value)
  }
}
</script>

<template>
  <header class="log-list-heading">
    <div>
      <h2 id="log-list-title">{{ t('log.title') }}</h2>
      <p>{{ t('log.description') }}</p>
    </div>
    <div class="log-page-actions">
      <NRadioGroup :value="props.activeType" size="medium" @update:value="handleActiveTypeChange">
        <NRadioButton
          v-if="props.availableTypes.includes('login')"
          v-permission="'monitor:login:list'"
          value="login"
        >
          {{ t('log.type.login') }}
        </NRadioButton>
        <NRadioButton
          v-if="props.availableTypes.includes('operation')"
          v-permission="'monitor:operation:list'"
          value="operation"
        >
          {{ t('log.type.operation') }}
        </NRadioButton>
        <NRadioButton
          v-if="props.availableTypes.includes('exception')"
          v-permission="'monitor:exception:list'"
          value="exception"
        >
          {{ t('log.type.exception') }}
        </NRadioButton>
      </NRadioGroup>
      <NButton
        v-if="props.availableTypes.includes(props.activeType)"
        v-permission="activeListPermission"
        quaternary
        circle
        size="medium"
        :loading="props.refreshLoading"
        :aria-label="t('log.refresh')"
        :title="t('log.refresh')"
        @click="emit('refresh')"
      >
        <template #icon>
          <NIcon><RefreshOutline /></NIcon>
        </template>
      </NButton>
      <span class="log-total">{{ props.total }}</span>
    </div>
  </header>
</template>

<style lang="scss" scoped>
.log-list-heading,
.log-page-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.log-list-heading {
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}

.log-list-heading h2,
.log-list-heading p,
.log-total {
  margin: 0;
}

.log-list-heading h2 {
  font-size: 16px;
}

.log-list-heading p {
  margin-top: 6px;
  color: var(--app-color-text-muted);
  font-size: 13px;
  line-height: 1.5;
}

.log-page-actions {
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.log-total {
  flex: 0 0 auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

@media (width <= 720px) {
  .log-list-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .log-page-actions {
    justify-content: flex-start;
  }
}
</style>
