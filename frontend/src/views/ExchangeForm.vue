<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { format, parseISO } from 'date-fns'
import {
  NButton,
  NCard,
  NDatePicker,
  NForm,
  NFormItem,
  NInput,
  NSpace,
  NSwitch,
  useMessage,
  type FormInst,
  type FormRules,
} from 'naive-ui'
import { createExchange, fetchExchange, updateExchange } from '@/api/exchange'
import type { ExchangeFormData } from '@/types/exchange'

const props = defineProps<{
  id?: string
}>()

const router = useRouter()
const message = useMessage()
const formRef = ref<FormInst | null>(null)
const submitting = ref(false)
const loading = ref(false)

const isEdit = computed(() => Boolean(props.id))

const form = ref<ExchangeFormData>({
  book_title: '',
  counterpart_nickname: '',
  sent_date: null,
  received_date: null,
  is_completed: false,
})

const rules: FormRules = {
  book_title: [{ required: true, message: '请输入书名', trigger: 'blur' }],
  counterpart_nickname: [{ required: true, message: '请输入对方昵称', trigger: 'blur' }],
}

const sentTimestamp = computed({
  get: () => (form.value.sent_date ? parseISO(form.value.sent_date).getTime() : null),
  set: (value: number | null) => {
    form.value.sent_date = value ? format(new Date(value), 'yyyy-MM-dd') : null
  },
})

const receivedTimestamp = computed({
  get: () =>
    form.value.received_date ? parseISO(form.value.received_date).getTime() : null,
  set: (value: number | null) => {
    form.value.received_date = value ? format(new Date(value), 'yyyy-MM-dd') : null
  },
})

async function loadExchange() {
  if (!props.id) return
  loading.value = true
  try {
    const data = await fetchExchange(Number(props.id))
    form.value = {
      book_title: data.book_title,
      counterpart_nickname: data.counterpart_nickname,
      sent_date: data.sent_date,
      received_date: data.received_date,
      is_completed: data.is_completed,
    }
  } catch {
    message.error('加载记录失败')
    router.push('/list')
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  await formRef.value?.validate()
  submitting.value = true
  try {
    if (isEdit.value && props.id) {
      await updateExchange(Number(props.id), form.value)
      message.success('已更新')
    } else {
      await createExchange(form.value)
      message.success('已创建')
    }
    router.push('/list')
  } catch {
    message.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

onMounted(loadExchange)
</script>

<template>
  <n-card :title="isEdit ? '编辑交换记录' : '新增交换记录'" :loading="loading">
    <n-form ref="formRef" :model="form" :rules="rules" label-placement="left" label-width="96">
      <n-form-item label="书名" path="book_title">
        <n-input v-model:value="form.book_title" placeholder="请输入书名" />
      </n-form-item>
      <n-form-item label="对方昵称" path="counterpart_nickname">
        <n-input v-model:value="form.counterpart_nickname" placeholder="请输入对方昵称" />
      </n-form-item>
      <n-form-item label="寄出日期" path="sent_date">
        <n-date-picker v-model:value="sentTimestamp" type="date" clearable style="width: 100%" />
      </n-form-item>
      <n-form-item label="收到日期" path="received_date">
        <n-date-picker
          v-model:value="receivedTimestamp"
          type="date"
          clearable
          style="width: 100%"
        />
      </n-form-item>
      <n-form-item label="是否完成" path="is_completed">
        <n-switch v-model:value="form.is_completed" />
      </n-form-item>
      <n-form-item>
        <n-space>
          <n-button type="primary" :loading="submitting" @click="handleSubmit">
            {{ isEdit ? '保存' : '创建' }}
          </n-button>
          <n-button @click="router.push('/list')">返回</n-button>
        </n-space>
      </n-form-item>
    </n-form>
  </n-card>
</template>
