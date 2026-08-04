<script setup lang="ts">
import { computed, reactive, ref, toRaw } from 'vue'
import {
  CheckmarkCircleOutline,
  CodeSlashOutline,
  CreateOutline,
  LayersOutline,
  ListOutline,
  ShieldCheckmarkOutline,
} from '@vicons/ionicons5'
import { NAlert, NButton, NIcon, NInput, NTag, useMessage } from 'naive-ui'

import AppForm from '@/components/AppForm/index.vue'
import type {
  AppFormField,
  AppFormGroup,
  AppFormRecord,
  FormDemoModel,
  FormDemoReviewer,
} from '@/types'

defineOptions({ name: 'FormDemoView' })

const message = useMessage()
const submitting = ref(false)
const submittedModel = ref<FormDemoModel | null>(null)
let reviewerSequence = 2

const createReviewer = (): FormDemoReviewer => ({
  id: `reviewer-${reviewerSequence++}`,
  name: '',
  role: 'reviewer',
  email: '',
})

const isObjectLike = (value: unknown): value is object =>
  typeof value === 'object' && value !== null

const cloneFormValue = (value: unknown): unknown => {
  if (Array.isArray(value)) {
    return value.map(cloneFormValue)
  }

  if (isObjectLike(value)) {
    const rawValue = toRaw(value)
    return Object.fromEntries(
      Object.entries(rawValue).map(([key, item]) => [key, cloneFormValue(item)]),
    )
  }

  return value
}

const initialValues: FormDemoModel = {
  projectName: '组件规范升级',
  owner: 'admin',
  email: 'admin@example.com',
  priority: 'normal',
  dueDate: Date.now() + 7 * 24 * 60 * 60 * 1000,
  active: true,
  remarks: '',
  reviewers: [
    {
      id: 'reviewer-1',
      name: '项目负责人',
      role: 'owner',
      email: 'owner@example.com',
    },
  ],
}

const form = reactive<FormDemoModel>(cloneFormValue(initialValues) as FormDemoModel)

const selectOptions = {
  owner: [
    { label: '系统管理员', value: 'admin' },
    { label: '运营负责人', value: 'operator' },
    { label: '产品负责人', value: 'product' },
  ],
  priority: [
    { label: '普通', value: 'normal' },
    { label: '紧急', value: 'urgent' },
  ],
  reviewerRole: [
    { label: '负责人', value: 'owner' },
    { label: '评审人', value: 'reviewer' },
    { label: '知会人', value: 'observer' },
  ],
}

const fields: AppFormField[] = [
  {
    key: 'projectName',
    path: 'projectName',
    label: '项目名称',
    required: true,
    componentProps: { placeholder: '请输入项目名称' },
  },
  {
    key: 'owner',
    path: 'owner',
    label: '项目负责人',
    type: 'select',
    required: true,
    componentProps: { options: selectOptions.owner, placeholder: '请选择负责人' },
  },
  {
    key: 'email',
    path: 'email',
    label: '通知邮箱',
    required: true,
    componentProps: { placeholder: 'name@example.com' },
    rules: [
      {
        type: 'email',
        message: '请输入正确的邮箱地址',
        trigger: ['input', 'blur'],
      },
    ],
  },
  {
    key: 'priority',
    path: 'priority',
    label: '优先级',
    type: 'select',
    componentProps: { options: selectOptions.priority },
  },
  {
    key: 'dueDate',
    path: 'dueDate',
    label: '计划完成日期',
    type: 'date',
    componentProps: { type: 'date', clearable: true, placeholder: '请选择日期' },
  },
  {
    key: 'active',
    path: 'active',
    label: '启用项目',
    type: 'switch',
  },
  {
    key: 'remarks',
    path: 'remarks',
    label: '备注说明',
    type: 'custom',
    span: '1 s:2 m:3',
  },
]

const reviewerFields: AppFormField[] = [
  {
    key: 'name',
    path: 'name',
    label: '成员姓名',
    required: true,
    componentProps: { placeholder: '请输入成员姓名' },
  },
  {
    key: 'role',
    path: 'role',
    label: '成员角色',
    type: 'select',
    componentProps: { options: selectOptions.reviewerRole },
  },
  {
    key: 'email',
    path: 'email',
    label: '成员邮箱',
    required: true,
    componentProps: { placeholder: 'name@example.com' },
    rules: [{ type: 'email', message: '请输入正确的邮箱地址', trigger: ['input', 'blur'] }],
  },
]

const groups: AppFormGroup[] = [
  {
    key: 'reviewers',
    path: 'reviewers',
    title: '评审成员',
    description: '分组字段会自动映射到 reviewers[index]，校验路径也会随索引更新。',
    itemKey: 'id',
    minItems: 1,
    maxItems: 5,
    fields: reviewerFields,
    createItem: createReviewer,
    addText: '新增成员',
    removeText: '移除成员',
  },
]

const resultJson = computed(() =>
  submittedModel.value ? JSON.stringify(submittedModel.value, null, 2) : '',
)

const handleSubmit = async (model: AppFormRecord): Promise<void> => {
  submitting.value = true
  try {
    await new Promise<void>((resolve) => {
      window.setTimeout(resolve, 450)
    })
    submittedModel.value = cloneFormValue(model) as FormDemoModel
    message.success('表单校验通过，演示提交已完成')
  } finally {
    submitting.value = false
  }
}

const handleReset = (): void => {
  submittedModel.value = null
  message.info('表单已恢复初始值')
}
</script>

<template>
  <main class="form-demo-page">
    <header class="form-demo-header">
      <div>
        <div class="form-demo-eyebrow">
          <NIcon :size="16" aria-hidden="true"><CreateOutline /></NIcon>
          <span>组件演示 / AppForm</span>
        </div>
        <h1>标准提交表单</h1>
        <p>集中演示布局配置、自定义字段、动态分组、标准校验和提交状态。</p>
      </div>
      <NTag type="info" round>交互示例</NTag>
    </header>

    <div class="form-demo-layout">
      <section class="form-demo-panel" aria-labelledby="form-demo-title">
        <div class="form-demo-panel__header">
          <div>
            <h2 id="form-demo-title">项目登记</h2>
            <p>字段配置由 schema 驱动，提交事件交由页面处理。</p>
          </div>
          <NIcon :size="24" color="var(--app-color-primary)" aria-hidden="true">
            <CheckmarkCircleOutline />
          </NIcon>
        </div>

        <AppForm
          :model="form"
          :initial-values="initialValues"
          :fields="fields"
          :groups="groups"
          :loading="submitting"
          :layout="{
            labelPlacement: 'top',
            columns: '1 s:2 m:3',
            responsive: 'screen',
            xGap: 20,
            yGap: 8,
          }"
          @submit="handleSubmit"
          @reset="handleReset"
        >
          <template #field-remarks="{ value, setValue }">
            <NInput
              type="textarea"
              :value="typeof value === 'string' ? value : ''"
              :autosize="{ minRows: 3, maxRows: 6 }"
              placeholder="补充项目背景、风险或交付说明"
              @update:value="setValue"
            />
          </template>

          <template #actions="{ loading, submit, reset }">
            <NButton attr-type="button" :disabled="loading" @click="reset"> 重置演示数据 </NButton>
            <NButton
              attr-type="button"
              type="primary"
              :loading="loading"
              class="form-demo-submit"
              @click="submit"
            >
              <template #icon>
                <NIcon><CheckmarkCircleOutline /></NIcon>
              </template>
              提交表单
            </NButton>
          </template>
        </AppForm>
      </section>

      <aside class="form-demo-aside" aria-labelledby="form-demo-guide-title">
        <NAlert type="info" :show-icon="false" class="form-demo-note">
          <strong>演示说明</strong>
          <p>提交会模拟短暂请求，用于观察 Loading 和重复提交保护；不会写入后端数据。</p>
        </NAlert>

        <section class="form-demo-guide">
          <div class="form-demo-guide__heading">
            <NIcon :size="18" aria-hidden="true"><LayersOutline /></NIcon>
            <h2 id="form-demo-guide-title">本页覆盖能力</h2>
          </div>
          <ul class="form-demo-capabilities">
            <li>
              <NIcon :size="16" aria-hidden="true"><ListOutline /></NIcon>
              <span>栅格布局与响应式字段排列</span>
            </li>
            <li>
              <NIcon :size="16" aria-hidden="true"><CodeSlashOutline /></NIcon>
              <span>自定义备注控件和字段插槽</span>
            </li>
            <li>
              <NIcon :size="16" aria-hidden="true"><LayersOutline /></NIcon>
              <span>评审成员分组的新增、删除和数量限制</span>
            </li>
            <li>
              <NIcon :size="16" aria-hidden="true"><ShieldCheckmarkOutline /></NIcon>
              <span>必填、邮箱和动态分组路径校验</span>
            </li>
          </ul>
        </section>

        <section v-if="submittedModel" class="form-demo-result">
          <div class="form-demo-guide__heading">
            <NIcon :size="18" aria-hidden="true"><CheckmarkCircleOutline /></NIcon>
            <h2>最近一次提交</h2>
          </div>
          <pre>{{ resultJson }}</pre>
        </section>
      </aside>
    </div>
  </main>
</template>

<style scoped>
.form-demo-page {
  display: grid;
  gap: 20px;
  min-width: 0;
  color: var(--app-color-text);
}

.form-demo-header,
.form-demo-panel__header,
.form-demo-guide__heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.form-demo-header h1,
.form-demo-header p,
.form-demo-eyebrow,
.form-demo-panel__header h2,
.form-demo-panel__header p,
.form-demo-guide__heading h2,
.form-demo-note p {
  margin: 0;
}

.form-demo-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  color: var(--app-color-primary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.form-demo-header h1 {
  font-size: 26px;
  line-height: 1.2;
}

.form-demo-header p,
.form-demo-panel__header p {
  margin-top: 8px;
  color: var(--app-color-text-muted);
  font-size: 14px;
}

.form-demo-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 320px);
  align-items: start;
  gap: 20px;
}

.form-demo-panel,
.form-demo-guide,
.form-demo-result {
  border: 1px solid var(--app-color-border);
  border-radius: 10px;
  background: var(--app-color-surface);
}

.form-demo-panel {
  min-width: 0;
  padding: 24px;
}

.form-demo-panel__header {
  align-items: center;
  margin-bottom: 24px;
}

.form-demo-panel__header h2,
.form-demo-guide__heading h2 {
  font-size: 16px;
  line-height: 1.4;
}

.form-demo-aside {
  display: grid;
  gap: 16px;
  min-width: 0;
}

.form-demo-note {
  line-height: 1.6;
}

.form-demo-note p {
  margin-top: 6px;
}

.form-demo-guide,
.form-demo-result {
  padding: 18px;
}

.form-demo-guide__heading {
  align-items: center;
  justify-content: flex-start;
  color: var(--app-color-primary);
}

.form-demo-guide__heading h2 {
  color: var(--app-color-text);
}

.form-demo-capabilities {
  display: grid;
  gap: 14px;
  margin: 18px 0 0;
  padding: 0;
  list-style: none;
}

.form-demo-capabilities li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  color: var(--app-color-text-muted);
  font-size: 13px;
  line-height: 1.5;
}

.form-demo-capabilities .n-icon {
  flex: 0 0 auto;
  margin-top: 2px;
  color: var(--app-color-primary);
}

.form-demo-result pre {
  max-height: 320px;
  margin: 16px 0 0;
  overflow: auto;
  padding: 12px;
  border-radius: 6px;
  color: var(--app-color-text-muted);
  background: var(--app-color-surface-muted);
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

@media (width <= 880px) {
  .form-demo-layout {
    grid-template-columns: 1fr;
  }
}

@media (width <= 560px) {
  .form-demo-panel {
    padding: 16px;
  }

  .form-demo-header {
    align-items: flex-start;
  }
}
</style>
