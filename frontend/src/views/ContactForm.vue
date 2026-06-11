<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton,
  NCard,
  NForm,
  NFormItem,
  NInput,
  NSpace,
  useMessage,
  type FormInst,
  type FormRules,
} from 'naive-ui'
import { createContact, fetchContact, updateContact } from '@/api/contact'
import type { ContactFormData } from '@/types/contact'

const props = defineProps<{
  id?: string
}>()

const router = useRouter()
const message = useMessage()
const formRef = ref<FormInst | null>(null)
const submitting = ref(false)
const loading = ref(false)

const isEdit = computed(() => Boolean(props.id))

const form = ref<ContactFormData>({
  nickname: '',
  contact_info: '',
  notes: null,
})

const rules: FormRules = {
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  contact_info: [{ required: true, message: '请输入联系方式', trigger: 'blur' }],
}

async function loadContact() {
  if (!props.id) return
  loading.value = true
  try {
    const data = await fetchContact(Number(props.id))
    form.value = {
      nickname: data.nickname,
      contact_info: data.contact_info,
      notes: data.notes,
    }
  } catch {
    message.error('加载联系人失败')
    router.push('/contacts')
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  await formRef.value?.validate()
  submitting.value = true
  try {
    if (isEdit.value && props.id) {
      await updateContact(Number(props.id), form.value)
      message.success('已更新')
    } else {
      await createContact(form.value)
      message.success('已创建')
    }
    router.push('/contacts')
  } catch {
    message.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

onMounted(loadContact)
</script>

<template>
  <n-card :title="isEdit ? '编辑联系人' : '新增联系人'" :loading="loading">
    <n-form ref="formRef" :model="form" :rules="rules" label-placement="left" label-width="96">
      <n-form-item label="昵称" path="nickname">
        <n-input v-model:value="form.nickname" placeholder="请输入昵称" />
      </n-form-item>
      <n-form-item label="联系方式" path="contact_info">
        <n-input v-model:value="form.contact_info" placeholder="请输入联系方式" />
      </n-form-item>
      <n-form-item label="备注说明" path="notes">
        <n-input
          v-model:value="form.notes"
          type="textarea"
          placeholder="请输入备注说明（可选）"
          :rows="3"
        />
      </n-form-item>
      <n-form-item>
        <n-space>
          <n-button type="primary" :loading="submitting" @click="handleSubmit">
            {{ isEdit ? '保存' : '创建' }}
          </n-button>
          <n-button @click="router.push('/contacts')">返回</n-button>
        </n-space>
      </n-form-item>
    </n-form>
  </n-card>
</template>
