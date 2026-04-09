<template>
  <ArtSearchBar
    ref="searchBarRef"
    v-model="formData"
    :items="formItems"
    :rules="rules"
    :label-width="90"
    class="user-search-bar"
    @reset="handleReset"
    @search="handleSearch"
  >
  </ArtSearchBar>
</template>

<script setup lang="ts">
  interface Props {
    modelValue: Record<string, any>
  }
  interface Emits {
    (e: 'update:modelValue', value: Record<string, any>): void
    (e: 'search', params: Record<string, any>): void
    (e: 'reset'): void
  }
  const props = defineProps<Props>()
  const emit = defineEmits<Emits>()

  // 表单数据双向绑定
  const searchBarRef = ref()
  const formData = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val)
  })

  // 校验规则
  const rules = {
    // userName: [{ required: true, message: '请输入用户名', trigger: 'blur' }]
  }

  // 角色选项（与数据库一致）
  const roleOptions = [
    { label: '普通用户', value: 'user' },
    { label: '医生', value: 'doctor' },
    { label: '管理员', value: 'admin' }
  ]

  // 状态选项（与数据库一致）
  const statusOptions = [
    { label: '活跃', value: 'active' },
    { label: '禁用', value: 'disabled' }
  ]

  // 表单配置
  const formItems = computed(() => [
    {
      label: '关键词',
      key: 'keyword',
      type: 'input',
      placeholder: '邮箱/手机/昵称',
      clearable: true
    },
    {
      label: '角色',
      key: 'role',
      type: 'select',
      props: {
        placeholder: '请选择角色',
        options: roleOptions,
        clearable: true
      }
    },
    {
      label: '状态',
      key: 'status',
      type: 'select',
      props: {
        placeholder: '请选择状态',
        options: statusOptions,
        clearable: true
      }
    }
  ])

  // 事件
  function handleReset() {
    console.log('重置表单')
    emit('reset')
  }

  async function handleSearch() {
    await searchBarRef.value.validate()
    emit('search', formData.value)
    console.log('表单数据', formData.value)
  }
</script>

<style lang="scss" scoped>
  .user-search-bar {
    padding: 20px 20px 0 !important;
    margin: -20px -20px 16px !important;
    background-color: var(--art-bg-color) !important;
    border-bottom: 1px solid var(--art-border-color);
    border-radius: 0 !important;

    :deep(.search-form-row) {
      margin-bottom: 0;
    }
  }
</style>
