<script setup lang="ts">
import { onBeforeUnmount } from 'vue'
import { useMessage } from 'naive-ui'

import { configureRequestMessage } from '@/utils/request-feedback'

defineOptions({ name: 'RequestMessageBridge' })

const message = useMessage()

configureRequestMessage((content) => {
  message.error(content)
})

onBeforeUnmount(() => {
  configureRequestMessage(null)
})
</script>

<template>
  <span hidden aria-hidden="true" />
</template>
