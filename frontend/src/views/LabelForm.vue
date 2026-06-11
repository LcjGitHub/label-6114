<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton,
  NCard,
  NColorPicker,
  NForm,
  NFormItem,
  NInput,
  NSpace,
  useMessage,
  type FormInst,
  type FormRules,
} from 'naive-ui'
import { createLabel, fetchLabel, updateLabel } from '@/api/label'
import type { LabelFormData } from '@/types/label'

const props = defineProps<{
  id?: string
}>()

const router = useRouter()
const message = useMessage()
const formRef = ref<FormInst | null>(null)
const submitting = ref(false)
const loading = ref(false)

const isEdit = computed(() => Boolean(props.id))

const form = ref<LabelFormData>({
  name: '',
  color: '#18a058',
})

const presetColors = [
  '#18a058',
  '#2080f0',
  '#f0a020',
  '#d03050',
  '#722ed1',
  '#13c2c2',
  '#52c41a',
  '#faad14',
  '#f5222d',
  '#2f54eb',
]

const rules: FormRules = {
  name: [{ required: true, message: '请输入标签名称', trigger: 'blur' }],
  color: [{ required: true, message: '请选择颜色', trigger: 'blur' }],
}

async function loadLabel() {
  if (!props.id) return
  loading.value = true
  try {
    const data = await fetchLabel(Number(props.id))
    form.value = {
      name: data.name,
      color: data.color,
    }
  } catch {
    message.error('加载标签失败')
    router.push('/labels')
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  await formRef.value?.validate()
  submitting.value = true
  try {
    if (isEdit.value && props.id) {
      await updateLabel(Number(props.id), form.value)
      message.success('已更新')
    } else {
      await createLabel(form.value)
      message.success('已创建')
    }
    router.push('/labels')
  } catch (err: any) {
    const errorMsg = err?.response?.data?.detail || (isEdit.value ? '更新失败' : '创建失败')
    message.error(errorMsg)
  } finally {
    submitting.value = false
  }
}

onMounted(loadLabel)
</script>

<template>
  <n-card :title="isEdit ? '编辑标签' : '新增标签'" :loading="loading">
    <n-form ref="formRef" :model="form" :rules="rules" label-placement="left" label-width="96">
      <n-form-item label="标签名称" path="name">
        <n-input v-model:value="form.name" placeholder="请输入标签名称" maxlength="50" />
      </n-form-item>
      <n-form-item label="颜色标识" path="color">
        <n-color-picker v-model:value="form.color" :swatches="presetColors" show-swatches />
      </n-form-item>
      <n-form-item>
        <n-space>
          <n-button type="primary" :loading="submitting" @click="handleSubmit">
            {{ isEdit ? '保存' : '创建' }}
          </n-button>
          <n-button @click="router.push('/labels')">返回</n-button>
        </n-space>
      </n-form-item>
    </n-form>
  </n-card>
</template>
