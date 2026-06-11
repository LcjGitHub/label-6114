<script setup lang="ts">
import {
  NConfigProvider,
  NLayout,
  NLayoutHeader,
  NLayoutContent,
  NSpace,
  NButton,
  NMessageProvider,
  NDialogProvider,
  zhCN,
  dateZhCN,
} from 'naive-ui'
import { useRouter, useRoute } from 'vue-router'
import { computed } from 'vue'

const router = useRouter()
const route = useRoute()

const isContactActive = computed(() =>
  ['contacts', 'contact-create', 'contact-edit'].includes(route.name as string)
)
</script>

<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <n-dialog-provider>
    <n-layout style="min-height: 100vh">
      <n-layout-header bordered style="padding: 0 24px; height: 64px; display: flex; align-items: center">
        <n-space align="center" justify="space-between" style="width: 100%">
          <strong style="font-size: 18px">杂志交换记录</strong>
          <n-space>
            <n-button
              quaternary
              :type="route.name === 'overview' ? 'primary' : 'default'"
              @click="router.push('/')"
            >
              数据概览
            </n-button>
            <n-button
              quaternary
              :type="route.name === 'list' ? 'primary' : 'default'"
              @click="router.push('/list')"
            >
              记录列表
            </n-button>
            <n-button type="primary" @click="router.push('/new')">新增记录</n-button>
            <n-button
              quaternary
              :type="isContactActive ? 'primary' : 'default'"
              @click="router.push('/contacts')"
            >
              通讯录
            </n-button>
            <n-button type="primary" @click="router.push('/contacts/new')">新增联系人</n-button>
          </n-space>
        </n-space>
      </n-layout-header>
      <n-layout-content style="padding: 24px; max-width: 960px; margin: 0 auto">
        <router-view />
      </n-layout-content>
    </n-layout>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
  background: #f5f5f5;
}
</style>
