<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton,
  NCard,
  NDescriptions,
  NDescriptionsItem,
  useMessage,
} from 'naive-ui'
import { fetchContact } from '@/api/contact'
import type { Contact } from '@/types/contact'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const loading = ref(false)
const contact = ref<Contact | null>(null)

async function loadContact() {
  const id = route.params.id as string
  if (!id) return
  loading.value = true
  try {
    contact.value = await fetchContact(Number(id))
  } catch {
    message.error('加载联系人失败')
    router.push('/contacts')
  } finally {
    loading.value = false
  }
}

onMounted(loadContact)
</script>

<template>
  <n-card title="联系人详情" :loading="loading">
    <n-descriptions v-if="contact" :column="1" label-placement="left" label-style="width: 96px">
      <n-descriptions-item label="昵称">
        {{ contact.nickname }}
      </n-descriptions-item>
      <n-descriptions-item label="联系方式">
        {{ contact.contact_info }}
      </n-descriptions-item>
      <n-descriptions-item label="备注说明">
        {{ contact.notes ?? '-' }}
      </n-descriptions-item>
    </n-descriptions>
    <template #footer>
      <n-button @click="router.push('/contacts')">返回列表</n-button>
    </template>
  </n-card>
</template>
