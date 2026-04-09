<template>
  <ElDialog
    v-model="dialogVisible"
    :title="dialogType === 'add' ? '添加用户' : '编辑用户角色'"
    width="30%"
    align-center
  >
    <ElForm ref="formRef" :model="formData" :rules="rules" label-width="100px">
      <!-- 新增模式 -->
      <template v-if="dialogType === 'add'">
        <ElFormItem label="邮箱" prop="email">
          <ElInput v-model="formData.email" placeholder="请输入邮箱（用于登录）" />
        </ElFormItem>
        <ElFormItem label="昵称" prop="nickname">
          <ElInput v-model="formData.nickname" placeholder="请输入用户昵称" />
        </ElFormItem>
        <ElFormItem label="手机号" prop="phone">
          <ElInput v-model="formData.phone" placeholder="请输入手机号（选填）" />
        </ElFormItem>
        <ElFormItem label="用户角色" prop="role">
          <ElSelect v-model="formData.role" placeholder="请选择用户角色">
            <ElOption
              v-for="option in roleOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </ElSelect>
        </ElFormItem>
        <ElAlert
          title="默认密码说明"
          type="info"
          :closable="false"
          show-icon
        >
          <ul style="margin: 0; padding-left: 20px; font-size: 13px">
            <li>管理员默认密码：admin123</li>
            <li>医生默认密码：doctor123</li>
            <li>普通用户默认密码：user123</li>
          </ul>
        </ElAlert>
      </template>

      <!-- 编辑模式 -->
      <template v-else>
      <ElFormItem label="用户ID">
        <ElInput v-model="formData.userId" disabled />
      </ElFormItem>
      <ElFormItem label="用户名">
        <ElInput v-model="formData.nickname" disabled />
      </ElFormItem>
      <ElFormItem label="邮箱">
        <ElInput v-model="formData.email" disabled />
      </ElFormItem>
      <ElFormItem label="用户角色" prop="role">
        <ElSelect v-model="formData.role" placeholder="请选择用户角色">
          <ElOption
            v-for="option in roleOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </ElSelect>
      </ElFormItem>
      </template>
    </ElForm>
    <template #footer>
      <div class="dialog-footer">
        <ElButton @click="dialogVisible = false">取消</ElButton>
        <ElButton type="primary" @click="handleSubmit">提交</ElButton>
      </div>
    </template>
  </ElDialog>
</template>

<script setup lang="ts">
  import { fetchUpdateUserRole, fetchCreateUser } from '@/api/system-manage'
  import type { FormInstance, FormRules } from 'element-plus'
  import { ElMessage } from 'element-plus'

  interface Props {
    visible: boolean
    type: string
    userData?: Partial<Api.SystemManage.UserListItem>
  }

  interface Emits {
    (e: 'update:visible', value: boolean): void
    (e: 'submit'): void
  }

  const props = defineProps<Props>()
  const emit = defineEmits<Emits>()

  // 角色选项列表
  const roleOptions = [
    { label: '普通用户', value: 'user' },
    { label: '医生', value: 'doctor' },
    { label: '管理员', value: 'admin' }
  ]

  // 对话框显示控制
  const dialogVisible = computed({
    get: () => props.visible,
    set: (value) => emit('update:visible', value)
  })

  const dialogType = computed(() => props.type)

  // 表单实例
  const formRef = ref<FormInstance>()

  // 表单数据
  const formData = reactive({
    userId: '',
    nickname: '',
    email: '',
    phone: '',
    role: '' as 'user' | 'doctor' | 'admin' | ''
  })

  // 表单验证规则
  const rules: FormRules = {
    email: [
      { required: true, message: '请输入邮箱', trigger: 'blur' },
      { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
    ],
    nickname: [
      { required: true, message: '请输入昵称', trigger: 'blur' },
      { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
    ],
    phone: [
      { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
    ],
    role: [{ required: true, message: '请选择用户角色', trigger: 'change' }]
  }

  /**
   * 初始化表单数据
   * 根据对话框类型（新增/编辑）填充表单
   */
  const initFormData = () => {
    if (dialogType.value === 'add') {
      // 新增模式，清空表单
      Object.assign(formData, {
        userId: '',
        nickname: '',
        email: '',
        phone: '',
        role: 'user'
      })
    } else {
      // 编辑模式，填充用户数据
    const row = props.userData
    Object.assign(formData, {
      userId: row?.id || '',
      nickname: row?.nickname || '',
      email: row?.email || '',
        phone: row?.phone || '',
      role: row?.role || ''
    })
    }
  }

  /**
   * 监听对话框状态变化
   * 当对话框打开时初始化表单数据并清除验证状态
   */
  watch(
    () => [props.visible, props.type, props.userData],
    ([visible]) => {
      if (visible) {
        initFormData()
        nextTick(() => {
          formRef.value?.clearValidate()
        })
      }
    },
    { immediate: true }
  )

  /**
   * 提交表单
   * 验证通过后调用 API 创建或更新用户
   */
  const handleSubmit = async () => {
    if (!formRef.value) return

    try {
      await formRef.value.validate()

      if (dialogType.value === 'add') {
        // 新增用户
        const response: any = await fetchCreateUser({
          email: formData.email,
          nickname: formData.nickname,
          role: formData.role as 'user' | 'doctor' | 'admin',
          phone: formData.phone || undefined
        })
        
        // 显示默认密码
        ElMessage.success({
          message: response.message || '用户创建成功',
          duration: 5000
        })
        
        dialogVisible.value = false
        emit('submit')
      } else {
        // 编辑用户角色
        if (formData.userId && formData.role) {
          await fetchUpdateUserRole(formData.userId, formData.role as 'user' | 'doctor' | 'admin')
          ElMessage.success('用户角色更新成功')
          dialogVisible.value = false
          emit('submit')
        }
      }
    } catch (error: any) {
      console.error('操作失败:', error)
      if (error !== false) {
        // 非表单验证失败
        ElMessage.error(error?.message || '操作失败，请稍后重试')
      }
    }
  }
</script>
