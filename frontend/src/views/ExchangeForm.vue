<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { format, parseISO } from 'date-fns'
import {
  NButton,
  NCard,
  NDatePicker,
  NEmpty,
  NForm,
  NFormItem,
  NInput,
  NModal,
  NPagination,
  NSpace,
  NSpin,
  NSwitch,
  useMessage,
  type FormInst,
  type FormRules,
} from 'naive-ui'
import { createExchange, fetchExchange, updateExchange } from '@/api/exchange'
import { fetchContacts } from '@/api/contact'
import type { ExchangeFormData } from '@/types/exchange'
import type { Contact } from '@/types/contact'

const props = defineProps<{
  id?: string
}>()

const router = useRouter()
const message = useMessage()
const formRef = ref<FormInst | null>(null)
const submitting = ref(false)
const loading = ref(false)
const dateAutoCompleted = ref(false)
const isProgrammaticToggle = ref(false)

const isEdit = computed(() => Boolean(props.id))

const form = ref<ExchangeFormData>({
  book_title: '',
  counterpart_nickname: '',
  sent_date: null,
  received_date: null,
  is_completed: false,
  notes: null,
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
    const hadDate = form.value.received_date !== null
    form.value.received_date = value ? format(new Date(value), 'yyyy-MM-dd') : null
    if (value) {
      if (!form.value.is_completed) {
        dateAutoCompleted.value = true
        isProgrammaticToggle.value = true
        form.value.is_completed = true
      }
    } else if (hadDate && dateAutoCompleted.value) {
      isProgrammaticToggle.value = true
      form.value.is_completed = false
      dateAutoCompleted.value = false
    }
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
      notes: data.notes,
    }
  } catch {
    message.error('加载记录失败')
    router.push('/list')
  } finally {
    loading.value = false
  }
}

function onCompletedManualToggle() {
  if (isProgrammaticToggle.value) {
    isProgrammaticToggle.value = false
    return
  }
  dateAutoCompleted.value = false
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

const contactPickerVisible = ref(false)
const contactList = ref<Contact[]>([])
const contactTotal = ref(0)
const contactPage = ref(1)
const contactPageSize = ref(10)
const contactKeyword = ref('')
const contactLoading = ref(false)

async function loadContactPicker() {
  contactLoading.value = true
  try {
    const result = await fetchContacts({
      page: contactPage.value,
      page_size: contactPageSize.value,
      keyword: contactKeyword.value || undefined,
    })
    contactList.value = result.items ?? []
    contactTotal.value = result.total
  } catch {
    message.error('加载通讯录失败')
  } finally {
    contactLoading.value = false
  }
}

function openContactPicker() {
  contactPage.value = 1
  contactKeyword.value = ''
  contactPickerVisible.value = true
  loadContactPicker()
}

function handleContactSearch() {
  contactPage.value = 1
  loadContactPicker()
}

function handleContactPageChange(page: number) {
  contactPage.value = page
  loadContactPicker()
}

function handleContactPageSizeChange(size: number) {
  contactPageSize.value = size
  contactPage.value = 1
  loadContactPicker()
}

function selectContact(contact: Contact) {
  form.value.counterpart_nickname = contact.nickname
  contactPickerVisible.value = false
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
        <n-button type="primary" ghost style="margin-left: 8px; flex-shrink: 0" @click="openContactPicker">
          选择
        </n-button>
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
        <n-switch v-model:value="form.is_completed" @update:value="onCompletedManualToggle" />
      </n-form-item>
      <n-form-item label="备注" path="notes">
        <n-input
          v-model:value="form.notes"
          type="textarea"
          placeholder="请输入备注说明（选填）"
          :autosize="{ minRows: 3, maxRows: 6 }"
          maxlength="500"
          show-count
          clearable
        />
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

  <n-modal
    v-model:show="contactPickerVisible"
    preset="card"
    title="从通讯录选择"
    style="width: 480px"
    :mask-closable="true"
  >
    <n-space vertical :size="12">
      <n-input
        v-model:value="contactKeyword"
        placeholder="搜索昵称或联系方式"
        clearable
        @keyup.enter="handleContactSearch"
        @clear="handleContactSearch"
      />
      <n-spin :show="contactLoading">
        <div v-if="contactList.length === 0" style="min-height: 120px; display: flex; align-items: center; justify-content: center">
          <n-empty description="暂无联系人" />
        </div>
        <div v-else class="contact-picker-list">
          <div
            v-for="contact in contactList"
            :key="contact.id"
            class="contact-picker-item"
            @click="selectContact(contact)"
          >
            <span class="contact-picker-nickname">{{ contact.nickname }}</span>
            <span class="contact-picker-info">{{ contact.contact_info }}</span>
          </div>
        </div>
      </n-spin>
      <n-pagination
        v-if="contactTotal > 0"
        :page="contactPage"
        :page-size="contactPageSize"
        :item-count="contactTotal"
        :page-sizes="[10, 20, 50]"
        show-size-picker
        size="small"
        @update:page="handleContactPageChange"
        @update:page-size="handleContactPageSizeChange"
      />
    </n-space>
  </n-modal>
</template>

<style scoped>
.contact-picker-list {
  max-height: 320px;
  overflow-y: auto;
}

.contact-picker-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.contact-picker-item:hover {
  background-color: rgba(24, 160, 88, 0.08);
}

.contact-picker-nickname {
  font-weight: 500;
  font-size: 14px;
}

.contact-picker-info {
  font-size: 13px;
  color: var(--n-text-color-3);
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
