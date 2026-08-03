<script setup lang="ts">
import { NLayoutFooter, NText } from 'naive-ui'

import { useLocale } from '@/hooks'

defineOptions({ name: 'AppFooter' })

const appTitle = import.meta.env.VITE_APP_TITLE || 'FastAPI Admin'
const currentYear = new Date().getFullYear()
const { t } = useLocale()
</script>

<template>
  <NLayoutFooter class="app-footer">
    <NText depth="3">© {{ currentYear }} {{ appTitle }}. {{ t('app.footer.rights') }}</NText>
  </NLayoutFooter>
</template>
